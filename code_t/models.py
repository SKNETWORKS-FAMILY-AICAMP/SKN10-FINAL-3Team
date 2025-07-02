# code_t/models.py
from django.db import models

class Code_T(models.Model):
    code = models.CharField(
        max_length=20,
        primary_key=True,
        verbose_name="코드"
    )
    code_label = models.CharField(
        max_length=50,
        verbose_name="코드 이름"
    )
    code_desc = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="코드 설명"
    )
    upper_code = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='upper_code',
        related_name='sub_codes',
        verbose_name="상위 코드"
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="설명"
    )

    class Meta:
        db_table = 'code_t'
        verbose_name = "공통 코드"
        verbose_name_plural = "공통 코드 목록"

    def __str__(self):
        return f"[{self.code}] {self.code_label}"