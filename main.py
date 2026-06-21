import os
import streamlit as st
from workflows import run_full_pipeline, regenerate_cheatsheet_workflow, regenerate_study_plan_workflow
from datastore import list_saved_subjects, load_subject_data, load_progress
from ui_components import priority_list, question_bank, flashcards, study_plan, cheatsheet, progress

st.set_page_config(page_title="SEMPREP", layout="wide")

st.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;'>
    <h1 style='color: white; margin: 0;'>SEMPREP</h1>
    <p style='color: #e0e0e0; margin: 5px 0 0 0;'>Your Last Minute Saviour</p>
</div>
""", unsafe_allow_html=True)

if "current_results" not in st.session_state:
    st.session_state.current_results = {}
if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = None

with st.sidebar:
    st.header("Upload & Settings")
    uploaded_zip = st.file_uploader("Upload ZIP", type=["zip"])
    days_remaining = st.number_input("Days until exam", min_value=1, max_value=30, value=5)
    force_rerun = st.checkbox("Force re-analysis")

    if uploaded_zip:
        temp_zip_path = "temp_uploaded.zip"
        with open(temp_zip_path, "wb") as f:
            f.write(uploaded_zip.read())

        if st.button("Run Analysis", use_container_width=True):
            with st.spinner("Analyzing..."):
                result = run_full_pipeline(temp_zip_path, days_remaining, force_rerun=force_rerun)
                if result["status"] == "success":
                    st.session_state.current_results = result["results"]
                    st.success("Done!")
                else:
                    st.error("Error")

    st.divider()
    st.header("Saved Subjects")
    saved = list_saved_subjects()
    for subj in saved:
        if st.button(f"📚 {subj}", use_container_width=True):
            st.session_state.selected_subject = subj

if st.session_state.current_results:
    subjects = list(st.session_state.current_results.keys())
    if subjects:
        st.session_state.selected_subject = subjects[0]

if st.session_state.selected_subject:
    subject = st.session_state.selected_subject
    data = load_subject_data(subject)

    if not data:
        st.error("No data")
    else:
        weighted_topics = data.get("weighted_topics", {})
        topics_list = []
        
        if isinstance(weighted_topics, dict):
            topics_list = weighted_topics.get("weighted_topics") or weighted_topics.get("topics") or []
        elif isinstance(weighted_topics, list):
            topics_list = weighted_topics
        
        st.markdown(f"## {subject}")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", len(topics_list))
        col2.metric("CRITICAL", sum(1 for t in topics_list if t.get("weight", 0) >= 9))
        col3.metric("HIGH", sum(1 for t in topics_list if 7 <= t.get("weight", 0) < 9))
        col4.metric("WEAK", len(load_progress(subject).get("weak_topics", [])))
        
        st.divider()
        
        tabs = st.tabs(["Priority", "Questions", "Flashcards", "Plan", "Cheat", "Progress"])
        
        with tabs[0]:
            priority_list.render_priority_list(data, days_remaining)
        
        with tabs[1]:
            question_bank.render_question_bank(data)
        
        with tabs[2]:
            flashcards.render_flashcards(data, subject)
        
        with tabs[3]:
            study_plan.render_study_plan(data, days_remaining)
        
        with tabs[4]:
            cheatsheet.render_cheatsheet(data, load_progress(subject).get("weak_topics", []))
        
        with tabs[5]:
            progress.render_progress(subject, topics_list, load_progress(subject))

else:
    st.info("Select a subject from sidebar")