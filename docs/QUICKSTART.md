# 快速开始指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 初始化数据库

```bash
python scripts/init_database.py
```

## 3. 启动 Web

```bash
streamlit run web/app.py
```

## 4. 上传论文

当前默认上传链路使用 `PyMuPDF`：

1. 打开“上传论文”
2. 选择 PDF 文件
3. 点击“开始导入”

系统会完成：

- PDF 解析
- SQLite 入库
- ChromaDB 向量索引

## 5. 搜索与综述

搜索：

```bash
python scripts/search_papers.py search "deep learning"
```

生成综述：

```bash
python scripts/generate_review.py "深度学习" -o review.md
```

## 6. 可选的 LLM 配置

如果你要启用综述生成或自定义模型，可配置：

```bash
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
```

## 说明

MinerU、Marker 和 LLM 元数据增强仍属于实验性路径，不作为当前默认文档流程。
