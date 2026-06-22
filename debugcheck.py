import json
import os

subject = "CN"
path = f"semprep_data/subjects/{subject}/analysis.json"

if not os.path.exists(path):
    print("File does not exist")
    exit()

with open(path, "r") as f:
    data = json.load(f)

print("Keys in saved data:")
for key in data.keys():
    print(f"  {key}")

print("\nweighted_topics type:", type(data.get("weighted_topics")))
print("\nweighted_topics content:")
print(json.dumps(data.get("weighted_topics", {}), indent=2)[:500])

print("\ntopic_map type:", type(data.get("topic_map")))
print("\ntopic_map content:")
print(json.dumps(data.get("topic_map", {}), indent=2)[:500])

print("\npriority_list preview:")
print(str(data.get("priority_list", ""))[:300])

print("\nquestion_bank preview:")
print(str(data.get("question_bank", ""))[:300])