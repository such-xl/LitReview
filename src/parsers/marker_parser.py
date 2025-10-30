from pathlib import Path
from typing import List, Dict
from . import PDFParser, ParsedPaper
import re

class MarkerParser(PDFParser):
    def __init__(self):
        try:
            from marker.convert import convert_single_pdf
            from marker.models import load_all_models
            self.convert_single_pdf = convert_single_pdf
            self.models = load_all_models()
        except ImportError:
            raise ImportError("请安装 marker-pdf: pip install marker-pdf")
    
    def parse(self, pdf_path: str) -> ParsedPaper:
        """使用Marker解析PDF"""
        full_text, images, metadata = self.convert_single_pdf(pdf_path, self.models)
        
        # 提取标题
        title = self._extract_title(full_text, metadata)
        
        # 提取作者
        authors = self._extract_authors(full_text)
        
        # 提取摘要
        abstract = self._extract_abstract(full_text)
        
        # 提取章节
        sections = self._extract_sections(full_text)
        
        # 提取表格
        tables = self._extract_tables(full_text)
        
        # 提取公式
        equations = self._extract_equations(full_text)
        
        # 提取参考文献
        references = self._extract_references(full_text)
        
        return ParsedPaper(
            title=title,
            authors=authors,
            abstract=abstract,
            full_text=full_text,
            markdown_text=full_text,
            sections=sections,
            tables=tables,
            equations=equations,
            references=references
        )
    
    def _extract_title(self, text: str, metadata: dict) -> str:
        """提取标题"""
        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if line and len(line) > 10 and not line.startswith('#'):
                return line
        return "Unknown Title"
    
    def _extract_authors(self, text: str) -> List[str]:
        """提取作者"""
        authors = []
        lines = text.split('\n')
        for i, line in enumerate(lines[:20]):
            if 'author' in line.lower() or '@' in line:
                author_line = lines[i+1] if i+1 < len(lines) else line
                authors = [a.strip() for a in re.split(r'[,;]', author_line) if a.strip()]
                break
        return authors if authors else ["Unknown Author"]
    
    def _extract_abstract(self, text: str) -> str:
        """提取摘要"""
        abstract_match = re.search(r'(?:^|\n)#+\s*Abstract\s*\n(.*?)(?:\n#+|\n\n)', text, re.IGNORECASE | re.DOTALL)
        if abstract_match:
            return abstract_match.group(1).strip()
        
        # 备选方案
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'abstract' in line.lower():
                abstract_lines = []
                for j in range(i+1, min(i+20, len(lines))):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        abstract_lines.append(lines[j].strip())
                    elif len(abstract_lines) > 3:
                        break
                return ' '.join(abstract_lines)
        return ""
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """提取章节"""
        sections = {}
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith('#'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.lstrip('#').strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_tables(self, text: str) -> List[Dict]:
        """提取表格"""
        tables = []
        table_pattern = r'\|(.+)\|'
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            if re.match(table_pattern, lines[i]):
                table_lines = [lines[i]]
                i += 1
                while i < len(lines) and re.match(table_pattern, lines[i]):
                    table_lines.append(lines[i])
                    i += 1
                if len(table_lines) > 2:
                    tables.append({"content": '\n'.join(table_lines)})
            i += 1
        
        return tables
    
    def _extract_equations(self, text: str) -> List[str]:
        """提取LaTeX公式"""
        equations = []
        
        # 提取 $$ ... $$ 格式
        equations.extend(re.findall(r'\$\$(.*?)\$\$', text, re.DOTALL))
        
        # 提取 $ ... $ 格式
        equations.extend(re.findall(r'\$([^\$]+)\$', text))
        
        return [eq.strip() for eq in equations if eq.strip()]
    
    def _extract_references(self, text: str) -> List[str]:
        """提取参考文献"""
        references = []
        
        # 查找References章节
        ref_match = re.search(r'(?:^|\n)#+\s*References?\s*\n(.*?)(?:\n#+|$)', text, re.IGNORECASE | re.DOTALL)
        if ref_match:
            ref_text = ref_match.group(1)
            # 按行分割，过滤空行
            references = [line.strip() for line in ref_text.split('\n') if line.strip() and len(line.strip()) > 20]
        
        return references
