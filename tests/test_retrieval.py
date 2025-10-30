import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from src.database import SQLManager, VectorManager
from src.retrieval import QueryEngine

def test_semantic_search():
    """测试语义搜索"""
    print("测试语义搜索...")
    
    sql_manager = SQLManager(str(settings.sqlite_path))
    vector_manager = VectorManager(str(settings.chroma_path))
    query_engine = QueryEngine(vector_manager, sql_manager)
    
    query = "deep learning natural language processing"
    results = query_engine.query(query, method="semantic", n_results=5)
    
    print(f"\n查询: {query}")
    print(f"找到 {len(results)} 篇论文")
    
    for i, paper in enumerate(results, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   相关度: {paper.get('relevance_score', 0):.3f}")

def test_hybrid_search():
    """测试混合搜索"""
    print("\n\n测试混合搜索...")
    
    sql_manager = SQLManager(str(settings.sqlite_path))
    vector_manager = VectorManager(str(settings.chroma_path))
    query_engine = QueryEngine(vector_manager, sql_manager)
    
    query = "machine learning"
    results = query_engine.query(query, method="hybrid", n_results=5)
    
    print(f"\n查询: {query}")
    print(f"找到 {len(results)} 篇论文")
    
    for i, paper in enumerate(results, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   综合得分: {paper.get('final_score', 0):.3f}")

def test_similar_papers():
    """测试相似论文查找"""
    print("\n\n测试相似论文查找...")
    
    sql_manager = SQLManager(str(settings.sqlite_path))
    vector_manager = VectorManager(str(settings.chroma_path))
    query_engine = QueryEngine(vector_manager, sql_manager)
    
    # 获取第一篇论文
    papers = sql_manager.get_all_papers()
    if not papers:
        print("数据库中没有论文")
        return
    
    paper_id = papers[0]['id']
    print(f"\n基准论文: {papers[0]['title']}")
    
    results = query_engine.find_similar(paper_id, n_results=3)
    
    print(f"\n找到 {len(results)} 篇相似论文")
    
    for i, paper in enumerate(results, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   相似度: {paper.get('relevance_score', 0):.3f}")

def test_list_papers():
    """测试列出所有论文"""
    print("\n\n测试列出所有论文...")
    
    sql_manager = SQLManager(str(settings.sqlite_path))
    vector_manager = VectorManager(str(settings.chroma_path))
    query_engine = QueryEngine(vector_manager, sql_manager)
    
    papers = query_engine.get_all_papers_summary()
    
    print(f"\n共有 {len(papers)} 篇论文")
    
    for paper in papers[:3]:
        print(f"\nID: {paper['id']}")
        print(f"标题: {paper['title']}")
        if paper.get('keywords'):
            print(f"关键词: {', '.join(paper['keywords'][:3])}")

if __name__ == "__main__":
    print("请确保数据库中已有论文数据\n")
    
    test_semantic_search()
    test_hybrid_search()
    test_similar_papers()
    test_list_papers()
