import json, glob, re
import pandas as pd
from pathlib import Path

def extract_label(text):
    """
    판례내용 전체 텍스트에서 결과(label)를 규칙 기반으로 추출
    """
    if "기각" in text and "인용" not in text:
        return "기각"
    elif "인용" in text and "기각" in text:
        return "일부 인용"
    elif "인용" in text:
        return "인용"
    elif "각하" in text:
        return "각하"
    elif "조정" in text:
        return "조정"
    return None

def extract_relevant_text(case):
    """
    판례 JSON에서 판결요지 + 판례내용 중 【주문】 이후 텍스트를 추출
    """
    요지 = case.get("판결요지", "").replace("<br/>", " ").strip()
    판례내용 = case.get("판례내용", "").replace("<br/>", " ").strip()
    주문_match = re.search(r"(【주\s*문】.*)", 판례내용)
    주문 = 주문_match.group(1) if 주문_match else ""
    return f"{요지} {주문}".strip()

def main():
    data_dir = Path("data/raw_json")
    output_file = Path("data/labeled/precedents_labeled.csv")
    records = []

    for file in data_dir.glob("*.json"):
        with open(file, 'r', encoding='utf-8') as f:
            case = json.load(f)
            text = extract_relevant_text(case)
            label = extract_label(text)
            if label and text:
                records.append({"text": text, "label": label})

    df = pd.DataFrame(records)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"✅ Saved labeled data to: {output_file}")

if __name__ == "__main__":
    main()
