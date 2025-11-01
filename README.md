# LitReview - 智能文献综述助手

基于RAG技术的智能文献综述生成系统，支持PDF解析、语义检索和自动综述生成。

**LitReview** = Literature Review Assistant

## 功能特性

- 📄 自动解析PDF论文（含公式、表格）
- 🤖 AI提取论文关键信息
- 🔍 语义检索相关论文
- 📝 自动生成文献综述
- 🌐 支持多种LLM（API和本地模型）

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

### 使用 MinerU

```python
from src.parsers import ParserFactory

# 创建 MinerU 解析器
parser = ParserFactory.create_parser("mineru", use_gpu=True)
result = parser.parse("data/pdfs/paper.pdf")
```

详细使用说明请查看 [MinerU 集成指南](docs/MINERU_INTEGRATION.md)

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
- [x] Phase 3: LLM集成
- [x] Phase 4: 向量检索
- [ ] Phase 5: 综述生成
- [ ] Phase 6: Web界面

## 许可证

MIT License
