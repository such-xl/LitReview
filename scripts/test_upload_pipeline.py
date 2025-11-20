#!/usr/bin/env python3
"""测试完整的上传流程：解析 -> LLM提取 -> 数据库存储"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.parsers.mineru_chunker import MinerUParser
from src.llm import LLMFactory
from src.database import SQLManager, VectorManager
from src.parsers import TextChunker
from config import settings

def test_upload_pipeline(pdf_path: str, use_llm=True, use_gpu=True):
    """测试完整上传流程"""
    
    print("=" * 60)
    print("测试上传流程")
    print("=" * 60)
    
    # 1. 初始化LLM
    llm = None
    if use_llm:
        try:
            print("\n[1/5] 初始化LLM...")
            llm = LLMFactory.create_llm(provider="ollama", model="llama2")
            print("✓ LLM已加载")
        except Exception as e:
            print(f"⚠ LLM加载失败: {e}")
    
    # 2. 解析PDF
    print("\n[2/5] 解析PDF...")
    parser = MinerUParser(use_gpu=use_gpu, llm=llm)
    parsed = parser.parse(pdf_path)
    
    print(f"✓ 解析完成")
    print(f"  - 标题: {parsed.title}")
    print(f"  - 作者: {', '.join(parsed.authors) if isinstance(parsed.authors, list) else parsed.authors}")
    print(f"  - 摘要长度: {len(parsed.abstract)} 字符")
    print(f"  - 全文长度: {len(parsed.full_text)} 字符")
    
    # 3. 存入数据库
    print("\n[3/5] 存入SQLite数据库...")
    sql_manager = SQLManager(str(settings.sqlite_path))
    
    paper_id = sql_manager.add_paper(
        title=parsed.title,
        pdf_path=pdf_path,
        authors=', '.join(parsed.authors) if isinstance(parsed.authors, list) else parsed.authors,
        raw_text=parsed.full_text,
        markdown_text=parsed.markdown_text
    )
    
    print(f"✓ 已存入数据库，paper_id: {paper_id}")
    
    # 4. 文本分块
    print("\n[4/5] 文本分块...")
    chunker = TextChunker(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    chunks = chunker.chunk_text(parsed.full_text, {"paper_id": paper_id})
    
    print(f"✓ 分块完成，共 {len(chunks)} 个块")
    
    # 5. 向量化存储
    print("\n[5/5] 向量化存储到ChromaDB...")
    vector_manager = VectorManager(str(settings.chroma_path))
    
    if chunks:
        chunk_texts = [chunk["text"] for chunk in chunks]
        vector_manager.add_fulltext(paper_id, chunk_texts)
        print(f"✓ 向量化完成")
    
    # 验证
    print("\n" + "=" * 60)
    print("验证结果")
    print("=" * 60)
    
    # 从数据库读取
    paper = sql_manager.get_paper(paper_id)
    print(f"\n数据库中的论文:")
    print(f"  - ID: {paper['id']}")
    print(f"  - 标题: {paper['title']}")
    print(f"  - 作者: {paper['authors']}")
    
    # 测试检索
    print(f"\n测试语义检索...")
    results = vector_manager.search(parsed.title[:50], top_k=1)
    if results:
        print(f"✓ 检索成功，找到 {len(results)} 个结果")
        print(f"  - 相似度: {results[0]['score']:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试上传流程")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("--no-llm", action="store_true", help="不使用LLM")
    parser.add_argument("--no-gpu", action="store_true", help="不使用GPU")
    
    args = parser.parse_args()
    
    if not Path(args.pdf_path).exists():
        print(f"错误: 文件不存在 {args.pdf_path}")
        sys.exit(1)
    
    test_upload_pipeline(
        args.pdf_path,
        use_llm=not args.no_llm,
        use_gpu=not args.no_gpu
    )
