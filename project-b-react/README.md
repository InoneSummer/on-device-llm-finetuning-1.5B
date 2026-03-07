# ProtoPie AI Engineer Portfolio
## UI Screenshot → HTML Code Generation (Multimodal Fine-tuning)

### 실행 순서

```bash
# 1. 환경 세팅 + 모델 다운로드 (9GB)
bash setup.sh

# 2. 데이터 준비 (webui 2,000샘플)
python3 prepare_data.py

# 3. 파인튜닝 전 베이스라인 저장
python3 baseline_test.py

# 4. 파인튜닝 시작 (자기 전에!) - 4~6시간
python3 finetune.py

# 5. 결과 비교 (다음날 아침)
python3 eval_after.py
```

### 스택
- **모델**: Qwen2.5-VL-7B-Instruct (MLX 8bit 양자화)
- **데이터**: ronantakizawa/webui (2,000샘플)
- **방법**: LoRA (rank=8, 16 layers)
- **하드웨어**: Mac mini M4 Pro 64GB

### 왜 이 접근법?
ProtoPie의 핵심 문제는 **UI 디자인 → 코드 변환**이에요.
텍스트만으로는 이 도메인을 충분히 커버할 수 없고,
멀티모달 모델(이미지 이해 + 코드 생성)이 필요합니다.
