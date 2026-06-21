import streamlit as st
import pandas as pd
from .parser import extract_table_from_markdown

def render_priority_list(data, days_remaining):
    st.subheader("Study Priority List")
    
    weighted_topics = data.get("weighted_topics", {})
    priority_text = data.get("priority_list", "")
    
    topics_list = []
    if isinstance(weighted_topics, dict):
        if "weighted_topics" in weighted_topics:
            topics_list = weighted_topics["weighted_topics"]
        elif "topics" in weighted_topics:
            topics_list = weighted_topics["topics"]
    elif isinstance(weighted_topics, list):
        topics_list = weighted_topics
    
    if not topics_list:
        st.warning("No topics data available")
        return
    
    threshold = 8 if days_remaining <= 2 else 6 if days_remaining <= 5 else 5
    priority_topics = [t for t in topics_list if t.get("weight", 0) >= threshold]
    priority_topics.sort(key=lambda x: x.get("weight", 0), reverse=True)
    
    if not priority_topics:
        st.info("No topics meet the priority threshold")
        return
    
    table_data = []
    for idx, topic in enumerate(priority_topics, 1):
        weight = topic.get("weight", 0)
        band = "CRITICAL" if weight >= 9 else "HIGH" if weight >= 7 else "MEDIUM"
        
        if weight >= 9:
            color = "🔴"
        elif weight >= 7:
            color = "🟡"
        else:
            color = "🟢"
        
        study_time = "4-6" if weight >= 9 else "2-4" if weight >= 7 else "1-2"
        
        table_data.append({
            "Rank": idx,
            "Priority": color,
            "Topic": topic.get("topic_name", topic.get("name", "Unknown")),
            "Weight": f"{weight:.1f}",
            "Band": band,
            "Study Time (hrs)": study_time,
            "Questions": len(topic.get("questions", []))
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader("Skip These Topics")
    
    skip_topics = [t for t in topics_list if t.get("weight", 0) < threshold]
    
    if skip_topics:
        cols = st.columns(2)
        for idx, topic in enumerate(skip_topics):
            with cols[idx % 2]:
                with st.container(border=True):
                    st.write(f"**{topic.get('topic_name', 'Unknown')}**")
                    st.caption(f"Weight: {topic.get('weight', 0):.1f}")
                    st.caption(f"Appeared: {len(topic.get('years_appeared', []))} times")
    else:
        st.success("No topics to skip!")
    
    if priority_text:
        st.divider()
        st.markdown("### Detailed Analysis from LLM")
        st.markdown(priority_text)