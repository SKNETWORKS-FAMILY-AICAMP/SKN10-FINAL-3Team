import os
import json
from datasets import Dataset
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from sklearn.metrics import accuracy_score, f1_score, classification_report
import torch
import numpy as np
from tqdm import tqdm

# 경로 설정
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 데이터 로드
def load_dataset(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Dataset.from_list(data)

tokenized_train = load_dataset("tokenized_train.json")
tokenized_val = load_dataset("tokenized_val.json")
tokenized_test = load_dataset("tokenized_test.json")

# tokenizer & model 로드
tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")
labels = set(tokenized_train["label"])
model = BertForSequenceClassification.from_pretrained(
    "bert-base-multilingual-cased",
    num_labels=max(labels) + 1 
)

# 평가 지표 정의
def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=1)
    labels = p.label_ids
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1_macro": f1_score(labels, preds, average="macro")
    }

# 학습 설정 (구버전 호환)
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    logging_dir=os.path.join(OUTPUT_DIR, "logs"),
    do_train=True,
    do_eval=True
)

# Trainer 구성
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    tokenizer=tokenizer
)

# 학습 시작
trainer.train()

# 수동 평가 실행
print("\n📊 테스트셋 성능:")
eval_result = trainer.evaluate(tokenized_test)
print(eval_result)

# 상세 리포트
preds = trainer.predict(tokenized_test)
preds_labels = np.argmax(preds.predictions, axis=1)
true_labels = preds.label_ids
print("\n📋 분류 리포트:")
print(classification_report(true_labels, preds_labels))

# tqdm 활용해 예측 결과 요약 출력
print("\n🔍 예측 샘플:")
for i in tqdm(range(min(10, len(preds_labels)))):
    print(f"[{i+1}] 예측: {preds_labels[i]} / 실제: {true_labels[i]}")

# 모델 저장
model.save_pretrained(os.path.join(OUTPUT_DIR, "bert_case_classifier"))
tokenizer.save_pretrained(os.path.join(OUTPUT_DIR, "bert_case_classifier"))
print("\n✅ 모델 저장 완료: outputs/bert_case_classifier")
