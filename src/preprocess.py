import os
import json
import pandas as pd
import re
from collections import defaultdict, Counter
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer
from datasets import Dataset

# 경로 설정
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw", "원본")
OUTPUT_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)

LABEL_CSV_PATH = os.path.join(DATA_DIR, "gpt4.1_label_1000d.csv")
LABEL_MAP_PATH = os.path.join(DATA_DIR, "label_map.json")

# 로딩
with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
    label_map = json.load(f)

id_to_label = {v: k for k, v in label_map.items()}

df_label = pd.read_csv(LABEL_CSV_PATH)

def extract_text(full_text: str, fallback_len: int = 1000) -> str:
    party_info = re.search(r"(【원고, 피상고인】.*?【피고, 상고인】)", full_text, re.DOTALL)
    judgement_info = re.search(r"(【주[\s]*문】.*?)(【이[\s]*유】|【이유】)", full_text, re.DOTALL)
    combined = ""
    if party_info:
        combined += party_info.group(1).strip() + "\n"
    if judgement_info:
        combined += judgement_info.group(1).strip()
    return combined.strip() if combined.strip() else full_text[:fallback_len].strip()

# 전처리
data_list = []
missing_stats = defaultdict(list)

for _, row in tqdm(df_label.iterrows(), total=len(df_label)):
    filename = str(row["파일명"]).strip()
    label_str = str(row["라벨링결과"]).strip()
    label = label_map.get(label_str)

    if label is None:
        missing_stats["label_map_error"].append(filename)
        continue

    json_path = os.path.join(RAW_DIR, filename)
    if not os.path.exists(json_path):
        missing_stats["file_missing"].append(filename)
        continue

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            case_data = json.load(f)
    except Exception as e:
        missing_stats["json_read_error"].append(filename)
        continue

    full_text = case_data.get("판례내용", "")
    if not full_text:
        missing_stats["no 판례내용"].append(filename)
        continue

    trimmed = extract_text(full_text)
    if trimmed == full_text[:1000].strip():
        missing_stats["regex_fail_fallback"].append(filename)

    data_list.append({"text": trimmed, "label": label})

# 희귀 클래스 제거
data_list = [x for x in data_list if x["label"] not in [3, 6]]

# Stratified split
train_val, test = train_test_split(
    data_list, test_size=0.1, random_state=42, stratify=[x["label"] for x in data_list]
)
train, val = train_test_split(
    train_val, test_size=2/9, random_state=42, stratify=[x["label"] for x in train_val]
)

# 토크나이저 로딩
tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")

def tokenize_function(example):
    return tokenizer(
        example["text"], padding="max_length", truncation=True, max_length=512
    )

# Dataset 변환 및 토크나이징
train_dataset = Dataset.from_list(train).map(tokenize_function, batched=True)
val_dataset = Dataset.from_list(val).map(tokenize_function, batched=True)
test_dataset = Dataset.from_list(test).map(tokenize_function, batched=True)

# 저장
with open(os.path.join(OUTPUT_DIR, "tokenized_train.json"), "w", encoding="utf-8") as f:
    json.dump(train_dataset.to_list(), f, ensure_ascii=False, indent=2)

with open(os.path.join(OUTPUT_DIR, "tokenized_val.json"), "w", encoding="utf-8") as f:
    json.dump(val_dataset.to_list(), f, ensure_ascii=False, indent=2)

with open(os.path.join(OUTPUT_DIR, "tokenized_test.json"), "w", encoding="utf-8") as f:
    json.dump(test_dataset.to_list(), f, ensure_ascii=False, indent=2)

# fallback 파일 저장
with open(os.path.join(OUTPUT_DIR, "regex_fallback_list.txt"), "w", encoding="utf-8") as f:
    for file in missing_stats["regex_fail_fallback"]:
        f.write(file + "\n")

print("\n✅ 전처리 및 토크나이징 완료. 총 샘플 수:")
print(f"Train: {len(train)} / Val: {len(val)} / Test: {len(test)}")
