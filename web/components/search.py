import streamlit as st

def render_search_page():
    st.header("🔍 搜索论文")
    
    # 搜索输入
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "输入搜索查询",
            placeholder="例如: deep learning, transformer, 自然语言处理"
        )
    
    with col2:
        search_method = st.selectbox(
            "搜索方法",
            ["hybrid", "semantic", "advanced"],
            format_func=lambda x: {
                "hybrid": "混合搜索",
                "semantic": "语义搜索",
                "advanced": "高级搜索"
            }[x]
        )
    
    # 高级选项
    with st.expander("🔧 高级选项"):
        n_results = st.slider("返回结果数", 5, 50, 10)
    
    # 搜索按钮
    if st.button("🔍 搜索", type="primary") and query:
        with st.spinner("搜索中..."):
            results = st.session_state.query_engine.query(
                query,
                method=search_method,
                n_results=n_results
            )
            
            # 显示结果
            if results:
                st.success(f"找到 {len(results)} 篇相关论文")
                
                for i, paper in enumerate(results, 1):
                    with st.expander(f"📄 {i}. {paper['title']}", expanded=(i <= 3)):
                        if paper.get('authors'):
                            st.markdown(f"**作者:** {paper['authors']}")
                        
                        if paper.get('year'):
                            st.markdown(f"**年份:** {paper['year']}")
                        
                        score_key = 'final_score' if 'final_score' in paper else 'relevance_score'
                        if score_key in paper:
                            st.metric("相关度", f"{paper[score_key]:.3f}")
            else:
                st.warning("未找到相关论文")
