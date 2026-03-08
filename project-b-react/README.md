# Project B: React Code Generation Fine-tuning

Fine-tuning **Qwen2.5-Coder-1.5B-Instruct** on a React + Tailwind CSS code generation dataset using LoRA on Apple Silicon (Mac Mini, 64GB).

## Motivation

Modern AI coding assistants are typically large, cloud-dependent models. This project explores a different question: **how small can a model be while still learning a specific coding style?**

The target use case is a front-end code generation assistant that reliably outputs self-contained React + Tailwind CSS components — without hallucinating external UI libraries or adding unrequested features. Rather than prompting a large general-purpose model, the goal is to fine-tune a compact model to internalize this pattern directly.

This also serves as a proof of concept for **on-device fine-tuning on Apple Silicon**, demonstrating that meaningful LoRA training is possible without cloud GPUs.

## Why This Model

**Qwen2.5-Coder-1.5B-Instruct** was chosen for the following reasons:

- **Small enough to show clear before/after improvement** — a 7B+ model already handles React/Tailwind well, making fine-tuning effects harder to demonstrate
- **Strong code foundation** — Qwen2.5-Coder is purpose-built for code generation, making it a realistic base for a coding assistant
- **MLX-compatible** — `mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit` runs efficiently on Apple Silicon via the MLX framework
- **Practical deployment target** — a 1.5B model quantized to 4-bit runs under 1GB memory, making it viable for edge or on-device deployment

## Results

| | Base Model | Fine-tuned |
|---|---|---|
| Library usage | Mixes Tailwind with `@chakra-ui/react` | Pure Tailwind CSS only |
| TypeScript | No type definitions | Proper interfaces and typed props |
| Code quality | Inconsistent, off-topic features added | Focused, clean, production-ready |

## Dataset

**[cfahlgren1/react-code-instructions](https://huggingface.co/datasets/cfahlgren1/react-code-instructions)**

- Total: 74,428 samples (natural language → complete `App.tsx`)
- Each sample contains a system prompt, user instruction, and a complete React + TypeScript + Tailwind CSS response
- Filtered: removed samples < 200 chars or > 8,000 chars
- Final: **500 train / 300 val** (random seed 42)

A smaller subset was deliberately chosen to make the fine-tuning effect more visible — with a strong base model and too much data, the model converges before meaningful stylistic adaptation occurs.

## Model

- **Base**: `mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit`
- **Framework**: [mlx-lm](https://github.com/ml-explore/mlx-examples/tree/main/llms/mlx_lm) (Apple MLX)
- **Method**: LoRA (Low-Rank Adaptation)

## Training

```bash
mlx_lm.lora \
  --model mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit \
  --data ./data/processed_b \
  --train \
  --batch-size 1 \
  --num-layers 8 \
  --iters 2000 \
  --learning-rate 5e-6 \
  --steps-per-report 10 \
  --steps-per-eval 200 \
  --save-every 200 \
  --adapter-path ./checkpoints_b2
```

| Parameter | Value |
|---|---|
| LoRA layers | 8 |
| Iterations | 2,000 |
| Learning rate | 5e-6 |
| Batch size | 1 |
| Final train loss | ~0.28 |
| Peak memory | ~1.8 GB |
| Hardware | Apple M-series, 64GB unified memory |

## Inference

```bash
mlx_lm.generate \
  --model mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit \
  --adapter-path ./checkpoints_b2 \
  --max-tokens 2000 \
  --extra-eos-token "<|im_end|>" \
  --prompt "<|im_start|>user
Create a single App.tsx file for a todo app using React and Tailwind CSS<|im_end|>
<|im_start|>assistant
"
```

## Before / After

### Before (base model)
See [`examples/before.tsx`](examples/before.tsx)

- Imports `@chakra-ui/react` despite being asked for Tailwind CSS only
- No TypeScript type definitions
- Adds unrelated features (`useColorMode`, dark mode toggle)

### After (fine-tuned)
See [`examples/after.tsx`](examples/after.tsx)

- Pure Tailwind CSS classes only
- Proper TypeScript interface (`Todo`)
- Clean, focused implementation matching the prompt
- SVG icons instead of library components

## Project Structure

```
project-b-react/
├── preprocess_b.py       # Data preprocessing script
├── checkpoints_b2/       # LoRA adapter weights
├── data/
│   └── processed_b/
│       ├── train.jsonl   # 500 training samples
│       └── val.jsonl     # 300 validation samples
└── examples/
    ├── before.tsx        # Base model output
    └── after.tsx         # Fine-tuned model output
```
