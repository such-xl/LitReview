#!/usr/bin/env python3
"""生成文献综述"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from src.database import SQLManager, VectorManager
from src.retrieval import QueryEngine
from src.llm import LLMFactory
from src.synthesis import LiteratureReviewGenerator, CitationManager

def generate_review(
    topic: str,
    n_papers: int = 20,
    output_file: Optional[str] = None,
    llm_provider: str = "ollama",
    model: str = None,
    structured: bool = False
):
    """生成文献综述"""
    
    print(f"主题: {topic}")
    print(f"使用论文数量: {n_papers}\n")
    
    # 初始化
    sql_manager = SQLManager(str(settings.sqlite_path))
    vector_manager = VectorManager(str(settings.chroma_path))
    query_engine = QueryEngine(vector_manager, sql_manager)
    
    # 搜索相关论文
    print("搜索相关论文...")
    papers = query_engine.query(topic, method="hybrid", n_results=n_papers)
    
    if not papers:
        print("未找到相关论文")
        return
    
    print(f"找到 {len(papers)} 篇相关论文\n")
    
    # 创建LLM
    llm = LLMFactory.create_llm(
        provider=llm_provider,
        model=model or settings.DEFAULT_LOCAL_MODEL,
        base_url=settings.OLLAMA_BASE_URL
    )
    
    # 生成综述
    generator = LiteratureReviewGenerator(llm, sql_manager)
    citation_manager = CitationManager()
    
    print("生成文献综述...\n")
    
    if structured:
        # 生成结构化综述
        review_sections = generator.generate_structured_review(papers, topic)
        
        # 组装完整综述
        review_text = f"# {topic} - 文献综述\n\n"
        
        for section_name, section_content in review_sections.items():
            review_text += f"## {section_name}\n\n{section_content}\n\n"
    else:
        # 生成完整综述
        review_text = generator.generate_review(papers, topic, max_papers=n_papers)
        review_text = f"# {topic} - 文献综述\n\n{review_text}\n\n"
    
    # 添加参考文献
    review_text += "## 参考文献\n\n"
    
    for i, paper in enumerate(papers, 1):
        citation_manager.add_citation(paper)
    
    review_text += citation_manager.generate_bibliography()
    
    # 输出
    print("=" * 80)
    print(review_text)
    print("=" * 80)
    
    # 保存到文件
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(review_text, encoding='utf-8')
        print(f"\n✓ 综述已保存到: {output_file}")
    
    return review_text

def generate_summary(topic: str, n_papers: int = 10):
    """生成简短摘要"""
    
    print(f"主题: {topic}\n")
    
    # 初始化
    sql_manager = SQLManager(str(settings.sqlite_path))
    vector_manager = VectorManager(str(settings.chroma_path))
    query_engine = QueryEngine(vector_manager, sql_manager)
    
    # 搜索相关论文
    print("搜索相关论文...")
    papers = query_engine.query(topic, method="hybrid", n_results=n_papers)
    
    if not papers:
        print("未找到相关论文")
        return
    
    print(f"找到 {len(papers)} 篇相关论文\n")
    
    # 创建LLM
    llm = LLMFactory.create_llm(provider="ollama")
    
    # 生成摘要
    generator = LiteratureReviewGenerator(llm, sql_manager)
    
    print("生成摘要...\n")
    summary = generator.generate_summary(papers, topic)
    
    print("=" * 80)
    print(summary)
    print("=" * 80)
    
    return summary

def main():
    import argparse
    from typing import Optional
    
    parser = argparse.ArgumentParser(description="生成文献综述")
    parser.add_argument("topic", help="研究主题")
    parser.add_argument("-n", "--num-papers", type=int, default=20, 
                       help="使用的论文数量 (默认: 20)")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("--provider", default="ollama",
                       choices=["ollama", "openai", "claude"],
                       help="LLM提供商 (默认: ollama)")
    parser.add_argument("--model", help="模型名称")
    parser.add_argument("--structured", action="store_true",
                       help="生成结构化综述（按章节）")
    parser.add_argument("--summary", action="store_true",
                       help="只生成简短摘要")
    
    args = parser.parse_args()
    
    if args.summary:
        generate_summary(args.topic, args.num_papers)
    else:
        generate_review(
            args.topic,
            args.num_papers,
            args.output,
            args.provider,
            args.model,
            args.structured
        )

if __name__ == "__main__":
    main()
