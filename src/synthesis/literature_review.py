from typing import List, Dict, Any, Optional
from config.prompts import REVIEW_GENERATION_PROMPT
from src.llm import LLMInterface
from src.database import SQLManager

class LiteratureReviewGenerator:
    def __init__(self, llm: LLMInterface, sql_manager: SQLManager):
        self.llm = llm
        self.sql_manager = sql_manager
    
    def generate_review(
        self,
        papers: List[Dict[str, Any]],
        topic: str,
        max_papers: int = 20
    ) -> str:
        """生成文献综述
        
        Args:
            papers: 论文列表
            topic: 研究主题
            max_papers: 最多使用的论文数量
        """
        
        # 限制论文数量
        papers = papers[:max_papers]
        
        # 准备论文信息
        papers_info = self._prepare_papers_info(papers)
        
        # 构建提示词
        prompt = REVIEW_GENERATION_PROMPT.format(
            topic=topic,
            papers_info=papers_info
        )
        
        # 生成综述
        review = self.llm.generate(
            prompt,
            system_prompt="你是一个专业的学术文献综述撰写专家。",
            temperature=0.5,
            max_tokens=4000
        )
        
        return review
    
    def generate_structured_review(
        self,
        papers: List[Dict[str, Any]],
        topic: str,
        sections: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """生成结构化综述（按章节）
        
        Args:
            papers: 论文列表
            topic: 研究主题
            sections: 章节列表
        """
        
        if sections is None:
            sections = [
                "研究背景与动机",
                "主要研究方法",
                "研究发现与趋势",
                "现有研究局限性",
                "未来研究方向"
            ]
        
        review_sections = {}
        
        for section in sections:
            section_review = self._generate_section(papers, topic, section)
            review_sections[section] = section_review
        
        return review_sections
    
    def _prepare_papers_info(self, papers: List[Dict[str, Any]]) -> str:
        """准备论文信息文本"""
        
        papers_text = []
        
        for i, paper in enumerate(papers, 1):
            # 获取分析信息
            analysis = self.sql_manager.get_paper_analysis(paper['id'])
            
            paper_info = f"\n[{i}] {paper['title']}"
            
            if paper.get('authors'):
                paper_info += f"\n作者: {paper['authors']}"
            
            if paper.get('year'):
                paper_info += f"\n年份: {paper['year']}"
            
            if analysis:
                if analysis.get('research_question'):
                    paper_info += f"\n研究问题: {analysis['research_question']}"
                
                if analysis.get('methodology'):
                    paper_info += f"\n方法: {analysis['methodology']}"
                
                if analysis.get('main_findings'):
                    findings = analysis['main_findings']
                    if isinstance(findings, list):
                        paper_info += f"\n主要发现: {'; '.join(findings[:3])}"
                
                if analysis.get('key_contributions'):
                    contributions = analysis['key_contributions']
                    if isinstance(contributions, list):
                        paper_info += f"\n核心贡献: {'; '.join(contributions[:2])}"
            
            papers_text.append(paper_info)
        
        return "\n".join(papers_text)
    
    def _generate_section(
        self,
        papers: List[Dict[str, Any]],
        topic: str,
        section_name: str
    ) -> str:
        """生成单个章节"""
        
        papers_info = self._prepare_papers_info(papers[:10])
        
        prompt = f"""
基于以下相关论文，撰写文献综述的"{section_name}"部分。

研究主题：{topic}

相关论文：
{papers_info}

要求：
1. 针对"{section_name}"这一主题进行深入分析
2. 总结共同趋势和模式
3. 对比不同研究的观点
4. 引用具体论文支撑观点（使用[编号]格式）
5. 学术正式语言，逻辑清晰
6. 长度约300-500字

请开始撰写：
"""
        
        return self.llm.generate(prompt, temperature=0.5, max_tokens=1000)
    
    def generate_summary(self, papers: List[Dict[str, Any]], topic: str) -> str:
        """生成简短摘要"""
        
        papers_info = self._prepare_papers_info(papers[:10])
        
        prompt = f"""
基于以下论文，为"{topic}"主题生成一个简短的研究现状摘要（200字以内）。

相关论文：
{papers_info}

请直接返回摘要，不要包含其他内容。
"""
        
        return self.llm.generate(prompt, temperature=0.3, max_tokens=500)
