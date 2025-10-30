import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from src.database import SQLManager, VectorManager
from src.retrieval import QueryEngine
from src.llm import LLMFactory
from src.synthesis import LiteratureReviewGenerator, CitationManager

def test_citation_manager():
    """测试引用管理"""
    print("测试引用管理...")
    
    citation_manager = CitationManager()
    
    # 模拟论文
    papers = [
        {
            'id': 1,
            'title': 'Deep Learning for NLP',
            'authors': 'Smith, J., & Johnson, A.',
            'year': 2020,
            'venue': 'ACL'
        },
        {
            'id': 2,
            'title': 'Transformer Networks',
            'authors': 'Brown, B.',
            'year': 2021,
            'venue': 'NeurIPS'
        }
    ]
    
    # 添加引用
    for paper in papers:
        citation = citation_manager.add_citation(paper)
        print(f"引用标记: {citation}")
    
    # 生成参考文献
    print("\n参考文献列表 (APA):")
    print(citation_manager.generate_bibliography("apa"))
    
    print("\n✓ 引用管理测试成功")

def test_review_generation():
    """测试综述生成"""
    print("\n\n测试综述生成...")
    
    sql_manager = SQLManager(str(settings.sqlite_path))
    vector_manager = VectorManager(str(settings.chroma_path))
    query_engine = QueryEngine(vector_manager, sql_manager)
    
    # 获取一些论文
    papers = sql_manager.get_all_papers()[:5]
    
    if not papers:
        print("数据库中没有论文，跳过测试")
        return
    
    print(f"使用 {len(papers)} 篇论文")
    
    # 创建LLM
    try:
        llm = LLMFactory.create_llm(provider="ollama")
        generator = LiteratureReviewGenerator(llm, sql_manager)
        
        # 生成摘要
        print("\n生成摘要...")
        summary = generator.generate_summary(papers, "机器学习")
        print(f"\n摘要:\n{summary}")
        
        print("\n✓ 综述生成测试成功")
        
    except Exception as e:
        print(f"✗ 综述生成测试失败: {e}")

def test_structured_review():
    """测试结构化综述"""
    print("\n\n测试结构化综述...")
    
    sql_manager = SQLManager(str(settings.sqlite_path))
    vector_manager = VectorManager(str(settings.chroma_path))
    
    papers = sql_manager.get_all_papers()[:3]
    
    if not papers:
        print("数据库中没有论文，跳过测试")
        return
    
    try:
        llm = LLMFactory.create_llm(provider="ollama")
        generator = LiteratureReviewGenerator(llm, sql_manager)
        
        # 生成结构化综述
        sections = ["研究背景", "主要方法"]
        review_sections = generator.generate_structured_review(
            papers, "深度学习", sections
        )
        
        print("\n结构化综述:")
        for section_name, content in review_sections.items():
            print(f"\n## {section_name}")
            print(content[:200] + "...")
        
        print("\n✓ 结构化综述测试成功")
        
    except Exception as e:
        print(f"✗ 结构化综述测试失败: {e}")

if __name__ == "__main__":
    print("请确保Ollama正在运行且数据库中有论文\n")
    
    test_citation_manager()
    test_review_generation()
    test_structured_review()
