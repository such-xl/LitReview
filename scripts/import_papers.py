#!/usr/bin/env python3
"""批量导入PDF论文"""

import sys
from pathlib import Path
from tqdm import tqdm

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from src.database import SQLManager, VectorManager
from src.parsers.marker_parser import MarkerParser
from src.parsers.pymupdf_parser import PyMuPDFParser
from src.parsers.text_chunker import TextChunker

def import_pdf(pdf_path: str, parser_type: str = "pymupdf"):
    """导入单个PDF"""
    # 初始化
    sql_manager = SQLManager(str(settings.sqlite_path))
    vector_manager = VectorManager(str(settings.chroma_path))
    chunker = TextChunker(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    
    # 选择解析器
    if parser_type == "marker":
        try:
            print("0使用PyMuPDF解析器")
            parser = MarkerParser()
        except ImportError:
            print("Marker未安装，使用PyMuPDF")
            parser = PyMuPDFParser()
    else:
        print("1使用PyMuPDF解析器")
        parser = PyMuPDFParser()
    
    print(f"解析PDF: {pdf_path}")
    
    try:
        # 解析PDF
        parsed = parser.parse(pdf_path)
        
        # 保存到数据库
        paper_id = sql_manager.add_paper(
            title=parsed.title,
            pdf_path=pdf_path,
            authors=', '.join(parsed.authors),
            raw_text=parsed.full_text,
            markdown_text=parsed.markdown_text
        )
        
        print(f"✓ 论文已保存 (ID: {paper_id}): {parsed.title}")
        
        # 分块并存储向量
        chunks = chunker.chunk_text(parsed.full_text, {"paper_id": paper_id, "title": parsed.title})
        
        if chunks:
            chunk_texts = [chunk["text"] for chunk in chunks]
            chunk_metadatas = [chunk.get("metadata", {}) for chunk in chunks]
            vector_manager.add_fulltext(paper_id, chunk_texts, chunk_metadatas)
            print(f"✓ 已创建 {len(chunks)} 个文本块")
        
        # 存储摘要向量
        if parsed.abstract:
            vector_manager.add_abstract(paper_id, parsed.abstract, {"paper_id": paper_id, "title": parsed.title})
            print(f"✓ 摘要已索引")
        
        return paper_id
        
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return None

def import_directory(directory: str, parser_type: str = "pymupdf"):
    """批量导入目录中的所有PDF"""
    pdf_dir = Path(directory)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"未找到PDF文件: {directory}")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件")
    
    success_count = 0
    for pdf_file in tqdm(pdf_files, desc="导入进度"):
        paper_id = import_pdf(str(pdf_file), parser_type)
        if paper_id:
            success_count += 1
    
    print(f"\n导入完成: {success_count}/{len(pdf_files)} 成功")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="导入PDF论文到数据库")
    parser.add_argument("path", help="PDF文件或目录路径")
    parser.add_argument("--parser", choices=["marker", "pymupdf"], default="pymupdf", 
                       help="PDF解析器类型 (默认: pymupdf)")
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if path.is_file() and path.suffix == '.pdf':
        import_pdf(str(path), args.parser)
    elif path.is_dir():
        import_directory(str(path), args.parser)
    else:
        print(f"无效路径: {path}")

if __name__ == "__main__":
    main()
