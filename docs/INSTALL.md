# 安装指南

## 方法1: 标准安装（推荐）

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装核心依赖
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

## 方法2: 分步安装

如果遇到依赖冲突，可以分步安装：

```bash
# 1. 基础工具
pip install python-dotenv tqdm pydantic pydantic-settings

# 2. 数据处理
pip install numpy pandas sqlalchemy

# 3. PDF解析
pip install PyMuPDF

# 4. 向量数据库
pip install chromadb

# 5. 嵌入模型
pip install sentence-transformers

# 6. LLM集成
pip install ollama

# 7. Web界面
pip install streamlit
```

## 方法3: 使用conda（推荐用于科研环境）

```bash
# 创建conda环境
conda create -n litreview python=3.10
conda activate litreview

# 安装依赖
pip install -r requirements-minimal.txt
```

## 常见问题

### 问题1: marker-pdf 安装失败
**解决方案**: marker-pdf 是可选的，可以只使用 PyMuPDF
```bash
# 跳过 marker-pdf，只安装 PyMuPDF
pip install PyMuPDF
```

### 问题2: chromadb 安装失败
**解决方案**: 确保 Python 版本 >= 3.8
```bash
python --version
pip install --upgrade pip setuptools wheel
pip install chromadb
```

### 问题3: sentence-transformers 安装慢
**解决方案**: 使用国内镜像
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple sentence-transformers
```

### 问题4: pyarrow 编译失败
**解决方案**: 使用预编译的二进制包
```bash
# 方法1: 使用conda安装（推荐）
conda install -c conda-forge pyarrow

# 方法2: 指定版本安装
pip install pyarrow==14.0.1 --no-build-isolation

# 方法3: 跳过streamlit，使用轻量级替代
pip install gradio  # 或其他Web框架
```

### 问题5: 在 Windows 上安装失败
**解决方案**: 安装 Visual C++ Build Tools
- 下载: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- 或使用 conda 环境

## 验证安装

```bash
# 测试导入
python -c "import streamlit; import chromadb; import fitz; print('安装成功！')"

# 初始化数据库
python scripts/init_database.py

# 启动应用
streamlit run web/app.py
```

## 可选依赖

### LiteLLM (支持更多LLM API)
```bash
pip install litellm
```

### Marker (高质量PDF解析)
```bash
pip install marker-pdf
```

### Plotly (数据可视化)
```bash
pip install plotly
```

## 系统要求

- Python: 3.8 - 3.11
- 内存: 至少 4GB RAM
- 磁盘: 至少 2GB 可用空间
- 操作系统: Linux, macOS, Windows
