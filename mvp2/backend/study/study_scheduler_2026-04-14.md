# 비동기 처리 & 스케줄링 원리 학습
> 2026-04-14 | 목표: 동작 원리를 충분히 알아서 설계 미스, 충돌, 블로킹 버그를 사전에 방지

---

## 목차
1. [Python asyncio 이벤트 루프 — 핵심 원리](#1-python-asyncio-이벤트-루프--핵심-원리)
2. [WebFlux(Project Reactor)와 비교](#2-webfluxproject-reactor와-비교)
3. [async / await 가 실제로 하는 일](#3-async--await-가-실제로-하는-일)
4. [FastAPI + Uvicorn 구조](#4-fastapi--uvicorn-구조)
5. [APScheduler가 이벤트 루프에 붙는 방식](#5-apscheduler가-이벤트-루프에-붙는-방식)
6. [이 프로젝트의 전체 흐름 (코드 기준)](#6-이-프로젝트의-전체-흐름-코드-기준)
7. [설계 미스 / 충돌 패턴 — 주의해야 할 것들](#7-설계-미스--충돌-패턴--주의해야-할-것들)
8. [정리: 언제 무엇을 쓰는가](#8-정리-언제-무엇을-쓰는가)

---

## 1. Python asyncio 이벤트 루프 — 핵심 원리

### 한 줄 요약
> **스레드 1개**가 루프를 돌면서, 지금 당장 진행 가능한 작업을 골라서 실행한다.

### 이벤트 루프란?

```
[이벤트 루프] ← 단일 스레드로 동작하는 "작업 선택기"

  루프가 한 번 돌 때마다:
    1. 실행 대기 중인 코루틴 목록을 확인
    2. I/O 완료 신호(소켓, 파일, 타이머) 확인
    3. 실행 가능한 것을 하나 골라서 실행
    4. 그 코루틴이 await를 만나면 → 제어권 반환 → 다음 코루틴 실행
    5. 반복
```

### 핵심 단어: "협력적 멀티태스킹 (Cooperative Multitasking)"

OS가 강제로 스레드를 중단시키는 **선점형(Preemptive)** 멀티태스킹과 달리,
asyncio는 **각 코루틴이 스스로 `await`에서 제어권을 내놓는** 방식.

```
선점형 (OS 스레드):  OS가 강제로 "너 잠깐 멈춰" → 다른 스레드 실행
협력적 (asyncio):   코루틴이 스스로 "나 잠깐 기다릴게 (await)" → 다른 코루틴 실행
```

**결론:** `await`를 안 쓰는 코드가 오래 걸리면 → 루프 전체가 그 동안 멈춘다 (Blocking).

---

### 이벤트 루프가 실제로 하는 것 — 타임라인

```
시간 →

코루틴 A: [실행중]→[await httpx.get]→...기다림...→[재개]→[완료]
코루틴 B:            [실행중]→[await httpx.get]→...기다림...→[재개]→[완료]
코루틴 C:                        [실행중]→[await claude.create]→.........→[재개]→[완료]

이벤트루프: A실행→A가 await에서 양보→B실행→B가 await에서 양보→C실행→C양보→A응답옴→A재개→...
```

A, B, C가 **동시에 실행되는 것처럼 보이지만** 실제로는 **스레드 1개가 번갈아 실행**.
진짜 병렬(parallelism)이 아니라 **동시성(concurrency)**.

---

### asyncio vs 스레드 vs 프로세스

| | asyncio | 멀티스레드 | 멀티프로세스 |
|---|---|---|---|
| 스레드 수 | 1개 | 여러 개 | 여러 개 |
| 병렬 실행 | X (동시성) | 제한적 (GIL) | O (진짜 병렬) |
| 적합한 작업 | I/O 대기 (네트워크, DB) | I/O + 일부 CPU | CPU 집중 계산 |
| 컨텍스트 스위치 비용 | 매우 낮음 | 높음 | 매우 높음 |
| 메모리 | 적음 | 스레드당 수 MB | 프로세스당 수백 MB |

**이 프로젝트가 asyncio를 쓰는 이유:**
- 작업 대부분이 "httpx 응답 기다림", "DB 응답 기다림", "Claude API 응답 기다림"
- I/O 대기 = 스레드가 놀고 있는 시간 → asyncio로 그 시간에 다른 작업 처리

---

## 2. WebFlux(Project Reactor)와 비교

WebFlux를 알고 있다면 Python asyncio는 **거의 같은 개념, 문법만 다름**.

### 공통점

| 개념 | WebFlux (Java) | asyncio (Python) |
|------|---------------|-----------------|
| 이벤트 루프 | Netty의 EventLoop | asyncio event loop |
| 비동기 단위 | `Mono<T>` / `Flux<T>` | `coroutine` (`async def`) |
| 제어권 반환 | 연산자 체인 자동 처리 | `await` |
| 스레드 모델 | EventLoop 스레드 (소수) | 단일 스레드 |
| I/O 처리 | Non-blocking NIO | Non-blocking (selector 기반) |
| 스케줄러 | `Schedulers.boundedElastic()` | `asyncio.get_event_loop()` |

### 핵심 차이점

**1. 선언 방식**
```java
// WebFlux: 연산자 체인으로 파이프라인 선언
Mono.fromCallable(() -> fetchData())
    .subscribeOn(Schedulers.boundedElastic())
    .map(data -> process(data))
    .subscribe();
```
```python
# asyncio: 순차 코드처럼 보이는 문법 (async/await)
async def job():
    data = await fetch_data()  # 내부는 non-blocking이지만 코드는 순차적으로 보임
    result = process(data)
    return result
```

WebFlux는 **데이터 파이프라인을 선언**하는 스타일,
asyncio는 **순차 코드처럼 보이는 비동기** 스타일. 가독성은 asyncio가 높음.

**2. GIL (Global Interpreter Lock) — Python의 한계**
```
Java(WebFlux): 진짜 멀티스레드 병렬 실행 가능
Python(asyncio): GIL 때문에 CPU 작업은 동시에 1개만 실행
                 → CPU 집중 작업(계산)은 asyncio로 빨라지지 않음
                 → I/O 대기 작업은 asyncio로 빨라짐 (대기 시간이 겹침)
```

**3. 에러 핸들링**
```java
// WebFlux: 체인 중간에 onErrorResume, onErrorReturn
.onErrorResume(e -> Mono.just(fallback))
```
```python
# asyncio: 일반 try/except
try:
    result = await risky_operation()
except Exception as e:
    result = fallback
```

**4. 백프레셔(Backpressure)**
- WebFlux `Flux`: 데이터 흐름 속도 제어 (소비자가 처리 못하면 생산자 속도 낮춤)
- asyncio: 기본 백프레셔 없음. `asyncio.Queue`로 직접 구현 필요.
  → 이 프로젝트의 `reanalysis_queue`가 단순 버전의 수동 큐

---

## 3. async / await 가 실제로 하는 일

### 코루틴(Coroutine)이란?

```python
async def crawl_news():   # 이 함수는 "코루틴 함수"
    ...
    return results
```

`async def`로 선언된 함수는 호출해도 **바로 실행되지 않는다**.
대신 **코루틴 객체**를 반환한다.

```python
coro = crawl_news()   # 실행 안 됨. 코루틴 객체만 생성.
result = await coro   # 이 시점에 실행됨. 끝날 때까지 여기서 대기.
```

### await가 하는 일 (내부 동작)

```python
async def daily_job():
    raw_news = await crawl_news()   # ← 여기서 무슨 일이?
    await process_market_news(raw_news)
```

```
1. crawl_news() 코루틴을 이벤트 루프에 등록
2. daily_job은 "crawl_news가 끝나면 나를 재개해줘" 라고 등록하고 제어권 반환
3. 이벤트 루프는 다른 대기 중인 코루틴 실행 (e.g. HTTP 요청 처리)
4. crawl_news 내부에서 httpx 응답이 오면 → crawl_news 재개
5. crawl_news가 return하면 → daily_job 재개 (raw_news에 결과 할당)
6. 다음 줄 실행
```

**핵심:** `await`는 "나 여기서 기다릴 테니 다른 거 먼저 해"라는 **양보 신호**.

### asyncio.gather — 동시 실행

```python
# 순차 실행: A 끝나고 B 시작 → 총 시간 = A + B
result_a = await task_a()
result_b = await task_b()

# 동시 실행: A, B 동시에 시작 → 총 시간 = max(A, B)
result_a, result_b = await asyncio.gather(task_a(), task_b())
```

이 프로젝트 `daily_job`에서 `crawl_news` → `process_market_news` 순서는
**의존 관계** (뉴스를 먼저 받아야 처리 가능)가 있어서 순차 실행이 맞음.
의존 없는 작업이라면 `gather`로 병렬화 가능.

---

## 4. FastAPI + Uvicorn 구조

### Uvicorn이란?
FastAPI 앱을 실제로 실행시키는 ASGI 서버.
내부적으로 **asyncio 이벤트 루프를 하나 만들고 그 안에서 FastAPI를 실행**.

```
[실행 명령] uvicorn app.main:app

  Uvicorn 시작
    └── asyncio 이벤트 루프 생성 (루프 A)
        ├── FastAPI 앱 등록
        ├── HTTP 요청 수신 소켓 등록 (non-blocking)
        └── 루프 시작 (무한 반복)

  요청이 오면:
    소켓에서 읽기 완료 신호 → 이벤트 루프가 라우터 코루틴 실행
    라우터에서 await DB쿼리 → 루프는 다른 요청 처리
    DB 응답 오면 → 라우터 재개 → 응답 전송
```

### 이 프로젝트 main.py의 문제점

```python
# 현재 코드 (main.py)
@app.on_event("startup")
def on_startup():              # ← 일반 함수 (동기)
    Base.metadata.create_all(engine)
```

```python
# 스케줄러 연결 시 올바른 방식
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 (이벤트 루프가 이미 살아있는 시점)
    setup_scheduler()
    scheduler.start()
    yield                  # ← FastAPI가 실행됨
    # 앱 종료 시
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
```

**왜 중요한가:**
`AsyncIOScheduler`는 **실행 중인 이벤트 루프**에 붙어야 함.
`scheduler.start()`가 이벤트 루프 밖(동기 함수 안)에서 호출되면 별도 스레드에서 루프를 만들어 작동하다가 FastAPI 루프와 **충돌** 가능.

---

## 5. APScheduler가 이벤트 루프에 붙는 방식

### AsyncIOScheduler 내부 동작

```
scheduler.start() 호출 시:

  1. 현재 실행 중인 asyncio 이벤트 루프 참조 획득
     (asyncio.get_event_loop() 또는 get_running_loop())

  2. 루프에 "타이머 콜백" 등록
     - "N초 후에 이 함수 실행해줘" 를 이벤트 루프의 call_later()로 등록

  3. 매 tick마다 스케줄러가 "지금 실행할 잡 있나?" 확인
     → 있으면 asyncio.ensure_future(job_func()) 로 코루틴을 루프에 제출
```

### 잡 실행 흐름

```
이벤트 루프 (FastAPI + Uvicorn):

  [HTTP 요청 처리] ... [대기] ... [HTTP 요청 처리] ...
                          ↑
                      이 대기 틈에 스케줄러가 타이머 체크

  03:00:00 도달 →
    스케줄러: "daily_job 실행할 시간!"
    → asyncio.ensure_future(daily_job()) 호출
    → daily_job 코루틴이 이벤트 루프에 Task로 등록됨
    → 루프가 daily_job을 실행 (HTTP 요청 처리와 번갈아가며)
```

### Task vs Coroutine

```python
# 코루틴: 이벤트 루프에 등록 안 된 상태. 혼자 실행 못함.
coro = daily_job()

# Task: 이벤트 루프에 등록된 상태. 루프가 알아서 실행.
task = asyncio.ensure_future(daily_job())  # 또는 asyncio.create_task(daily_job())
```

APScheduler는 잡을 실행할 때 내부적으로 `ensure_future()`를 써서
**daily_job을 이벤트 루프의 Task로 등록**한다.

### 잡이 오래 걸리면?

```
[daily_job 실행 중] — crawl_news → await → process → await → detect → await → ...

daily_job이 await를 만날 때마다 이벤트 루프가 HTTP 요청 처리 가능
daily_job이 await 없이 CPU 계산만 한다면 → 그 시간 동안 HTTP 처리 멈춤 (블로킹!)
```

**이 프로젝트는 모든 긴 작업이 `await` 포함** (httpx, claude API) → 문제 없음.

### 잡 중복 실행 (놓치기 쉬운 함정)

```python
scheduler.add_job(
    daily_job,
    CronTrigger(hour=3, minute=0),
    id="daily_job",
    replace_existing=True,     # ← 이게 없으면 앱 재시작 시 잡이 2개 등록됨
)
```

`replace_existing=True` 없이 앱을 여러 번 재시작하면 같은 잡이 여러 개 등록되어
**매일 3시에 daily_job이 N번 실행**되는 버그 발생.

---

## 6. 이 프로젝트의 전체 흐름 (코드 기준)

```
uvicorn 실행
  └── asyncio 이벤트 루프 시작
      ├── FastAPI lifespan 진입
      │     ├── setup_scheduler() — 잡 목록 등록 (아직 실행 안 함)
      │     └── scheduler.start() — 스케줄러가 이벤트 루프에 붙음
      │
      ├── HTTP 요청 처리 (라우터 코루틴들)
      │
      └── 매일 03:00
            ├── daily_job Task 생성 → 루프에 등록
            │     ├── await crawl_news()
            │     │     └── await httpx.get() × N  ← I/O 대기, 루프는 HTTP 처리 가능
            │     ├── await process_market_news()
            │     │     └── await claude.messages.create() × N  ← I/O 대기
            │     ├── await detect_policy_changes()
            │     │     └── await claude.messages.create() × N
            │     ├── await crawl_trends()
            │     │     └── await httpx.post() × N
            │     └── await consume_reanalysis_queue()
            │           └── await generate_analysis_for_one() × M
            │                 └── await claude.messages.create()
            │
            └── 매 분기 quarterly_job 도 동일한 방식
```

---

## 7. 설계 미스 / 충돌 패턴 — 주의해야 할 것들

### 7-1. 동기 블로킹 코드를 async 함수 안에 넣는 실수

```python
# 잘못된 예
async def process_market_news(raw_news):
    for article in raw_news:
        time.sleep(1)           # ← 블로킹! 이 1초 동안 서버 전체 멈춤
        result = sync_heavy_calc(article)  # CPU 집중 작업도 블로킹

# 올바른 예 — I/O는 await, CPU 작업은 executor로 분리
import asyncio

async def process_market_news(raw_news):
    for article in raw_news:
        await asyncio.sleep(1)  # ← non-blocking. 루프는 다른 작업 처리 가능
        # CPU 집중 작업은 별도 스레드풀에서 실행
        result = await asyncio.get_event_loop().run_in_executor(
            None, sync_heavy_calc, article
        )
```

**이 프로젝트 적용:** 모든 무거운 작업이 httpx/claude API (외부 I/O) → 문제 없음.
나중에 텍스트 전처리 같은 CPU 작업이 추가되면 `run_in_executor` 필요.

---

### 7-2. Playwright — 블로킹 혼용 주의

```python
# async_playwright는 OK (async 버전)
from playwright.async_api import async_playwright

async def crawl():
    async with async_playwright() as p:      # ← async with. OK.
        browser = await p.chromium.launch()  # ← await. OK.

# sync_playwright는 블로킹 — async 함수 안에서 절대 사용 금지
from playwright.sync_api import sync_playwright  # ← 잘못된 import

async def crawl_wrong():
    with sync_playwright() as p:   # ← 블로킹! 이벤트 루프 멈춤
        ...
```

이 프로젝트는 `async_playwright`를 올바르게 사용 중. 유지 필요.

---

### 7-3. SQLAlchemy — 동기 엔진 vs 비동기 엔진

현재 `db.py`는 **동기 SQLAlchemy** 사용:
```python
from sqlalchemy import create_engine  # 동기 엔진
engine = create_engine(DATABASE_URL)
```

async 함수 안에서 동기 SQLAlchemy를 쓰면 DB 쿼리 동안 루프가 블로킹된다.

**선택지:**

| 방법 | 설명 | 난이도 |
|------|------|--------|
| 동기 SQLAlchemy + `run_in_executor` | 현재 엔진 유지, 스레드풀에서 실행 | 중 |
| 비동기 SQLAlchemy (`AsyncSession`) | `create_async_engine` + `asyncpg` | 높음 |
| 동기 그대로 사용 | 크롤러는 3시간마다 실행 → 성능 임계치 아님 | 낮음 |

**이 프로젝트 현실적 판단:**
daily_job은 매일 1회, 요청이 없는 새벽 3시에 실행.
동시 요청 폭주가 없다면 동기 SQLAlchemy를 그대로 써도 실용적으로 문제없음.
단, **user API 요청과 크롤러 DB 쿼리가 동시에 많아진다면** 비동기 전환 고려.

```python
# 비동기 전환 시 필요한 것 (나중을 위한 메모)
# pip install sqlalchemy[asyncio] asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pw@host/db")
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

### 7-4. daily_job 실행 중 에러 처리

APScheduler는 잡 실행 중 예외가 발생해도 **스케줄러 자체는 멈추지 않는다**.
하지만 **그 잡의 이후 단계**는 실행되지 않음.

```python
# 현재 코드 (scheduler.py)
async def daily_job():
    raw_news = await crawl_news()
    await process_market_news(raw_news)  # ← 여기서 예외나면
    await detect_policy_changes(raw_news)  # ← 이건 실행 안 됨
```

```python
# 개선 방향: 각 단계를 독립적으로 실행 (한 단계 실패가 전체 멈추는 것 방지)
async def daily_job():
    raw_news = []
    try:
        raw_news = await crawl_news()
    except Exception as e:
        logger.error(f"crawl_news 실패: {e}")

    if raw_news:
        try:
            await process_market_news(raw_news)
        except Exception as e:
            logger.error(f"process_market_news 실패: {e}")
        # detect_policy_changes는 crawl_news 결과와 독립적으로 진행
        try:
            await detect_policy_changes(raw_news)
        except Exception as e:
            logger.error(f"detect_policy_changes 실패: {e}")
    ...
```

---

### 7-5. 두 번의 scheduler.start() 호출 (재시작 충돌)

```python
# 문제: 이미 실행 중인 스케줄러를 다시 start()하면 RuntimeError
scheduler.start()
scheduler.start()  # ← RuntimeError: Scheduler is already running

# 방어 코드
if not scheduler.running:
    scheduler.start()
```

---

### 7-6. consume_reanalysis_queue의 순환 참조

```python
# reanalysis_queue.py
async def consume_reanalysis_queue():
    # 최상위에서 import하면 순환 참조 발생
    # → 함수 안에서 지연 import로 해결
    from app.collector.processors.analysis_generator import generate_analysis_for_one
    ...
```

이 패턴은 의도적인 해결책. `analysis_generator`가 `reanalysis_queue`를 import하고,
`reanalysis_queue`가 `analysis_generator`를 import하면 순환 참조 발생.
함수 안 import는 실행 시점에 로드되므로 해결됨. 이 구조 유지할 것.

---

## 8. 정리: 언제 무엇을 쓰는가

### 비동기 선택 기준

```
작업 종류?
  ├── 외부 네트워크 / DB 대기  → async def + await  (이 프로젝트 대부분)
  ├── CPU 집중 (계산, 텍스트 처리) → run_in_executor (별도 스레드풀)
  └── 완전한 병렬 계산           → multiprocessing (별도 프로세스)
```

### 이 프로젝트의 작업 분류

| 작업 | 종류 | 현재 처리 |
|------|------|-----------|
| httpx 요청 | I/O 대기 | `await` ✓ |
| Claude API 호출 | I/O 대기 | `await` ✓ |
| Playwright 크롤링 | I/O 대기 | `await` ✓ |
| BeautifulSoup 파싱 | CPU (경량) | 동기 호출 (파싱은 ms 단위 → 허용 범위) |
| SQLAlchemy 쿼리 | I/O 대기 | 동기 (TODO: 추후 비동기 전환 검토) |
| hashlib 해시 | CPU (경량) | 동기 호출 (ns 단위 → 문제없음) |

### APScheduler 핵심 체크리스트

- [ ] `scheduler.start()`는 **이벤트 루프가 살아있을 때** 호출 (lifespan 안에서)
- [ ] `replace_existing=True` → 재시작 시 중복 잡 방지
- [ ] 잡 함수는 `async def` → `AsyncIOScheduler`가 Task로 등록
- [ ] 잡 함수 안에서 블로킹 코드 사용 금지 (time.sleep, sync DB 쿼리 등)
- [ ] 각 단계별 try/except → 한 단계 실패가 전체 멈추는 것 방지
