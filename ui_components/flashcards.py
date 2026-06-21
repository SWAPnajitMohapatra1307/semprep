import streamlit as st
from .parser import parse_flashcard_text

def render_flashcards(data, subject):
    st.subheader("Interactive Flashcards")
    
    weighted_topics = data.get("weighted_topics", {})
    topics_list = []
    
    if isinstance(weighted_topics, dict):
        if "weighted_topics" in weighted_topics:
            topics_list = weighted_topics["weighted_topics"]
        elif "topics" in weighted_topics:
            topics_list = weighted_topics["topics"]
    elif isinstance(weighted_topics, list):
        topics_list = weighted_topics
    
    high_weight_topics = [t for t in topics_list if t.get("weight", 0) >= 7.5]
    
    if not high_weight_topics:
        st.info("No high-priority topics (weight >= 7.5) for flashcards")
        return
    
    if f"card_idx_{subject}" not in st.session_state:
        st.session_state[f"card_idx_{subject}"] = 0
    if f"flipped_{subject}" not in st.session_state:
        st.session_state[f"flipped_{subject}"] = False
    
    current_idx = st.session_state[f"card_idx_{subject}"]
    topic = high_weight_topics[current_idx]
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("← Prev", use_container_width=True):
            st.session_state[f"card_idx_{subject}"] = max(0, current_idx - 1)
            st.session_state[f"flipped_{subject}"] = False
            st.rerun()
    
    with col2:
        st.metric(f"Card {current_idx + 1}/{len(high_weight_topics)}", f"Weight: {topic.get('weight', 0):.1f}")
    
    with col3:
        if st.button("Next →", use_container_width=True):
            st.session_state[f"card_idx_{subject}"] = min(len(high_weight_topics) - 1, current_idx + 1)
            st.session_state[f"flipped_{subject}"] = False
            st.rerun()
    
    is_flipped = st.session_state[f"flipped_{subject}"]
    
    if not is_flipped:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 60px 30px; border-radius: 15px; text-align: center; 
                    margin: 30px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h3 style='color: white; margin: 0 0 20px 0;'>QUESTION</h3>
            <p style='color: white; font-size: 20px; margin: 0;'>{topic.get('topic_name', 'Topic')}</p>
            <p style='color: #e0e0e0; font-size: 14px; margin: 15px 0 0 0;'>Click button to reveal answer</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); 
                    padding: 60px 30px; border-radius: 15px; text-align: center; 
                    margin: 30px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h3 style='color: white; margin: 0 0 20px 0;'>ANSWER</h3>
            <p style='color: white; font-size: 18px; margin: 0; line-height: 1.6;'>
            {topic.get('topic_name', 'Topic')} appears {len(topic.get('years_appeared', []))} times in PYQs
            <br><br>Weight Score: {topic.get('weight', 0):.1f}/10
            <br>Typical Marks: {topic.get('typical_marks', 'N/A')}
            <br><br>Key Point: This is a frequently asked topic
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("Flip Card", use_container_width=True, key="flip_btn"):
        st.session_state[f"flipped_{subject}"] = not is_flipped
        st.rerun()