# LitReview - 智能文献综述助手

基于RAG技术的智能文献综述生成系统，支持PDF解析、语义检索和自动综述生成。

**LitReview** = Literature Review Assistant

## 功能特性

- 📄 自动解析PDF论文（含公式、表格）
- 🤖 LLM智能提取元数据（标题、作者、摘要等）
- 💾 自动存入数据库（SQLite + ChromaDB）
- 🔍 语义检索相关论文
- 📝 自动生成文献综述
- 🌐 支持多种LLM（Ollama/OpenAI/Claude）
- 🖥️ 友好的Web界面

## 技术栈

- **PDF解析**: MinerU / Marker / PyMuPDF
- **向量数据库**: ChromaDB
- **嵌入模型**: sentence-transformers
- **LLM集成**: LiteLLM + Ollama
- **数据库**: SQLite
- **Web框架**: Streamlit

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt

# 可选：安装 MinerU 用于高质量 PDF 解析
pip install magic-pdf[full]
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置API密钥等
```

### 3. 初始化数据库

```bash
python scripts/init_database.py
```

### 4. 安装Ollama（可选，用于本地模型）

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull llama2
```

### 5. 运行应用

```bash
streamlit run web/app.py
```

## PDF 解析器选择

项目支持多种 PDF 解析器，可根据需求选择：

| 解析器 | 优势 | 适用场景 |
|--------|------|----------|
| **MinerU** | GPU加速、高质量、支持公式表格 | 推荐，适合大批量处理 |
| **Marker** | 质量好、支持公式 | 中等规模处理 |
| **PyMuPDF** | 速度快、轻量级 | 快速预览、简单文档 |
| **LLM** | 最高质量、智能理解 | 小批量高质量需求 |

### 使用 MinerU + LLM

```python
from src.parsers.mineru_chunker import create_mineru_parser

# 创建带LLM的MinerU解析器（推荐）
parser = create_mineru_parser(
    use_gpu=True,
    llm_provider="ollama",
    llm_model="llama2"
)
result = parser.parse("data/pdfs/paper.pdf")

print(result.title)      # LLM智能提取
print(result.authors)    # 高准确率
print(result.abstract)   # 完整摘要
```

详细使用说明:
- [MinerU 集成指南](docs/MINERU_INTEGRATION.md)
- [MinerU + LLM 使用](docs/MINERU_LLM_USAGE.md)
- [Web上传功能](docs/WEB_UPLOAD_GUIDE.md)

## 项目结构

```
literature-review-rag/
├── config/              # 配置文件
├── data/               # 数据目录
│   ├── pdfs/          # PDF文件
│   ├── database/      # 数据库文件
│   └── logs/          # 日志
├── src/               # 源代码
│   ├── parsers/       # PDF解析
│   ├── database/      # 数据库操作
│   ├── llm/           # LLM集成
│   ├── analysis/      # 论文分析
│   ├── retrieval/     # 检索模块
│   └── synthesis/     # 综述生成
├── scripts/           # 工具脚本
├── web/              # Web界面
└── tests/            # 测试

```

## 开发进度

- [x] Phase 1: 基础设施搭建
- [x] Phase 2: PDF解析 (PyMuPDF/Marker/MinerU)
- [x] Phase 3: LLM集成 (Ollama/OpenAI/Claude)
- [x] Phase 4: 向量检索 (ChromaDB)
- [x] Phase 5: LLM智能元数据提取
- [x] Phase 6: Web上传界面
- [ ] Phase 7: 综述生成
- [ ] Phase 8: 完善Web界面

## 测试

### 测试完整上传流程

```bash
# 测试单个PDF（使用LLM + GPU）
python scripts/test_upload_pipeline.py data/pdfs/paper.pdf

# 不使用LLM
python scripts/test_upload_pipeline.py data/pdfs/paper.pdf --no-llm

# 不使用GPU
python scripts/test_upload_pipeline.py data/pdfs/paper.pdf --no-gpu
```

### 使用Web界面

1. 启动应用: `streamlit run web/app.py`
2. 在侧边栏配置LLM（推荐Ollama）
3. 点击"📤 上传论文"
4. 选择MinerU解析器
5. 勾选"使用LLM提取元数据"
6. 上传PDF文件

详见 [Web上传指南](docs/WEB_UPLOAD_GUIDE.md)

## 许可证

MIT License
