# Web上传功能使用指南

## 功能概述

通过Streamlit网页界面上传PDF论文，系统自动：
1. 解析PDF（支持MinerU/Marker/PyMuPDF）
2. 使用LLM智能提取元数据（标题、作者、摘要等）
3. 存入SQLite数据库
4. 向量化并存入ChromaDB

## 使用步骤

### 1. 启动Web应用

```bash
streamlit run web/app.py
```

### 2. 配置LLM（侧边栏）

在侧边栏配置LLM提供商：

**Ollama（推荐）**
- LLM提供商: `ollama`
- 模型名称: `llama2` 或 `qwen`
- Ollama URL: `http://localhost:11434`

**OpenAI**
- LLM提供商: `openai`
- 模型名称: `gpt-3.5-turbo`
- API Key: 输入你的密钥

**Gemini**
- LLM提供商: `gemini`
- 模型名称: `gemini-pro`
- API Key: 输入你的密钥

**自定义API**
- LLM提供商: `custom`
- 模型名称: 你的模型
- API URL: 你的API地址
- API Key: 你的密钥

### 3. 上传论文

1. 点击"📤 上传论文"
2. 选择解析器：
   - **MinerU**: 高质量GPU加速（推荐）
   - **Marker**: 中等质量
   - **PyMuPDF**: 快速轻量
3. 勾选"使用LLM提取元数据"（推荐）
4. 如果选择MinerU，可勾选"使用GPU加速"
5. 上传PDF文件（支持批量）
6. 点击"开始导入"

### 4. 查看结果

- 导入成功后会显示成功数量
- 在"📄 论文管理"页面查看已导入的论文
- 侧边栏显示论文总数

## 工作流程

```
PDF上传 
  ↓
MinerU解析 (GPU加速)
  ↓
生成JSON + Markdown
  ↓
LLM提取元数据 (智能)
  ├─ title
  ├─ authors
  ├─ abstract
  ├─ keywords
  └─ year
  ↓
存入SQLite数据库
  ↓
文本分块 (1000字符/块)
  ↓
向量化存入ChromaDB
  ↓
完成 ✓
```

## 数据存储

### SQLite数据库
- 位置: `data/database/papers.db`
- 表: `papers` (论文基本信息)
- 字段: id, title, authors, year, pdf_path, raw_text, markdown_text

### ChromaDB向量库
- 位置: `data/database/chroma/`
- 用途: 语义检索

## LLM提取 vs 正则表达式

| 方法 | 准确率 | 速度 | 成本 |
|------|--------|------|------|
| LLM提取 | 95%+ | 5-30秒/篇 | 有成本（Ollama免费） |
| 正则表达式 | 60-70% | <1秒/篇 | 免费 |

## 注意事项

1. **首次使用Ollama需下载模型**
   ```bash
   ollama pull llama2
   ```

2. **GPU加速需要**
   - CUDA环境
   - PyTorch with CUDA
   - 足够的显存（建议8GB+）

3. **批量上传建议**
   - 每次不超过10篇
   - 大文件可能需要较长时间

4. **错误处理**
   - MinerU失败会自动回退到PyMuPDF
   - LLM失败会自动回退到正则表达式
   - 不会中断整个导入流程

## 示例配置

### 配置1：最高质量（推荐）
- 解析器: MinerU
- GPU加速: ✓
- LLM提取: ✓
- LLM提供商: Ollama (llama2)

### 配置2：快速预览
- 解析器: PyMuPDF
- GPU加速: ✗
- LLM提取: ✗

### 配置3：平衡模式
- 解析器: Marker
- GPU加速: ✗
- LLM提取: ✓
- LLM提供商: Ollama (llama2)

## 故障排查

**问题1: LLM加载失败**
- 检查Ollama是否运行: `ollama list`
- 检查模型是否下载: `ollama pull llama2`
- 检查端口是否正确: 默认11434

**问题2: GPU不可用**
- 检查CUDA: `nvidia-smi`
- 检查PyTorch: `python -c "import torch; print(torch.cuda.is_available())"`
- 可以不勾选GPU加速，使用CPU

**问题3: 解析失败**
- 检查PDF是否损坏
- 尝试其他解析器
- 查看错误信息

## 性能参考

| 配置 | 速度 | 质量 |
|------|------|------|
| MinerU + GPU + LLM | 30-60秒/篇 | ⭐⭐⭐⭐⭐ |
| MinerU + CPU + LLM | 60-120秒/篇 | ⭐⭐⭐⭐⭐ |
| Marker + LLM | 20-40秒/篇 | ⭐⭐⭐⭐ |
| PyMuPDF + 正则 | 1-5秒/篇 | ⭐⭐⭐ |
