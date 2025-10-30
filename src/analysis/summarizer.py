from typing import Dict, Any
from src.llm import LLMInterface

class PaperSummarizer:
    def __init__(self, llm: LLMInterface):
        self.llm = llm
    
    def summarize(self, paper_text: str, max_length: int = 300) -> str:
        """生成论文摘要"""
        
        prompt = f"""
请为以下学术论文生成一个简洁的摘要（{max_length}字以内）。

论文内容：
{paper_text[:5000]}

摘要应包含：
1. 研究问题
2. 主要方法
3. 核心发现

请直接返回摘要文本，不要包含其他内容。
"""
        
        system_prompt = "你是一个专业的学术论文摘要生成助手。"
        
        return self.llm.generate(prompt, system_prompt, temperature=0.3)
    
    def summarize_section(self, section_name: str, section_text: str) -> str:
        """总结单个章节"""
        
        prompt = f"""
请总结以下论文章节的主要内容（100字以内）：

章节：{section_name}

内容：
{section_text[:2000]}

请直接返回总结，不要包含其他内容。
"""
        
        return self.llm.generate(prompt, temperature=0.3)
