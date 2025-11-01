import os
import subprocess
import json
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

class PaperParserCLI:
    """使用 MinerU (GPU加速) 解析 PDF 并存储到 ChromaDB"""
    
    _model_singleton = None  # 类级别的模型缓存
    
    def __init__(self, chroma_persist_dir="./chroma_db", use_gpu=True):
        """初始化解析器和ChromaDB客户端"""
        # 初始化ChromaDB
        self.client = chromadb.PersistentClient(path=chroma_persist_dir)
        
        # 使用默认的embedding函数
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # 创建或获取collection
        self.collection = self.client.get_or_create_collection(
            name="research_papers",
            embedding_function=self.embedding_fn,
            metadata={"description": "Research papers parsed from PDFs"}
        )
        
        self.use_gpu = use_gpu
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
    
    def parse_pdf_with_mineru(self, pdf_path, output_dir="./output"):
        """使用 MinerU 命令行工具解析 PDF (支持GPU加速)"""
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        print(f"{'🚀 GPU' if self.use_gpu else '🐢 CPU'} 加速解析")
        
        # 使用命令行工具（更稳定）
        cmd = [
            "mineru",
            "-p", str(pdf_path),
            "-o", str(output_dir)
        ]
        
        if self.use_gpu:
            cmd.extend(["--device", "cuda"])
        
        print(f"📄 正在解析: {pdf_path.name}")
        print(f"执行: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠ 命令行失败，尝试 PyMuPDF 快速解析...")
            return self._parse_with_pymupdf(pdf_path, output_dir)
        
        # 读取生成的Markdown
        return self._read_markdown_output(pdf_path, output_dir)
    
    def _parse_with_pymupdf(self, pdf_path, output_dir):
        """备用方案：使用 PyMuPDF 快速解析"""
        try:
            import fitz
        except ImportError:
            raise ImportError("请安装: pip install PyMuPDF")
        
        doc = fitz.open(pdf_path)
        md_content = ""
        
        for page in doc:
            md_content += page.get_text()
        
        doc.close()
        
        # 保存
        md_path = output_dir / f"{pdf_path.stem}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✓ 解析完成 (PyMuPDF): {md_path}")
        return md_content, str(output_dir)
    
    def _read_markdown_output(self, pdf_path, output_dir):
        """读取生成的 Markdown 文件"""
        pdf_name = pdf_path.stem
        
        # 尝试不同的可能路径
        possible_paths = [
            output_dir / pdf_name / "auto" / f"{pdf_name}.md",
            output_dir / pdf_name / f"{pdf_name}.md",
            output_dir / f"{pdf_name}.md",
        ]
        
        for md_path in possible_paths:
            if md_path.exists():
                print(f"找到 Markdown 文件: {md_path}")
                with open(md_path, 'r', encoding='utf-8') as f:
                    return f.read(), str(md_path.parent)
        
        raise FileNotFoundError(
            f"无法找到生成的 Markdown 文件。检查了以下路径:\n" + 
            "\n".join(str(p) for p in possible_paths)
        )
    
    def chunk_text(self, text, chunk_size=1000, overlap=200):
        """将文本分块，支持重叠"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            # 尝试在句子边界处分割
            if end < text_length:
                # 尝试多种分隔符
                for separator in ['。\n', '。', '\n\n', '\n', '. ', '.']:
                    last_sep = chunk.rfind(separator)
                    if last_sep > chunk_size * 0.5:
                        chunk = chunk[:last_sep + len(separator)]
                        end = start + last_sep + len(separator)
                        break
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            start = end - overlap
        
        return chunks
    
    def store_to_chromadb(self, pdf_path, chunks):
        """将分块后的内容存储到ChromaDB"""
        pdf_name = Path(pdf_path).stem
        
        # 准备文档、ID和元数据
        documents = chunks
        ids = [f"{pdf_name}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "source": pdf_name,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "file_path": str(pdf_path)
            }
            for i in range(len(chunks))
        ]
        
        # 添加到ChromaDB
        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        print(f"✓ 成功存储 {len(chunks)} 个文本块到 ChromaDB")
    
    def process_paper(self, pdf_path, chunk_size=1000, overlap=200):
        """完整处理流程：解析PDF -> 分块 -> 存储"""
        print(f"\n{'='*60}")
        print(f"开始处理论文: {pdf_path}")
        print(f"{'='*60}\n")
        
        # 1. 解析PDF
        print("📄 [1/3] 解析 PDF...")
        md_content, output_dir = self.parse_pdf_with_mineru(pdf_path)
        print(f"✓ 解析完成，内容长度: {len(md_content)} 字符")
        
        # 2. 分块
        print(f"\n📑 [2/3] 分块文本 (chunk_size={chunk_size}, overlap={overlap})...")
        chunks = self.chunk_text(md_content, chunk_size, overlap)
        print(f"✓ 分块完成，共 {len(chunks)} 个块")
        
        # 3. 存储到ChromaDB
        print(f"\n💾 [3/3] 存储到 ChromaDB...")
        self.store_to_chromadb(pdf_path, chunks)
        
        print(f"\n{'='*60}")
        print("✓ 处理完成！")
        print(f"{'='*60}\n")
        
        return {
            "pdf_path": pdf_path,
            "output_dir": output_dir,
            "chunks_count": len(chunks),
            "md_length": len(md_content)
        }
    
    def query(self, query_text, n_results=5):
        """查询相关文档片段"""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
    
    def get_paper_chunks(self, paper_name):
        """获取特定论文的所有块"""
        results = self.collection.get(
            where={"source": paper_name}
        )
        return results


# 使用示例
if __name__ == "__main__":
    # 初始化解析器
    parser = PaperParserCLI(chroma_persist_dir="./paper_db")
    
    # 处理单个PDF
    pdf_file = "data/pdfs/b.pdf"  # 替换为你的PDF路径
    
    if os.path.exists(pdf_file):
        # 处理论文
        result = parser.process_paper(
            pdf_file,
            chunk_size=1000,  # 每块字符数
            overlap=200       # 块之间的重叠
        )
        
        print("\n📊 处理结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 查询示例
        print("\n🔍 查询示例:")
        query_result = parser.query("深度学习", n_results=3)
        for i, doc in enumerate(query_result['documents'][0]):
            print(f"\n--- 结果 {i+1} ---")
            print(doc[:200] + "...")
    else:
        print(f"❌ PDF 文件不存在: {pdf_file}")
        print("请将 'your_paper.pdf' 替换为实际的PDF文件路径")