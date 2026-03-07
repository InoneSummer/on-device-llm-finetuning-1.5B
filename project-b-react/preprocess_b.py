# preprocess_b.py
from datasets import load_dataset
import json, os, random

print("Loading dataset...")
ds = load_dataset("cfahlgren1/react-code-instructions", split="train")
print(f"전체: {len(ds)}개")

results = []
skipped_short = 0
skipped_long = 0

for row in ds:
    messages = row.get("messages", [])
    if not messages:
        continue
    
    # assistant 응답 길이 필터
    assistant_content = messages[-1].get("content", "")
    if len(assistant_content) < 200:
        skipped_short += 1
        continue
    if len(assistant_content) > 8000:
        skipped_long += 1
        continue
    
    results.append({"messages": messages})

print(f"필터 후: {len(results)}개")
print(f"  - 너무 짧아서 제외: {skipped_short}개")
print(f"  - 너무 길어서 제외: {skipped_long}개")

# 랜덤 샘플링
random.seed(42)
random.shuffle(results)

train_data = results[:500]
val_data = results[500:800]

os.makedirs("data/processed_b2", exist_ok=True)

with open("data/processed_b2/train.jsonl", "w") as f:
    for item in train_data:
        f.write(json.dumps(item) + "\n")

with open("data/processed_b2/val.jsonl", "w") as f:
    for item in val_data:
        f.write(json.dumps(item) + "\n")

print(f"train: {len(train_data)}개, val: {len(val_data)}개")
print("Done!")