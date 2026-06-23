You are generating an EXAM QUESTION BANK with MODEL ANSWERS for CSE semester exams.

Base EVERYTHING strictly on the weighted_topics JSON provided. Do not invent topics.

Rules:
1. For CRITICAL topics (weight >= 9):
   - 2 short questions (2 marks) with 1-2 line direct answers
   - 2 medium questions (5 marks) with bullet-point keyword answers

2. For HIGH topics (weight 7-8):
   - 2 short questions (2 marks) with direct answers
   - 1 medium question (5 marks) with bullet-point keywords

3. For MEDIUM topics (weight 5-6):
   - 1 short question (2 marks)
   - 1 medium question (5 marks)

4. For LOW topics (weight < 5): SKIP entirely

5. DO NOT generate any 10 mark questions under any circumstance.
   Maximum marks per question is 5.

6. Base questions as closely as possible on actual PYQ questions in the topic data.
   Prefer re-using actual PYQ wordings with light cleaning over inventing new ones.
   Do NOT introduce concepts not present in the given topic data.

7. Answers must use keywords and bullet points only. No full paragraphs.

Format EXACTLY like this:

### Topic Name (Weight: X.X | Band: CRITICAL)

**Q1 (2 marks):** Question text here
**Answer:**
- keyword 1
- keyword 2

**Q2 (2 marks):** Question text here
**Answer:**
- keyword 1
- keyword 2

**Q3 (5 marks):** Question text here
**Answer:**
- Point 1: explanation
- Point 2: explanation
- Point 3: explanation
- Point 4: explanation

**Q4 (5 marks):** Question text here
**Answer:**
- Point 1
- Point 2
- Point 3

---
IMPORTANT:
- Do NOT generate any HTML.
- Do NOT use <div>, <span>, or inline styles.
- Do NOT wrap output in triple backticks.
- Return only clean markdown with headings and bullet points.


Repeat for each topic. Sort topics by weight descending.