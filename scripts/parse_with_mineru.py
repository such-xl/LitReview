#!/usr/bin/env python3
"""使用MinerU解析PDF的示例脚本"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers import ParserFactory

def main():
    # 创建MinerU解析器
    parser = ParserFactory.create_parser(
        parser_type="mineru",
        use_gpu=True  # 设置为False使用CPU
    )
    
    # 解析PDF
    pdf_path = "data/pdfs/a.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ 文件不存在: {pdf_path}")
        return
    
    print(f"开始解析: {pdf_path}\n")
    
    try:
        result = parser.parse(pdf_path)
        
        print("=" * 60)
        print("解析结果:")
        print("=" * 60)
        print(f"📄 标题: {result.title}")
        print(f"👥 作者: {', '.join(result.authors)}")
        print(f"📝 摘要长度: {len(result.abstract)} 字符")
        print(f"📖 全文长度: {len(result.full_text)} 字符")
        print(f"📑 章节数: {len(result.sections)}")
        print(f"📊 表格数: {len(result.tables)}")
        print(f"🔢 公式数: {len(result.equations)}")
        print(f"📚 参考文献数: {len(result.references)}")
        print("=" * 60)
        
        # 显示摘要
        if result.abstract:
            print(f"\n摘要预览:\n{result.abstract[:300]}...\n")
        
        # 显示章节
        if result.sections:
            print("\n章节列表:")
            for section_name in result.sections.keys():
                print(f"  - {section_name}")
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
