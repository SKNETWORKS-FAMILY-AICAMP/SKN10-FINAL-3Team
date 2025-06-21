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

# ========== 2. 사건(Event) 테이블 데이터 삽입 ==========
print("\n📥 [2] Event 테이블 데이터 삽입 시작...")

event_file = './csv_data/event_table_data.csv'
event_df = pd.read_csv(event_file, encoding='utf-8-sig')

for _, row in event_df.iterrows():
    try:
        Event.objects.create(
            e_title=row['e_title'],
            e_description=row['e_description'],
            client=row['client'],
            cat_cd=row['cat_cd'],
            cat_02=row['cat_02'],
            cat_03=row['cat_03'],
            memo=row.get('memo'),
            org_cd=row['org_cd'],
            estat_cd=row['estat_cd'],
            lstat_cd=row['lstat_cd'],
            estat_num_cd=row.get('estat_num_cd', ''),
            submit_at=datetime.strptime(row['submit_at'], '%Y-%m-%d') if pd.notna(row['submit_at']) else None,
            creator_name=row['creator_name'],
            created_at=datetime.strptime(row['created_at'], '%Y-%m-%d'),
            update_at=datetime.strptime(row['update_at'], '%Y-%m-%d'),
        )
        print(f"✅ 사건 추가됨: {row['e_title']}")
    except Exception as e:
        print(f"❌ 에러 발생 ({row['e_title']}): {e}")
        
# ========== 3. 판례 테이블(CASE) 데이터 삽입 ==========
print("📥 [3] 판례 테이블(CASE) 데이터 삽입 시작...")

case_file = './csv_data/case_table_data.csv'
case_df = pd.read_csv(case_file, encoding='utf-8-sig')

for idx, row in case_df.iterrows():
    try:
        Case.objects.create(
            case_num = row['case_num'],
            court_name = row['court_name'],
            case_name = row['case_name'],
            case_at = pd.to_datetime(row['case_at']),
            refer_cases = row.get('refer_cases', None),
            refer_statutes = row.get('refer_statutes', None),
            decision_summary = row['decision_summary'],
            case_full = row['case_full'],
            decision_issue = row['decision_issue'],
            case_result = row['case_result'],
            facts_summary = row['facts_summary'],
            facts_keywords = row['facts_keywords'],
            issue_summary = row['issue_summary'],
            issue_keywords = row['issue_keywords'],
            keywords = row['keywords'],
        )
        print(f"✅ 판례 추가됨: {row['case_num']} - {row['case_name'][:20]}")
    except Exception as e:
        print(f"❌ 에러 발생 ({row['case_num']}): {e}")
