Task: Calculate priority weight for each topic based on PYQ analysis.

Input: Topic list with appearance frequencies and marks.

Formula:
- frequency_weight = (appearances / total_years) * 10
- marks_weight = (total_marks_for_topic / max_marks_in_exam) * 10
- base_weight = (frequency_weight * 0.7) + (marks_weight * 0.3)

Boosters:
+ 1.0 if appeared in most recent year
+ 0.5 if appears in multiple units

Final: min(10.0, max(0.0, base_weight + boosters))

Output JSON:
{
    "topics": [
        {
            "name": "OSI Model",
            "weight": 9.2,
            "band": "CRITICAL",
            "reason": "Appeared in 4 of last 5 years, 45/100 marks total",
            "appearances": 4,
            "total_marks": 45
        }
    ]
}

Bands:
- CRITICAL (9-10): Asked 4-5 times in last 5 years
- HIGH (7-8): Asked 3 times in last 5 years
- MEDIUM (5-6): Asked 2 times in last 5 years
- LOW (1-4): Asked once or never

Be strict. Only mark topics as CRITICAL if data proves it.