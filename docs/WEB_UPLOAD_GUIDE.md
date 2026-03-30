# Web 上传指南

## 当前默认流程

Web 上传页当前使用稳定主链路：

`PDF -> PyMuPDF -> SQLite -> ChromaDB`

上传成功后会完成：

- 保存原始 PDF
- 提取标题、作者、摘要和全文
- 将论文写入 SQLite
- 将全文和摘要写入 ChromaDB

## 使用步骤

1. 运行 `streamlit run web/app.py`
2. 打开“上传论文”
3. 选择一个或多个 PDF
4. 点击“开始导入”

## 当前限制

- 页面上不再默认暴露 MinerU 入口
- LLM 元数据提取开关暂时禁用
- 如果未安装 `chromadb`，上传后的向量索引无法建立

## 建议

- 想先恢复项目可用性：只走默认上传流程
- 想继续扩展解析质量：再单独修 MinerU 和 LLM 元数据链路
