# 快速开始指南

## 1. 安装依赖

```bash
# 推荐：使用最小化依赖
pip install -r requirements-minimal.txt

# 或者：完整依赖
pip install -r requirements.txt

# 国内用户推荐使用conda或查看 docs/INSTALL_CHINA.md
# 如果遇到问题，请查看 docs/INSTALL.md
```

## 2. 初始化数据库

```bash
python scripts/init_database.py
```

## 3. 启动Web界面

```bash
streamlit run web/app.py
# 或使用启动脚本
./run.sh
```

## 4. 使用流程

### 4.1 上传论文
1. 点击「上传论文」
2. 选择PDF文件
3. 点击「开始导入」

### 4.2 搜索论文
1. 点击「搜索论文」
2. 输入查询关键词
3. 选择搜索方法
4. 查看搜索结果

### 4.3 生成综述
1. 点击「生成综述」
2. 输入研究主题
3. 选择论文数量和综述类型
4. 点击「生成综述」
5. 下载生成的综述

## 5. 命令行工具

### 导入论文
```bash
python scripts/import_papers.py data/pdfs/
```

### 分析论文
```bash
python scripts/analyze_papers.py --all
```

### 搜索论文
```bash
python scripts/search_papers.py search "deep learning"
```

### 生成综述
```bash
python scripts/generate_review.py "深度学习" -o review.md
```

## 6. 配置Ollama（可选）

```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull llama2

# 启动服务
ollama serve
```
