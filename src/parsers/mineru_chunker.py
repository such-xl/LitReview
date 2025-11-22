import subprocess
from pathlib import Path
from typing import List, Dict
import re
import time


class MinerUParser:
    """使用 MinerU (Docker) 解析 PDF"""
    
    def __init__(self, output_dir="./data/MinerU", backend="vlm-http-client", vlm_url="http://127.0.0.1:30000"):
        """初始化MinerU解析器
        
        Args:
            output_dir: 输出目录
            backend: VLM后端类型
            vlm_url: VLM服务URL
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.backend = backend
        self.vlm_url = vlm_url
    
    def parse(self, pdf_path: str, timeout=300) -> str:
        """解析PDF文件，返回Markdown文本
        
        Args:
            pdf_path: PDF文件路径
            timeout: 超时时间（秒）
            
        Returns:
            str: 解析后的Markdown文本
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
        return self._read_markdown_output(pdf_path, wait_time=300)
    
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
        markdown_text = self.parser.parse(pdf_path)
        
        # 分块
        chunks = self._chunk_by_paragraphs(markdown_text, max_chunk_size)
        
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
