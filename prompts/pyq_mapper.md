Task: Extract questions from exam papers and map them to topics.

Input: Raw text from previous year question papers.

Output: JSON with exact structure:

{
    "questions": [
        {
            "id": "Q1",
            "text": "exact question text as written",
            "year": 2023,
            "marks": 10,
            "topics": ["OSI Model", "Network Layers"],
            "unit": "Unit 1"
        }
    ],
    "topics": [
        {
            "name": "OSI Model",
            "appearances": 4,
            "total_marks": 45,
            "years": [2020, 2021, 2022, 2023],
            "frequency_percent": 80
        }
    ]
}

Rules:
- Extract EXACT question text. Do not paraphrase.
- If marks not mentioned, leave null.
- Map each question to 1-3 topics maximum.
- Count frequency across years.
- Be precise. If you cannot extract data clearly, omit it.