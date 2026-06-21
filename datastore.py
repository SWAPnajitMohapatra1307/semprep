import os
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = "semprep_data"

def init_datastore():
    dirs = [
        DATA_DIR,
        os.path.join(DATA_DIR, "subjects"),
        os.path.join(DATA_DIR, "progress"),
        os.path.join(DATA_DIR, "sessions")
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def save_subject_data(subject: str, analysis_result: dict):
    init_datastore()
    subject_dir = os.path.join(DATA_DIR, "subjects", subject)
    Path(subject_dir).mkdir(parents=True, exist_ok=True)
    
    data_to_save = {
        "subject": subject,
        "last_updated": datetime.now().isoformat(),
        "topic_map": analysis_result.get("topic_map", {}),
        "weighted_topics": analysis_result.get("weighted_topics", {}),
        "priority_list": analysis_result.get("priority_list", ""),
        "question_bank": analysis_result.get("question_bank", ""),
        "flashcards": analysis_result.get("flashcards", ""),
        "study_plan": analysis_result.get("study_plan", ""),
        "cheatsheet": analysis_result.get("cheatsheet", "")
    }
    
    save_path = os.path.join(subject_dir, "analysis.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=2, ensure_ascii=False)

def load_subject_data(subject: str) -> dict:
    save_path = os.path.join(DATA_DIR, "subjects", subject, "analysis.json")
    if not os.path.exists(save_path):
        return None
    with open(save_path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_saved_subjects() -> list:
    subjects_dir = os.path.join(DATA_DIR, "subjects")
    if not os.path.exists(subjects_dir):
        return []
    return [d for d in os.listdir(subjects_dir) if os.path.isdir(os.path.join(subjects_dir, d))]

def save_progress(subject: str, progress_data: dict):
    init_datastore()
    progress_dir = os.path.join(DATA_DIR, "progress")
    progress_file = os.path.join(progress_dir, f"{subject}_progress.json")
    
    existing = load_progress(subject)
    existing.update(progress_data)
    existing["last_updated"] = datetime.now().isoformat()
    
    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

def load_progress(subject: str) -> dict:
    progress_file = os.path.join(DATA_DIR, "progress", f"{subject}_progress.json")
    if not os.path.exists(progress_file):
        return {
            "subject": subject,
            "weak_topics": [],
            "mastered_topics": [],
            "skipped_topics": [],
            "last_updated": None
        }
    with open(progress_file, "r", encoding="utf-8") as f:
        return json.load(f)

def mark_topic_weak(subject: str, topic_name: str):
    progress = load_progress(subject)
    
    if topic_name not in progress["weak_topics"]:
        progress["weak_topics"].append(topic_name)
    
    if topic_name in progress["mastered_topics"]:
        progress["mastered_topics"].remove(topic_name)
    
    save_progress(subject, progress)

def mark_topic_mastered(subject: str, topic_name: str):
    progress = load_progress(subject)
    
    if topic_name not in progress["mastered_topics"]:
        progress["mastered_topics"].append(topic_name)
    
    if topic_name in progress["weak_topics"]:
        progress["weak_topics"].remove(topic_name)
    
    save_progress(subject, progress)

def mark_topic_skipped(subject: str, topic_name: str):
    progress = load_progress(subject)
    
    if topic_name not in progress["skipped_topics"]:
        progress["skipped_topics"].append(topic_name)
    
    save_progress(subject, progress)

def get_weak_topics(subject: str) -> list:
    progress = load_progress(subject)
    return progress.get("weak_topics", [])

def save_session(session_data: dict):
    init_datastore()
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_file = os.path.join(DATA_DIR, "sessions", f"session_{session_id}.json")
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
    return session_id

def delete_subject_data(subject: str):
    import shutil
    subject_dir = os.path.join(DATA_DIR, "subjects", subject)
    if os.path.exists(subject_dir):
        shutil.rmtree(subject_dir)
    
    progress_file = os.path.join(DATA_DIR, "progress", f"{subject}_progress.json")
    if os.path.exists(progress_file):
        os.remove(progress_file)

def get_all_progress_summary() -> dict:
    subjects = list_saved_subjects()
    summary = {}
    for subject in subjects:
        progress = load_progress(subject)
        data = load_subject_data(subject)
        total_topics = 0
        if data and "weighted_topics" in data:
            wt = data["weighted_topics"]
            if isinstance(wt, dict) and "weighted_topics" in wt:
                total_topics = len(wt["weighted_topics"])
        summary[subject] = {
            "total_topics": total_topics,
            "weak_count": len(progress.get("weak_topics", [])),
            "mastered_count": len(progress.get("mastered_topics", [])),
            "skipped_count": len(progress.get("skipped_topics", [])),
            "last_updated": data.get("last_updated") if data else None
        }
    return summary

