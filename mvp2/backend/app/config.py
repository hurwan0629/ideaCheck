from pydantic_settings import BaseSettings, SettingsConfigDict

print("config.Settings 실행됨")

class Settings(BaseSettings):
  DATABASE_URL: str



  # .env 파일 읽기
  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8"
  )

# 기본 public 공개 -> 바로 사용 가능
settings=Settings()