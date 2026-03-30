import streamlit as st
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from src.database import SQLManager, VectorManager
from src.retrieval import QueryEngine
# from web.components.upload import render_upload_page
from web.components.search import render_search_page
from web.components.review_generator import render_review_page
from web.components.papers import render_papers_page
from web.components.upload import render_upload_page

st.set_page_config(
    page_title="LitReview - 智能文献综述助手",
    page_icon="📚",
    layout="wide"
)

if 'sql_manager' not in st.session_state:
    st.session_state.sql_manager = SQLManager(str(settings.sqlite_path))
    st.session_state.vector_manager = VectorManager(str(settings.chroma_path))
    st.session_state.query_engine = QueryEngine(
        st.session_state.vector_manager,
        st.session_state.sql_manager
    )

def main():
    st.title("📚 LitReview - 智能文献综述助手")
    
    st.sidebar.title("导航")
    page = st.sidebar.radio(
        "选择功能",
        ["📄 论文管理", "📤 上传论文", "🔍 搜索论文", "📝 生成综述"]
    )
    
    papers = st.session_state.sql_manager.get_all_papers()
    st.sidebar.markdown("---")
    st.sidebar.metric("论文总数", len(papers))
    st.sidebar.caption("当前上传链路默认使用 PyMuPDF，优先保证可用性。")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ 配置")
    
    llm_provider = st.sidebar.selectbox(
        "LLM提供商", 
        ["ollama", "openai", "claude", "gemini", "custom"]
    )
    
    if llm_provider == "ollama":
        model = st.sidebar.text_input("模型名称", value="llama2")
        base_url = st.sidebar.text_input("Ollama URL", value="http://localhost:11434")
        api_key = None
    elif llm_provider == "gemini":
        model = st.sidebar.text_input("模型名称", value="gemini-pro")
        api_key = st.sidebar.text_input("API Key", type="password")
        base_url = None
    elif llm_provider == "custom":
        model = st.sidebar.text_input("模型名称", value="gpt-3.5-turbo")
        base_url = st.sidebar.text_input("API URL", value="https://api.openai.com/v1")
        api_key = st.sidebar.text_input("API Key", type="password")
    else:
        model = st.sidebar.text_input("模型名称", value="gpt-3.5-turbo")
        api_key = st.sidebar.text_input("API Key", type="password")
        base_url = None
    
    st.session_state.llm_provider = llm_provider
    st.session_state.llm_model = model
    st.session_state.llm_api_key = api_key
    st.session_state.llm_base_url = base_url
    
    if page == "📄 论文管理":
        render_papers_page()
    elif page == "📤 上传论文":
        render_upload_page()
    elif page == "🔍 搜索论文":
        render_search_page()
    elif page == "📝 生成综述":
        render_review_page()

if __name__ == "__main__":
    main()
