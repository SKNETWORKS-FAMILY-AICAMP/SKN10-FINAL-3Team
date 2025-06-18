from django.db import models
from django.conf import settings

class Event(models.Model):
    event_id = models.AutoField(
        primary_key=True,
        verbose_name="사건 ID"
    )
    # 실시간 연결을 위한 외래키 필드
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # 사용자가 삭제되면 이 연결은 NULL이 됨
        null=True,
        blank=True,
        verbose_name="작성자 계정"
    )
    
    # 기록 보존을 위한 스냅샷 필드
    creator_name = models.CharField(
        max_length=50, 
        null=True,
        blank=True,
        verbose_name="작성자 이름",
        help_text="사건 생성 시점의 작성자 이름(기록용)"
    )
    e_title = models.CharField(
        max_length=100,
        verbose_name="사건명"
    )
    e_description = models.TextField(
        verbose_name="사건 본문"
    )
    client = models.CharField(
        max_length=20,
        verbose_name="클라이언트"
    )
    cat_cd = models.CharField(
        max_length=20,
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

    org_cd = models.CharField(
        max_length=20,
        verbose_name="담당 부서",
        null=True,
        blank=True
    )

    estat_cd = models.CharField(
        max_length=20,
        verbose_name="의뢰 및 진행 상태"
    )
    lstat_cd = models.CharField(
        max_length=20,
        null=True,
        verbose_name="심급"
    )
    estat_num_cd = models.CharField(
        max_length=20,
        verbose_name="종결 세분화",
        null=True,
        blank=True
    )

    submit_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="소송 재기일"
    )
    created_at = models.DateTimeField(
        # 객체가 처음 생성될 때 해당 필드에 자동으로 현재 시각(timezone.now())을 저장
        # auto_now_add=True,
        verbose_name="생성일"
    )
    update_at = models.DateTimeField(
        # 객체가 저장될 때마다 해당 필드에 자동으로 현재 시각을 업데이트
        # auto_now=True,
        verbose_name="수정일"
    )

    class Meta:
        db_table = 'event'
        verbose_name = "사건"
        verbose_name_plural = "사건 목록"

    def __str__(self):
        return f"{self.e_title} ({self.event_id})"
