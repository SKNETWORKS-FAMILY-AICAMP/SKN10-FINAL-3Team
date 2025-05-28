import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import sys
import os

# 1. 모델 경로 및 라벨 정의
MODEL_DIR = "models/classifier"
labels = ["기각", "각하", "인용", "일부 인용", "조정"]  # 학습 시 정렬된 순서에 맞춰야 함
id2label = {i: label for i, label in enumerate(labels)}

# 2. 모델 및 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

# 3. 판례 본문 입력 받기 (CLI 또는 테스트용)
if len(sys.argv) > 1:
    input_text = sys.argv[1]
else:
    input_text = input("판례 본문을 입력하세요:\n")

# 4. 토크나이즈 및 텐서 변환
inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding="max_length", max_length=512)

# 5. 모델 추론
with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits
    pred_id = torch.argmax(logits, dim=-1).item()
    pred_label = id2label[pred_id]

# 6. 결과 출력
print(f"\n🧾 예측된 판결 결과: {pred_label}")
