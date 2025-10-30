#!/bin/bash
echo "🚀 启动 LitReview - 智能文献综述助手..."
if [ ! -f "data/database/papers.db" ]; then
    echo "📦 初始化数据库..."
    python scripts/init_database.py
fi
echo "🌐 启动Web界面..."
streamlit run web/app.py
