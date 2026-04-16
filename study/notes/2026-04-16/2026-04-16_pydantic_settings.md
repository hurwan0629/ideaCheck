# pydantic-settings | BaseSettings / SettingsConfigDict

## 왜 쓰는가

`.env` 파일의 환경변수를 파이썬 클래스로 타입 안전하게 읽기 위해.

`os.getenv("DATABASE_URL")` 방식은 타입이 항상 `str | None`이고,
오타나 누락을 런타임 전까지 모름.

`BaseSettings`는 앱 시작 시 `.env`를 읽고 검증 → 없으면 즉시 에러.

---

## 기본 구조

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # 현재 파일 기준 상위 폴더

class Settings(BaseSettings):
    DATABASE_URL: str           # 필수 — 없으면 앱 시작 시 ValidationError
    NAVER_CLIENT_ID: str        # 필수
    NAVER_CLIENT_SECRET: str    # 필수
    DEBUG: bool = False         # 선택 — 없으면 기본값 False 사용

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )

settings = Settings()  # 이 시점에 .env 읽고 검증
```

---

## SettingsConfigDict 주요 옵션

```python
model_config = SettingsConfigDict(
    env_file=".env",               # .env 파일 경로
    env_file_encoding="utf-8",     # 인코딩 (한글 있으면 필수)
    env_prefix="APP_",             # 변수명 앞에 공통 접두사 붙이기
                                   # → APP_DATABASE_URL 로 읽힘
    case_sensitive=False,          # 대소문자 구분 (기본 False)
    extra="ignore",                # .env에 클래스에 없는 변수 있어도 무시
                                   # "forbid"로 바꾸면 에러
)
```

---

## 변수명 규칙

`.env` 파일명과 클래스 필드명은 **대소문자 무관하게** 매핑됨 (기본 설정).

```
# .env
NAVER_CLIENT_ID=abc123
```
```python
class Settings(BaseSettings):
    naver_client_id: str   # 이렇게 써도 읽힘
    NAVER_CLIENT_ID: str   # 이렇게 써도 읽힘
```

관례상 클래스 필드도 대문자로 맞추는 게 보기 좋음.

**하이픈(-) 불가** — 파이썬 변수명 규칙상 안 됨. 언더스코어(_) 사용.

```python
X-Naver-Client-Id: str   # X — 문법 오류
NAVER_CLIENT_ID: str     # O
```

---

## 사용 방법

```python
# 어디서든 import해서 바로 사용
from app.config import settings

print(settings.DATABASE_URL)
print(settings.NAVER_CLIENT_ID)
```

`settings`는 모듈 레벨에서 한 번만 생성되고 재사용됨.
Spring의 `@Value` / `@ConfigurationProperties`와 같은 역할.

---

## 설치

```bash
pip install pydantic-settings
```

`pydantic` v2 이상에서는 `pydantic-settings`가 분리된 패키지.
