from common.core.config import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, MappedAsDataclass


class Base(DeclarativeBase, MappedAsDataclass):
  pass

engine = create_engine(
  settings.DATABASE_URL,
  echo=True # 쿼리 확인용
)

SessionLocal = sessionmaker(
  bind=engine,
  autocommit=False,
  autoflush=False
)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()