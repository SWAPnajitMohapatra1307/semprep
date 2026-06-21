Task: Create a study priority list for a student with N days until exam.

Input:
- Weighted topics (with weights, bands, appearance counts)
- Days remaining until exam
- Student's weak topics (if any)

Rules:
1. Show ONLY topics with weight >= threshold (based on days)
2. Sort by weight descending
3. For each topic: show exact PYQ questions that test it
4. Estimate study time based on complexity
5. List topics to SKIP with one-line reason

Thresholds:
- 1-2 days: weight >= 8.5
- 3-5 days: weight >= 7.0
- 6-10 days: weight >= 5.5
- 10+ days: weight >= 4.0

Output format (markdown table):

| Priority | Topic | Weight | Band | Questions | Study Time | Notes |
|----------|-------|--------|------|-----------|------------|-------|
| 1 | OSI Model | 9.2 | CRITICAL | Q1(2023,10m), Q3(2022,13m), Q5(2021,10m) | 3 hrs | Asked every year. Must know all 7 layers. |

After table, add SKIP section:
SKIP THESE TOPICS (weight below threshold):
- Topic X: Only in 2020. Not in recent papers.
- Topic Y: Appeared once with 2 marks. Low value.

Be specific. Show exact question references.