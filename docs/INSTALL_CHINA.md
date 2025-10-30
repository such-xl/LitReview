# 国内安装指南

## 快速安装（推荐）

### 方法1: 使用Conda（最稳定）

```bash
# 1. 安装Miniconda
# 下载: https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/

# 2. 配置清华镜像
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --set show_channel_urls yes

# 3. 创建环境
conda create -n litreview python=3.10
conda activate litreview

# 4. 安装依赖
conda install numpy pandas sqlalchemy tqdm
conda install -c conda-forge chromadb sentence-transformers
pip install PyMuPDF ollama python-dotenv pydantic pydantic-settings

# 5. 安装streamlit（可选）
conda install -c conda-forge streamlit
# 如果失败，跳过Web界面
```

### 方法2: 使用国内pip镜像

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 2. 配置pip镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 安装核心依赖（不含Web界面）
pip install -r requirements-no-web.txt

# 4. 尝试安装streamlit（可选）
pip install streamlit
# 如果失败，继续下一步
```

### 方法3: 跳过Web界面

如果streamlit安装失败，可以只使用命令行工具：

```bash
# 安装核心依赖
pip install -r requirements-no-web.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 验证安装
python -c "import chromadb; import fitz; print('✅ 核心功能安装成功！')"
```

## 使用命令行工具（无需Web界面）

```bash
# 初始化数据库
python scripts/init_database.py

# 导入论文
python scripts/import_papers.py data/pdfs/

# 分析论文
python scripts/analyze_papers.py --all

# 搜索论文
python scripts/search_papers.py search "深度学习"

# 生成综述
python scripts/generate_review.py "深度学习" -o review.md
```

## pyarrow 问题解决

### 方案1: 使用conda（推荐）
```bash
conda install -c conda-forge pyarrow
pip install streamlit
```

### 方案2: 使用预编译版本
```bash
pip install pyarrow==14.0.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install streamlit -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方案3: 跳过streamlit
```bash
# 只安装核心功能，使用命令行工具
pip install -r requirements-no-web.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 常用镜像源

```bash
# 清华源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name

# 阿里云
pip install -i https://mirrors.aliyun.com/pypi/simple/ package_name

# 中科大
pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ package_name

# 豆瓣
pip install -i https://pypi.douban.com/simple/ package_name
```

## 永久配置镜像

```bash
# Linux/Mac
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

# Windows
# 在 C:\Users\用户名\pip\pip.ini 中添加：
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
```

## 验证安装

```bash
# 测试核心功能
python scripts/init_database.py

# 如果安装了streamlit
streamlit run web/app.py

# 如果没有streamlit，使用命令行
python scripts/search_papers.py list
```
