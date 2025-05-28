import os, json, re
import pandas as pd
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# 1. 모델 로드
MODEL_DIR = "models/classifier"
labels = ["기각", "각하", "인용", "일부 인용", "조정"]
id2label = {i: l for i, l in enumerate(labels)}

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

# 2. 판례 텍스트 추출 함수
def extract_text(case_json):
    요지 = case_json.get("판결요지", "").replace("<br/>", " ").strip()
    본문 = case_json.get("판례내용", "").replace("<br/>", " ").strip()
    주문_match = re.search(r"(【주\s*문】.*)", 본문)
    주문 = 주문_match.group(1) if 주문_match else ""
    return f"{요지} {주문}".strip()

# 3. JSON 파일 불러오기
json_dir = Path("data/test_set")
json_files = list(json_dir.glob("*.json"))
results = []

for file in json_files:
    with open(file, 'r', encoding='utf-8') as f:
        case = json.load(f)
        text = extract_text(case)

        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=512)
        with torch.no_grad():
            logits = model(**inputs).logits
            pred_id = torch.argmax(logits, dim=-1).item()
            pred_label = id2label[pred_id]

        results.append({
            "filename": file.name,
            "predicted_label": pred_label,
            "text": text[:150] + "..."  # 텍스트 일부 요약 표시
        })

# 4. 결과 저장
df = pd.DataFrame(results)
df.to_csv("data/test_set_results.csv", index=False, encoding="utf-8-sig")
print("✅ 예측 결과 저장 완료: data/test_set_results.csv")
