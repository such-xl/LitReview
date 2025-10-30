#!/usr/bin/env python3
"""搜索论文"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from src.database import SQLManager, VectorManager
from src.retrieval import QueryEngine

def search(query: str, method: str = "hybrid", n_results: int = 10):
    """搜索论文"""
    
    # 初始化
    sql_manager = SQLManager(str(settings.sqlite_path))
    vector_manager = VectorManager(str(settings.chroma_path))
    query_engine = QueryEngine(vector_manager, sql_manager)
    
    print(f"搜索: {query}")
    print(f"方法: {method}\n")
    
    # 执行搜索
    results = query_engine.query(query, method=method, n_results=n_results)
    
    if not results:
        print("未找到相关论文")
        return
    
    print(f"找到 {len(results)} 篇相关论文:\n")
    
    for i, paper in enumerate(results, 1):
        print(f"{i}. {paper['title']}")
        print(f"   作者: {paper.get('authors', 'N/A')}")
        print(f"   年份: {paper.get('year', 'N/A')}")
        
        if 'final_score' in paper:
            print(f"   相关度: {paper['final_score']:.3f}")
        elif 'relevance_score' in paper:
            print(f"   相关度: {paper['relevance_score']:.3f}")
        
        print()

def find_similar(paper_id: int, n_results: int = 5):
    """查找相似论文"""
    
    sql_manager = SQLManager(str(settings.sqlite_path))
    vector_manager = VectorManager(str(settings.chroma_path))
    query_engine = QueryEngine(vector_manager, sql_manager)
    
    # 获取原论文
    paper = sql_manager.get_paper(paper_id)
    if not paper:
        print(f"论文不存在: {paper_id}")
        return
    
    print(f"查找与以下论文相似的文献:")
    print(f"  {paper['title']}\n")
    
    # 查找相似论文
    results = query_engine.find_similar(paper_id, n_results)
    
    if not results:
        print("未找到相似论文")
        return
    
    print(f"找到 {len(results)} 篇相似论文:\n")
    
    for i, similar in enumerate(results, 1):
        print(f"{i}. {similar['title']}")
        print(f"   作者: {similar.get('authors', 'N/A')}")
        print(f"   相似度: {similar.get('relevance_score', 0):.3f}")
        print()

def list_papers():
    """列出所有论文"""
    
    sql_manager = SQLManager(str(settings.sqlite_path))
    vector_manager = VectorManager(str(settings.chroma_path))
    query_engine = QueryEngine(vector_manager, sql_manager)
    
    papers = query_engine.get_all_papers_summary()
    
    if not papers:
        print("数据库中没有论文")
        return
    
    print(f"共有 {len(papers)} 篇论文:\n")
    
    for paper in papers:
        print(f"ID: {paper['id']}")
        print(f"标题: {paper['title']}")
        print(f"作者: {paper.get('authors', 'N/A')}")
        print(f"年份: {paper.get('year', 'N/A')}")
        
        if paper.get('keywords'):
            print(f"关键词: {', '.join(paper['keywords'][:5])}")
        
        print()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="搜索论文")
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索论文')
    search_parser.add_argument('query', help='搜索查询')
    search_parser.add_argument('--method', choices=['semantic', 'hybrid', 'advanced'],
                              default='hybrid', help='搜索方法')
    search_parser.add_argument('-n', '--num', type=int, default=10, help='返回结果数量')
    
    # 相似论文命令
    similar_parser = subparsers.add_parser('similar', help='查找相似论文')
    similar_parser.add_argument('paper_id', type=int, help='论文ID')
    similar_parser.add_argument('-n', '--num', type=int, default=5, help='返回结果数量')
    
    # 列表命令
    subparsers.add_parser('list', help='列出所有论文')
    
    args = parser.parse_args()
    
    if args.command == 'search':
        search(args.query, args.method, args.num)
    elif args.command == 'similar':
        find_similar(args.paper_id, args.num)
    elif args.command == 'list':
        list_papers()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
