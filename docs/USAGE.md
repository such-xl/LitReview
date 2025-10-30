# 使用指南

## Phase 2: PDF解析功能

### 1. 初始化数据库

```bash
python scripts/init_database.py
```

### 2. 导入单个PDF

```bash
# 使用PyMuPDF（快速）
python scripts/import_papers.py path/to/paper.pdf

# 使用Marker（高质量，需要先安装）
python scripts/import_papers.py path/to/paper.pdf --parser marker
```

### 3. 批量导入PDF目录

```bash
# 导入data/pdfs目录下的所有PDF
python scripts/import_papers.py data/pdfs/

# 使用Marker解析器
python scripts/import_papers.py data/pdfs/ --parser marker
```

### 4. 在代码中使用

```python
from src.parsers import ParserFactory, TextChunker
from src.database import SQLManager, VectorManager
from config import settings

# 创建解析器
parser = ParserFactory.create_parser("pymupdf")

# 解析PDF
parsed = parser.parse("path/to/paper.pdf")

print(f"标题: {parsed.title}")
print(f"作者: {', '.join(parsed.authors)}")
print(f"摘要: {parsed.abstract}")

# 文本分块
chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
chunks = chunker.chunk_text(parsed.full_text)

print(f"分块数量: {len(chunks)}")

# 保存到数据库
sql_manager = SQLManager(str(settings.sqlite_path))
paper_id = sql_manager.add_paper(
    title=parsed.title,
    pdf_path="path/to/paper.pdf",
    authors=', '.join(parsed.authors),
    raw_text=parsed.full_text,
    markdown_text=parsed.markdown_text
)

# 保存向量
vector_manager = VectorManager(str(settings.chroma_path))
chunk_texts = [chunk["text"] for chunk in chunks]
vector_manager.add_fulltext(paper_id, chunk_texts)
```

### 5. 测试解析器

```bash
# 将测试PDF放在 data/pdfs/test.pdf
python tests/test_parsers.py
```

## 解析器对比

| 特性 | PyMuPDF | Marker |
|------|---------|--------|
| 速度 | 快 | 慢 |
| 公式支持 | 基础 | 优秀（LaTeX） |
| 表格提取 | 好 | 优秀 |
| 安装难度 | 简单 | 复杂 |
| 推荐场景 | 快速原型 | 生产环境 |

## 下一步

- Phase 3: LLM集成 - 提取论文关键信息
- Phase 4: 向量检索 - 语义搜索论文
- Phase 5: 综述生成 - 自动生成文献综述
