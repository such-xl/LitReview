import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.parsers.pymupdf_parser import PyMuPDFParser
from src.parsers.text_chunker import TextChunker

def test_pymupdf_parser():
    """测试PyMuPDF解析器"""
    print("测试PyMuPDF解析器...")
    
    # 创建测试PDF路径
    test_pdf = project_root / "data" / "pdfs" / "test.pdf"
    
    if not test_pdf.exists():
        print(f"请将测试PDF放在: {test_pdf}")
        return
    
    parser = PyMuPDFParser()
    parsed = parser.parse(str(test_pdf))
    
    print(f"\n标题: {parsed.title}")
    print(f"作者: {', '.join(parsed.authors)}")
    print(f"摘要长度: {len(parsed.abstract)} 字符")
    print(f"全文长度: {len(parsed.full_text)} 字符")
    print(f"章节数: {len(parsed.sections)}")
    print(f"表格数: {len(parsed.tables)}")
    print(f"公式数: {len(parsed.equations)}")
    print(f"参考文献数: {len(parsed.references)}")
    
    if parsed.sections:
        print(f"\n章节列表:")
        for section_name in parsed.sections.keys():
            print(f"  - {section_name}")

def test_text_chunker():
    """测试文本分块"""
    print("\n测试文本分块...")
    
    chunker = TextChunker(chunk_size=500, chunk_overlap=100)
    
    test_text = """
    This is the first paragraph. It contains some text.
    
    This is the second paragraph. It contains more text and is longer than the first one.
    
    This is the third paragraph. It also contains text.
    """ * 10
    
    chunks = chunker.chunk_text(test_text)
    
    print(f"文本长度: {len(test_text)} 字符")
    print(f"分块数量: {len(chunks)}")
    
    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i}:")
        print(f"  长度: {chunk['length']} 字符")
        print(f"  预览: {chunk['text'][:100]}...")

if __name__ == "__main__":
    test_pymupdf_parser()
    test_text_chunker()
