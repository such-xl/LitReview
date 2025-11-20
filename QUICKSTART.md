# 快速开始指南

## 5分钟上手 LitReview

### 1. 安装Ollama（本地LLM）

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull llama2
```

### 2. 启动Web应用

```bash
streamlit run web/app.py
```

浏览器自动打开 `http://localhost:8501`

### 3. 配置LLM（侧边栏）

- **LLM提供商**: 选择 `ollama`
- **模型名称**: 输入 `llama2`
- **Ollama URL**: `http://localhost:11434`

### 4. 上传论文

1. 点击 **"📤 上传论文"**
2. 选择解析器: **MinerU**（推荐）
3. ✅ 勾选 **"使用LLM提取元数据"**
4. ✅ 勾选 **"使用GPU加速"**（如果有GPU）
5. 点击 **"Browse files"** 上传PDF
6. 点击 **"开始导入"**

### 5. 查看结果

- 点击 **"📄 论文管理"** 查看已导入的论文
- 点击 **"🔍 搜索论文"** 进行语义检索

## 命令行测试

```bash
# 测试单个PDF
python scripts/test_upload_pipeline.py data/pdfs/your_paper.pdf

# 不使用LLM（快速模式）
python scripts/test_upload_pipeline.py data/pdfs/your_paper.pdf --no-llm

# 不使用GPU
python scripts/test_upload_pipeline.py data/pdfs/your_paper.pdf --no-gpu
```

## Python代码示例

```python
from src.parsers.mineru_chunker import create_mineru_parser

# 创建解析器（自动配置LLM）
parser = create_mineru_parser(
    use_gpu=True,
    llm_provider="ollama",
    llm_model="llama2"
)

# 解析PDF
result = parser.parse("paper.pdf")

# 查看结果
print(f"标题: {result.title}")
print(f"作者: {', '.join(result.authors)}")
print(f"摘要: {result.abstract[:200]}...")
```

## 配置选项

### 高质量模式（推荐）
- 解析器: **MinerU**
- GPU加速: ✅
- LLM提取: ✅
- 速度: 30-60秒/篇
- 质量: ⭐⭐⭐⭐⭐

### 快速模式
- 解析器: **PyMuPDF**
- GPU加速: ❌
- LLM提取: ❌
- 速度: 1-5秒/篇
- 质量: ⭐⭐⭐

### 平衡模式
- 解析器: **Marker**
- GPU加速: ❌
- LLM提取: ✅
- 速度: 20-40秒/篇
- 质量: ⭐⭐⭐⭐

## 常见问题

### Q: Ollama连接失败？
```bash
# 检查Ollama是否运行
ollama list

# 如果没运行，启动它
ollama serve
```

### Q: GPU不可用？
- 不勾选"使用GPU加速"，使用CPU模式
- 或安装CUDA和PyTorch with CUDA

### Q: 解析失败？
- 尝试其他解析器（Marker或PyMuPDF）
- 检查PDF文件是否损坏

### Q: LLM提取失败？
- 系统会自动回退到正则表达式提取
- 不影响整体流程

## 下一步

- 📖 阅读 [Web上传指南](docs/WEB_UPLOAD_GUIDE.md)
- 🔧 查看 [MinerU+LLM使用](docs/MINERU_LLM_USAGE.md)
- 📊 了解 [集成总结](docs/INTEGRATION_SUMMARY.md)

## 需要帮助？

- 查看 `docs/` 目录下的详细文档
- 运行测试脚本验证配置
- 检查日志文件 `data/logs/`

祝使用愉快！🎉
