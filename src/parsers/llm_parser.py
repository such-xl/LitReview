from typing import List, Dict
from . import PDFParser, ParsedPaper
import json

class LLMParser(PDFParser):
    def __init__(self, llm_client):
        """
        Args:
            llm_client: LLMInterface实例
        """
        try:
            import fitz
            self.fitz = fitz
        except ImportError:
            raise ImportError("请安装 PyMuPDF: pip install PyMuPDF")
        
        self.llm = llm_client
        print("使用LLM智能解析器")
    
    def parse(self, pdf_path: str) -> ParsedPaper:
        """使用LLM智能解析PDF"""
        doc = self.fitz.open(pdf_path)
        
        # 提取原始文本
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        
        doc.close()
        
        # 使用LLM提取结构化信息
        parsed_data = self._llm_extract(full_text)
        
        return ParsedPaper(
            title=parsed_data.get("title", "Unknown Title"),
            authors=parsed_data.get("authors", ["Unknown Author"]),
            abstract=parsed_data.get("abstract", ""),
            full_text=full_text,
            markdown_text=parsed_data.get("markdown_text", full_text),
            sections=parsed_data.get("sections", {}),
            tables=parsed_data.get("tables", []),
            equations=parsed_data.get("equations", []),
            references=parsed_data.get("references", [])
        )
    
    def _llm_extract(self, text: str) -> Dict:
        """使用LLM提取论文结构化信息"""
        
        # 限制文本长度（避免超过token限制）
        max_chars = 30000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...(文本已截断)"
        
        prompt = f"""请分析以下学术论文，提取结构化信息。返回JSON格式：

论文内容：
{text}

请提取：
1. title: 论文标题
2. authors: 作者列表（数组）
3. abstract: 摘要
4. sections: 章节内容（对象，key为章节名，value为内容）
5. tables: 表格列表（数组，每个表格包含描述）
6. equations: 重要公式列表（数组）
7. references: 参考文献列表（数组）
8. markdown_text: 将论文转换为Markdown格式

返回格式：
{{
  "title": "...",
  "authors": ["...", "..."],
  "abstract": "...",
  "sections": {{"Introduction": "...", "Methods": "..."}},
  "tables": [{{"description": "...", "content": "..."}}],
  "equations": ["...", "..."],
  "references": ["...", "..."],
  "markdown_text": "..."
}}

只返回JSON，不要其他说明。"""

        try:
            response = self.llm.generate(
                prompt=prompt,
                system_prompt="你是一个专业的学术论文解析助手，擅长提取论文的结构化信息。",
                temperature=0.1,
                max_tokens=8000
            )
            
            # 提取JSON
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response)
        
        except Exception as e:
            print(f"LLM解析失败: {e}")
            # 返回基础信息
            return {
                "title": text.split('\n')[0][:100] if text else "Unknown Title",
                "authors": ["Unknown Author"],
                "abstract": "",
                "sections": {},
                "tables": [],
                "equations": [],
                "references": [],
                "markdown_text": text
            }
