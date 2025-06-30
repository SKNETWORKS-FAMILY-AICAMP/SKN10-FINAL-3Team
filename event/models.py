from django.db import models
from django.conf import settings

class Event(models.Model):
    event_id = models.AutoField(
        primary_key=True,
        verbose_name="사건 ID"
    )

    # 1. 실시간 연결 필드 (필수)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="작성자 계정"
    )

    # 2. 기록용 작성자 이름 (필수)
    creator_name = models.CharField(
        max_length=50,
        verbose_name="작성자 이름",
        help_text="사건 생성 시점의 작성자 이름(기록용)"
    )
    
    event_num = models.CharField(
        max_length=60,
        null=True,
        blank=True,
        verbose_name="사건 번호"
    )

    # 3. 사건 기본 정보 (필수)
    e_title = models.CharField(
        max_length=100,
        verbose_name="사건명"
    )
    e_description = models.TextField(
        verbose_name="사건 본문"
    )
    claim_summary = models.TextField(
        verbose_name="청구 내용",
        help_text="청구 취지 및 청구 원인을 요약한 문장 (예: 불법행위에 따른 손해배상 청구)"
    )
    client = models.CharField(
        max_length=20,
        verbose_name="클라이언트"
    )
    client_role = models.CharField(
        max_length=10,
        verbose_name="클라이언트 역할",
        help_text="예: 원고, 피고"
    )
    # 4. 사건 유형 (필수)
    cat_cd = models.CharField(
        max_length=20,
        verbose_name="사건 유형"
    )
    cat_02 = models.CharField(
        max_length=100,
        verbose_name="세부 유형"
    )

    # 5. 담당 부서 (필수)
    org_cd = models.CharField(
        max_length=20,
        verbose_name="담당 부서"
    )

    # 6. 사건 상태 (진행상태는 필수)
    estat_cd = models.CharField(
        max_length=20,
        verbose_name="의뢰 및 진행 상태"
    )
    lstat_cd = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="심급"
    )
    estat_num_cd = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="종결 세분화"
    )

    # 7. 부가 정보 (선택적)
    memo = models.TextField(
        null=True,
        blank=True,
        verbose_name="메모"
    )
    event_file = models.TextField(
        null=True,
        blank=True,
        verbose_name="증거자료"
    )
    submit_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="소송 제기일"
    )
    
    ai_strategy = models.TextField(
        null=True,
        blank=True,
        default='미지정',
        verbose_name="ai 추천 전략"
    )

    # 8. 자동 생성 필드
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