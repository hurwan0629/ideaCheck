# 2026-04-15 | SQLAlchemy 세션 관리 + FastAPI DI + pgvector 학습 계획

> 목표: collector jobs에서 DB를 실제로 읽고 쓰기 위한 세션 패턴 이해
> + FastAPI의 의존성 주입 방식 이해 (Spring Boot는 알지만 FastAPI는 새로움)
> + pgvector 실제 사용법

---

## 왜 이걸 알아야 하나

collector의 `daily_job`, `quarterly_job`이 DB에 접근하려면 세션이 필요하다.
FastAPI의 `Depends(get_db)` 방식은 HTTP 요청 흐름에서만 작동한다.
collector는 스케줄러(스레드)에서 실행되므로 직접 세션을 열고 닫는 패턴이 필요하다.
→ FastAPI DI가 내부에서 뭘 하는지 알아야, collector에서 "없이 쓰는 방법"도 판단할 수 있다.

---

## 학습 순서

### 01. SQLAlchemy 기본 구조
파일: `2026-04-15_01_sqlalchemy_basics.md`

- Engine이란 뭔가 (DB 커넥션 풀)
- Session이란 뭔가 (작업 단위, UnitOfWork)
- Engine → SessionFactory → Session 생성 흐름
- Spring의 DataSource / EntityManager와 비교

---

### 02. SessionLocal + 트랜잭션
파일: `2026-04-15_02_session_transaction.md`

- `SessionLocal = sessionmaker(bind=engine)` 의미
- `db = SessionLocal()` / `db.close()` 수동 관리
- `with SessionLocal() as db:` 컨텍스트 매니저 방식
- `db.add()` / `db.commit()` / `db.rollback()` / `db.close()` 각 역할
- 왜 finally에서 close() 해야 하나 (커넥션 풀 반납)
- Spring @Transactional과 비교

---

### 03. FastAPI 의존성 주입 (Depends)
파일: `2026-04-15_03_fastapi_depends.md`

- Spring Boot DI(@Autowired, @Bean)와 뭐가 다른가
- `Depends()`의 동작 방식 — 요청마다 실행되는 함수
- 의존성 체인: `Depends`가 `Depends`를 받는 경우
- 스코프: Spring의 @RequestScope와 유사한 개념
- Generator 함수(`yield`)를 Depends에 쓰는 이유 (try-finally 보장)
- `Depends`로 주입받은 값이 어떻게 라우터 함수 파라미터에 들어오나

---

### 04. get_db() 패턴 — Depends + SessionLocal의 결합
파일: `2026-04-15_04_get_db.md`

- `get_db()` 전체 흐름:
  ```python
  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()
  ```
- 왜 yield인가 (응답 반환 후에도 finally 실행됨)
- `Depends(get_db)`가 라우터 파라미터로 들어오는 순간 무슨 일이 일어나나
- collector처럼 Depends 없는 환경에서 동일 패턴 재현하는 법

---

### 05. 실제 쿼리 패턴
파일: `2026-04-15_05_query_patterns.md`

- `db.query(Model).filter(...).first()` / `.all()`
- `db.add(instance)` INSERT
- UPDATE: 객체 가져와서 필드 수정 후 commit
- DELETE: `db.delete(instance)`
- 우리 프로젝트에서 쓸 패턴들 (뉴스 저장, 정책 INSERT 등)

---

### 06. collector에 적용
파일: `2026-04-15_06_apply_to_collector.md`

- `jobs/daily.py`에서 세션 여는 패턴 결정
- 함수마다 세션 열지 vs job 시작에서 하나 열지 → 트레이드오프
- `processors/`에 세션 전달하는 방식
- 실제 코드 작성

---

### 07. pgvector 실제 사용
파일: `2026-04-15_07_pgvector.md`

- pgvector 컬럼 타입 (`Vector(1536)`)
- SQLAlchemy 모델에서 pgvector 타입 선언하는 법
- 임베딩 생성 흐름: 텍스트 → OpenAI embedding API → `list[float]`
- 임베딩 저장: `db.add()` + commit
- 유사도 검색 쿼리 (`<->` 연산자, cosine distance)
- RAG 흐름에서 Top-K 뽑아서 Claude 컨텍스트에 넣는 패턴

---

## 오늘 세션 끝나면 체크
- [ ] 01 완료
- [ ] 02 완료
- [ ] 03 완료
- [ ] 04 완료
- [ ] 05 완료
- [ ] 06 완료 (collector에 실제 적용)
- [ ] 07 완료 (pgvector)
