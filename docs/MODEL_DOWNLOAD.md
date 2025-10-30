# 模型下载说明

## ChromaDB嵌入模型下载

首次运行时，ChromaDB会自动下载 `all-MiniLM-L6-v2` 模型（约90MB）。

### 方法1: 等待自动下载（推荐）

直接等待下载完成，通常需要几分钟。

### 方法2: 手动下载（如果自动下载失败）

```bash
# 创建目录
mkdir -p ~/.cache/chroma/onnx_models/all-MiniLM-L6-v2

# 下载模型文件
cd ~/.cache/chroma/onnx_models/all-MiniLM-L6-v2

# 从Hugging Face下载
wget https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/onnx.tar.gz

# 或使用国内镜像
wget https://hf-mirror.com/sentence-transformers/all-MiniLM-L6-v2/resolve/main/onnx.tar.gz

# 解压
tar -xzf onnx.tar.gz
```

### 方法3: 使用代理加速

```bash
# 设置代理
export http_proxy=http://192.168.31.112:10809
export https_proxy=http://192.168.31.112:10809

# 重新运行应用
streamlit run web/app.py
```

### 方法4: 使用其他嵌入模型

如果下载一直失败，可以修改配置使用其他模型：

```python
# 编辑 config/settings.py
EMBEDDING_MODEL = "paraphrase-MiniLM-L3-v2"  # 更小的模型
```

### 检查下载进度

```bash
# 查看文件大小
ls -lh ~/.cache/chroma/onnx_models/all-MiniLM-L6-v2/

# 完整的模型文件约90MB
# 如果文件小于90MB，说明还在下载中
```

### 常见问题

**Q: 下载很慢怎么办？**
A: 使用代理或手动从国内镜像下载

**Q: 下载失败怎么办？**
A: 删除缓存目录重试：`rm -rf ~/.cache/chroma/onnx_models/`

**Q: 可以跳过模型下载吗？**
A: 不可以，ChromaDB需要嵌入模型才能工作

**Q: 模型下载到哪里了？**
A: `~/.cache/chroma/onnx_models/all-MiniLM-L6-v2/`
