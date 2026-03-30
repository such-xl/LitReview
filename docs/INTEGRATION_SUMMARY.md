# 项目现状总结

## 当前稳定主链路

项目现在优先保证下面这条链路可维护：

`PyMuPDF -> SQLManager -> VectorManager -> QueryEngine -> LiteratureReviewGenerator`

对应入口：

- Web：`streamlit run web/app.py`
- 导入：`python scripts/import_papers.py data/pdfs/ --parser pymupdf`
- 搜索：`python scripts/search_papers.py search "query"`
- 综述：`python scripts/generate_review.py "topic"`

## 这次收口处理了什么

- 统一了 `SQLManager` 的数据模型和调用方式
- 补齐了 `get_paper_analysis()` 等缺失接口
- 修复了上传页和脚本对数据库接口的漂移
- 删除了旧上传组件和若干实验脚本
- 移除了仓库中的硬编码密钥
- 将文档改为反映当前真实状态

## 当前仍属实验性的内容

- MinerU 解析
- Marker 解析
- LLM 元数据提取
- 若干历史测试脚本和对比文档

这些代码没有全部删除，是因为后续仍可能继续修复；但它们不应被视为默认可用能力。

## 当前环境依赖

稳定运行至少需要：

- `streamlit`
- `chromadb`
- `PyMuPDF`
- `sentence-transformers`
- `pydantic`
- `pydantic-settings`

## 剩余风险

- 当前仓库仍有部分历史文档讨论 MinerU 和旧流程，阅读时需要以最新 README 为准
- 没有完整自动化测试；目前主要做了静态编译检查和 SQLite 层烟测
- 若本机缺少 `chromadb`，搜索和向量索引相关功能无法运行
