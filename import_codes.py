import os
import django
import pandas as pd
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # 프로젝트 이름 맞게 수정
django.setup()

from code_t.models import Code_T
from event.models import Event
from case.models import Case

# ========== 1. 코드 테이블(CODE_T) 데이터 삽입 ==========
print("📥 [1] Code_T 테이블 데이터 삽입 시작...")

code_file = './csv_data/code_table_data.csv'
code_df = pd.read_csv(code_file, encoding='utf-8-sig')

for _, row in code_df.iterrows():
    code = row['code']
    code_label = row['code_label']
    code_desc = row.get('code_desc', None)
    upper_code = row.get('upper_code', None)
    description = row.get('description', None)

    upper_code_obj = None
    if pd.notna(upper_code):
        try:
            upper_code_obj = Code_T.objects.get(code=upper_code)
        except Code_T.DoesNotExist:
            print(f"⚠️ 상위 코드 {upper_code}가 존재하지 않음. 무시하고 진행.")

    obj, created = Code_T.objects.update_or_create(
        code=code,
        defaults={
            'code_label': code_label,
            'code_desc': code_desc,
            'upper_code': upper_code_obj,
            'description': description,
        }
    )
    print(f"{'✔️ 추가됨' if created else '🔄 업데이트됨'}: {code} - {code_label}")

# ========== 2. 사건(Event) 테이블 데이터 삽입 ========== #
print("\n📥 [2] Event 테이블 데이터 삽입 시작...")

event_file = './csv_data/event_table_data.csv'
event_df = pd.read_csv(event_file, encoding='utf-8-sig')

total_rows = len(event_df)
inserted_rows = 0
skipped_rows = 0

# ✅ 필수 항목 정의 → submit_at도 포함
required_fields = ['event_num', 'e_title', 'client', 'org_cd', 'estat_cd', 'submit_at']

for _, row in event_df.iterrows():
    # ✅ 필수 필드 누락 여부 확인
    if any(pd.isna(row.get(field)) or str(row.get(field)).strip() == '' for field in required_fields):
        skipped_rows += 1
        print(f"⛔ 필수 필드 누락으로 생략됨: {row.get('event_num', 'UNKNOWN')} - {row.get('e_title', '')}")
        continue

    try:
        # ✅ 여기까지 온 경우, submit_at은 무조건 값이 있음
        try:
            submit_at = pd.to_datetime(row['submit_at'], errors='raise')
        except Exception as e:
            print(f"⚠️ 날짜 파싱 실패 → 생략됨: {row['event_num']} ({row['submit_at']}) - {e}")
            skipped_rows += 1
            continue

        obj, created = Event.objects.update_or_create(
            event_num=row['event_num'],
            defaults={
                'e_title': row['e_title'],
                'e_description': row['e_description'],
                'claim_summary': row['claim_summary'],
                'client': row['client'],
                'client_role': row['client_role'],
                'cat_cd': row['cat_cd'],
                'cat_02': row['cat_02'],
                'org_cd': row['org_cd'],
                'estat_cd': row['estat_cd'],
                'lstat_cd': row.get('lstat_cd') if pd.notna(row.get('lstat_cd')) else None,
                'estat_num_cd': row.get('estat_num_cd') if pd.notna(row.get('estat_num_cd')) else None,
                'memo': row.get('memo') if pd.notna(row.get('memo')) else None,
                'event_file': row.get('event_file') if pd.notna(row.get('event_file')) else None,
                'submit_at': submit_at,
                'creator_name': row['creator_name'],
                'ai_strategy': row.get('ai_strategy') if pd.notna(row.get('ai_strategy')) else '미지정',
            }
        )

        print(f"{'✔️ 추가됨' if created else '🔄 업데이트됨'}: {row['event_num']} - {row['e_title']}")
        inserted_rows += 1

    except Exception as e:
        print(f"❌ 에러 발생 ({row.get('event_num', 'UNKNOWN')}): {e}")
        skipped_rows += 1


print(f"\n📊 전체 {total_rows}건 중 {inserted_rows}건 삽입 완료, {skipped_rows}건 생략됨.")

# ========== 3. 판례 테이블(CASE) 데이터 삽입 ========== 
print("📥 [3] 판례 테이블(CASE) 데이터 삽입 시작...")

case_file = './csv_data/case_table_data.csv'
case_df = pd.read_csv(case_file, encoding='utf-8-sig')

inserted_count = 0
updated_count = 0

for idx, row in case_df.iterrows():
    case_num = row['case_num']

    try:
        obj, created = Case.objects.update_or_create(
            case_num=case_num,
            defaults={
                'court_name': row['court_name'],
                'case_name': row['case_name'],
                'case_at': pd.to_datetime(row['case_at']) if pd.notna(row['case_at']) else None,
                'refer_cases': row.get('refer_cases', None),
                'refer_statutes': row.get('refer_statutes', None),
                'decision_summary': row['decision_summary'],
                'case_full': row['case_full'],
                'decision_issue': row['decision_issue'],
                'case_result': row['case_result'],
                'facts_summary': row['facts_summary'],
                'facts_keywords': row['facts_keywords'],
                'issue_summary': row['issue_summary'],
                'issue_keywords': row['issue_keywords'],
                'keywords': row['keywords'],
            }
        )
        if created:
            inserted_count += 1
            print(f"✅ 판례 추가됨: {case_num} - {row['case_name'][:20]}")
        else:
            updated_count += 1
            print(f"🔄 판례 업데이트됨: {case_num} - {row['case_name'][:20]}")

    except Exception as e:
        print(f"❌ 에러 발생 ({case_num}): {e}")

print(f"\n📊 총 {inserted_count}건 추가, {updated_count}건 업데이트 완료.")
