import subprocess
from pathlib import Path
from typing import List, Dict
from . import PDFParser, ParsedPaper
import re

class MinerUParser(PDFParser):
    """使用 MinerU (GPU加速) 解析 PDF"""
    
    def __init__(self, use_gpu=True, output_dir="./data/processed"):
        """初始化MinerU解析器
        
        Args:
            use_gpu: 是否使用GPU加速
            output_dir: 输出目录
        """
        self.use_gpu = use_gpu
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self._check_gpu()
    
    def _check_gpu(self):
        """检查GPU可用性"""
        if self.use_gpu:
            try:
                import torch
                if torch.cuda.is_available():
                    print(f"✓ GPU 可用: {torch.cuda.get_device_name(0)}")
                else:
                    print("⚠ GPU 不可用，将使用 CPU")
                    self.use_gpu = False
            except ImportError:
                print("⚠ PyTorch 未安装，将使用 CPU")
                self.use_gpu = False
    
    def parse(self, pdf_path: str) -> ParsedPaper:
        """解析PDF文件"""
        pdf_path = Path(pdf_path)
        
        print(f"{'🚀 GPU' if self.use_gpu else '🐢 CPU'} 加速解析: {pdf_path.name}")
        
        # 使用MinerU解析
        cmd = ["mineru", "-p", str(pdf_path), "-o", str(self.output_dir)]
        if self.use_gpu:
            cmd.extend(["--device", "cuda"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠ MinerU失败，回退到PyMuPDF")
            return self._parse_with_pymupdf(pdf_path)
        
        # 读取Markdown
        markdown_text = self._read_markdown_output(pdf_path)
        
        # 解析结构化信息
        return ParsedPaper(
            title=self._extract_title(markdown_text),
            authors=self._extract_authors(markdown_text),
            abstract=self._extract_abstract(markdown_text),
            full_text=markdown_text,
            markdown_text=markdown_text,
            sections=self._extract_sections(markdown_text),
            tables=self._extract_tables(markdown_text),
            equations=self._extract_equations(markdown_text),
            references=self._extract_references(markdown_text)
        )
    
    def _parse_with_pymupdf(self, pdf_path: Path) -> ParsedPaper:
        """备用方案：使用PyMuPDF"""
        try:
            import fitz
        except ImportError:
            raise ImportError("请安装: pip install PyMuPDF")
        
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        
        return ParsedPaper(
            title=self._extract_title(full_text),
            authors=self._extract_authors(full_text),
            abstract=self._extract_abstract(full_text),
            full_text=full_text,
            markdown_text=full_text,
            sections=self._extract_sections(full_text),
            tables=[],
            equations=self._extract_equations(full_text),
            references=self._extract_references(full_text)
        )
    
    def _read_markdown_output(self, pdf_path: Path) -> str:
        """读取生成的Markdown文件"""
        pdf_name = pdf_path.stem
        possible_paths = [
            self.output_dir / pdf_name / "auto" / f"{pdf_name}.md",
            self.output_dir / pdf_name / f"{pdf_name}.md",
            self.output_dir / f"{pdf_name}.md",
        ]
        
        for md_path in possible_paths:
            if md_path.exists():
                with open(md_path, 'r', encoding='utf-8') as f:
                    return f.read()
        
        raise FileNotFoundError(f"未找到Markdown文件: {pdf_name}")
    
    def _extract_title(self, text: str) -> str:
        """提取标题"""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        return lines[0] if lines else "Unknown Title"
    
    def _extract_authors(self, text: str) -> List[str]:
        """提取作者"""
        lines = text.split('\n')
        for i, line in enumerate(lines[:30]):
            if 'author' in line.lower():
                author_line = lines[i+1] if i+1 < len(lines) else line
                return [a.strip() for a in re.split(r'[,;]', author_line) if a.strip()]
        return ["Unknown Author"]
    
    def _extract_abstract(self, text: str) -> str:
        """提取摘要"""
        match = re.search(r'(?:Abstract|ABSTRACT)\s*\n(.*?)(?:\n\n|\n[A-Z])', text, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """提取章节"""
        sections = {}
        keywords = ['introduction', 'method', 'result', 'discussion', 'conclusion']
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            if any(k in line.lower() for k in keywords) and len(line.strip()) < 100:
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        return sections
    
    def _extract_tables(self, text: str) -> List[Dict]:
        """提取表格（从Markdown）"""
        tables = []
        table_pattern = r'\|.*\|\n\|[-:| ]+\|\n(\|.*\|\n)+'
        for match in re.finditer(table_pattern, text):
            tables.append({"content": match.group(0)})
        return tables
    
    def _extract_equations(self, text: str) -> List[str]:
        """提取公式"""
        equations = []
        for line in text.split('\n'):
            if any(s in line for s in ['=', '∑', '∫', '∂', '$$']):
                if 10 < len(line.strip()) < 200:
                    equations.append(line.strip())
        return equations[:50]
    
    def _extract_references(self, text: str) -> List[str]:
        """提取参考文献"""
        match = re.search(r'(?:References|REFERENCES)\s*\n(.*?)$', text, re.DOTALL)
        if match:
            ref_text = match.group(1)
            return [r.strip() for r in re.split(r'\n\[\d+\]|\n\d+\.', ref_text) if len(r.strip()) > 30]
        return []


class MinerUChunker:
    """MinerU解析器的分块和存储工具（用于向量数据库）"""
    
    def __init__(self, parser: MinerUParser = None):
        self.parser = parser or MinerUParser()
    
    def chunk_text(self, text: str, chunk_size=1000, overlap=200) -> List[str]:
        """文本分块"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            if end < len(text):
                for sep in ['。\n', '。', '\n\n', '\n', '. ', '.']:
                    last_sep = chunk.rfind(sep)
                    if last_sep > chunk_size * 0.5:
                        chunk = chunk[:last_sep + len(sep)]
                        end = start + last_sep + len(sep)
                        break
            
            if chunk.strip():
                chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks


if __name__ == "__main__":
    # 测试MinerU解析器
    parser = MinerUParser(use_gpu=True)
    
    pdf_file = "data/pdfs/a.pdf"
    if Path(pdf_file).exists():
        result = parser.parse(pdf_file)
        print(f"\n标题: {result.title}")
        print(f"作者: {', '.join(result.authors)}")
        print(f"摘要: {result.abstract[:200]}...")
        print(f"章节数: {len(result.sections)}")
    else:
        print(f"文件不存在: {pdf_file}")