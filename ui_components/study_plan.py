import streamlit as st

def render_study_plan(data, days_remaining):
    st.subheader("Day-by-Day Study Plan")
    
    st.info(f"You have {days_remaining} days until exam")
    
    weighted_topics = data.get("weighted_topics", {})
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
    
    critical = [t for t in topics_list if t.get("weight", 0) >= 9]
    high = [t for t in topics_list if 7 <= t.get("weight", 0) < 9]
    medium = [t for t in topics_list if 5 <= t.get("weight", 0) < 7]
    
    tabs = st.tabs([f"Day {i+1}" for i in range(min(days_remaining, 7))])
    
    for day_idx, tab in enumerate(tabs, 1):
        with tab:
            st.markdown(f"### Day {day_idx}")
            
            if day_idx == 1:
                topics_for_day = critical[:2]
                topic_type = "CRITICAL"
            elif day_idx == 2:
                topics_for_day = critical[2:] + high[:2]
                topic_type = "CRITICAL + HIGH"
            elif day_idx < days_remaining:
                topics_for_day = high[max(0, (day_idx-2)*2):] + medium[:max(0, 3-(day_idx-2))]
                topic_type = "HIGH + MEDIUM"
            else:
                st.success("REVISION DAY")
                st.write("Review all critical and high topics")
                continue
            
            if topics_for_day:
                for topic in topics_for_day:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{topic.get('topic_name', 'Topic')}**")
                            st.caption(f"Type: {topic_type} | Weight: {topic.get('weight', 0):.1f}")
                        with col2:
                            st.metric("Time", "2-3h")
            else:
                st.info("No new topics scheduled for this day")