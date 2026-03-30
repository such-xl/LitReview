# LitReview

一个面向个人研究场景的文献综述助手，核心流程是：

`PDF 导入 -> SQLite/ChromaDB 建库 -> 检索 -> 综述生成`

当前仓库已经完成了一次收口，优先保留稳定主链路。Web 上传默认使用 `PyMuPDF`，LLM 元数据增强和 MinerU 高质量解析仍保留实验代码，但不再作为默认入口。

## 当前可用功能

- PDF 上传并入库
- SQLite 存储论文元信息和全文
- ChromaDB 全文/摘要向量索引
- 语义检索和混合检索
- 基于已入库论文生成摘要或综述
- Streamlit Web 界面

## 当前状态

- 稳定主链路：`PyMuPDF + SQLite + ChromaDB + Streamlit`
- 可选能力：Ollama / OpenAI / Claude / Gemini
- 实验能力：MinerU、Marker、LLM 元数据提取

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

如果你只想先跑核心功能，至少需要这些关键依赖：

```bash
pip install streamlit chromadb PyMuPDF sentence-transformers pydantic pydantic-settings
```

### 2. 配置环境变量

项目不再内置任何 API Key。可在 `.env` 中配置，例如：

```bash
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. 初始化数据库

```bash
python scripts/init_database.py
```

如果当前环境未安装 `chromadb`，脚本会只初始化 SQLite 并给出提示。

### 4. 运行应用

```bash
streamlit run web/app.py
```

## Web 使用说明

1. 打开“上传论文”，上传 PDF。
2. 系统会解析文本、写入 SQLite，并建立向量索引。
3. 在“搜索论文”中执行语义或混合检索。
4. 在“生成综述”中基于检索结果生成摘要或综述。

## 命令行

导入论文：

```bash
python scripts/import_papers.py data/pdfs/ --parser pymupdf
```

搜索论文：

```bash
python scripts/search_papers.py search "deep learning"
```

生成综述：

```bash
python scripts/generate_review.py "深度学习" -o review.md
```

上传链路测试：

```bash
python scripts/test_upload_pipeline.py data/pdfs/paper.pdf --parser pymupdf
```

## 目录

```text
config/          配置
data/            数据目录
docs/            文档
scripts/         命令行脚本
src/             核心模块
web/             Streamlit 界面
tests/           测试
```

## 文档

- [快速开始](docs/QUICKSTART.md)
- [安装说明](docs/INSTALL.md)
- [Web 上传说明](docs/WEB_UPLOAD_GUIDE.md)
- [项目现状](docs/INTEGRATION_SUMMARY.md)

## 说明

仓库中仍保留了一些未完全收口的实验模块，尤其是 MinerU 和部分 LLM 元数据抽取代码。如果你的目标是先把项目跑起来，建议只走默认的 `PyMuPDF` 路线。
