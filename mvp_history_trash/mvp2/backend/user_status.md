# 기술 수준 자가 진단 문제지
> 답변 후 Claude에게 "user_status.md 채점해줘" 라고 하면 분석표를 만들어줍니다.
> 모르면 "모름", 애매하면 "애매함" 이라고 써도 됩니다. 아는 척 하지 않는 게 정확한 분석에 도움됩니다.

---

## A. CS / 동시성 기초

**A1.** 아래 두 단어의 차이를 본인 말로 설명해봐요.
- 동시성 (Concurrency)
- 병렬성 (Parallelism)

```
답: 동시성은 실제로 cpu가 스케줄러를 통해 하나의 작업을 빠르게 스위칭시켜 멀티프로세스(멀티스레드)를 운영하는 방식이며 병렬성은 실제로 코어 수만큼 동시에 작업을 진행하는 것입니다.
```

---

**A2.** 스레드와 프로세스의 차이가 뭔가요? 메모리 관점에서 설명해봐요.

```
답: 프로세스는 메모리를 공유하지 않지만 스레드는 힙 메모리를 공유합니다.
```

---

**A3.** "블로킹(Blocking)" 이 정확히 무슨 상태인지 설명해봐요.

```
답: 원래 publisher-subscriber 형태로 이벤트 루프에서 ㅇㅇ 작업이 끝나면 호출해줘. A() 작업 할게라고 해놨는데 사실 A() 작업에서 I/O작업이 존재하여 결국 스레드를 점유하여 흐름을 막는 상태입니다. (DB와는 별개의 개념)
```

---

**A4.** 아래 코드에서 문제가 있는 부분을 찾고 이유를 설명해봐요.

```python
async def daily_job():
    import time
    time.sleep(5)
    result = await crawl_news()
    return result
```

```
답: async인데 sleep()가 존재합니다. (blocking 문제)
```

---

## B. asyncio / 이벤트 루프

**B1.** asyncio 이벤트 루프가 "단일 스레드"인데도 여러 요청을 처리할 수 있는 이유가 뭔가요?

```
답:  while True: 와 같은 형태로 이벤트 루프 기반으로 i/o대기 시간을 없앴기 때문입니다.
```

---

**B2.** 아래 두 코드의 실행 시간 차이가 있나요? 있다면 왜 그런가요?

```python
# 코드 1
result_a = await task_a()   # 2초 걸림
result_b = await task_b()   # 2초 걸림

# 코드 2
result_a, result_b = await asyncio.gather(task_a(), task_b())
```

```
답: 잘 모르겠습니다. gather()함수 자체를 모릅니다. (asyncio객체도)
```

---

**B3.** 아래 코드를 실행하면 어떻게 되나요?

```python
async def fetch():
    return "done"

result = fetch()
print(result)
```

```
답: json이라면 promise객체가 나오는것과 같이 coro 객체가 나오지 않을까요? (아직 대기중인 작업 객체가 나옴)
```

---

**B4.** `async def` 함수와 일반 `def` 함수, FastAPI에서 각각 어떻게 실행되나요?

```
답: def는 스레드 추가 생성. 각각 스프링의 parallel, boundedElastic 스레드풀 에서 돌아가는것과 같음
```

---

## C. FastAPI 구조

**C1.** Uvicorn이 뭐고 FastAPI랑 어떤 관계인가요?

```
답: Uvicorn은 스프링의 톰캣 역할을 하며 FastAPI가 돌아갈 환경을 제공해줍니다.
```

---

**C2.** 아래 코드는 FastAPI 앱 시작/종료 시 뭔가를 실행하려는 코드인데, 어떻게 동작하는지 설명해봐요.

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("시작")
    yield
    print("종료")

app = FastAPI(lifespan=lifespan)
```

```
답: 잘 모르곘습니다. 
```

---

**C3.** 아래 두 라우터 중 DB 쿼리가 오래 걸릴 때 다른 요청을 막는 건 어느 쪽인가요? 이유도 설명해봐요.

```python
@app.get("/a")
async def route_a():
    result = db.execute(query)  # 동기 SQLAlchemy
    return result

@app.get("/b")
def route_b():
    result = db.execute(query)  # 동기 SQLAlchemy
    return result
```

```
답: route_a입니다. 비동기 스레드를 점유하여 흐름을 막기 때문입니다.
```

---

## D. APScheduler / 스케줄링

**D1.** `AsyncIOScheduler`와 `BackgroundScheduler`의 차이가 뭔가요? (모르면 모름이라고)

```
답: 모릅니다. 단어로 추정하면 비동기방식과 스레드 방식 아닐까요
```

---

**D2.** 아래 코드에서 `replace_existing=True`를 빼면 어떤 문제가 생기나요?

```python
scheduler.add_job(
    daily_job,
    CronTrigger(hour=3, minute=0),
    id="daily_job",
    replace_existing=True,
)
```

```
답: 정확한 이유는 모르지만 misfire가 실행되는걸 막는다고 들어본거같습니다. (원리나 깊이는 전혀 없이 그냥 들은 이야기입니다.)
```

---

**D3.** 스케줄러에 등록된 잡이 실행 중에 에러가 나면 스케줄러 자체가 멈추나요?

``` 
답: 멈추지 않을거같습니다. 이유는 모르지만 여러 작업이 등록되어야하기 때문에 하나가 여러 작업을 막게 설계되지 않았을거같아서입니다.
```

---

## E. 설계 판단

**E1.** 크롤러 서버를 지금 당장 분리하지 않는 이유가 뭔가요? (이 프로젝트 기준)

```
답: 크롤링 시간이 주기대비 짧기 때문에 대기시간을 걱정할 필요 없고 db도 트래픽이 가볍다는 가정이기 때문에 하나로 해도 돼기 때문입니다.
```

---

**E2.** `reanalysis_queue`를 `list` 대신 `set`으로 만든 이유가 뭔가요?

```
답: reanalysis_queue가 어디있는지 잘 모르겠고 어디서 쓰는지도 모르겠지만 문맥상 다시 분석하는 경우 동일한 결과를 추가하지 않기 위함입니다.
```

---

**E3.** 아래 상황에서 어떤 방식을 선택하겠어요? 이유도 써봐요.

> 뉴스 기사 본문에서 특정 키워드 빈도를 계산하는 함수가 있음.
> CPU를 많이 쓰는 순수 계산 작업임. (네트워크 없음)
> 이걸 `async def daily_job()` 안에서 호출해야 함.

- (a) 그냥 `result = count_keywords(text)` 로 호출
- (b) `await asyncio.get_event_loop().run_in_executor(None, count_keywords, text)`
- (c) 별도 프로세스로 분리

``` 
답: (b)이고 cpu를 먹는 작업이지만 프로세스를 분리하기에는 그정도의 독립성이나 중요성은 없기 때문에 스레드를 생성하는게 맞습니다.
```

---

## F. 자유 서술

**F1.** WebFlux를 써본 경험이 있나요? 있다면 어느 정도 수준인지 간단히 써봐요.

```
답: 거의 사용하지 않았고 Reactive 프로그래밍, 선언형 프로그래밍, 이벤트 루프 등의 개념만 공부했고, 그냥 스프링 간단 예제정도만 클론코딩 해보았습니다. pom.xml의 의존성들의 역할과 webflux가 webmvc와 전혀 다른 방식(Netty) 사용 및 트랜잭션 등 처리를 따로 해줘야한다 정도를 아는 정도입니다. 
```

---

**F2.** 지금 이 프로젝트에서 본인이 가장 불확실하게 느끼는 부분이 뭔가요?

```
답: fastapi의 구조나 여러 라이브러리를 알지 못하여 효율적인 설계를 하지 못한다는 점입니다. 클로드가 코드를 짜주면 읽고 이해하는데 시간이 좀 걸리며 답답함이 조금 느껴지기도 하지만 어쩔수 없다는 생각도 조금 있습니다.
```

---

---

# 채점 결과 분석표
> 2026-04-14 채점 | 다음 세션에서 이 파일을 읽으면 수준에 맞는 설명을 바로 제공할 수 있습니다.

## 영역별 수준

| 영역 | 수준 | 비고 |
|------|------|------|
| CS 기초 (동시성/병렬성/스레드) | **탄탄** | 개념 정확히 이해 |
| 블로킹 개념 | **방향은 맞으나 부분적** | 아래 참고 |
| asyncio 이벤트 루프 원리 | **방향은 잡혀있음** | 표현 부정확한 부분 있음 |
| asyncio 구체적 API | **미숙** | gather, create_task 등 모름 |
| FastAPI 구조 | **비유 수준** | Uvicorn=톰캣은 맞으나 세부 동작 모름 |
| lifespan / asynccontextmanager | **모름** | |
| APScheduler 세부 API | **모름** | 동작 직관은 있음 |
| 설계 판단력 | **좋음** | 실용적 사고 가능 |
| WebFlux 경험 | **개념 수준** | 실무 경험 없음, 개념 공부만 |

---

## 잘 이해하고 있는 것

- 동시성(스위칭) vs 병렬성(코어 병렬) 구분 정확
- 스레드는 힙 공유, 프로세스는 독립 메모리 — 정확
- `async def` 안에서 `time.sleep()` = 블로킹 문제 — 즉시 파악
- `async def` vs `def` in FastAPI 처리 방식 — 스프링 비유로 정확히 이해
- Uvicorn = 톰캣 역할 — 정확한 비유
- `route_a` (async + 동기 SQLAlchemy) = 이벤트 루프 블로킹 — 정확
- 코루틴 = Promise 유추 및 미실행 객체 반환 — 정확
- CPU 작업에 `run_in_executor` 선택 + 이유 — 정확
- set 사용 이유 (중복 제거) — 정확
- 설계 판단 (E파트 전반) — 실용적 사고 잘 됨

---

## 보완이 필요한 것

**1. 블로킹 정의가 I/O에 한정됨**
- 현재 이해: "I/O 작업이 있어서 스레드를 점유하는 상태"
- 정확한 정의: "작업 완료까지 스레드가 다른 일을 못하고 대기하는 상태" (I/O든 CPU든 동일)
- CPU 집중 작업도 블로킹임을 연결해서 이해할 것

**2. asyncio "대기 시간을 없앤다" 표현**
- 현재 이해: I/O 대기 시간 자체가 없어진다
- 정확한 표현: I/O 대기 시간 동안 다른 작업을 끼워 넣어 활용한다
- 미묘한 차이지만 설계 시 중요 (대기는 여전히 존재함)

**3. asyncio.gather() 모름**
- 여러 코루틴을 동시에 실행하는 핵심 API
- 코드 1 (순차) = 4초, 코드 2 (gather) = 2초 — 이 차이를 모르면 성능 설계 미스 가능

**4. lifespan / asynccontextmanager 모름**
- 현재 main.py의 `on_event("startup")`은 deprecated
- 스케줄러 연결 시 반드시 필요한 패턴
- `yield` 기준으로 시작/종료 코드를 나누는 구조

**5. replace_existing vs misfire 혼동**
- replace_existing: 같은 id 잡 중복 등록 방지
- misfire_grace_time: 실행 시각을 놓쳤을 때 허용 범위 (별개 옵션)

---

## Claude가 이 사용자에게 설명할 때 적용할 지침

- Spring/WebFlux 비유 적극 활용 (Uvicorn=톰캣, boundedElastic=스레드풀 등)
- CS 기초 설명은 생략해도 됨 (이미 이해하고 있음)
- asyncio API (gather, create_task 등) 나올 때 예시 코드와 함께 설명
- lifespan 패턴은 yield 기준으로 "try-finally처럼 생각해라"로 설명하면 이해 빠를 것
- 설계 판단 능력이 있으므로 "왜 이렇게 설계했는가"를 함께 설명하면 흡수 빠름
- 모른다고 솔직하게 쓰는 편 → 아는 척 유도하지 말고 모르는 건 짧게 정확하게 설명
