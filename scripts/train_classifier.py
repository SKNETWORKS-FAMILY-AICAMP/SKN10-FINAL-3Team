import pandas as pd
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer
)
from sklearn.model_selection import train_test_split
from pathlib import Path
import torch

# 1. 데이터 로드
df = pd.read_csv("data/labeled/precedents_labeled.csv")
labels = sorted(df["label"].unique())
label2id = {l: i for i, l in enumerate(labels)}
id2label = {i: l for l, i in label2id.items()}
df["label_id"] = df["label"].map(label2id)

# 2. 학습/평가 분리 및 HuggingFace Dataset 변환
train_df, eval_df = train_test_split(df, test_size=0.2, stratify=df["label_id"], random_state=42)

train_dataset = Dataset.from_pandas(
    train_df[["text", "label_id"]].rename(columns={"label_id": "labels"})
)
eval_dataset = Dataset.from_pandas(
    eval_df[["text", "label_id"]].rename(columns={"label_id": "labels"})
)

# 3. 토크나이저
model_name = "klue/bert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=512)

train_dataset = train_dataset.map(tokenize, batched=True)
eval_dataset = eval_dataset.map(tokenize, batched=True)

# 4. 모델 로딩
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=len(label2id),
    id2label=id2label,
    label2id=label2id
)

# 5. 학습 설정
training_args = TrainingArguments(
    output_dir="./models/classifier",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss"
)

# 6. 성능 지표 계산 함수
def compute_metrics(p):
    preds = p.predictions.argmax(axis=-1)
    labels = p.label_ids
    accuracy = (preds == labels).mean()
    return {"accuracy": accuracy}

# 7. Trainer 생성 및 학습 시작
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

trainer.train()

# 8. 모델 저장
trainer.save_model("./models/classifier")
tokenizer.save_pretrained("./models/classifier")

print("✅ 모델 학습 및 저장 완료!")
