from typing import List, Dict, Any, Optional
import re

class CitationManager:
    """引用管理器"""
    
    def __init__(self):
        self.citations = {}
        self.citation_counter = 0
    
    def add_citation(
        self,
        paper: Dict[str, Any],
        citation_style: str = "apa"
    ) -> str:
        """添加引用并返回引用标记
        
        Args:
            paper: 论文信息
            citation_style: 引用格式 (apa, mla, chicago)
        """
        
        paper_id = paper['id']
        
        if paper_id not in self.citations:
            self.citation_counter += 1
            self.citations[paper_id] = {
                'number': self.citation_counter,
                'paper': paper,
                'style': citation_style
            }
        
        return f"[{self.citations[paper_id]['number']}]"
    
    def format_citation(
        self,
        paper: Dict[str, Any],
        style: str = "apa"
    ) -> str:
        """格式化单个引用"""
        
        if style == "apa":
            return self._format_apa(paper)
        elif style == "mla":
            return self._format_mla(paper)
        elif style == "chicago":
            return self._format_chicago(paper)
        else:
            return self._format_apa(paper)
    
    def _format_apa(self, paper: Dict[str, Any]) -> str:
        """APA格式"""
        authors = paper.get('authors', 'Unknown')
        year = paper.get('year', 'n.d.')
        title = paper.get('title', 'Untitled')
        venue = paper.get('venue', '')
        
        citation = f"{authors} ({year}). {title}."
        if venue:
            citation += f" {venue}."
        
        return citation
    
    def _format_mla(self, paper: Dict[str, Any]) -> str:
        """MLA格式"""
        authors = paper.get('authors', 'Unknown')
        title = paper.get('title', 'Untitled')
        venue = paper.get('venue', '')
        year = paper.get('year', 'n.d.')
        
        citation = f'{authors}. "{title}."'
        if venue:
            citation += f" {venue},"
        citation += f" {year}."
        
        return citation
    
    def _format_chicago(self, paper: Dict[str, Any]) -> str:
        """Chicago格式"""
        authors = paper.get('authors', 'Unknown')
        year = paper.get('year', 'n.d.')
        title = paper.get('title', 'Untitled')
        venue = paper.get('venue', '')
        
        citation = f'{authors}. {year}. "{title}."'
        if venue:
            citation += f" {venue}."
        
        return citation
    
    def generate_bibliography(self, style: str = "apa") -> str:
        """生成参考文献列表"""
        
        if not self.citations:
            return ""
        
        # 按编号排序
        sorted_citations = sorted(
            self.citations.values(),
            key=lambda x: x['number']
        )
        
        bibliography = []
        for citation in sorted_citations:
            number = citation['number']
            paper = citation['paper']
            formatted = self.format_citation(paper, style)
            bibliography.append(f"[{number}] {formatted}")
        
        return "\n".join(bibliography)
    
    def extract_citations_from_text(self, text: str) -> List[int]:
        """从文本中提取引用编号"""
        
        pattern = r'\[(\d+)\]'
        matches = re.findall(pattern, text)
        return [int(m) for m in matches]
    
    def get_cited_papers(self, text: str) -> List[Dict[str, Any]]:
        """获取文本中引用的所有论文"""
        
        citation_numbers = self.extract_citations_from_text(text)
        
        cited_papers = []
        for paper_id, citation in self.citations.items():
            if citation['number'] in citation_numbers:
                cited_papers.append(citation['paper'])
        
        return cited_papers
    
    def clear(self):
        """清空引用"""
        self.citations = {}
        self.citation_counter = 0
