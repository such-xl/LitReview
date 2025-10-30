from typing import List, Dict, Any, Optional
from src.database import VectorManager, SQLManager
from .semantic_search import SemanticSearch
import re

class HybridSearch:
    def __init__(self, vector_manager: VectorManager, sql_manager: SQLManager):
        self.vector_manager = vector_manager
        self.sql_manager = sql_manager
        self.semantic_search = SemanticSearch(vector_manager, sql_manager)
    
    def search(
        self, 
        query: str, 
        n_results: int = 10,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """混合搜索（语义 + 关键词）
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            semantic_weight: 语义搜索权重
            keyword_weight: 关键词搜索权重
        """
        
        # 语义搜索
        semantic_results = self.semantic_search.search_papers(query, n_results * 2)
        
        # 关键词搜索
        keyword_results = self._keyword_search(query, n_results * 2)
        
        # 合并结果
        merged = self._merge_results(
            semantic_results, 
            keyword_results,
            semantic_weight,
            keyword_weight
        )
        
        return merged[:n_results]
    
    def _keyword_search(self, query: str, n_results: int) -> List[Dict[str, Any]]:
        """关键词搜索（基于SQL LIKE）"""
        
        papers = self.sql_manager.get_all_papers()
        
        # 提取查询关键词
        keywords = [k.lower() for k in re.findall(r'\w+', query) if len(k) > 2]
        
        # 计算匹配分数
        scored_papers = []
        for paper in papers:
            score = self._calculate_keyword_score(paper, keywords)
            if score > 0:
                paper['keyword_score'] = score
                scored_papers.append(paper)
        
        # 排序
        scored_papers.sort(key=lambda x: x['keyword_score'], reverse=True)
        
        return scored_papers[:n_results]
    
    def _calculate_keyword_score(self, paper: Dict[str, Any], keywords: List[str]) -> float:
        """计算关键词匹配分数"""
        
        # 构建搜索文本
        search_text = " ".join([
            paper.get('title', ''),
            paper.get('authors', ''),
            paper.get('raw_text', '')[:1000]  # 只搜索前1000字符
        ]).lower()
        
        # 计算匹配
        score = 0.0
        for keyword in keywords:
            count = search_text.count(keyword)
            if count > 0:
                # 标题匹配权重更高
                if keyword in paper.get('title', '').lower():
                    score += 3.0
                score += count * 0.5
        
        return score
    
    def _merge_results(
        self,
        semantic_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        semantic_weight: float,
        keyword_weight: float
    ) -> List[Dict[str, Any]]:
        """合并搜索结果"""
        
        # 归一化分数
        if semantic_results:
            max_semantic = max(p.get('relevance_score', 0) for p in semantic_results)
            if max_semantic > 0:
                for p in semantic_results:
                    p['relevance_score'] = p.get('relevance_score', 0) / max_semantic
        
        if keyword_results:
            max_keyword = max(p.get('keyword_score', 0) for p in keyword_results)
            if max_keyword > 0:
                for p in keyword_results:
                    p['keyword_score'] = p.get('keyword_score', 0) / max_keyword
        
        # 合并
        merged = {}
        
        for paper in semantic_results:
            paper_id = paper['id']
            merged[paper_id] = paper.copy()
            merged[paper_id]['final_score'] = paper.get('relevance_score', 0) * semantic_weight
        
        for paper in keyword_results:
            paper_id = paper['id']
            if paper_id in merged:
                merged[paper_id]['final_score'] += paper.get('keyword_score', 0) * keyword_weight
            else:
                merged[paper_id] = paper.copy()
                merged[paper_id]['final_score'] = paper.get('keyword_score', 0) * keyword_weight
        
        # 排序
        results = list(merged.values())
        results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        return results
    
    def advanced_search(
        self,
        query: str,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        authors: Optional[List[str]] = None,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """高级搜索（带过滤条件）"""
        
        # 先进行混合搜索
        results = self.search(query, n_results * 3)
        
        # 应用过滤
        filtered = []
        for paper in results:
            # 年份过滤
            if year_from and paper.get('year'):
                if paper['year'] < year_from:
                    continue
            
            if year_to and paper.get('year'):
                if paper['year'] > year_to:
                    continue
            
            # 作者过滤
            if authors:
                paper_authors = paper.get('authors', '').lower()
                if not any(author.lower() in paper_authors for author in authors):
                    continue
            
            filtered.append(paper)
            
            if len(filtered) >= n_results:
                break
        
        return filtered
