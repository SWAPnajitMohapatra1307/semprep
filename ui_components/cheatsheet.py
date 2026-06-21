import streamlit as st

def render_cheatsheet(data, weak_topics):
    st.subheader("Last-Minute Cheat Sheet")
    
    st.warning("Ultra-compact format. Focus on memory hooks and formulas only.")
    
    weighted_topics = data.get("weighted_topics", {})
    cheatsheet_text = data.get("cheatsheet", "")
    
    topics_list = []
    if isinstance(weighted_topics, dict):
        if "weighted_topics" in weighted_topics:
            topics_list = weighted_topics["weighted_topics"]
        elif "topics" in weighted_topics:
            topics_list = weighted_topics["topics"]
    elif isinstance(weighted_topics, list):
        topics_list = weighted_topics
    
    if weak_topics:
        st.markdown("### WEAK TOPICS (EXTRA FOCUS)")
        weak_topic_objs = [t for t in topics_list if t.get("topic_name") in weak_topics or t.get("name") in weak_topics]
        for topic in weak_topic_objs:
            with st.container(border=True):
                st.markdown(f"**{topic.get('topic_name', topic.get('name'))}** (Weight: {topic.get('weight', 0):.1f})")
                st.markdown("""
                - Key definition
                - Important points
                - Common mistakes
                - Exam tricks
                """)
    
    st.divider()
    st.markdown("### CRITICAL TOPICS")
    
    critical = [t for t in topics_list if t.get("weight", 0) >= 9]
    for topic in critical[:3]:
        with st.container(border=True):
            st.markdown(f"**{topic.get('topic_name', topic.get('name'))}** (Weight: {topic.get('weight', 0):.1f})")
            st.markdown(f"Years: {', '.join(map(str, topic.get('years_appeared', [])))} | Marks: {topic.get('typical_marks', 'N/A')}")
    
    if cheatsheet_text:
        st.divider()
        st.markdown("### Generated Cheat Sheet")
        st.markdown(cheatsheet_text)