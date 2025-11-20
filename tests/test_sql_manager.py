#!/usr/bin/env python3
"""测试 SQLManager 的 add_paper 功能"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.sql_manager import SQLManager
from scripts.analyze_papers import ArticleMetadata, Author

def create_test_pdf():
    """创建一个测试用的假PDF文件"""
    test_pdf = project_root / "data" / "pdfs" / "test_paper.pdf"
    test_pdf.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入一些假内容
    test_pdf.write_bytes(b"This is a test PDF file for testing purposes.")
    return str(test_pdf)

def test_add_paper():
    """测试添加论文功能"""
    
    # 1. 创建测试数据
    metadata = ArticleMetadata(
        title="Curiosity-Driven Reinforcement Learning for Dynamic Scheduling",
        abstract="This paper proposes a curiosity-driven RL framework for dynamic flexible job shop scheduling with stochastic job arrivals.",
        keywords=["Reinforcement Learning", "Job Shop Scheduling", "Curiosity-Driven Learning"],
        authors=[
            Author(name="张三", affiliation="清华大学"),
            Author(name="李四", affiliation="北京大学"),
            Author(name="王五", affiliation="")
        ],
        year=2024,
        venue="NeurIPS 2024",
        contributions=[
            "提出了好奇心驱动的强化学习框架",
            "改进了动态调度性能",
            "在多个基准测试上取得SOTA结果"
        ],
        ai_summary="本文提出了一种基于好奇心驱动的强化学习方法，用于解决动态柔性作业车间调度问题，显著提升了调度效率。"
    )
    
    # 2. 创建测试PDF
    pdf_path = create_test_pdf()
    print(f"✓ 创建测试PDF: {pdf_path}")
    
    # 3. 初始化数据库
    db_path = project_root / "data" / "database" / "test_papers.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 删除旧的测试数据库
    if db_path.exists():
        db_path.unlink()
    
    sql_manager = SQLManager(str(db_path))
    print(f"✓ 初始化数据库: {db_path}")
    
    # 4. 添加论文
    paper_id = sql_manager.add_paper(pdf_path=pdf_path, meta=metadata)
    print(f"✓ 添加论文成功，ID: {paper_id}")
    
    # 5. 读取并验证
    paper = sql_manager.get_paper(paper_id)
    
    print("\n" + "="*60)
    print("论文信息:")
    print("="*60)
    print(f"ID: {paper['id']}")
    print(f"标题: {paper['title']}")
    print(f"年份: {paper['year']}")
    print(f"会议: {paper['venue']}")
    print(f"摘要: {paper['abstract'][:100]}...")
    print(f"关键词: {paper['keywords']}")
    print(f"贡献点: {paper['contributions']}")
    print(f"AI摘要: {paper['ai_summary']}")
    print(f"作者JSON: {paper['authors']}")
    print(f"PDF路径: {paper['pdf_path']}")
    print(f"创建时间: {paper['created_at']}")
    print("="*60)
    
    # 6. 测试重复添加（应该返回相同ID）
    paper_id2 = sql_manager.add_paper(pdf_path=pdf_path, meta=metadata)
    print(f"\n✓ 重复添加测试: ID {paper_id2} (应该等于 {paper_id})")
    assert paper_id == paper_id2, "重复添加应该返回相同ID"
    
    # 7. 测试获取所有论文
    all_papers = sql_manager.get_all_papers()
    print(f"✓ 数据库中共有 {len(all_papers)} 篇论文")
    
    print("\n✅ 所有测试通过！")

if __name__ == "__main__":
    test_add_paper()
