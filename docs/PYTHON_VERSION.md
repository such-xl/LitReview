# Python版本问题

## 问题
Python 3.14.0 太新，pyarrow等库还没有提供预编译包。

## 解决方案

### 方案1: 使用Python 3.10或3.11（推荐）

```bash
# 使用pyenv安装Python 3.10
curl https://pyenv.run | bash

# 安装Python 3.10
pyenv install 3.10.13

# 在项目中使用
cd /home/xiale/papers/mcp
pyenv local 3.10.13

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements-minimal.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方案2: 使用Conda（最简单）

```bash
# 创建Python 3.10环境
conda create -n litreview python=3.10 -y
conda activate litreview

# 安装所有依赖（包含pyarrow）
conda install -c conda-forge pyarrow streamlit chromadb sentence-transformers -y
pip install PyMuPDF ollama python-dotenv pydantic pydantic-settings tqdm
```

### 方案3: 使用系统Python

```bash
# Ubuntu/Debian
sudo apt install python3.10 python3.10-venv

# 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements-minimal.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 推荐的Python版本

- ✅ Python 3.10 (推荐)
- ✅ Python 3.11 (推荐)
- ⚠️ Python 3.12 (部分包可能不兼容)
- ❌ Python 3.13+ (太新，很多包没有预编译版本)

## 快速解决

```bash
# 最快的方法：使用conda
conda create -n litreview python=3.10 -y
conda activate litreview
conda install -c conda-forge streamlit pyarrow -y
pip install -r requirements-no-web.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
