import re
import subprocess
import time
from pathlib import Path
from typing import Dict, List

from . import PDFParser, ParsedPaper


class MinerUParser(PDFParser):
    """使用 MinerU CLI 解析 PDF，并转换为项目统一的 ParsedPaper。"""
    
    def __init__(
        self,
        output_dir: str = "./data/MinerU",
        backend: str = "vlm-http-client",
        vlm_url: str = "http://127.0.0.1:30000",
        use_gpu: bool = True,
    ):
        """初始化MinerU解析器
        
        Args:
            output_dir: 输出目录
            backend: VLM后端类型
            vlm_url: VLM服务URL
            use_gpu: 兼容工厂接口，当前仅保留在实例上供后续扩展
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.backend = backend
        self.vlm_url = vlm_url
        self.use_gpu = use_gpu
    
    def parse(self, pdf_path: str, timeout: int = 300) -> ParsedPaper:
        """解析PDF文件，返回Markdown文本
        
        Args:
            pdf_path: PDF文件路径
            timeout: 超时时间（秒）
            
        Returns:
            ParsedPaper: 项目统一格式的解析结果
        """
        pdf_path = Path(pdf_path)
        print(f"🚀 解析: {pdf_path.name}")
        
        # 使用MinerU解析
        cmd = ["mineru", "-p", str(pdf_path), "-o", str(self.output_dir), "-b", self.backend, "-u", self.vlm_url]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        
        if result.returncode != 0:
            print(f"stderr: {result.stderr}")
            print(f"stdout: {result.stdout}")
            raise RuntimeError(f"MinerU解析失败: {result.stderr}")
        
        print("✓ MinerU命令执行完成，等待文件生成...")
        
        # 等待文件生成
        markdown_text = self._read_markdown_output(pdf_path, wait_time=300)
        return self._build_parsed_paper(markdown_text)
    
    def _read_markdown_output(self, pdf_path: Path, wait_time=30) -> str:
        """读取生成的Markdown文件，支持等待"""
        pdf_name = pdf_path.stem
        possible_paths = [
            self.output_dir / pdf_name / "auto" / f"{pdf_name}.md",
            self.output_dir / pdf_name / f"{pdf_name}.md",
            self.output_dir / f"{pdf_name}.md",
        ]
        
        # 轮询等待文件生成
        start_time = time.time()
        while time.time() - start_time < wait_time:
            for md_path in possible_paths:
                if md_path.exists():
                    print(f"✓ 找到文件: {md_path}")
                    return md_path.read_text(encoding='utf-8')
            
            # 搜索所有.md文件
            for md_path in self.output_dir.rglob("*.md"):
                if pdf_name in md_path.stem:
                    print(f"✓ 找到文件: {md_path}")
                    return md_path.read_text(encoding='utf-8')
            
            time.sleep(1)
            print(f"等待文件生成... ({int(time.time() - start_time)}s)")
        
        # 超时后显示详细信息
        print(f"\n查找路径:")
        for p in possible_paths:
            print(f"  - {p} (存在: {p.exists()})")
        print(f"\n输出目录内容:")
        for p in self.output_dir.rglob("*"):
            print(f"  - {p}")
        
        raise FileNotFoundError(f"未找到Markdown文件: {pdf_name} (等待{wait_time}秒后超时)")

    def _build_parsed_paper(self, markdown_text: str) -> ParsedPaper:
        """将 MinerU 输出的 Markdown 归一化为项目内统一结构。"""
        title = self._extract_title(markdown_text)
        authors = self._extract_authors(markdown_text)
        abstract = self._extract_abstract(markdown_text)
        sections = self._extract_sections(markdown_text)
        tables = self._extract_tables(markdown_text)
        equations = self._extract_equations(markdown_text)
        references = self._extract_references(markdown_text)

        return ParsedPaper(
            title=title,
            authors=authors,
            abstract=abstract,
            full_text=markdown_text,
            markdown_text=markdown_text,
            sections=sections,
            tables=tables,
            equations=equations,
            references=references,
        )

    def _extract_title(self, text: str) -> str:
        for line in text.splitlines():
            candidate = line.strip().lstrip("#").strip()
            if candidate and len(candidate) > 10:
                return candidate
        return "Unknown Title"

    def _extract_authors(self, text: str) -> List[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for index, line in enumerate(lines[:20]):
            lower = line.lower()
            if "author" in lower or "authors" in lower:
                if index + 1 < len(lines):
                    authors = [
                        author.strip()
                        for author in re.split(r"[,;]| and ", lines[index + 1])
                        if author.strip()
                    ]
                    if authors:
                        return authors
        return ["Unknown Author"]

    def _extract_abstract(self, text: str) -> str:
        match = re.search(
            r"(?:^|\n)#+\s*Abstract\s*\n(.*?)(?:\n#+\s|\Z)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if match:
            return match.group(1).strip()
        return ""

    def _extract_sections(self, text: str) -> Dict[str, str]:
        sections: Dict[str, str] = {}
        current_section = None
        current_lines: List[str] = []

        for line in text.splitlines():
            if line.startswith("#"):
                if current_section:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = line.lstrip("#").strip()
                current_lines = []
            elif current_section:
                current_lines.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_lines).strip()

        return sections

    def _extract_tables(self, text: str) -> List[Dict]:
        tables = []
        current_table: List[str] = []

        for line in text.splitlines():
            if line.strip().startswith("|") and line.strip().endswith("|"):
                current_table.append(line)
            else:
                if len(current_table) >= 2:
                    tables.append({"content": "\n".join(current_table)})
                current_table = []

        if len(current_table) >= 2:
            tables.append({"content": "\n".join(current_table)})

        return tables

    def _extract_equations(self, text: str) -> List[str]:
        equations = []
        equations.extend(re.findall(r"\$\$(.*?)\$\$", text, re.DOTALL))
        equations.extend(re.findall(r"\$([^\$]+)\$", text))
        return [equation.strip() for equation in equations if equation.strip()]

    def _extract_references(self, text: str) -> List[str]:
        match = re.search(
            r"(?:^|\n)#+\s*References?\s*\n(.*?)(?:\n#+\s|\Z)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return []

        ref_lines = [line.strip() for line in match.group(1).splitlines() if line.strip()]
        return [line for line in ref_lines if len(line) > 20]


class MinerUChunker:
    """MinerU解析器的分块工具（用于向量数据库）"""
    
    def __init__(self, parser: MinerUParser = None):
        self.parser = parser or MinerUParser()
    
    def parse_and_chunk(self, pdf_path: str, max_chunk_size=1500) -> List[Dict[str, str]]:
        """解析PDF并按段落分块
        
        Args:
            pdf_path: PDF文件路径
            max_chunk_size: 最大块大小（字符数）
            
        Returns:
            List[Dict]: [{"text": "...", "index": 0}, ...]
        """
        # 解析PDF
        parsed_paper = self.parser.parse(pdf_path)
        
        # 分块
        chunks = self._chunk_by_paragraphs(parsed_paper.markdown_text, max_chunk_size)
        
        # 添加索引
        return [{"text": chunk, "index": i} for i, chunk in enumerate(chunks)]
    
    def _chunk_by_paragraphs(self, text: str, max_size: int) -> List[str]:
        """按段落分块，保持语义完整"""
        paragraphs = re.split(r'\n\n+', text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_size = len(para)
            
            # 单个段落超长，强制切分
            if para_size > max_size:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                chunks.extend(self._force_split(para, max_size))
            # 加入当前段落会超长，先保存当前块
            elif current_size + para_size > max_size:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            # 正常累加
            else:
                current_chunk.append(para)
                current_size += para_size
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _force_split(self, text: str, max_size: int) -> List[str]:
        """强制切分超长段落（保留句子完整性）"""
        chunks = []
        sentences = re.split(r'([。.!?]\s*)', text)
        current = ""
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else "")
            if len(current) + len(sentence) > max_size:
                if current:
                    chunks.append(current.strip())
                current = sentence
            else:
                current += sentence
        
        if current:
            chunks.append(current.strip())
        
        return chunks


if __name__ == "__main__":
    # 使用示例
    chunker = MinerUParser()
    
    pdf_file = "data/pdfs/unparsed/conference_101719.pdf"
    chunker.parse(pdf_path=pdf_file)
    # if Path(pdf_file).exists():
    #     chunks = chunker.parse_and_chunk(pdf_file, max_chunk_size=1500)
    #     print(f"\n✓ 解析完成，共 {len(chunks)} 个块")
    #     print(f"\n第一块预览:\n{chunks[0]['text'][:200]}...")
    # else:
    #     print(f"文件不存在: {pdf_file}")
