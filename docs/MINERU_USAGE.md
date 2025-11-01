# MinerU Text Chunker 使用指南

## 安装

```bash
# 使用 uv (推荐)
uv pip install "mineru[core]"

# 或使用 pip
pip install "mineru[core]"
```

## 使用方法

### 1. 命令行使用

```bash
# 基本使用
python scripts/chunk_with_mineru.py data/pdfs/a.pdf

# 自定义参数
python scripts/chunk_with_mineru.py data/pdfs/a.pdf \
  --chunk-size 1500 \
  --overlap 300 \
  --output data/processed/a_chunks.json
```

### 2. Python代码使用

```python
from src.parsers import MinerUChunker

# 创建chunker
chunker = MinerUChunker(chunk_size=1000, chunk_overlap=200)

# 从PDF分块
chunks = chunker.chunk_from_pdf("data/pdfs/paper.pdf")

# 从Markdown分块
chunks = chunker.chunk_from_markdown("data/processed/paper.md")

# 保存结果
chunker.save_chunks(chunks, "output.json")
```

### 3. Chunk格式

```json
{
  "text": "chunk内容",
  "index": 0,
  "length": 856,
  "metadata": {
    "source": "paper.pdf",
    "section": "Introduction"
  }
}
```

## 特性

- 基于MinerU的高质量PDF解析
- 智能识别章节结构
- 支持公式、表格保留
- 可配置的chunk大小和重叠
- Markdown格式输出
