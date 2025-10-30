#!/usr/bin/env python3
"""初始化数据库"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from src.database import SQLManager, VectorManager

def main():
    print("初始化数据库...")
    
    # 初始化SQLite
    print(f"创建SQLite数据库: {settings.sqlite_path}")
    sql_manager = SQLManager(str(settings.sqlite_path))
    print("✓ SQLite数据库初始化完成")
    
    # 初始化ChromaDB
    print(f"创建ChromaDB: {settings.chroma_path}")
    vector_manager = VectorManager(str(settings.chroma_path))
    print("✓ ChromaDB初始化完成")
    
    print("\n数据库初始化成功！")
    print(f"SQLite路径: {settings.sqlite_path}")
    print(f"ChromaDB路径: {settings.chroma_path}")

if __name__ == "__main__":
    main()
