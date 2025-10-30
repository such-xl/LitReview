# API 文档

## 核心模块使用指南

### 1. PDF解析

```python
from src.parsers import ParserFactory, TextChunker

# 创建解析器
parser = ParserFactory.create_parser("pymupdf")

# 解析PDF
parsed = parser.parse("path/to/paper.pdf")

# 文本分块
chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
chunks = chunker.chunk_text(parsed.full_text)
```

### 2. 数据库操作

```python
from src.database import SQLManager, VectorManager
from config import settings

# SQLite操作
sql_manager = SQLManager(str(settings.sqlite_path))

# 添加论文
paper_id = sql_manager.add_paper(
    title="论文标题",
    pdf_path="path/to/paper.pdf",
    authors="作者1, 作者2",
    raw_text="论文全文"
)

# 获取论文
paper = sql_manager.get_paper(paper_id)

# 向量数据库操作
vector_manager = VectorManager(str(settings.chroma_path))

# 添加向量
vector_manager.add_fulltext(paper_id, chunks)
vector_manager.add_abstract(paper_id, abstract)

# 搜索
results = vector_manager.search_fulltext("查询文本", n_results=10)
```

### 3. LLM集成

```python
from src.llm import LLMFactory

# 创建Ollama模型
llm = LLMFactory.create_llm(provider="ollama", model="llama2")

# 创建OpenAI模型
llm = LLMFactory.create_llm(
    provider="openai",
    model="gpt-4",
    api_key="your-api-key"
)

# 生成文本
response = llm.generate(
    prompt="你的提示词",
    system_prompt="系统提示词",
    temperature=0.3
)

# 生成结构化输出
result = llm.generate_structured(
    prompt="提取论文信息",
    schema={}
)
```

### 4. 论文分析

```python
from src.analysis import PaperExtractor, PaperSummarizer
from src.llm import LLMFactory

llm = LLMFactory.create_llm(provider="ollama")

# 信息提取
extractor = PaperExtractor(llm)
analysis = extractor.extract_info(paper_text)

# 摘要生成
summarizer = PaperSummarizer(llm)
summary = summarizer.summarize(paper_text)
```

### 5. 检索查询

```python
from src.retrieval import QueryEngine
from src.database import SQLManager, VectorManager

sql_manager = SQLManager(str(settings.sqlite_path))
vector_manager = VectorManager(str(settings.chroma_path))
query_engine = QueryEngine(vector_manager, sql_manager)

# 语义搜索
results = query_engine.query(
    "deep learning",
    method="semantic",
    n_results=10
)

# 混合搜索
results = query_engine.query(
    "machine learning",
    method="hybrid",
    n_results=10
)

# 高级搜索
results = query_engine.query(
    "neural networks",
    method="advanced",
    year_from=2020,
    year_to=2023,
    n_results=10
)

# 查找相似论文
similar = query_engine.find_similar(paper_id, n_results=5)
```

### 6. 综述生成

```python
from src.synthesis import LiteratureReviewGenerator, CitationManager
from src.llm import LLMFactory

llm = LLMFactory.create_llm(provider="ollama")
sql_manager = SQLManager(str(settings.sqlite_path))

# 创建生成器
generator = LiteratureReviewGenerator(llm, sql_manager)

# 生成完整综述
review = generator.generate_review(papers, topic="深度学习")

# 生成结构化综述
sections = generator.generate_structured_review(
    papers,
    topic="深度学习",
    sections=["研究背景", "主要方法", "研究趋势"]
)

# 生成摘要
summary = generator.generate_summary(papers, topic="深度学习")

# 引用管理
citation_manager = CitationManager()
for paper in papers:
    citation_manager.add_citation(paper)

bibliography = citation_manager.generate_bibliography(style="apa")
```

## 命令行工具

### 初始化数据库
```bash
python scripts/init_database.py
```

### 导入论文
```bash
# 单个PDF
python scripts/import_papers.py paper.pdf

# 批量导入
python scripts/import_papers.py data/pdfs/

# 使用Marker解析器
python scripts/import_papers.py data/pdfs/ --parser marker
```

### 分析论文
```bash
# 分析单篇
python scripts/analyze_papers.py --paper-id 1

# 分析所有
python scripts/analyze_papers.py --all

# 使用OpenAI
python scripts/analyze_papers.py --all --provider openai --model gpt-4
```

### 搜索论文
```bash
# 搜索
python scripts/search_papers.py search "deep learning"

# 语义搜索
python scripts/search_papers.py search "neural networks" --method semantic

# 查找相似
python scripts/search_papers.py similar 1 -n 5

# 列出所有
python scripts/search_papers.py list
```

### 生成综述
```bash
# 生成综述
python scripts/generate_review.py "深度学习" -n 20

# 保存到文件
python scripts/generate_review.py "深度学习" -o output/review.md

# 结构化综述
python scripts/generate_review.py "深度学习" --structured

# 只生成摘要
python scripts/generate_review.py "深度学习" --summary

# 使用OpenAI
python scripts/generate_review.py "深度学习" --provider openai --model gpt-4
```
