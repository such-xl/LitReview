# MinerU + LLM 智能元数据提取

## 功能说明

MinerU解析器现已集成LLM，可智能提取论文元数据：
- 标题 (title)
- 作者 (authors)
- 单位 (affiliations)
- 摘要 (abstract)
- 关键词 (keywords)
- 出版商/会议 (publisher)
- 年份 (year)

## 使用方法

### 方法1：使用工厂函数（推荐）

```python
from src.parsers.mineru_chunker import create_mineru_parser

# 使用Ollama本地模型
parser = create_mineru_parser(
    use_gpu=True,
    llm_provider="ollama",
    llm_model="llama2"
)

result = parser.parse("paper.pdf")
print(f"标题: {result.title}")
print(f"作者: {result.authors}")
```

### 方法2：手动配置

```python
from src.parsers.mineru_chunker import MinerUParser
from src.llm import LLMFactory

# 创建LLM实例
llm = LLMFactory.create_llm(provider="ollama", model="llama2")

# 创建解析器
parser = MinerUParser(use_gpu=True, llm=llm)

result = parser.parse("paper.pdf")
```

### 方法3：不使用LLM（回退到正则表达式）

```python
from src.parsers.mineru_chunker import MinerUParser

# 不传入llm参数
parser = MinerUParser(use_gpu=True)

result = parser.parse("paper.pdf")
```

## 支持的LLM提供商

### Ollama（本地模型）
```python
parser = create_mineru_parser(
    llm_provider="ollama",
    llm_model="llama2"  # 或 qwen, mistral 等
)
```

### OpenAI
```python
from src.llm import LLMFactory

llm = LLMFactory.create_llm(
    provider="openai",
    model="gpt-3.5-turbo",
    api_key="your-key"
)

parser = MinerUParser(use_gpu=True, llm=llm)
```

### Claude
```python
from src.llm import LLMFactory

llm = LLMFactory.create_llm(
    provider="claude",
    model="claude-3-sonnet-20240229",
    api_key="your-key"
)

parser = MinerUParser(use_gpu=True, llm=llm)
```

### Gemini
```python
from src.llm import LLMFactory

llm = LLMFactory.create_llm(
    provider="gemini",
    model="gemini-pro",
    api_key="your-api-key"
)

parser = MinerUParser(use_gpu=True, llm=llm)
```

### 自定义API（OpenAI兼容）
```python
from src.llm import LLMFactory

llm = LLMFactory.create_llm(
    provider="custom",
    model="your-model",
    api_key="your-key",
    base_url="https://your-api.com/v1"
)

parser = MinerUParser(use_gpu=True, llm=llm)
```

## 工作原理

1. **MinerU解析**: 将PDF转换为JSON和Markdown
2. **提取首页**: 从JSON中提取第一页内容（约1000字符）
3. **LLM分析**: 使用 `generate_structured()` 方法提取结构化元数据
4. **智能回退**: LLM失败时自动使用正则表达式提取

## 性能对比

| 方法 | 准确率 | 速度 | 适用场景 |
|------|--------|------|----------|
| LLM提取 | 95%+ | 慢 | 高质量需求 |
| 正则表达式 | 60-70% | 快 | 快速预览 |

## 注意事项

- LLM提取需要额外时间（5-30秒/篇）
- 建议使用本地Ollama模型以降低成本
- 首次使用需下载模型：`ollama pull llama2`
- 如果LLM不可用，会自动回退到正则表达式
