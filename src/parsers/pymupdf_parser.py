from pathlib import Path
from typing import List, Dict
from . import PDFParser, ParsedPaper
import re

class PyMuPDFParser(PDFParser):
    def __init__(self):
        try:
            import fitz
            self.fitz = fitz
        except ImportError:
            raise ImportError("请安装 PyMuPDF: pip install PyMuPDF")
        print("使用PyMuPDF解析器2") 
    def parse(self, pdf_path: str) -> ParsedPaper:
        """使用PyMuPDF解析PDF"""
        doc = self.fitz.open(pdf_path)
        
        # 提取全文
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        
        # 转换为Markdown格式
        markdown_text = self._to_markdown(full_text)
        
        # 提取标题
        title = self._extract_title(doc, full_text)
        
        # 提取作者
        authors = self._extract_authors(doc, full_text)
        
        # 提取摘要
        abstract = self._extract_abstract(full_text)
        
        # 提取章节
        sections = self._extract_sections(full_text)
        
        # 提取表格
        tables = self._extract_tables(doc)
        
        # 提取公式（简单识别）
        equations = self._extract_equations(full_text)
        
        # 提取参考文献
        references = self._extract_references(full_text)
        
        doc.close()
        
        return ParsedPaper(
            title=title,
            authors=authors,
            abstract=abstract,
            full_text=full_text,
            markdown_text=markdown_text,
            sections=sections,
            tables=tables,
            equations=equations,
            references=references
        )
    
    def _to_markdown(self, text: str) -> str:
        """简单转换为Markdown格式"""
        lines = text.split('\n')
        markdown_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                markdown_lines.append('')
                continue
            
            # 检测标题（全大写或较短的行）
            if len(line) < 100 and (line.isupper() or len(line.split()) < 10):
                if any(keyword in line.lower() for keyword in ['abstract', 'introduction', 'method', 'result', 'conclusion', 'reference']):
                    markdown_lines.append(f'\n## {line}\n')
                    continue
            
            markdown_lines.append(line)
        
        return '\n'.join(markdown_lines)
    
    def _extract_title(self, doc, text: str) -> str:
        """提取标题"""
        # 尝试从元数据获取
        metadata = doc.metadata
        if metadata.get('title'):
            return metadata['title']
        
        # 从文本提取
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            return lines[0]
        
        return "Unknown Title"
    
    def _extract_authors(self, doc, text: str) -> List[str]:
        """提取作者"""
        # 尝试从元数据获取
        metadata = doc.metadata
        if metadata.get('author'):
            return [metadata['author']]
        
        # 从文本提取
        lines = text.split('\n')
        for i, line in enumerate(lines[:30]):
            if any(keyword in line.lower() for keyword in ['author', 'by']):
                author_line = lines[i+1] if i+1 < len(lines) else line
                authors = [a.strip() for a in re.split(r'[,;]', author_line) if a.strip()]
                if authors:
                    return authors
        
        return ["Unknown Author"]
    
    def _extract_abstract(self, text: str) -> str:
        """提取摘要"""
        abstract_pattern = r'(?:Abstract|ABSTRACT)\s*\n(.*?)(?:\n\n|\n[A-Z][a-z]+\s*\n)'
        match = re.search(abstract_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """提取章节"""
        sections = {}
        section_keywords = ['introduction', 'method', 'result', 'discussion', 'conclusion', 'related work', 'experiment']
        
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # 检测章节标题
            is_section = any(keyword in line_lower for keyword in section_keywords)
            if is_section and len(line.strip()) < 100:
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_tables(self, doc) -> List[Dict]:
        """提取表格"""
        tables = []
        for page_num, page in enumerate(doc):
            page_tables = page.find_tables()
            for table in page_tables:
                tables.append({
                    "page": page_num + 1,
                    "content": str(table.extract())
                })
        return tables
    
    def _extract_equations(self, text: str) -> List[str]:
        """简单提取可能的公式"""
        equations = []
        
        # 查找包含数学符号的行
        math_symbols = ['=', '∑', '∫', '∂', '≈', '≤', '≥', '±', '×', '÷']
        lines = text.split('\n')
        
        for line in lines:
            if any(symbol in line for symbol in math_symbols):
                line = line.strip()
                if 10 < len(line) < 200:
                    equations.append(line)
        
        return equations[:50]  # 限制数量
    
    def _extract_references(self, text: str) -> List[str]:
        """提取参考文献"""
        references = []
        
        # 查找References章节
        ref_pattern = r'(?:References|REFERENCES|Bibliography)\s*\n(.*?)(?:\n\n[A-Z]|$)'
        match = re.search(ref_pattern, text, re.DOTALL)
        
        if match:
            ref_text = match.group(1)
            # 按编号或换行分割
            ref_lines = re.split(r'\n\[\d+\]|\n\d+\.', ref_text)
            references = [ref.strip() for ref in ref_lines if len(ref.strip()) > 30]
        
        return references
