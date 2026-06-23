import os
import json
import requests
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, DEFAULT_MODEL


def load_prompt(prompt_filename: str) -> str:
    prompt_path = os.path.join("prompts", prompt_filename)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def call_openrouter(system_instruction: str, user_message: str, model: str = None) -> str:
    if model is None:
        model = DEFAULT_MODEL

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.1,
        "max_tokens": 4000
    }

    response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

    result = response.json()
    return result["choices"][0]["message"]["content"]


def extract_json_from_response(text: str) -> dict:
    text = text.strip()

    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end != -1:
            text = text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end != -1:
            text = text[start:end].strip()

    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end != 0:
            return json.loads(text[start:end])
    except json.JSONDecodeError:
        pass

    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start != -1 and end != 0:
            parsed = json.loads(text[start:end])
            return {"weighted_topics": parsed}
    except json.JSONDecodeError:
        pass

    return {"raw_response": text}


def analyze_content(all_texts: list, pyq_texts: list, subject: str) -> dict:
    system_prompt = """You are a JSON generator. You only output valid JSON.
No explanations. No code. No markdown outside of a JSON block.
Only return a single JSON object."""

    combined_all = ""
    for i, text in enumerate(all_texts):
        combined_all += f"\n\n=== FILE {i+1} ===\n{text[:2000]}"

    combined_pyq = ""
    for i, text in enumerate(pyq_texts):
        combined_pyq += f"\n\n=== PYQ {i+1} ===\n{text[:2000]}"

    user_message = f"""
Analyze these {subject} study materials and extract topics.

ALL STUDY MATERIALS (notes + PYQs + references):
{combined_all}

PREVIOUS YEAR QUESTION PAPERS (PYQs) — use these to tag questions with years:
{combined_pyq if combined_pyq else "No PYQ files available for this subject."}

Instructions:
1. Extract all important topics from ALL study materials above.
2. For each topic, list important questions or concepts.
3. If a question also appeared in a PYQ, tag it with the year it appeared.
4. If no PYQs are available, still extract topics from notes/references.
5. Do not skip a subject just because it has no PYQs.

Return ONLY this JSON structure:

{{
    "subject": "{subject}",
    "has_pyqs": {"true" if pyq_texts else "false"},
    "topics": [
        {{
            "topic_name": "OSI Model",
            "questions": [
                {{
                    "text": "Explain the 7 layers of OSI model with functions",
                    "pyq_years": ["2022", "2023"],
                    "marks": 10
                }},
                {{
                    "text": "Difference between OSI and TCP/IP model",
                    "pyq_years": [],
                    "marks": 5
                }}
            ],
            "years_appeared": ["2022", "2023"],
            "typical_marks": 10,
            "unit": "Unit 1"
        }}
    ]
}}

Rules:
- pyq_years: list of years this question appeared in PYQs (empty list if not in any PYQ)
- years_appeared: all years this topic appeared across all PYQs
- Extract at least 3-5 topics minimum
- Only output JSON, no Python code, no explanation
"""

    response = call_openrouter(system_prompt, user_message)
    result = extract_json_from_response(response)
    return result


def calculate_weights(topic_data: dict, total_years: int, has_pyqs: bool) -> dict:
    system_prompt = """You are a JSON generator. You only output valid JSON.
No explanations. No code. No markdown outside of a JSON block.
Only return a single JSON object."""

    topics = topic_data.get("topics", [])
    if not topics:
        topics = topic_data.get("weighted_topics", [])

    user_message = f"""
Calculate priority weights for these exam topics.

Total years of PYQs available: {total_years}
Has PYQ data: {has_pyqs}

Topics: {json.dumps(topics, indent=2)}

Formula:
- If has_pyqs is true:
  frequency_score = (len(years_appeared) / total_years) * 10
- If has_pyqs is false:
  frequency_score = 5.0 (neutral, since we have no PYQ data)
- marks_score = (typical_marks / 20) * 10
- base_weight = (frequency_score * 0.7) + (marks_score * 0.3)
- Add 1.0 if most recent year in years_appeared
- Final = min(10.0, max(1.0, base_weight))

Return ONLY this JSON:

{{
    "weighted_topics": [
        {{
            "topic_name": "OSI Model",
            "weight": 9.2,
            "band": "CRITICAL",
            "years_appeared": ["2022", "2023"],
            "typical_marks": 10,
            "unit": "Unit 1",
            "has_pyq": true,
            "questions": [
                {{
                    "text": "Explain 7 layers of OSI model",
                    "pyq_years": ["2022", "2023"],
                    "marks": 10
                }}
            ]
        }}
    ]
}}

Bands:
- CRITICAL: weight >= 9
- HIGH: weight 7-8.9
- MEDIUM: weight 5-6.9
- LOW: weight < 5

Only output JSON. No code. No explanation.
"""

    response = call_openrouter(system_prompt, user_message)
    result = extract_json_from_response(response)
    return result


def generate_priority_list(weighted_topics: dict, days_remaining: int) -> str:
    system_prompt = load_prompt("system_prompt.md")
    priority_list_prompt = load_prompt("prioritylist.md")

    user_message = f"""
{priority_list_prompt}

Days remaining: {days_remaining}

Weighted Topics:
{json.dumps(weighted_topics, indent=2)}

Generate priority study list in markdown table format.
For topics with pyq_years, show those years in the table.
"""

    response = call_openrouter(system_prompt, user_message)
    return response


def generate_question_bank(weighted_topics: dict, subject: str) -> str:
    system_prompt = load_prompt("system_prompt.md")
    question_bank_prompt = load_prompt("questionbank.md")

    user_message = f"""
{question_bank_prompt}

Subject: {subject}

Weighted Topics (with PYQ year tags):
{json.dumps(weighted_topics, indent=2)}

For each question that has pyq_years, add a badge like:
[Asked in 2022] [Asked in 2023]

Generate the full question bank with 2/5 mark questions and keyword answers.
Do NOT include any 10 mark questions.
Only generate 2 mark and 5 mark questions.
"""

    response = call_openrouter(system_prompt, user_message)
    return response


def generate_flashcards(weighted_topics: dict, subject: str) -> str:
    system_prompt = load_prompt("system_prompt.md")
    flashcard_prompt = load_prompt("flashcard_gen.md")

    topics = weighted_topics.get("weighted_topics", [])
    high_priority = [t for t in topics if t.get("weight", 0) >= 7]

    user_message = f"""
{flashcard_prompt}

Subject: {subject}

High Priority Topics:
{json.dumps(high_priority, indent=2)}

Generate flashcards for each topic.
If topic has pyq_years, include "PYQ: {{}}" in the answer.

Format exactly like this:

---
TOPIC: OSI Model
FRONT: What are the 7 layers of the OSI model?
BACK: Physical, Data Link, Network, Transport, Session, Presentation, Application
MEMORY HOOK: Please Do Not Throw Sausage Pizza Away
DIFFICULTY: Medium
PYQ: 2022, 2023
---
"""

    response = call_openrouter(system_prompt, user_message)
    return response


def generate_study_plan(weighted_topics: dict, days_remaining: int, subject: str) -> str:
    system_prompt = load_prompt("system_prompt.md")

    user_message = f"""
Subject: {subject}
Days until exam: {days_remaining}

Weighted Topics:
{json.dumps(weighted_topics, indent=2)}

Create a day by day study plan in markdown format.

Rules:
- Day 1: CRITICAL topics only (weight >= 9)
- Day 2-3: HIGH topics (weight 7-8)
- Day 4+: MEDIUM topics (weight 5-6)
- Last day: Revision only
- For topics with pyq_years, note them as "Previously asked in exam"

Format:
## Day 1
- Topic Name (Weight: X) - 2 hours
  - Focus: specific concept
  - PYQ History: 2022, 2023

## Day 2
...
"""

    response = call_openrouter(system_prompt, user_message)
    return response


def generate_cheatsheet(weighted_topics: dict, weak_topics: list, subject: str) -> str:
    system_prompt = load_prompt("system_prompt.md")
    cheatsheet_prompt = load_prompt("cheatsheet_gen.md")

    weak_str = ", ".join(weak_topics) if weak_topics else "None"

    user_message = f"""
{cheatsheet_prompt}

Subject: {subject}
Student weak topics: {weak_str}

Weighted Topics:
{json.dumps(weighted_topics, indent=2)}

Generate last minute cheat sheet.
For topics with pyq_years, mark them with "* PYQ TOPIC *"

Format:
## CRITICAL TOPICS
### Topic Name (Weight: X) * PYQ TOPIC *
- Key definition
- Formula or acronym
- Memory hook

## WEAK TOPICS (Extra Focus)
### Weak Topic Name
- Key definition
- Common exam tricks
"""

    response = call_openrouter(system_prompt, user_message)
    return response


def run_full_analysis(subject: str, pyq_texts: list, total_years: int, days_remaining: int, weak_topics: list = None, all_texts: list = None) -> dict:
    if weak_topics is None:
        weak_topics = []

    if all_texts is None:
        all_texts = pyq_texts

    has_pyqs = len(pyq_texts) > 0

    print(f"Step 1: Analyzing content for {subject} (has_pyqs={has_pyqs})")
    topic_map = analyze_content(all_texts, pyq_texts, subject)

    print(f"Step 2: Calculating weights for {subject}")
    weighted_topics = calculate_weights(topic_map, total_years, has_pyqs)

    print(f"Step 3: Generating priority list")
    priority_list = generate_priority_list(weighted_topics, days_remaining)

    print(f"Step 4: Generating question bank")
    question_bank = generate_question_bank(weighted_topics, subject)

    print(f"Step 5: Generating flashcards")
    flashcards = generate_flashcards(weighted_topics, subject)

    print(f"Step 6: Generating study plan")
    study_plan = generate_study_plan(weighted_topics, days_remaining, subject)

    print(f"Step 7: Generating cheat sheet")
    cheatsheet = generate_cheatsheet(weighted_topics, weak_topics, subject)

    return {
        "subject": subject,
        "topic_map": topic_map,
        "weighted_topics": weighted_topics,
        "priority_list": priority_list,
        "question_bank": question_bank,
        "flashcards": flashcards,
        "study_plan": study_plan,
        "cheatsheet": cheatsheet,
        "has_pyqs": has_pyqs
    }