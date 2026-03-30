# 快速开始

## 最短路径

```bash
pip install -r requirements.txt
python scripts/init_database.py
streamlit run web/app.py
```

然后在 Web 界面中：

1. 打开“上传论文”
2. 上传 PDF
3. 打开“搜索论文”检索已导入内容
4. 打开“生成综述”生成摘要或综述

## 命令行

导入：

```bash
python scripts/import_papers.py data/pdfs/ --parser pymupdf
```

搜索：

```bash
python scripts/search_papers.py search "deep learning"
```

生成综述：

```bash
python scripts/generate_review.py "深度学习" -o review.md
```

## 建议

- 想先跑通项目：用 `pymupdf`
- 想启用 LLM：先在侧边栏配置 Ollama 或 API Key
- 如果 `chromadb` 未安装，检索和上传后的向量索引不会可用
