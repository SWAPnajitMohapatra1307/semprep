import streamlit as st
from .parser import parse_questions_from_text

def render_question_bank(data):
    st.subheader("PYQ Question Bank")
    
    weighted_topics = data.get("weighted_topics", {})
    qb_text = data.get("question_bank", "")
    
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
    
    topics_with_questions = [t for t in topics_list if t.get("questions")]
    
    if not topics_with_questions:
        st.info("No questions found in analysis")
        return
    
    selected_topic = st.selectbox(
        "Select Topic",
        [t.get("topic_name", t.get("name", "Unknown")) for t in topics_with_questions]
    )
    
    topic = next(t for t in topics_with_questions if t.get("topic_name", t.get("name")) == selected_topic)
    
    st.markdown(f"### {selected_topic}")
    st.caption(f"Weight: {topic.get('weight', 0):.1f} | Years: {', '.join(map(str, topic.get('years_appeared', [])))}")
    
    questions = topic.get("questions", [])
    
    if isinstance(questions, list) and questions:
        for idx, question in enumerate(questions, 1):
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**Q{idx}:** {str(question)[:100]}...")
                with col2:
                    marks = topic.get("typical_marks", "N/A")
                    st.metric("Marks", marks)
                
                if st.checkbox(f"Show answer for Q{idx}", key=f"q_{idx}"):
                    st.markdown("""
                    <div style='background-color: #f0f0f0; padding: 15px; border-left: 4px solid #667eea; border-radius: 5px;'>
                    <b>Answer Outline:</b>
                    <ul>
                    <li>Review lecture notes for this topic</li>
                    <li>Check similar PYQ answers</li>
                    <li>Practice with variations</li>
                    </ul>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No questions available for this topic")
    
    if qb_text:
        st.divider()
        st.markdown("### Full Question Bank from Analysis")
        st.markdown(qb_text)