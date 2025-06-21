import os
import django
import pandas as pd

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from case.models import Case

# CSV 로드
df = pd.read_csv('./csv_data/case_table_data.csv', encoding='utf-8-sig')
print('len(df):', len(df))
csv_case_nums = set(df['case_num'].unique())
print(f"📥 CSV에서 추출한 case_num 개수: {len(csv_case_nums)}")

# DB에 있는 case_num 추출
existing_case_nums = set(Case.objects.values_list('case_num', flat=True))

# 중복된 case_num
duplicated_case_nums = csv_case_nums.intersection(existing_case_nums)

# ✅ DB에 존재하지 않는 case_num = CSV에만 있는 case_num
not_in_db_case_nums = csv_case_nums - existing_case_nums

print(f"📌 DB에 없는 case_num 목록 (예시 5건): {list(not_in_db_case_nums)[:5]}")
print(f"🔢 DB에 없는 case_num 개수: {len(not_in_db_case_nums)}")
