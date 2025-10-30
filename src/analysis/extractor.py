from typing import Dict, Any
from config.prompts import EXTRACTION_PROMPT
from src.llm import LLMInterface

class PaperExtractor:
    def __init__(self, llm: LLMInterface):
        self.llm = llm
    
    def extract_info(self, paper_text: str, max_length: int = 8000) -> Dict[str, Any]:
        """提取论文关键信息"""
        
        # 截断过长的文本
        if len(paper_text) > max_length:
            paper_text = paper_text[:max_length] + "\n...(文本已截断)"
        
        # 构建提示词
        prompt = EXTRACTION_PROMPT.format(paper_text=paper_text)
        
        # 调用LLM
        try:
            result = self.llm.generate_structured(prompt, schema={})
            
            # 验证必需字段
            required_fields = ['research_question', 'methodology', 'main_findings', 
                             'key_contributions', 'limitations', 'future_work', 'keywords']
            
            for field in required_fields:
                if field not in result:
                    result[field] = [] if field in ['main_findings', 'key_contributions', 
                                                     'limitations', 'keywords'] else ""
            
            return result
            
        except Exception as e:
            print(f"提取失败: {e}")
            # 返回空结果
            return {
                'research_question': "",
                'methodology': "",
                'main_findings': [],
                'key_contributions': [],
                'limitations': [],
                'future_work': "",
                'keywords': []
            }
    
    def extract_from_sections(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """从章节中提取信息（更精确）"""
        
        # 优先使用摘要和结论
        key_sections = []
        
        for section_name, content in sections.items():
            section_lower = section_name.lower()
            if any(keyword in section_lower for keyword in 
                   ['abstract', 'introduction', 'conclusion', 'method', 'result']):
                key_sections.append(f"## {section_name}\n{content}")
        
        combined_text = "\n\n".join(key_sections)
        
        return self.extract_info(combined_text)
