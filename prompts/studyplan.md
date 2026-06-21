Task: Create a day-by-day study plan for exam prep.

Input:
- Weighted topics
- Days remaining
- Days should be allocated proportional to topic weight

Rules:
1. Day 1-2: CRITICAL topics only (weight >= 9)
2. Day 3+: HIGH topics (weight 7-8)
3. Day 5+: MEDIUM topics (weight 5-6)
4. Last day: Revision only
5. Max 6 hours study per day
6. Each topic gets time = (weight / total_weight) * available_hours

Example output (for 7 days):

Day 1 (4 hours):
- OSI Model (Weight: 9.2) - 2.5 hours
  Focus: All 7 layers with examples. Memorize and practice.
  PYQs to solve: 2023(10m), 2022(13m), 2021(10m)

Day 2 (4 hours):
- TCP/IP (Weight: 8.9) - 1.5 hours
- Network Security (Weight: 7.5) - 1 hour

...continue for each day...

Day 7 (2 hours):
REVISION ONLY - No new topics
- Revise OSI Model
- Revise TCP/IP
- Quick review of flashcards