from django.db import models

class Case(models.Model):
    # 1. 판례 ID
    case_id = models.AutoField(
        primary_key=True,
        verbose_name="판례 ID"
    )

    # 2. 사건 번호, 법원명, 사건명, 선고일자
    case_num = models.TextField(
        verbose_name="사건 번호"
    )
    court_name = models.CharField(
        max_length=50,
        verbose_name="법원명"
    )
    case_name = models.TextField(
        verbose_name="사건명"
    )
    case_at = models.DateTimeField(
        verbose_name="선고일자"
    )

    # 3. 참조 판례, 참조 조문 (nullable)
    refer_cases = models.TextField(
        null=True, blank=True,
        verbose_name="참조 판례"
    )
    refer_statutes = models.TextField(
        null=True, blank=True,
        verbose_name="참조 조문"
    )

    # 4. 판결요지, 판례내용, 판시사항, 판례결과
    decision_summary = models.TextField(
        verbose_name="판결요지"
    )
    case_full = models.TextField(
        verbose_name="판례내용"
    )
    decision_issue = models.TextField(
        verbose_name="판시사항"
    )
    case_result = models.CharField(
        max_length=60,
        verbose_name="판례결과"
    )

    # 5. 사실관계 요약, 사실관계 키워드
    facts_summary = models.TextField(
        verbose_name="사실관계 요약"
    )
    facts_keywords = models.CharField(
        max_length=200,
        verbose_name="사실관계 키워드"
    )

    # 6. 쟁점 요약, 쟁점 키워드
    issue_summary = models.TextField(
        verbose_name="쟁점 요약"
    )
    issue_keywords = models.CharField(
        max_length=210,
        verbose_name="쟁점 키워드"
    )

    # 7. 키워드
    keywords = models.TextField(
        verbose_name="키워드"
    )

    class Meta:
        db_table = 'case'
        verbose_name = "판례"
        verbose_name_plural = "판례 목록"

    def __str__(self):
        return f"{self.case_num} - {self.case_name[:20]}"
