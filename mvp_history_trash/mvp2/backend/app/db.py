from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from contextlib import contextmanager

from .config import settings


DATABASE_URL=settings.DATABASE_URL

# database connection 만들기
engine = create_engine(
  DATABASE_URL,
  pool_size=5,
  max_overflow=10,
  pool_pre_ping=True
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

@contextmanager
def get_session():
  db = SessionLocal()
  try:
    yield db
    db.commit()
  except:
    db.rollback()
    raise
  finally:
    db.close()