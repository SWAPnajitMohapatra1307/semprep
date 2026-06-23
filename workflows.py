import os
import shutil
from pathlib import Path
from file_processor import process_upload
from agent import run_full_analysis
from datastore import save_subject_data, load_subject_data, save_session, get_weak_topics

TEMP_DIR = "temp_extracted"


def cleanup_temp():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)


def get_pyq_texts(subject_bucket: dict) -> list:
    pyq_texts = []
    for file_data in subject_bucket.get("PYQ", []):
        text = file_data.get("raw_text", "")
        if text:
            pyq_texts.append(text)
    return pyq_texts


def get_notes_texts(subject_bucket: dict) -> list:
    notes_texts = []
    for file_data in subject_bucket.get("Notes", []):
        text = file_data.get("raw_text", "")
        if text:
            notes_texts.append(text)
    for file_data in subject_bucket.get("Reference", []):
        text = file_data.get("raw_text", "")
        if text:
            notes_texts.append(text)
    return notes_texts


def estimate_total_years(pyq_texts: list) -> int:
    import re
    years = set()
    for text in pyq_texts:
        found = re.findall(r'\b(20\d{2})\b', text)
        for y in found:
            years.add(y)
    if len(years) == 0:
        return 3
    return max(len(years), 1)

def run_subject_workflow(subject: str, subject_bucket: dict, days_remaining: int, force_rerun: bool = False) -> dict:
    if not force_rerun:
        existing = load_subject_data(subject)
        if existing:
            print(f"Loaded {subject} from cache")
            return {
                "status": "loaded_from_cache",
                "subject": subject,
                "data": existing
            }

    pyq_texts = get_pyq_texts(subject_bucket)

    all_texts = []
    for ftype in ["PYQ", "Notes", "Reference", "Unknown"]:
        for file_data in subject_bucket.get(ftype, []):
            text = file_data.get("raw_text", "")
            if text.strip():
                all_texts.append(text)

    if not all_texts:
        return {
            "status": "error",
            "subject": subject,
            "error": f"No readable files found for {subject}"
        }

    total_years = estimate_total_years(pyq_texts) if pyq_texts else 1
    weak_topics = get_weak_topics(subject)

    print(f"Running analysis for {subject}: {len(all_texts)} total files, {len(pyq_texts)} PYQs, {total_years} years")

    analysis_result = run_full_analysis(
        subject=subject,
        pyq_texts=pyq_texts,
        total_years=total_years,
        days_remaining=days_remaining,
        weak_topics=weak_topics,
        all_texts=all_texts
    )

    save_subject_data(subject, analysis_result)

    return {
        "status": "success",
        "subject": subject,
        "data": analysis_result
    }

def run_full_pipeline(zip_path: str, days_remaining: int, selected_subjects: list = None, force_rerun: bool = False) -> dict:
    cleanup_temp()

    print("Extracting ZIP and detecting subjects per file...")
    subject_buckets = process_upload(zip_path, TEMP_DIR)

    if not subject_buckets:
        return {
            "status": "error",
            "error": "No processable files found in the ZIP.",
            "results": {}
        }

    if selected_subjects:
        subject_buckets = {k: v for k, v in subject_buckets.items() if k in selected_subjects}

    subject_buckets.pop("Unknown", None)

    if not subject_buckets:
        return {
            "status": "error",
            "error": "Could not detect any known subjects. Check filenames or content.",
            "results": {}
        }

    print(f"Subjects detected: {list(subject_buckets.keys())}")

    results = {}
    errors = {}

    for subject, bucket in subject_buckets.items():
        print(f"Processing subject: {subject}")
        result = run_subject_workflow(
            subject=subject,
            subject_bucket=bucket,
            days_remaining=days_remaining,
            force_rerun=force_rerun
        )

        if result["status"] == "error":
            errors[subject] = result["error"]
        else:
            results[subject] = result["data"]

    session_data = {
        "zip_path": zip_path,
        "days_remaining": days_remaining,
        "subjects_processed": list(results.keys()),
        "subjects_failed": list(errors.keys()),
        "selected_subjects": selected_subjects
    }
    save_session(session_data)

    return {
        "status": "success" if results else "error",
        "results": results,
        "errors": errors,
        "subjects_found": list(subject_buckets.keys()),
        "subjects_processed": list(results.keys())
    }


def regenerate_cheatsheet_workflow(subject: str, days_remaining: int) -> str:
    from agent import generate_cheatsheet
    from datastore import get_weak_topics, load_subject_data, save_subject_data

    data = load_subject_data(subject)
    if not data:
        return "No data found for this subject. Please run the full analysis first."

    weak_topics = get_weak_topics(subject)
    weighted_topics = data.get("weighted_topics", {})

    new_cheatsheet = generate_cheatsheet(
        weighted_topics=weighted_topics,
        weak_topics=weak_topics,
        subject=subject
    )

    data["cheatsheet"] = new_cheatsheet
    save_subject_data(subject, data)
    return new_cheatsheet


def regenerate_study_plan_workflow(subject: str, days_remaining: int) -> str:
    from agent import generate_study_plan
    from datastore import load_subject_data, save_subject_data

    data = load_subject_data(subject)
    if not data:
        return "No data found for this subject. Please run the full analysis first."

    weighted_topics = data.get("weighted_topics", {})

    new_plan = generate_study_plan(
        weighted_topics=weighted_topics,
        days_remaining=days_remaining,
        subject=subject
    )

    data["study_plan"] = new_plan
    save_subject_data(subject, data)
    return new_plan


def get_subject_summary(subject: str) -> dict:
    from datastore import load_subject_data, load_progress

    data = load_subject_data(subject)
    progress = load_progress(subject)

    if not data:
        return {
            "subject": subject,
            "status": "not_analyzed",
            "total_topics": 0,
            "critical_topics": 0,
            "high_topics": 0,
            "weak_topics": progress.get("weak_topics", []),
            "mastered_topics": progress.get("mastered_topics", [])
        }

    weighted_topics = data.get("weighted_topics", {})
    topics_list = []

    if isinstance(weighted_topics, dict):
        topics_list = weighted_topics.get("weighted_topics") or weighted_topics.get("topics") or []
    elif isinstance(weighted_topics, list):
        topics_list = weighted_topics

    critical = [t for t in topics_list if t.get("weight", 0) >= 9]
    high = [t for t in topics_list if 7 <= t.get("weight", 0) < 9]

    return {
        "subject": subject,
        "status": "analyzed",
        "total_topics": len(topics_list),
        "critical_topics": len(critical),
        "high_topics": len(high),
        "weak_topics": progress.get("weak_topics", []),
        "mastered_topics": progress.get("mastered_topics", []),
        "last_updated": data.get("last_updated")
    }