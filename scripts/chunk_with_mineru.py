#!/usr/bin/env python3
"""使用MinerU对PDF文档进行分块"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.mineru_chunker import MinerUChunker


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='使用MinerU对PDF进行分块')
    parser.add_argument('pdf_path', help='PDF文件路径')
    parser.add_argument('--chunk-size', type=int, default=1000, help='分块大小')
    parser.add_argument('--overlap', type=int, default=200, help='重叠大小')
    parser.add_argument('--output', help='输出JSON文件路径')
    
    args = parser.parse_args()
    
    # 创建chunker
    chunker = MinerUChunker(
        chunk_size=args.chunk_size,
        chunk_overlap=args.overlap
    )
    
    # 处理PDF
    print(f"正在处理: {args.pdf_path}")
    chunks = chunker.chunk_from_pdf(args.pdf_path)
    
    print(f"生成了 {len(chunks)} 个chunks")
    
    # 保存结果
    if args.output:
        output_path = args.output
    else:
        pdf_path = Path(args.pdf_path)
        output_path = pdf_path.parent / f"{pdf_path.stem}_chunks.json"
    
    chunker.save_chunks(chunks, output_path)
    print(f"已保存到: {output_path}")
    
    # 显示前3个chunks的预览
    print("\n前3个chunks预览:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i} ---")
        print(f"长度: {chunk['length']}")
        print(f"章节: {chunk['metadata'].get('section', 'N/A')}")
        print(f"内容预览: {chunk['text'][:200]}...")


if __name__ == "__main__":
    main()
