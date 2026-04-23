from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend 폴더

class Settings(BaseSettings):
  DATABASE_URL: str
  NAVER_CLIENT_ID: str
  NAVER_CLIENT_SECRET: str
  ANTHROPIC_API_KEY: str = ""
  OPENAI_API_KEY: str


  # .env 파일 읽기
  model_config = SettingsConfigDict(
    env_file=BASE_DIR / ".env",
    env_file_encoding="utf-8"
  )

# 기본 public 공개 -> 바로 사용 가능
settings=Settings()