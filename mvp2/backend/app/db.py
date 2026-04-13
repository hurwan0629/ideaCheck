from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import settings

DATABASE_URL=settings.DATABASE_URL

# database connection 만들기
engine = create_engine(
  DATABASE_URL
)

# 쿼리 작업 단위
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 부모 클래스
class Base(DeclarativeBase):
  pass

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()