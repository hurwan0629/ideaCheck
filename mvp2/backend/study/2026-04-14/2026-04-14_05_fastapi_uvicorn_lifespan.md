# 05. FastAPI + Uvicorn 구조와 lifespan
> 학습 목표: FastAPI가 어떻게 실행되는지 구조를 이해하고, 앱 생명주기를 올바르게 관리한다.
> 선행 학습: 01, 02, 03

---

## 0. 왜 알아야 하나

구조를 모르면:
- 스케줄러를 잘못된 시점에 시작시켜 이벤트 루프 충돌
- `async def` vs `def` 라우터 선택을 감으로 결정
- 앱 종료 시 리소스 정리가 안 됨

---

## 1. ASGI — FastAPI와 Uvicorn의 계약

**ASGI (Asynchronous Server Gateway Interface)**:
서버(Uvicorn)와 앱(FastAPI)이 통신하는 인터페이스 규약.
Python의 웹 표준. 톰캣-서블릿 규약과 동일한 개념.

```
[클라이언트]
    ↓ HTTP 요청
[Uvicorn]  ← ASGI 서버. 소켓 관리, 이벤트 루프 생성, HTTP 파싱
    ↓ ASGI 인터페이스 (scope, receive, send)
[FastAPI]  ← ASGI 앱. 라우팅, 의존성 주입, 응답 생성
    ↓
[라우터 함수]
```

---

## 2. Uvicorn 시작 흐름

```
uvicorn app.main:app 실행

  1. asyncio 이벤트 루프 생성
  2. TCP 소켓 열기 (0.0.0.0:8000)
  3. FastAPI 앱의 lifespan 실행 (yield 이전)
  4. 루프 시작 (while True)

  루프 동작:
    소켓에서 새 연결 → 코루틴으로 처리 (non-blocking)
    HTTP 요청 파싱 → FastAPI에 전달
    FastAPI가 라우터 실행 → 응답 반환
    소켓으로 응답 전송

  종료 신호 (Ctrl+C):
  5. lifespan yield 이후 코드 실행
  6. 루프 종료
  7. 미완료 Task 취소
```

---

## 3. async def vs def 라우터 — 내부 처리 차이

### async def 라우터

```python
@app.get("/async")
async def async_route():
    result = await db.execute(query)
    return result
```

처리 흐름:
```
요청 도착 → 이벤트 루프가 직접 코루틴 실행
await 만날 때마다 다른 요청 처리 가능
```

### def 라우터

```python
@app.get("/sync")
def sync_route():
    result = db.execute(query)   # 블로킹 코드
    return result
```

처리 흐름:
```
요청 도착 → FastAPI가 anyio 스레드풀에 제출
           (이벤트 루프는 자유로움)
스레드풀 워커가 sync_route 실행 (블로킹이어도 OK)
완료되면 이벤트 루프에 결과 반환
```

**FastAPI가 def를 스레드풀에 넣어주는 이유:**
동기 라이브러리(동기 SQLAlchemy, requests 등)도 안전하게 사용 가능하도록.

### 선택 기준

```
라우터 함수 안에 async 라이브러리를 쓰는가?
  YES (httpx, aiofiles 등) → async def

동기 라이브러리만 쓰는가?
  YES (동기 SQLAlchemy, requests 등) → def (스레드풀 혜택)

async def 안에 동기 라이브러리를?
  → 이벤트 루프 블로킹 → 피해야 함
```

---

## 4. asynccontextmanager와 yield 원리

02에서 코루틴이 yield로 제어권을 반환한다고 했다.
`@asynccontextmanager`는 이것을 활용해 `async with` 문을 만든다.

### contextlib.asynccontextmanager 동작

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def my_context():
    print("진입")     # __aenter__ 역할
    yield "리소스"    # with 블록에 값 전달, 블록 실행 동안 여기서 대기
    print("종료")     # __aexit__ 역할

# 사용
async with my_context() as resource:
    print(f"사용 중: {resource}")

# 출력:
# 진입
# 사용 중: 리소스
# 종료
```

`yield` 기준으로 나뉜다:
- `yield` 이전 = `__aenter__`: `async with` 블록 진입 시 실행
- `yield` 이후 = `__aexit__`: `async with` 블록 종료 시 실행 (에러가 나도 실행)

### try/finally와 연결

```python
@asynccontextmanager
async def safe_context():
    resource = await setup()
    try:
        yield resource
    finally:
        await cleanup()  # 에러로 종료되어도 반드시 실행
```

Spring의 `@PreDestroy`나 Java의 try-with-resources와 동일한 보장.

---

## 5. FastAPI lifespan 완전 이해

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.collector.scheduler import scheduler, setup_scheduler
from app.db import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── yield 이전: 앱 시작 준비 ──────────────────────────
    # 이 시점: Uvicorn이 이벤트 루프를 만들었고, FastAPI가 올라오기 직전
    # → 이벤트 루프가 확실히 살아있음 → AsyncIOScheduler.start() 안전

    Base.metadata.create_all(engine)  # 테이블 생성 (동기 OK, 빠른 작업)
    setup_scheduler()                  # 잡 등록 (실행 안 함)
    scheduler.start()                  # 이벤트 루프에 스케줄러 붙이기

    # ── yield: FastAPI 앱 실행 ────────────────────────────
    yield
    # HTTP 요청 처리 중 (이 라인은 종료 신호 전까지 넘어오지 않음)

    # ── yield 이후: 앱 종료 정리 ─────────────────────────
    scheduler.shutdown()               # 스케줄러 정리

app = FastAPI(lifespan=lifespan)
```

### 왜 scheduler.start()를 lifespan 안에서 해야 하나

```
잘못된 방법: 모듈 최상단
  scheduler = AsyncIOScheduler()
  scheduler.start()   # ← 이 시점에 이벤트 루프가 없음
                      # APScheduler가 자체 스레드에 루프를 만듦
                      # FastAPI 루프와 별개 루프 2개 → 충돌 가능

올바른 방법: lifespan yield 이전
  이미 Uvicorn이 만든 루프가 살아있음
  scheduler.start() → 그 루프에 붙음
  이후 스케줄러 잡이 FastAPI 루프에서 실행 → 안전
```

---

## 6. 현재 main.py와의 차이

```python
# 현재 (문제 있음)
@app.on_event("startup")    # deprecated
def on_startup():           # 동기 함수
    Base.metadata.create_all(engine)

# 개선 버전
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    setup_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
```

`on_event("startup")`은 FastAPI에서 deprecated됐고,
`lifespan`이 공식 권장 방식이다.

---

## 이해도 측정

### 개념 문항

**C1.** `def` 라우터가 이벤트 루프를 블로킹하지 않는 이유를 설명해봐요.

```
답: 별도 스레드풀에서 동작해서
```

**C2.** `async def` 라우터 안에서 동기 SQLAlchemy를 쓰면 안 되는 이유가 뭔가요?
그리고 `def` 라우터 안에서 동기 SQLAlchemy를 쓰는 건 왜 괜찮은가요?

```
답: asyncio의 이벤트루프를 블로킹해서
```

**C3.** lifespan의 yield 이전/이후가 각각 실행되는 시점을 설명해봐요.

```
답: 이거 잘 이해를 못했는데 yield가 등록된 작업들 수행하는 시점이고 이전은 서버가 시작될 때, 이후는 서버가 종료될 때.
(Base.metadata.create(engine)같은것도 따로 하라는 이유가 잘 이해를 못했달까 기존에 쓰던 방식이 FastAPI의 start 타이밍에 하는거이고 lifespan사용하는게 uvicorn 생명주기를 기준으로 동작하는건가?)
```

---

### 코드 감각 문항

**P1.** 아래 코드의 실행 순서를 맞춰봐요.

```python
@asynccontextmanager
async def lifespan(app):
    print("A")
    yield
    print("B")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    print("C")
    return {}
```

앱 시작 → GET / 요청 1회 → 앱 종료 시 출력 순서:

```
답: app=FastAPI() -> print(A)->C->(서버 종료시)B
```

**P2.** 아래 두 라우터 중 DB 쿼리 응답이 0.5초 걸릴 때, 동시에 100개 요청이 오면 어떻게 다르게 동작하나요?

```python
@app.get("/a")
async def route_a():
    result = sync_db.execute(query)   # 동기 SQLAlchemy 0.5초
    return result

@app.get("/b")
def route_b():
    result = sync_db.execute(query)   # 동기 SQLAlchemy 0.5초
    return result
```

```
답: /b는 스레드풀에 있을 수 있는 스레드 개수만큼 반비례해서 속도가 줄어드는데 a는 이벤트루프로 하나씩 해서 결국 50초 걸림
```

**P3.** 아래 lifespan 코드에서 앱이 에러로 비정상 종료될 때 scheduler.shutdown()이 실행되지 않습니다. try/finally를 써서 항상 실행되도록 고쳐봐요.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()
```

```python
# 수정 후:
@asynccontextmanager
async def lifespan(app: FastAPI):
```

```
답:
  scheduler.start()
  try:
    yield
  finally:
    scheduler.shutdown()
```

---

## 채점 결과

**전체 점수: 80/100**

### 개념 문항 (C1~C3): 21/30

**C1 — 80점**
핵심은 잡았는데 한 문장으로 너무 짧음. "anyio 스레드풀에서 실행되므로 이벤트 루프 스레드와 별개의 스레드에서 동작"까지 나오면 100점.

**C2 — 60점**
첫 번째 질문(async def에서 왜 안 되나)만 답함. **두 번째 질문(def에서 왜 괜찮나)에 대한 답이 없음.**
> def 라우터는 스레드풀에서 실행되므로 이벤트 루프와 별개 → 이벤트 루프 블로킹 없음

**C3 — 70점**
"이전 = 시작, 이후 = 종료" 타이밍은 맞음. 근데 "yield가 등록된 작업들 수행하는 시점"은 틀림.
> yield는 **FastAPI가 HTTP 요청을 처리하는 동안** 여기서 멈춰 있는 것.
> 등록된 작업 수행이 아니라 "앱 실행 중 상태를 유지하는 구간"

의문으로 남긴 부분:
> on_event startup → FastAPI 내부 타이밍
> lifespan → Uvicorn이 이벤트 루프 만든 직후 타이밍
> 즉 lifespan이 더 이른 시점이고 scheduler.start()처럼 이벤트 루프가 필요한 작업은 lifespan에서만 안전하게 동작함

---

### 코드 문항 (P1~P3): 59/70

**P1 — 85점**
순서 A → C → B 맞음. `app=FastAPI()`를 출력 순서에 포함시킨 건 어색하지만 핵심은 정확.

**P2 — 80점**
`/a` 50초는 정확. `/b` 설명에서 "반비례해서 속도가 줄어드는데" 표현이 약간 어색함.
> `/b`: anyio 스레드풀 기본값 약 40개 → 40개씩 묶어서 병렬 처리
> 100개 요청 / 40 스레드 × 0.5초 ≈ **약 1.5초**
> `/a`: 이벤트 루프 블로킹 → 순차 → **50초**

**P3 — 100점**
정확함.

---

### 총평

4번보다 이해도가 높아진 게 보임. 특히 lifespan 흐름, async def vs def 선택 기준, try/finally 패턴 모두 잘 잡힘.

**약한 부분 하나**: C3에서 `yield`의 역할 — "등록된 작업 수행"이 아니라 "앱 실행 중 상태 유지 구간"이라는 감각을 한번 더 짚고 가면 좋겠어.
