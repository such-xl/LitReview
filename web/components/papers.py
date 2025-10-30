import streamlit as st

def render_papers_page():
    st.header("📄 论文管理")
    
    papers = st.session_state.sql_manager.get_all_papers()
    
    if not papers:
        st.info("📭 数据库中还没有论文，请前往「上传论文」页面添加")
        return
    
    st.success(f"共有 {len(papers)} 篇论文")
    
    for paper in papers:
        with st.expander(f"📄 {paper['title']}", expanded=False):
            st.markdown(f"**ID:** {paper['id']}")
            
            if paper.get('authors'):
                st.markdown(f"**作者:** {paper['authors']}")
            
            if paper.get('year'):
                st.markdown(f"**年份:** {paper['year']}")
            
            analysis = st.session_state.sql_manager.get_paper_analysis(paper['id'])
            if analysis:
                st.success("✅ 已分析")
                if analysis.get('keywords'):
                    keywords = analysis['keywords']
                    if isinstance(keywords, list):
                        st.markdown(f"**关键词:** {', '.join(keywords[:5])}")
            else:
                st.warning("⚠️ 未分析")
