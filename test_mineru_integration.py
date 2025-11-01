#!/usr/bin/env python3
"""快速测试 MinerU 集成"""

from pathlib import Path
from src.parsers import ParserFactory

def test_integration():
    """测试 MinerU 集成"""
    
    print("=" * 60)
    print("测试 MinerU 集成")
    print("=" * 60)
    
    # 测试 1: 创建解析器
    print("\n[1/4] 测试创建解析器...")
    try:
        parser = ParserFactory.create_parser("mineru", use_gpu=True)
        print("✓ 解析器创建成功")
    except Exception as e:
        print(f"✗ 解析器创建失败: {e}")
        return
    
    # 测试 2: 检查 GPU 支持
    print("\n[2/4] 检查 GPU 支持...")
    print(f"✓ GPU 配置: {parser.use_gpu}")
    
    # 测试 3: 解析 PDF
    print("\n[3/4] 测试 PDF 解析...")
    pdf_path = "data/pdfs/a.pdf"
    
    if not Path(pdf_path).exists():
        print(f"⚠ 测试 PDF 不存在: {pdf_path}")
        print("  请将 PDF 文件放到 data/pdfs/ 目录")
    else:
        try:
            result = parser.parse(pdf_path)
            print(f"✓ 解析成功")
            print(f"  - 标题: {result.title[:50]}...")
            print(f"  - 作者: {', '.join(result.authors[:3])}")
            print(f"  - 全文长度: {len(result.full_text)} 字符")
            print(f"  - 章节数: {len(result.sections)}")
        except Exception as e:
            print(f"✗ 解析失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 测试 4: 测试所有解析器
    print("\n[4/4] 测试所有解析器类型...")
    parser_types = ["pymupdf", "mineru"]
    
    for ptype in parser_types:
        try:
            p = ParserFactory.create_parser(ptype, use_gpu=False)
            print(f"✓ {ptype}: 可用")
        except Exception as e:
            print(f"✗ {ptype}: {e}")
    
    print("\n" + "=" * 60)
    print("✓ 集成测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_integration()
