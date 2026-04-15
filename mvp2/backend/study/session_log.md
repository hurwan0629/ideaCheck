# 세션 로그
> Claude와의 대화 중 의미있는 내용을 날짜별로 기록.
> 세션 종료 시 Claude가 추가. 너무 자세하게 쓰지 말고 "무엇을 다뤘는지, 뭐가 걸렸는지"만 기록.

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

## 2026-04-15 | 세션 시스템 구성

**다룬 내용**
- CLAUDE.md, my_level.md, session_log.md 세션 시스템 설계

**새로 이해한 것**
- CLAUDE.md: Claude Code가 세션 시작 시 자동으로 읽는 파일
- my_level.md + session_log.md 운영 방식

**아직 불명확한 것**
- 없음
