# Gemini 使用指南

## 安装依赖

```bash
pip install google-generativeai
```

## 获取API Key

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建API密钥
3. 复制密钥

## 使用方法

### 方法1: Web界面

1. 启动应用: `streamlit run web/app.py`
2. 在侧边栏配置:
   - **LLM提供商**: 选择 `gemini`
   - **模型名称**: `gemini-pro` 或 `gemini-1.5-pro`
   - **API Key**: 输入你的密钥
3. 上传PDF即可

### 方法2: Python代码

```python
from src.parsers.mineru_chunker import create_mineru_parser
from src.llm import LLMFactory

# 创建Gemini LLM
llm = LLMFactory.create_llm(
    provider="gemini",
    model="gemini-pro",
    api_key="your-api-key"
)

# 创建解析器
from src.parsers.mineru_chunker import MinerUParser
parser = MinerUParser(use_gpu=True, llm=llm)

# 解析PDF
result = parser.parse("paper.pdf")
print(result.title)
```

### 方法3: 环境变量

```bash
# .env 文件
GEMINI_API_KEY=your-api-key
```

```python
import os
from src.llm import LLMFactory

llm = LLMFactory.create_llm(
    provider="gemini",
    api_key=os.getenv("GEMINI_API_KEY")
)
```

## 支持的模型

- `gemini-pro` - 标准模型（推荐）
- `gemini-1.5-pro` - 最新模型
- `gemini-1.5-flash` - 快速模型

## 特点

- ✅ 免费额度充足
- ✅ 支持长上下文
- ✅ 多语言支持好
- ✅ 响应速度快

## 注意事项

1. 需要科学上网（部分地区）
2. 免费额度: 60次/分钟
3. 上下文长度: 最高2M tokens (gemini-1.5-pro)

## 对比其他LLM

| 提供商 | 免费额度 | 速度 | 质量 | 推荐度 |
|--------|---------|------|------|--------|
| Ollama | 无限 | 中 | 好 | ⭐⭐⭐⭐⭐ |
| Gemini | 60次/分 | 快 | 优秀 | ⭐⭐⭐⭐⭐ |
| OpenAI | 付费 | 快 | 优秀 | ⭐⭐⭐⭐ |
| Claude | 付费 | 快 | 优秀 | ⭐⭐⭐⭐ |
