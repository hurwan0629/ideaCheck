# 기술 수준 현황
> 마지막 업데이트: 2026-04-14
> 이 파일은 세션마다 업데이트. 새로 이해한 건 "알고 있는 것"으로, 여전히 모르면 "gaps" 유지.

---

## 영역별 수준

| 영역 | 수준 | 비고 |
|------|------|------|
| CS 기초 (동시성/병렬성/스레드) | 탄탄 | 설명 생략해도 됨 |
| 블로킹 개념 | 방향은 맞음 | I/O에만 한정하는 경향 있음 (CPU도 블로킹임) |
| asyncio 이벤트 루프 원리 | 이해함 | "대기 시간이 없어진다" → "겹쳐서 활용한다"로 수정 완료 |
| asyncio API (gather, create_task 등) | 학습 완료 | 2026-04-14 study_scheduler 파일에서 정리 |
| FastAPI 구조 | 비유 수준 → 이해 진행 중 | Uvicorn=톰캣 이해, 이벤트 루프 연결 구조 파악 |
| lifespan / asynccontextmanager | 이해함 | yield 기준 시작/종료 구조 파악 |
| APScheduler | 학습 완료 | AsyncIOScheduler, CronTrigger, replace_existing 이해 |
| SQLAlchemy (동기) | 기초 | 동기 vs 비동기 엔진 차이 파악, 실제 사용은 아직 |
| 설계 판단력 | 좋음 | 실용적 사고 가능, 구조적 판단 잘 함 |
| WebFlux 경험 | 개념 수준 | 개념 공부 + 간단 예제, 실무 경험 없음 |

---

## 잘 이해하고 있는 것

- 동시성(스위칭) vs 병렬성(코어 병렬)
- 스레드는 힙 공유, 프로세스는 독립 메모리
- `async def` 안에서 `time.sleep()` = 블로킹 문제 즉시 파악
- `async def` vs `def` in FastAPI 처리 방식 (스프링 스레드풀 비유로 이해)
- Uvicorn = 톰캣 역할
- `route_a` (async + 동기 SQLAlchemy) = 이벤트 루프 블로킹
- 코루틴 = Promise 유추, 미실행 객체 반환
- CPU 작업에 `run_in_executor` 선택 이유
- `set` 사용 이유 (중복 제거, O(1) 조회)
- asyncio.gather() 동작 원리 (순차 vs 동시 실행 시간 차이)
- lifespan 패턴 (`yield` 기준 시작/종료)
- APScheduler 이벤트 루프 연결 방식
- replace_existing=True 의미 (중복 잡 방지)
- httpx / BeautifulSoup / Playwright 각 역할과 선택 기준
- pgvector / RAG 개념 (벡터 유사도 검색)

---

## 현재 Gaps (아직 불명확한 것)

- SQLAlchemy 실제 세션 관리 (`get_db()` 주입 방식 미경험)
- asyncpg / AsyncSession 실제 사용
- 임베딩 API 연동 (OpenAI embedding API)
- pgvector 실제 쿼리 작성

---

## 최근 학습 이력

| 날짜 | 내용 |
|------|------|
| 2026-04-14 | collector 라이브러리 전체 정리 (httpx, BS4, Playwright, Claude API, pgvector, APScheduler) |
| 2026-04-14 | asyncio 이벤트 루프 원리, FastAPI+Uvicorn 구조, 설계 미스 패턴 정리 |
