"""
prepare_data.py
webui 데이터셋에서 4000자 이하 샘플 2,000개 확보 + mlx-vlm 파인튜닝 포맷으로 변환
"""

import json
import os
from pathlib import Path
from datasets import load_dataset
from PIL import Image
from tqdm import tqdm

# ── 설정 ──────────────────────────────────────────
TARGET_SAMPLES = 2000       # 확보할 최종 샘플 수
MAX_CODE_CHARS = 4000       # HTML 코드 최대 길이
MAX_IMAGE_SIZE = 800        # 이미지 긴 변 최대 px
OUTPUT_DIR     = Path("data/processed")
IMAGE_DIR      = Path("data/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = (
    "You are an expert UI developer. "
    "Given a screenshot of a UI, generate clean and functional HTML/CSS code "
    "that accurately reproduces the layout, components, and visual style shown."
)

# ── 데이터 로드 (전체 셔플) ────────────────────────
print(f"webui 데이터셋 로딩 중... (목표: {TARGET_SAMPLES}샘플, 최대 코드길이: {MAX_CODE_CHARS}자)")
dataset = load_dataset("ronantakizawa/webui", split="train")
dataset = dataset.shuffle(seed=42)
print(f"  전체 데이터셋: {len(dataset)}샘플")
print(f"  컬럼: {dataset.column_names}")

# ── 포맷 변환 (목표 샘플 수 채울 때까지) ────────────
records = []
skipped = 0
img_idx = 0

pbar = tqdm(dataset, desc="변환 중")
for sample in pbar:
    if len(records) >= TARGET_SAMPLES:
        break

    try:
        # 코드 먼저 확인 (이미지 저장 전에 필터링)
        code = sample.get("text") or sample.get("code") or sample.get("html") or ""
        if not code.strip():
            skipped += 1
            continue

        # 4000자 초과 샘플 스킵
        if len(code.strip()) > MAX_CODE_CHARS:
            skipped += 1
            continue

        # 이미지 처리 및 리사이즈
        img = sample["image"]
        if not isinstance(img, Image.Image):
            img = Image.fromarray(img)
        img = img.convert("RGB")

        # 긴 변 기준 리사이즈
        w, h = img.size
        if max(w, h) > MAX_IMAGE_SIZE:
            scale = MAX_IMAGE_SIZE / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        img_path = IMAGE_DIR / f"sample_{img_idx:04d}.jpg"
        img.save(img_path, "JPEG", quality=85)
        img_idx += 1

        record = {
            "images": str(img_path),
            "messages": [
                {"role": "system",    "content": SYSTEM_PROMPT},
                {"role": "user",      "content": "<image>\nGenerate the HTML/CSS code for this UI."},
                {"role": "assistant", "content": code.strip()}
            ]
        }
        records.append(record)
        pbar.set_postfix({"확보": len(records), "스킵": skipped})

    except Exception as e:
        skipped += 1
        if skipped <= 5:
            print(f"\n  [경고] 스킵: {e}")

print(f"\n  총 확보: {len(records)}샘플, 스킵: {skipped}")

# ── train / val 분리 (90 / 10) ──────────────────────
split_idx  = int(len(records) * 0.9)
train_data = records[:split_idx]
val_data   = records[split_idx:]

with open(OUTPUT_DIR / "train.jsonl", "w") as f:
    for r in train_data:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

with open(OUTPUT_DIR / "val.jsonl", "w") as f:
    for r in val_data:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

with open(OUTPUT_DIR / "meta.json", "w") as f:
    json.dump({
        "total": len(records),
        "train": len(train_data),
        "val": len(val_data),
        "skipped": skipped,
        "max_code_chars": MAX_CODE_CHARS,
        "max_image_size": MAX_IMAGE_SIZE,
        "columns": dataset.column_names
    }, f, indent=2)

print(f"\n완료! train={len(train_data)}, val={len(val_data)}, skipped={skipped}")
print("다음 단계: python3 baseline_test.py")