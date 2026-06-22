import json
import re

def parse_flashcard_text(text):
    if not text:
        return None

    cards = []
    blocks = re.split(r'\n---+\n', text)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        front = None
        back = None
        topic = None
        weight = None
        memory_hook = None
        difficulty = None

        topic_match = re.search(r'TOPIC:\s*(.+)', block, re.IGNORECASE)
        front_match = re.search(r'FRONT:\s*(.+)', block, re.IGNORECASE)
        back_match = re.search(r'BACK:\s*(.*?)(?=MEMORY HOOK:|DIFFICULTY:|TOPIC:|FRONT:|---|\Z)', block, re.IGNORECASE | re.DOTALL)
        memory_match = re.search(r'MEMORY HOOK:\s*(.+)', block, re.IGNORECASE)
        difficulty_match = re.search(r'DIFFICULTY:\s*(.+)', block, re.IGNORECASE)
        weight_match = re.search(r'Weight:\s*([\d.]+)', block, re.IGNORECASE)

        if topic_match:
            topic = topic_match.group(1).strip()
        if front_match:
            front = front_match.group(1).strip()
        if back_match:
            back = back_match.group(1).strip()
        if memory_match:
            memory_hook = memory_match.group(1).strip()
        if difficulty_match:
            difficulty = difficulty_match.group(1).strip()
        if weight_match:
            weight = float(weight_match.group(1))

        if front and back:
            card = {
                "topic": topic or front[:30],
                "front": front,
                "back": back,
                "memory_hook": memory_hook,
                "difficulty": difficulty,
                "weight": weight or 0
            }
            cards.append(card)

    return cards if cards else None

def extract_table_from_markdown(markdown_text):
    lines = markdown_text.split('\n')
    table_data = []

    for line in lines:
        if '|' in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) > 1 and not all(set(x) <= set('- ') for x in parts):
                table_data.append(parts)

    return table_data if table_data else None