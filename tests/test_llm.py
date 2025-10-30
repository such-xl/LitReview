import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.llm.llm_factory import LLMFactory
from src.analysis.extractor import PaperExtractor
from src.analysis.summarizer import PaperSummarizer

def test_ollama():
    """测试Ollama模型"""
    print("测试Ollama模型...")
    
    try:
        llm = LLMFactory.create_llm(provider="ollama", model="llama2")
        
        response = llm.generate(
            "请用一句话介绍什么是机器学习。",
            temperature=0.3
        )
        
        print(f"响应: {response}")
        print("✓ Ollama测试成功")
        
    except Exception as e:
        print(f"✗ Ollama测试失败: {e}")

def test_extractor():
    """测试信息提取"""
    print("\n测试信息提取...")
    
    test_text = """
    Title: Deep Learning for Natural Language Processing
    
    Abstract: This paper presents a novel approach to natural language processing 
    using deep learning techniques. We propose a new architecture that combines 
    transformers with attention mechanisms.
    
    Introduction: Natural language processing has been revolutionized by deep learning.
    
    Methods: We use a transformer-based architecture with multi-head attention.
    
    Results: Our model achieves state-of-the-art performance on several benchmarks.
    
    Conclusion: We demonstrate that our approach is effective for NLP tasks.
    """
    
    try:
        llm = LLMFactory.create_llm(provider="ollama", model="llama2")
        extractor = PaperExtractor(llm)
        
        result = extractor.extract_info(test_text)
        
        print(f"研究问题: {result.get('research_question', 'N/A')}")
        print(f"方法: {result.get('methodology', 'N/A')}")
        print(f"关键词: {result.get('keywords', [])}")
        print("✓ 提取测试成功")
        
    except Exception as e:
        print(f"✗ 提取测试失败: {e}")

def test_summarizer():
    """测试摘要生成"""
    print("\n测试摘要生成...")
    
    test_text = """
    This paper introduces a new method for image classification using convolutional 
    neural networks. We propose a novel architecture that achieves better accuracy 
    than previous approaches. Our experiments show significant improvements on 
    standard benchmarks.
    """
    
    try:
        llm = LLMFactory.create_llm(provider="ollama", model="llama2")
        summarizer = PaperSummarizer(llm)
        
        summary = summarizer.summarize(test_text, max_length=100)
        
        print(f"摘要: {summary}")
        print("✓ 摘要测试成功")
        
    except Exception as e:
        print(f"✗ 摘要测试失败: {e}")

if __name__ == "__main__":
    print("请确保Ollama正在运行: ollama serve")
    print("并且已下载模型: ollama pull llama2\n")
    
    test_ollama()
    test_extractor()
    test_summarizer()
