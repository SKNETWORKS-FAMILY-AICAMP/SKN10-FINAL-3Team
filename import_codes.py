# import_codes.py

import os
import django
import pandas as pd

# Django 설정 불러오기
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # 프로젝트 이름으로 수정
django.setup()

from code_t.models import Code_T  # code_t 앱의 Code 모델 임포트

# CSV 파일 경로
csv_file = 'data/code_table_data.csv'

# CSV 읽기
df = pd.read_csv(csv_file, encoding='utf-8-sig')

# 저장
for _, row in df.iterrows():
    code = row['code']
    code_label = row['code_label']
    code_desc = row.get('code_desc', None)
    upper_code = row.get('upper_code', None)
    description = row.get('description', None)

    # 상위 코드가 있는 경우 객체 참조
    upper_code_obj = None
    if pd.notna(upper_code):
        try:
            upper_code_obj = Code_T.objects.get(code=upper_code)
        except Code_T.DoesNotExist:
            print(f"⚠️ 상위 코드 {upper_code}가 존재하지 않음. 무시하고 진행.")

    # 중복 여부 확인 후 저장
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