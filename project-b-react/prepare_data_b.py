from datasets import load_dataset
import json
import re
from pathlib import Path
from tqdm import tqdm

NUM_SAMPLES = 2000
OUTPUT_DIR = Path("data/react_code")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("react-code-instructions 로딩 중...")
dataset = load_dataset("cfahlgren1/react-code-instructions", split="train", streaming=True)

samples = []
skipped = 0

for item in tqdm(dataset, total=NUM_SAMPLES):
    if len(samples) >= NUM_SAMPLES:
        break

    messages = item["messages"]
    # user 메시지와 assistant 메시지 추출
    user_msg = next((m for m in messages if m["role"] == "user"), None)
    asst_msg = next((m for m in messages if m["role"] == "assistant"), None)

    if not user_msg or not asst_msg:
        skipped += 1
        continue

    # assistant 응답에서 tsx/jsx 코드 블록만 추출
    code_match = re.search(r"```(?:tsx|jsx|typescript|javascript)?\n(.*?)```", asst_msg["content"], re.DOTALL)
    code = code_match.group(1).strip() if code_match else asst_msg["content"].strip()

    if len(code) < 100:  # 너무 짧은 건 스킵
        skipped += 1
        continue

    sample = {
        "messages": [
            {"role": "user", "content": user_msg["content"]},
            {"role": "assistant", "content": code}
        ]
    }
    samples.append(sample)

split = int(len(samples) * 0.9)
train_samples = samples[:split]
val_samples = samples[split:]

def save_jsonl(data, path):
    with open(path, "w") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

save_jsonl(train_samples, OUTPUT_DIR / "train.jsonl")
save_jsonl(val_samples, OUTPUT_DIR / "val.jsonl")

print(f"완료! train={len(train_samples)}, val={len(val_samples)}, skipped={skipped}")