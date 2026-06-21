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
        "temperature": 0.2,
        "max_tokens": 4000
    }
    
    response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
    
    result = response.json()
    return result["choices"][0]["message"]["content"]

def extract_json_from_response(text: str) -> dict:
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
            return json.loads(text[start:end])
    except json.JSONDecodeError:
        pass
    
    return {"raw_response": text}

def analyze_pyqs(pyq_texts: list, subject: str) -> dict:
    system_prompt = load_prompt("system_prompt.md")
    pyq_mapper = load_prompt("pyq_mapper.md")
    
    combined_text = ""
    for i, text in enumerate(pyq_texts):
        combined_text += f"\n\n=== PAPER {i+1} ===\n{text[:5000]}"
    
    user_message = f"""
{pyq_mapper}

Subject: {subject}

Previous Year Question Papers (raw text):
{combined_text}

Extract questions and topics. Return valid JSON.
"""
    
    response = call_openrouter(system_prompt, user_message)
    result = extract_json_from_response(response)
    return result

def calculate_weights(topic_data: dict, total_years: int) -> dict:
    system_prompt = load_prompt("system_prompt.md")
    weight_calc = load_prompt("weight_calculator.md")
    
    user_message = f"""
{weight_calc}

Total years of PYQs: {total_years}

Topic Data:
{json.dumps(topic_data, indent=2)}

Calculate weights for each topic. Return valid JSON with weighted_topics array.
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

Generate priority study list. Use markdown table format. Be specific with question references.
"""
    
    response = call_openrouter(system_prompt, user_message)
    return response

def generate_question_bank(weighted_topics: dict, subject: str) -> str:
    system_prompt = load_prompt("system_prompt.md")
    question_bank_prompt = load_prompt("questionbank.md")
    
    user_message = f"""
{question_bank_prompt}

Subject: {subject}

Weighted Topics:
{json.dumps(weighted_topics, indent=2)}

Generate question bank. Include ONLY actual PYQ questions. Provide answer outlines in bullet points.
"""
    
    response = call_openrouter(system_prompt, user_message)
    return response

def generate_flashcards(weighted_topics: dict, subject: str) -> str:
    system_prompt = load_prompt("system_prompt.md")
    flashcard_prompt = load_prompt("flashcard_gen.md")
    
    user_message = f"""
{flashcard_prompt}

Subject: {subject}

Weighted Topics:
{json.dumps(weighted_topics, indent=2)}

Generate flashcards ONLY for topics with weight >= 7.5. Use the specified format.
"""
    
    response = call_openrouter(system_prompt, user_message)
    return response

def generate_study_plan(weighted_topics: dict, days_remaining: int, subject: str) -> str:
    system_prompt = load_prompt("system_prompt.md")
    study_plan_prompt = load_prompt("studyplan.md")
    
    user_message = f"""
{study_plan_prompt}

Subject: {subject}
Days remaining: {days_remaining}

Weighted Topics:
{json.dumps(weighted_topics, indent=2)}

Create day-by-day study plan. Allocate topics by weight. Show exact PYQ references.
"""
    
    response = call_openrouter(system_prompt, user_message)
    return response

def generate_cheatsheet(weighted_topics: dict, weak_topics: list, subject: str) -> str:
    system_prompt = load_prompt("system_prompt.md")
    cheatsheet_prompt = load_prompt("cheatsheet_gen.md")
    
    weak_topics_str = ", ".join(weak_topics) if weak_topics else "None"
    
    user_message = f"""
{cheatsheet_prompt}

Subject: {subject}
Student's weak topics: {weak_topics_str}

Weighted Topics:
{json.dumps(weighted_topics, indent=2)}

Generate cheat sheet. Max 2 pages. Include weak topics with extra space. Ultra-compact format.
"""
    
    response = call_openrouter(system_prompt, user_message)
    return response

def run_full_analysis(subject: str, pyq_texts: list, total_years: int, days_remaining: int, weak_topics: list = None) -> dict:
    if weak_topics is None:
        weak_topics = []
    
    print(f"Analyzing {subject}... Step 1: Extracting PYQs")
    topic_map = analyze_pyqs(pyq_texts, subject)
    
    print(f"Analyzing {subject}... Step 2: Calculating weights")
    weighted_topics = calculate_weights(topic_map, total_years)
    
    print(f"Analyzing {subject}... Step 3: Priority list")
    priority_list = generate_priority_list(weighted_topics, days_remaining)
    
    print(f"Analyzing {subject}... Step 4: Question bank")
    question_bank = generate_question_bank(weighted_topics, subject)
    
    print(f"Analyzing {subject}... Step 5: Flashcards")
    flashcards = generate_flashcards(weighted_topics, subject)
    
    print(f"Analyzing {subject}... Step 6: Study plan")
    study_plan = generate_study_plan(weighted_topics, days_remaining, subject)
    
    print(f"Analyzing {subject}... Step 7: Cheat sheet")
    cheatsheet = generate_cheatsheet(weighted_topics, weak_topics, subject)
    
    return {
        "subject": subject,
        "topic_map": topic_map,
        "weighted_topics": weighted_topics,
        "priority_list": priority_list,
        "question_bank": question_bank,
        "flashcards": flashcards,
        "study_plan": study_plan,
        "cheatsheet": cheatsheet
    }