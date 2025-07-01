from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

# RDB 테이블
## Event 테이블
class Event(Base):
    __tablename__ = 'event'

    event_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    # 사건 기본 정보
    e_description = Column(Text, nullable=False)
    claim_summary = Column(Text, nullable=False)
    client_role = Column(String(10), nullable=False)
    event_file = Column(Text, nullable=True)

    # AI 전략
    ai_strategy = Column(Text, nullable=True, default='미지정')

    # 생성/수정 시간
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    update_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)