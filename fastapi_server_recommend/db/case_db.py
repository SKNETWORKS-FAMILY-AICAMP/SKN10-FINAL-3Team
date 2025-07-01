from sqlalchemy import Column, Integer, Text, DateTime
from database import Base

class Case(Base):
    __tablename__ = 'case'

    case_id = Column(Integer, primary_key=True, autoincrement=True, index=True) # 고유ID값
    case_num = Column(Text, nullable=False)                                     # 사건번호
    court_name = Column(Text, nullable=False)                                   # 법원명
    case_at = Column(DateTime(timezone=True), nullable=False)                   # 선고일자
    refer_case = Column(Text, nullable=True)                                    # 참조판례
    refer_statutes = Column(Text, nullable=True)                                # 참조법령
    decision_summary = Column(Text, nullable=True)                              # 판결요지
    case_full = Column(Text, nullable=False)                                    # 판례내용
    decision_issue = Column(Text, nullable=False)                               # 판시사항
    case_result = Column(Text, nullable=False)                                  # 판례결과
    facts_summary = Column(Text, nullable=False)                                # 사실관계 요약
    facts_keywords = Column(Text, nullable=False)                               # 사실관계 키워드
    issue_summary = Column(Text, nullable=False)                                # 쟁점 요약
    issue_keywords = Column(Text, nullable=False)                               # 쟁점 키워드
    keywords = Column(Text, nullable=False)         