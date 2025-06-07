from django.db import models
from code_t.models import Code_T
from django.contrib.auth import get_user_model

User = get_user_model()

class Event(models.Model):
    event_id = models.AutoField(
        primary_key=True,
        verbose_name="사건 ID"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="사용자 번호"
    )
    e_title = models.CharField(
        max_length=100,
        verbose_name="사건명"
    )
    e_description = models.TextField(
        verbose_name="본문"
    )
    client = models.CharField(
        max_length=20,
        verbose_name="클라이언트"
    )

    # 사건 유형 (대/중/소)
    cat_cd = models.ForeignKey(
        Code_T,
        on_delete=models.SET_NULL,
        null=True,
        related_name="event_cat_cd",
        verbose_name="사건 유형(대)"
    )
    cat_02 = models.CharField(
        max_length=50,
        verbose_name="사건 유형(중)",
        null=True,
        blank=True
    )
    cat_03 = models.CharField(
        max_length=50,
        verbose_name="사건 유형(소)",
        null=True,
        blank=True
    )

    memo = models.TextField(
        null=True,
        blank=True,
        verbose_name="메모"
    )

    org_cd = models.ForeignKey(
        Code_T,
        on_delete=models.SET_NULL,
        null=True,
        related_name="event_org_cd",
        verbose_name="담당 부서"
    )

    # 상태값들
    estat_cd = models.ForeignKey(
        Code_T,
        on_delete=models.SET_NULL,
        null=True,
        related_name="event_estat_cd",
        verbose_name="의뢰 및 진행 상태"
    )
    lstat_cd = models.ForeignKey(
        Code_T,
        on_delete=models.SET_NULL,
        null=True,
        related_name="event_lstat_cd",
        verbose_name="소송 심급"
    )
    estat_num_cd = models.ForeignKey(
        Code_T,
        on_delete=models.SET_NULL,
        null=True,
        related_name="event_estat_num_cd",
        verbose_name="사건 종결 세분화"
    )

    submit_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="소송 재기일"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일"
    )
    update_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일"
    )

    class Meta:
        db_table = 'event'
        verbose_name = "사건"
        verbose_name_plural = "사건 목록"

    def __str__(self):
        return f"{self.e_title} ({self.event_id})"
