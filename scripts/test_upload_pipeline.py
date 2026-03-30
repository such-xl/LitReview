#!/usr/bin/env python3
"""测试完整的上传流程：解析 -> 数据库存储 -> 向量索引"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import SQLManager, VectorManager
from src.parsers import ParserFactory, TextChunker
from config import settings

def test_upload_pipeline(pdf_path: str, parser_type: str = "pymupdf"):
    """测试完整上传流程"""
    
    print("=" * 60)
    print("测试上传流程")
    print("=" * 60)
    
    print("\n[1/4] 解析PDF...")
    parser = ParserFactory.create_parser(parser_type, use_gpu=False)
    parsed = parser.parse(pdf_path)
    
    print(f"✓ 解析完成")
    print(f"  - 标题: {parsed.title}")
    print(f"  - 作者: {', '.join(parsed.authors) if isinstance(parsed.authors, list) else parsed.authors}")
    print(f"  - 摘要长度: {len(parsed.abstract)} 字符")
    print(f"  - 全文长度: {len(parsed.full_text)} 字符")
    
    print("\n[2/4] 存入SQLite数据库...")
    sql_manager = SQLManager(str(settings.sqlite_path))
    
    paper_id = sql_manager.add_paper(
        title=parsed.title,
        pdf_path=pdf_path,
        authors=", ".join(parsed.authors) if isinstance(parsed.authors, list) else parsed.authors,
        abstract=parsed.abstract,
        raw_text=parsed.full_text,
        markdown_text=parsed.markdown_text
    )
    
    print(f"✓ 已存入数据库，paper_id: {paper_id}")
    
    print("\n[3/4] 文本分块...")
    chunker = TextChunker(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    chunks = chunker.chunk_text(parsed.full_text, {"paper_id": paper_id})
    
    print(f"✓ 分块完成，共 {len(chunks)} 个块")
    
    print("\n[4/4] 向量化存储到ChromaDB...")
    vector_manager = VectorManager(str(settings.chroma_path))
    
    if chunks:
        chunk_texts = [chunk["text"] for chunk in chunks]
        chunk_metadatas = [chunk.get("metadata", {}) for chunk in chunks]
        vector_manager.add_fulltext(paper_id, chunk_texts, chunk_metadatas)
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
    results = vector_manager.search_fulltext(parsed.title[:50], n_results=1)
    if results.get("ids") and results["ids"][0]:
        print(f"✓ 检索成功，找到 {len(results['ids'][0])} 个结果")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试上传流程")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("--parser", choices=["pymupdf", "marker"], default="pymupdf", help="解析器类型")
    
    args = parser.parse_args()
    
    if not Path(args.pdf_path).exists():
        print(f"错误: 文件不存在 {args.pdf_path}")
        sys.exit(1)
    
    test_upload_pipeline(
        args.pdf_path,
        parser_type=args.parser,
    )
