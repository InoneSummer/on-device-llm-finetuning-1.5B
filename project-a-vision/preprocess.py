# preprocess.py
from datasets import load_dataset
from PIL import Image
import json, os, random

print("Loading dataset...")
ds = load_dataset("ronantakizawa/webui")

def process_split(split, max_samples=None):
    data = ds[split]
    print(f"{split}: 전체 {len(data)}개")
    
    results = []
    skipped_viewport = 0
    skipped_short = 0
    
    for row in data:
        if row.get("viewport") != "mobile":
            skipped_viewport += 1
            continue
        
        html = row.get("html", "")
        css = row.get("css", "")
        combined = html
        
        if len(combined) < 200:
            skipped_short += 1
            continue
        
        img = row["image"].resize((512, 512), Image.LANCZOS)
        if img.mode == "RGBA":
            img = img.convert("RGB")
        
        img_filename = f"sample_{row['sample_id']}.jpg"
        img_path = f"data/images_v2/{img_filename}"
        os.makedirs("data/images_v2", exist_ok=True)
        img.save(img_path, "JPEG")
        
        results.append({
            "images": img_path,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert UI developer. Given a screenshot of a UI, generate clean and functional HTML/CSS code that accurately reproduces the layout, components, and visual style shown."
                },
                {
                    "role": "user",
                    "content": "<image>\nGenerate the HTML/CSS code for this UI."
                },
                {
                    "role": "assistant",
                    "content": combined
                }
            ]
        })
    
    print(f"  - viewport 제외: {skipped_viewport}개")
    print(f"  - 너무 짧아서 제외: {skipped_short}개")
    
    if max_samples and len(results) > max_samples:
        random.seed(42)
        results = random.sample(results, max_samples)
    
    print(f"{split}: 최종 {len(results)}개 샘플")
    return results

os.makedirs("data/processed_v2", exist_ok=True)

train_data = process_split("train", max_samples=2000)
val_data = process_split("validation", max_samples=500)

with open("data/processed_v2/train.jsonl", "w") as f:
    for item in train_data:
        f.write(json.dumps(item) + "\n")

with open("data/processed_v2/val.jsonl", "w") as f:
    for item in val_data:
        f.write(json.dumps(item) + "\n")

with open("data/processed_v2/meta.json", "w") as f:
    json.dump({"prompt_feature": "messages", "image_feature": "images"}, f)

print("Done!")