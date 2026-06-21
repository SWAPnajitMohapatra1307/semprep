import streamlit as st
from datastore import mark_topic_weak, mark_topic_mastered

def render_progress(subject, topics_list, progress_data):
    st.subheader("Track Your Progress")
    
    weak_topics = progress_data.get("weak_topics", [])
    mastered_topics = progress_data.get("mastered_topics", [])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Mastered", len(mastered_topics))
    with col2:
        st.metric("Weak", len(weak_topics))
    with col3:
        st.metric("Not Reviewed", len(topics_list) - len(mastered_topics) - len(weak_topics))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Mastered Topics ✓")
        if mastered_topics:
            for topic in mastered_topics:
                st.success(f"✓ {topic}")
        else:
            st.info("No mastered topics yet")
    
    with col2:
        st.markdown("### Weak Topics ⚠️")
        if weak_topics:
            for topic in weak_topics:
                st.warning(f"⚠ {topic}")
        else:
            st.info("No weak topics marked")
    
    st.divider()
    st.subheader("Mark Topic Status")
    
    for topic in topics_list:
        topic_name = topic.get("topic_name", topic.get("name", "Unknown"))
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            if topic_name in mastered_topics:
                st.write(f"✓ **{topic_name}**")
            elif topic_name in weak_topics:
                st.write(f"⚠ **{topic_name}**")
            else:
                st.write(f"⭕ **{topic_name}**")
        
        with col2:
            if st.button("Weak", key=f"weak_{topic_name}", use_container_width=True):
                mark_topic_weak(subject, topic_name)
                st.success(f"Marked '{topic_name}' as weak")
                st.rerun()
        
        with col3:
            if st.button("Mastered", key=f"master_{topic_name}", use_container_width=True):
                mark_topic_mastered(subject, topic_name)
                st.success(f"Marked '{topic_name}' as mastered")
                st.rerun()