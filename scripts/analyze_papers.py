#!/usr/bin/env python3
"""批量分析论文"""

import sys
from pathlib import Path
from tqdm import tqdm

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from src.database import SQLManager, VectorManager
from src.llm.llm_factory import LLMFactory
from src.analysis.extractor import PaperExtractor

def analyze_paper(paper_id: int, llm_provider: str = "ollama", model: str = None):
    """分析单篇论文"""
    
    # 初始化
    sql_manager = SQLManager(str(settings.sqlite_path))
    vector_manager = VectorManager(str(settings.chroma_path))
    
    # 创建LLM
    llm = LLMFactory.create_llm(
        provider=llm_provider,
        model=model or settings.DEFAULT_LOCAL_MODEL,
        base_url=settings.OLLAMA_BASE_URL
    )
    
    extractor = PaperExtractor(llm)
    
    # 获取论文
    paper = sql_manager.get_paper(paper_id)
    if not paper:
        print(f"论文不存在: {paper_id}")
        return False
    
    print(f"分析论文 (ID: {paper_id}): {paper['title']}")
    
    # 提取信息
    try:
        analysis = extractor.extract_info(paper['raw_text'] or paper['markdown_text'])
        
        # 保存分析结果
        sql_manager.add_analysis(paper_id, analysis, f"{llm_provider}/{model or settings.DEFAULT_LOCAL_MODEL}")
        
        print(f"✓ 分析完成")
        print(f"  研究问题: {analysis['research_question'][:100]}...")
        print(f"  关键词: {', '.join(analysis['keywords'][:5])}")
        
        # 保存分析向量
        analysis_text = f"""
研究问题: {analysis['research_question']}
方法: {analysis['methodology']}
主要发现: {' '.join(analysis['main_findings'])}
核心贡献: {' '.join(analysis['key_contributions'])}
关键词: {' '.join(analysis['keywords'])}
"""
        vector_manager.add_analysis(paper_id, analysis_text, {
            "paper_id": paper_id,
            "title": paper['title']
        })
        
        return True
        
    except Exception as e:
        print(f"✗ 分析失败: {e}")
        return False

def analyze_all_papers(llm_provider: str = "ollama", model: str = None):
    """分析所有未分析的论文"""
    
    sql_manager = SQLManager(str(settings.sqlite_path))
    
    # 获取所有论文
    papers = sql_manager.get_all_papers()
    
    if not papers:
        print("没有找到论文")
        return
    
    print(f"找到 {len(papers)} 篇论文")
    
    # 过滤已分析的论文
    unanalyzed = []
    for paper in papers:
        analysis = sql_manager.get_paper_analysis(paper['id'])
        if not analysis:
            unanalyzed.append(paper)
    
    if not unanalyzed:
        print("所有论文都已分析")
        return
    
    print(f"需要分析 {len(unanalyzed)} 篇论文")
    
    success_count = 0
    for paper in tqdm(unanalyzed, desc="分析进度"):
        if analyze_paper(paper['id'], llm_provider, model):
            success_count += 1
    
    print(f"\n分析完成: {success_count}/{len(unanalyzed)} 成功")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="分析论文并提取关键信息")
    parser.add_argument("--paper-id", type=int, help="指定论文ID")
    parser.add_argument("--all", action="store_true", help="分析所有未分析的论文")
    parser.add_argument("--provider", default="ollama", 
                       choices=["ollama", "openai", "claude"],
                       help="LLM提供商 (默认: ollama)")
    parser.add_argument("--model", help="模型名称")
    
    args = parser.parse_args()
    
    if args.paper_id:
        analyze_paper(args.paper_id, args.provider, args.model)
    elif args.all:
        analyze_all_papers(args.provider, args.model)
    else:
        print("请指定 --paper-id 或 --all")
        parser.print_help()

if __name__ == "__main__":
    main()
