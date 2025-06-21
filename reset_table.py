# scripts/reset_case_table.py
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from case.models import Case
from django.db import connection

print("⚠️ 모든 데이터를 삭제하고 AUTO_INCREMENT를 초기화합니다.")
Case.objects.all().delete()

with connection.cursor() as cursor:
    cursor.execute("ALTER TABLE `case` AUTO_INCREMENT = 1")

print("✅ 초기화 완료")
