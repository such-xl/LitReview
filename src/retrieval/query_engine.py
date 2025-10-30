from typing import List, Dict, Any, Optional
from src.database import VectorManager, SQLManager
from .semantic_search import SemanticSearch
from .hybrid_search import HybridSearch

class QueryEngine:
    """统一的查询接口"""
    
    def __init__(self, vector_manager: VectorManager, sql_manager: SQLManager):
        self.vector_manager = vector_manager
        self.sql_manager = sql_manager
        self.semantic_search = SemanticSearch(vector_manager, sql_manager)
        self.hybrid_search = HybridSearch(vector_manager, sql_manager)
    
    def query(
        self,
        query: str,
        method: str = "hybrid",
        n_results: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """统一查询接口
        
        Args:
            query: 查询文本
            method: 搜索方法 (semantic, hybrid, keyword, advanced)
            n_results: 返回结果数量
            **kwargs: 其他参数
        """
        
        if method == "semantic":
            search_type = kwargs.get('search_type', 'fulltext')
            return self.semantic_search.search_papers(query, n_results, search_type)
        
        elif method == "hybrid":
            semantic_weight = kwargs.get('semantic_weight', 0.7)
            keyword_weight = kwargs.get('keyword_weight', 0.3)
            return self.hybrid_search.search(query, n_results, semantic_weight, keyword_weight)
        
        elif method == "advanced":
            return self.hybrid_search.advanced_search(
                query,
                year_from=kwargs.get('year_from'),
                year_to=kwargs.get('year_to'),
                authors=kwargs.get('authors'),
                n_results=n_results
            )
        
        else:
            raise ValueError(f"不支持的搜索方法: {method}")
    
    def find_similar(self, paper_id: int, n_results: int = 5) -> List[Dict[str, Any]]:
        """查找相似论文"""
        return self.semantic_search.search_similar_papers(paper_id, n_results)
    
    def search_by_topic(self, topic: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """按主题搜索"""
        return self.query(topic, method="hybrid", n_results=n_results)
    
    def get_paper_with_analysis(self, paper_id: int) -> Optional[Dict[str, Any]]:
        """获取论文及其分析结果"""
        paper = self.sql_manager.get_paper(paper_id)
        if not paper:
            return None
        
        analysis = self.sql_manager.get_paper_analysis(paper_id)
        if analysis:
            paper['analysis'] = analysis
        
        return paper
    
    def get_all_papers_summary(self) -> List[Dict[str, Any]]:
        """获取所有论文的摘要信息"""
        papers = self.sql_manager.get_all_papers()
        
        summaries = []
        for paper in papers:
            summary = {
                'id': paper['id'],
                'title': paper['title'],
                'authors': paper['authors'],
                'year': paper['year'],
                'created_at': paper['created_at']
            }
            
            # 添加分析信息
            analysis = self.sql_manager.get_paper_analysis(paper['id'])
            if analysis:
                summary['keywords'] = analysis.get('keywords', [])
                summary['research_question'] = analysis.get('research_question', '')
            
            summaries.append(summary)
        
        return summaries
