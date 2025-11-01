# MinerU 集成指南

MinerU 已成功集成到 LitReview 项目中，作为高质量 PDF 解析的替代方案。

## 功能特性

- ✅ 符合项目 PDFParser 接口规范
- ✅ 支持 GPU 加速（可选）
- ✅ 自动降级到 PyMuPDF（当 MinerU 失败时）
- ✅ 提取结构化信息（标题、作者、摘要、章节等）
- ✅ 通过 ParserFactory 统一创建

## 安装依赖

```bash
# 基础安装
pip install magic-pdf[full]

# GPU 加速（可选）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 使用方法

### 1. 通过 ParserFactory 使用（推荐）

```python
from src.parsers import ParserFactory

# 创建 MinerU 解析器
parser = ParserFactory.create_parser(
    parser_type="mineru",
    use_gpu=True  # 是否使用 GPU
)

# 解析 PDF
result = parser.parse("data/pdfs/paper.pdf")

print(f"标题: {result.title}")
print(f"作者: {', '.join(result.authors)}")
print(f"摘要: {result.abstract}")
```

### 2. 直接使用 MinerUParser

```python
from src.parsers import MinerUParser

parser = MinerUParser(
    use_gpu=True,
    output_dir="./data/processed"
)

result = parser.parse("data/pdfs/paper.pdf")
```

### 3. 使用命令行脚本

```bash
# 解析单个 PDF
python scripts/parse_with_mineru.py

# 或直接运行
./scripts/parse_with_mineru.py
```

### 4. 配置文件方式

在 `.env` 文件中设置：

```bash
PDF_PARSER=mineru
USE_GPU=true
```

然后在代码中：

```python
from config.settings import settings
from src.parsers import ParserFactory

parser = ParserFactory.create_parser(
    parser_type=settings.PDF_PARSER,
    use_gpu=settings.USE_GPU
)
```

## 与其他解析器对比

| 解析器 | 速度 | 质量 | 公式支持 | 表格支持 | GPU加速 |
|--------|------|------|----------|----------|---------|
| PyMuPDF | ⭐⭐⭐⭐⭐ | ⭐⭐ | ❌ | ⭐ | ❌ |
| Marker | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | ⭐⭐⭐ | ❌ |
| MinerU | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐ | ✅ |
| LLM | ⭐ | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ | ❌ |

## 文本分块工具

MinerU 还提供了专门的分块工具：

```python
from src.parsers import MinerUChunker

chunker = MinerUChunker()

# 分块文本
chunks = chunker.chunk_text(
    text=long_text,
    chunk_size=1000,
    overlap=200
)
```

## 输出结构

MinerU 解析后返回 `ParsedPaper` 对象：

```python
@dataclass
class ParsedPaper:
    title: str              # 论文标题
    authors: List[str]      # 作者列表
    abstract: str           # 摘要
    full_text: str          # 全文
    markdown_text: str      # Markdown 格式
    sections: Dict[str, str]  # 章节内容
    tables: List[Dict]      # 表格
    equations: List[str]    # 公式
    references: List[str]   # 参考文献
```

## 故障排除

### MinerU 命令未找到

```bash
pip install magic-pdf[full]
```

### GPU 不可用

系统会自动降级到 CPU 模式，或设置：

```python
parser = ParserFactory.create_parser("mineru", use_gpu=False)
```

### 解析失败

MinerU 会自动降级到 PyMuPDF 备用方案。

## 性能优化建议

1. **GPU 加速**: 对于大批量处理，建议使用 GPU
2. **批量处理**: 一次性处理多个文件以分摊初始化开销
3. **输出目录**: 设置合适的输出目录避免重复解析

## 示例：批量处理

```python
from pathlib import Path
from src.parsers import ParserFactory

parser = ParserFactory.create_parser("mineru", use_gpu=True)

pdf_dir = Path("data/pdfs")
for pdf_file in pdf_dir.glob("*.pdf"):
    try:
        result = parser.parse(str(pdf_file))
        print(f"✓ {pdf_file.name}: {result.title}")
    except Exception as e:
        print(f"✗ {pdf_file.name}: {e}")
```

## 与向量数据库集成

```python
from src.parsers import MinerUParser, MinerUChunker
from src.database import VectorManager

# 解析
parser = MinerUParser()
result = parser.parse("paper.pdf")

# 分块
chunker = MinerUChunker()
chunks = chunker.chunk_text(result.markdown_text)

# 存储到向量数据库
vector_db = VectorManager()
vector_db.add_documents(chunks, metadata={"title": result.title})
```

## 更多信息

- [MinerU 官方文档](https://github.com/opendatalab/MinerU)
- [项目 API 文档](./API.md)
- [快速开始指南](./QUICKSTART.md)
