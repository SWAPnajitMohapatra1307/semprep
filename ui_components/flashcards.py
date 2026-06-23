import streamlit as st
from .parser import parse_flashcard_text

def render_flashcards(data, subject):
    
    st.markdown("""
<style>

/* Prev, Next, Flip buttons */
.stButton > button {
    color: #FFC000 !important;
    border: 1px solid #FFC000 !important;
    background-color: transparent !important;
    font-weight: 600 !important;
    letter-spacing: 1px;
    transition: all 0.3s ease;
}

/* Hover effect */
.stButton > button:hover {
    background-color: rgba(255, 192, 0, 0.1) !important;
    color: #FFD54F !important;
    border-color: #FFD54F !important;
}

/* Click effect */
.stButton > button:active {
    background-color: rgba(255, 192, 0, 0.2) !important;
}

</style>
""", unsafe_allow_html=True)
    st.subheader("Interactive Flashcards")

    weighted_topics = data.get("weighted_topics", {})
    flashcard_text = data.get("flashcards", "")

    topics_list = []
    if isinstance(weighted_topics, dict):
        if "weighted_topics" in weighted_topics:
            topics_list = weighted_topics["weighted_topics"]
        elif "topics" in weighted_topics:
            topics_list = weighted_topics["topics"]
    elif isinstance(weighted_topics, list):
        topics_list = weighted_topics

    parsed_cards = parse_flashcard_text(flashcard_text)

    if parsed_cards:
        cards = parsed_cards
    else:
        cards = []
        for topic in topics_list:
            if topic.get("weight", 0) >= 7:
                questions = topic.get("questions", [])
                for q in questions:
                    cards.append({
                        "topic": topic.get("topic_name", "Unknown"),
                        "front": str(q),
                        "back": f"Topic: {topic.get('topic_name')}\nWeight: {topic.get('weight', 0):.1f}\nYears: {', '.join(map(str, topic.get('years_appeared', [])))}\nMarks: {topic.get('typical_marks', 'N/A')}",
                        "weight": topic.get("weight", 0)
                    })

    if not cards:
        st.info("No flashcards available. Questions need to be extracted from PYQs first.")
        if flashcard_text:
            st.markdown(flashcard_text)
        return

    if f"card_idx_{subject}" not in st.session_state:
        st.session_state[f"card_idx_{subject}"] = 0
    if f"flipped_{subject}" not in st.session_state:
        st.session_state[f"flipped_{subject}"] = False

    current_idx = st.session_state[f"card_idx_{subject}"]
    current_idx = min(current_idx, len(cards) - 1)
    card = cards[current_idx]

    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if st.button("← Prev", use_container_width=True):
            st.session_state[f"card_idx_{subject}"] = max(0, current_idx - 1)
            st.session_state[f"flipped_{subject}"] = False
            st.rerun()

    with col2:
        topic_label = card.get("topic", card.get("front", "")[:30])
        weight_label = f"Weight: {card.get('weight', 0):.1f}" if card.get("weight") else ""
        st.markdown(f"**Card {current_idx + 1} / {len(cards)}** — {topic_label} {weight_label}")

    with col3:
        if st.button("Next →", use_container_width=True):
            st.session_state[f"card_idx_{subject}"] = min(len(cards) - 1, current_idx + 1)
            st.session_state[f"flipped_{subject}"] = False
            st.rerun()

    is_flipped = st.session_state[f"flipped_{subject}"]

    if not is_flipped:
        st.markdown(f"""
                    
        
        <div style='
    background: linear-gradient(
    135deg,
    rgba(18, 14, 2, 1) 0%,
    rgba(45, 38, 12, 1) 50%,
    rgba(18, 14, 2, 1) 100%
);
            padding: 50px 40px;
            border-radius: 15px;
            text-align: center;
            margin: 20px 0;
            min-height: 220px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            justify-content: center;
        '>
            <p style='color: #e0e0e0; font-size: 13px; margin: 0 0 15px 0; letter-spacing: 2px;'>QUESTION</p>
            <p style='color: white; font-size: 18px; margin: 0; font-weight: 500; line-height: 1.6;'>{card.get("front", "No question")}</p>
            <p style='color: #c0c0c0; font-size: 12px; margin: 20px 0 0 0;'>Click Flip to reveal answer</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        back_text = card.get("back", "No answer available").replace("\n", "<br>")
        st.markdown(f"""
        <div style='
                background: linear-gradient(
                135deg,
                rgba(5, 60, 20, 0.95) 0%,
                rgba(15, 40, 25, 1) 50%,
                rgba(5, 60, 20, 0.95) 100%
            );
            padding: 50px 40px;
            border-radius: 15px;
            text-align: center;
            margin: 20px 0;
            min-height: 220px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        '>
            <p style='color: #e0e0e0; font-size: 13px; margin: 0 0 15px 0; letter-spacing: 2px;'>ANSWER</p>
            <p style='color: white; font-size: 16px; margin: 0; line-height: 1.8;'>{back_text}</p>
        </div>
        """, unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("Flip Card", use_container_width=True, key="flip_btn"):
            st.session_state[f"flipped_{subject}"] = not is_flipped
            st.rerun()
    with col_b:
        st.progress((current_idx + 1) / len(cards))