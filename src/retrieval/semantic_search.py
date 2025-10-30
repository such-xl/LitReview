from typing import List, Dict, Any, Optional
from src.database import VectorManager, SQLManager

class SemanticSearch:
    def __init__(self, vector_manager: VectorManager, sql_manager: SQLManager):
        self.vector_manager = vector_manager
        self.sql_manager = sql_manager
    
    def search_papers(
        self, 
        query: str, 
        n_results: int = 10,
        search_type: str = "fulltext"
    ) -> List[Dict[str, Any]]:
        """语义搜索论文
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            search_type: 搜索类型 (fulltext, abstract, analysis)
        """
        
        # 向量搜索
        if search_type == "fulltext":
            results = self.vector_manager.search_fulltext(query, n_results * 2)
        elif search_type == "abstract":
            results = self.vector_manager.search_abstracts(query, n_results)
        elif search_type == "analysis":
            results = self.vector_manager.search_analysis(query, n_results)
        else:
            raise ValueError(f"不支持的搜索类型: {search_type}")
        
        # 提取paper_id并去重
        paper_ids = []
        seen = set()
        
        if results['metadatas']:
            for metadata in results['metadatas'][0]:
                paper_id = metadata.get('paper_id')
                if paper_id and paper_id not in seen:
                    paper_ids.append(paper_id)
                    seen.add(paper_id)
                    if len(paper_ids) >= n_results:
                        break
        
        # 获取论文详情
        papers = []
        for paper_id in paper_ids:
            paper = self.sql_manager.get_paper(paper_id)
            if paper:
                # 添加相关度分数
                idx = results['metadatas'][0].index(
                    next(m for m in results['metadatas'][0] if m.get('paper_id') == paper_id)
                )
                paper['relevance_score'] = 1 - results['distances'][0][idx] if results['distances'] else 0
                papers.append(paper)
        
        return papers
    
    def search_similar_papers(
        self, 
        paper_id: int, 
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """查找相似论文"""
        
        # 获取论文
        paper = self.sql_manager.get_paper(paper_id)
        if not paper:
            return []
        
        # 使用摘要或标题作为查询
        query = paper.get('markdown_text', '') or paper.get('title', '')
        
        # 搜索
        results = self.search_papers(query[:2000], n_results + 1, "abstract")
        
        # 排除自己
        return [p for p in results if p['id'] != paper_id][:n_results]
    
    def search_by_keywords(
        self, 
        keywords: List[str], 
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """基于关键词搜索"""
        
        query = " ".join(keywords)
        return self.search_papers(query, n_results, "analysis")
