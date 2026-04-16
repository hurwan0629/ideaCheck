# 세션 로그
> Claude와의 대화 중 의미있는 내용을 날짜별로 기록.
> 세션 종료 시 Claude가 추가. 너무 자세하게 쓰지 말고 "무엇을 다뤘는지, 뭐가 걸렸는지"만 기록.

---

## 2026-04-16 | competitor_crawler 설계 및 구현

**다룬 내용**
- httpx.Client vs 브라우저 차이 (User-Agent, TLS fingerprint, 봇 차단 단계)
- JS 필요 여부 자동 감지 방법 (SPA 패턴 heuristic vs AI 판단 비교)
- 크롤링 데이터 AI 추출 설계 (HTML 전체 vs body 텍스트만, 한 번 호출로 통합)
- SQLAlchemy 변경 감지(dirty tracking) — 필드만 바꾸면 commit 시 자동 UPDATE

**새로 이해한 것**
- httpx는 TLS fingerprint도 Python 고유값이라 User-Agent 속여도 강한 봇 차단은 뚫기 어려움
- Playwright headless도 `navigator.webdriver` 플래그로 감지 가능 → `--disable-blink-features=AutomationControlled` 로 숨김
- AI type 추출 시 고정 카테고리를 프롬프트에 명시하지 않으면 매번 다른 값이 나옴

**아직 불명확한 것**
- Cloudflare Enterprise 수준 차단 시 현실적인 대안 (공식 API 외엔 사실상 없음)

---

## 2026-04-14 | asyncio + APScheduler + collector 라이브러리

**다룬 내용**
- asyncio 이벤트 루프 원리 (협력적 멀티태스킹, await가 하는 일)
- WebFlux vs asyncio 비교표 정리
- asyncio.gather() 동작 방식 (순차 vs 동시 실행)
- FastAPI + Uvicorn 구조, lifespan 패턴
- APScheduler: AsyncIOScheduler가 이벤트 루프에 붙는 방식, Task vs Coroutine
- collector 라이브러리 전체: httpx, BeautifulSoup, Playwright, Claude API, pgvector, hashlib, set

**새로 이해한 것**
- asyncio.gather() → 순차 4초 vs 동시 2초 차이
- lifespan의 yield 기준 시작/종료 구조 (try-finally처럼)
- APScheduler가 ensure_future()로 잡을 Task로 등록하는 내부 방식
- replace_existing=True = 중복 잡 방지 (misfire_grace_time은 별개)
- pgvector / RAG 개념 흐름 (임베딩 → 유사도 검색 → Top-K만 Claude에 전달)

**아직 불명확한 것**
- SQLAlchemy 실제 세션 관리 (get_db() 주입 방식)
- asyncpg / AsyncSession 전환 시 실제 코드

---

## 2026-04-15 | SQLAlchemy 세션 관리 + FastAPI DI + pgvector

**다룬 내용**
- SQLAlchemy Engine / Session / SessionLocal 구조 (Spring DataSource/EntityManager 비교)
- 트랜잭션 관리 (commit/rollback/close 순서, finally 이유)
- FastAPI Depends 의존성 주입 — Spring DI와의 차이, yield 사용 이유
- get_db() 패턴 전체 흐름 (Depends + SessionLocal 결합)
- collector에서 Depends 없이 세션 직접 관리하는 방식
- 실제 쿼리 패턴 (SELECT/INSERT/UPDATE/flush)
- pgvector: 컬럼 선언, 임베딩 저장, cosine distance 검색, RAG 흐름

**새로 이해한 것**
- FastAPI Depends는 컨테이너가 없고, 요청마다 함수를 직접 실행하는 방식
- yield Depends = Spring AOP의 @Transactional처럼 전후 코드 분리
- collector는 get_db() 안의 로직(SessionLocal + try/finally)을 직접 재현하면 됨
- 단계마다 세션을 따로 여는 이유 — 뉴스/정책/트렌드 실패 전파 방지
- db.flush() — commit 전에 id 확보할 때 (외래키 연결에 필요)
- pgvector cosine_distance() — 텍스트 유사도에 적합한 이유 (방향만 비교)

**아직 불명확한 것**
- asyncpg / AsyncSession (async 전환 시 실제 코드, 현 프로젝트는 sync라 일단 보류)

---

## 2026-04-16 | 환경 세팅 & 서버 첫 실행

**다룬 내용**
- pydantic-settings로 .env 읽기 (BaseSettings, alias, env_file)
- 네이버 검색 API 구조 (검색 권한 하나로 뉴스/블로그 등 전부 커버)
- Playwright 설치 구조 (pip + playwright install 두 단계 필요한 이유)
- venv 경로 하드코딩 문제 (폴더 이름 바꾸면 재생성 필요)
- `get_session()` contextmanager — 예외 시 rollback 동작 확인 (crawl_trends 버그로 실제 체험)

**새로 이해한 것**
- pydantic-settings는 FastAPI 없이 단독 사용 가능한 독립 라이브러리
- Python 변수명에 하이픈 불가 → Field(alias=) 로 우회
- Playwright는 Python 바인딩 + Node.js 서버 + 브라우저 프로세스 3계층 구조
- `with get_session()` 안에서 예외 나면 그 안의 모든 저장이 rollback됨 → 트랜잭션 범위 설계 중요

**아직 불명확한 것**
- Google Trends pytrends 한국 IP 차단 해결 방법

---

## 2026-04-15 | 세션 시스템 구성

**다룬 내용**
- CLAUDE.md, my_level.md, session_log.md 세션 시스템 설계

**새로 이해한 것**
- CLAUDE.md: Claude Code가 세션 시작 시 자동으로 읽는 파일
- my_level.md + session_log.md 운영 방식

**아직 불명확한 것**
- 없음
