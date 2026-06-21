import json
import re

def parse_priority_list_text(text):
    lines = text.split('\n')
    topics = []
    
    for line in lines:
        if '|' in line and any(x in line for x in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 5:
                topics.append({
                    'topic_name': parts[2] if len(parts) > 2 else 'Unknown',
                    'weight': float(re.search(r'\d+\.\d+', parts[3] or '0').group()) if len(parts) > 3 else 0,
                    'band': parts[4] if len(parts) > 4 else 'UNKNOWN'
                })
    
    return topics if topics else None

def parse_questions_from_text(text):
    lines = text.split('\n')
    questions = []
    current_question = None
    
    for line in lines:
        if re.match(r'^#+\s*.*\(Weight:', line):
            current_question = {'topic': line.strip(), 'questions': []}
        elif re.match(r'^\d+\.\s', line) or re.match(r'^###\s*Question', line):
            if current_question is not None:
                current_question['questions'].append(line.strip())
    
    return questions if questions else None

def parse_flashcard_text(text):
    cards = []
    blocks = text.split('---')
    
    for block in blocks:
        if 'FRONT' in block and 'BACK' in block:
            front_match = re.search(r'FRONT[:\s]+"?([^"]+)"?', block, re.IGNORECASE)
            back_match = re.search(r'BACK[:\s]+(.*?)(?=MEMORY|DIFFICULTY|$)', block, re.IGNORECASE | re.DOTALL)
            
            if front_match and back_match:
                cards.append({
                    'front': front_match.group(1).strip(),
                    'back': back_match.group(1).strip()[:200]
                })
    
    return cards if cards else None

def extract_table_from_markdown(markdown_text):
    lines = markdown_text.split('\n')
    table_data = []
    in_table = False
    
    for line in lines:
        if '|' in line:
            in_table = True
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) > 1 and not any(x == '-' * len(x) for x in parts):
                table_data.append(parts)
    
    return table_data if table_data else None