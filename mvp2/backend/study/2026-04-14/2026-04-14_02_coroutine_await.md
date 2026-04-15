# 02. 코루틴과 await 내부 동작
> 학습 목표: await가 이벤트 루프와 어떻게 제어권을 주고받는지 정확히 이해한다.
> 선행 학습: 01_asyncio_event_loop.md

---

## 0. 왜 알아야 하나

await의 내부를 모르면:
- "await를 붙이면 비동기가 된다"는 잘못된 이해로 이어짐
- await가 없는 async 함수도 블로킹될 수 있음을 모름
- Future/Task/Coroutine의 차이를 구분 못해 디버깅이 어려워짐

---

## 1. 코루틴은 어디서 왔나 — 제너레이터 연결고리

Python의 async/await는 **제너레이터(generator)** 에서 진화했다.
제너레이터를 먼저 보면 코루틴이 쉽게 이해된다.

```python
# 제너레이터: yield로 실행을 일시 중단하고 값을 반환
def counter():
    print("1 이전")
    yield 1          # 여기서 멈추고 1 반환. 호출자가 next() 하면 재개.
    print("2 이전")
    yield 2
    print("끝")

gen = counter()
print(next(gen))   # "1 이전" 출력 후 1 반환 (멈춤)
print(next(gen))   # "2 이전" 출력 후 2 반환 (멈춤)
print(next(gen))   # "끝" 출력 후 StopIteration
```

**yield = 실행 중단 + 호출자에게 제어권 반환.**

코루틴은 이 아이디어를 이벤트 루프와 연결한 것이다.

---

## 2. 코루틴의 실제 구조

```python
async def fetch_data():
    print("요청 전")
    result = await some_io_operation()   # ← 여기가 핵심
    print("요청 후")
    return result
```

내부적으로 Python은 이걸 대략 이렇게 처리한다:

```python
# 실제 동작을 단순화한 의사 코드
def fetch_data():
    print("요청 전")
    future = some_io_operation()  # Future 객체 생성
    yield future                  # 이벤트 루프에게: "이거 완료되면 나 깨워줘"
    result = future.result()      # 이벤트 루프가 재개시켜 줄 때 결과 가져옴
    print("요청 후")
    return result
```

`await` = `yield` + "완료 시 나를 재개해달라는 콜백 등록"

---

## 3. Future — 이벤트 루프와 코루틴의 다리

**Future**: "아직 완료되지 않은 작업의 자리표시자"

```python
future = asyncio.Future()
# future.result() → 아직 완료 안 됨 → InvalidStateError
# future.done()   → False

# 나중에 이벤트 루프나 OS가:
future.set_result("완료된 값")
# future.result() → "완료된 값"
# future.done()   → True
```

### await의 실제 흐름

```
코루틴:  await future
           ↓
         1. future가 완료됐나? → No
         2. "future 완료되면 나(코루틴)를 재개해줘" 콜백 등록
         3. 이벤트 루프에 제어권 반환 (yield)
           ↓
이벤트루프: 다른 코루틴 실행 중...
           ↓
OS:       I/O 완료 신호 → future.set_result(data)
           ↓
이벤트루프: future에 등록된 콜백 호출 → 코루틴 재개
           ↓
코루틴:   result = future.result()  # data 꺼냄
          다음 코드 실행
```

---

## 4. Coroutine / Future / Task 구분

세 개가 혼용되는데 각각 다르다.

```python
# Coroutine: async def 함수를 호출한 결과물. 아직 실행 안 됨.
coro = fetch_data()
type(coro)  # <class 'coroutine'>

# Future: 완료 여부와 결과를 추적하는 객체. 직접 만들 일은 드묾.
fut = asyncio.Future()
type(fut)   # <class 'Future'>

# Task: Coroutine을 이벤트 루프에 등록한 것. Future의 하위 클래스.
#       등록 즉시 실행 시작.
task = asyncio.create_task(fetch_data())
type(task)  # <class 'Task'>
```

### 관계도

```
Future
  └── Task
        └── 내부에 Coroutine을 감싸고 있음
              Coroutine이 yield할 때마다 Task가 이벤트 루프와 통신
```

### await 가능한 것들 (Awaitable)

```python
await coroutine   # 코루틴 직접
await task        # Task (Future 하위 클래스)
await future      # Future
```

공통점: `__await__` 메서드를 가진 객체. Python이 이걸 보고 yield 체인을 만들어 처리.

---

## 5. async def이지만 await가 없으면?

```python
async def no_await():
    # await가 없음
    result = 1 + 1
    return result
```

이 함수는 코루틴 함수지만 **await 시 이벤트 루프에 제어권을 한 번도 반환하지 않는다.**
즉, 실행되는 동안 다른 코루틴이 끼어들 수 없다.

```python
async def main():
    await asyncio.gather(
        no_await(),    # 제어권 반환 없이 바로 완료
        heavy_calc(),  # 위가 빨리 끝나서 별 문제 없음 (이 경우는 OK)
    )
```

계산이 가벼우면 문제없지만, CPU 무거운 작업을 `await` 없이 async def로 감싸면 블로킹이다.

---

## 6. 코루틴 실행 방법 4가지

```python
# 1. await (가장 기본)
result = await fetch_data()
# → 현재 코루틴이 멈추고 fetch_data 완료 대기

# 2. asyncio.create_task() (백그라운드 등록)
task = asyncio.create_task(fetch_data())
# → fetch_data를 루프에 등록. 현재 코루틴은 계속 실행.
# → 나중에 result = await task 로 결과 회수

# 3. asyncio.gather() (동시 실행 + 모두 대기)
results = await asyncio.gather(fetch_data(), fetch_other())
# → 둘 다 등록하고 둘 다 완료될 때까지 대기

# 4. asyncio.run() (최상위 진입점)
asyncio.run(fetch_data())
# → 새 이벤트 루프 만들어서 실행. 스크립트 최상단에서만 사용.
```

---

## 7. 이 프로젝트에서 보는 패턴

```python
# scheduler.py
async def daily_job():
    raw_news = await crawl_news()          # crawl_news 완료 대기
    await process_market_news(raw_news)    # 위 결과 필요 → 순차 await
    await detect_policy_changes(raw_news)  # 동일
    await crawl_trends()                   # 독립적이지만 순차로 작성됨
    await consume_reanalysis_queue()       # 동일
```

현재 코드는 전부 순차 await. 
`crawl_trends()`와 `consume_reanalysis_queue()`는 사실 독립적이라 gather 가능.
(04_asyncio_api.md에서 다룸)

---

## 이해도 측정

### 개념 문항

**C1.** `await`가 이벤트 루프에 하는 일을 두 단계로 나눠 설명해봐요.
(힌트: 1. 등록, 2. ?)

```
답: 1. 이벤트 루프에 등록, 제어권 반환 (yield 후 콜백 등록)
```

**C2.** Coroutine과 Task의 차이가 뭔가요?

```
답: Corutine는 실행중이 아닐 수 있고 Task는 실행중이다? (잘 모르겠음)
```

**C3.** `async def` 함수에 `await`가 하나도 없어도 문제가 생길 수 있는 경우는 언제인가요?

```
답: cpu 연산이 오래걸리거나 blocking 작업이 있을 때
```

---

### 코드 감각 문항

**P1.** 아래 코드 중 `fetch()`가 실제로 실행되는 것을 모두 골라봐요.

```python
# (a)
coro = fetch()

# (b)
result = await fetch()

# (c)
task = asyncio.create_task(fetch())

# (d)
asyncio.run(fetch())

# (e)
results = await asyncio.gather(fetch())
```

```
답: a는 아님, b는 등록되었고 실행됨. c도 진행중. d는 이벤트 루프에 등록 -> 돌아감. e는 당연히 돌아감
```

**P2.** 아래 코드에서 "B 시작"이 출력되는 시점은 언제인가요?

```python
async def A():
    print("A 시작")
    await asyncio.sleep(5)
    print("A 완료")

async def B():
    print("B 시작")

async def main():
    task_a = asyncio.create_task(A())
    task_b = asyncio.create_task(B())
    await task_a
    await task_b
```

```
답: 약 5초 뒤 (main()함수에서 첫 await 시점에서 5초를 기다리게 되기 때문에 A()에서 또 이벤트 루프에 등록한다 해도 두개 다 await가 붙은 시점에서 5초 기다림. 안기다리려면 둘디 await가 없어야함.)
```

**P3.** 아래 코드의 문제점이 뭔가요?

```python
async def process_all(items):
    results = []
    for item in items:
        coro = process_item(item)   # 코루틴 생성만 함
        results.append(coro)        # 리스트에 추가
    return results                  # 코루틴 객체 리스트 반환 (실행 안 됨)
```

```
답: 실제로 코루틴이 실행이 안된다? 누군가가 다시 실행해주어야하는데 결국 함수로 만들 의미가 크게 없기도 하고 async를 붙이는 의미도 없다.
```

---

## 채점 결과

### C1 — await가 이벤트 루프에 하는 일 두 단계 | **65 / 100**

> "이벤트 루프에 등록, 제어권 반환 (yield 후 콜백 등록)"

두 단계를 괄호 안에 섞어 썼는데, 명확히 분리하면:

1. **콜백 등록** — Future에 "완료되면 나(코루틴)를 재개해줘"라고 콜백을 달아둠
2. **제어권 반환** — yield를 통해 이벤트 루프에 제어권을 넘김 (루프가 다른 코루틴 실행 가능)

두 단계의 내용 자체는 이해하고 있음. 다만 힌트가 "1. 등록, 2. ?"였는데 2번(제어권 반환)을 앞에 쓰고 괄호에 섞어 넣어 구분이 불명확했음.

---

### C2 — Coroutine vs Task 차이 | **60 / 100**

> "Coroutine은 실행 중이 아닐 수 있고 Task는 실행 중이다? (잘 모르겠음)"

방향은 맞음. 구체적으로 정리하면:

- **Coroutine**: `async def`를 호출해서 생성된 객체. `await`나 `create_task` 없이는 이벤트 루프에 등록되지 않아 실행 안 됨.
- **Task**: `asyncio.create_task(coro)`로 코루틴을 루프에 등록한 것. **생성 즉시 실행 시작**됨. Future의 하위 클래스.

"잘 모르겠음"이라고 스스로 표시한 게 정직하고 맞는 판단. 개념은 어렴풋이 잡혀 있음.

---

### C3 — await 없는 async def가 문제가 되는 경우 | **95 / 100**

> "cpu 연산이 오래걸리거나 blocking 작업이 있을 때"

거의 완벽. CPU 연산(제어권 반환 포인트 없이 루프 점유)과 블로킹 작업(time.sleep, 동기 DB 호출 등) 모두 정확히 짚었음.

---

### P1 — 실제로 실행되는 코드 고르기 | **100 / 100**

> "a는 아님, b~e 모두 실행됨"

완벽. `coro = fetch()`는 코루틴 객체 생성만 할 뿐 실행되지 않는다는 것, 나머지는 모두 루프에 등록되어 실행된다는 것 정확히 이해함.

---

### P2 — "B 시작"이 출력되는 시점 | **15 / 100**

> "약 5초 뒤 (첫 await 시점에서 5초를 기다리기 때문에)"

틀림. 핵심 오해: `await task_a`는 main 코루틴이 대기하는 것이지 이벤트 루프 전체가 멈추는 게 아님.

실제 흐름:
```
main: create_task(A()) → 루프에 등록
main: create_task(B()) → 루프에 등록
main: await task_a     → main이 대기하며 제어권 반환
루프: A() 실행 → "A 시작" 출력 → sleep(5) await → 제어권 반환
루프: B() 실행 → "B 시작" 출력  ← 거의 0초 시점
루프: 5초 후 A() 재개 → "A 완료" 출력
main: await task_b → B는 이미 완료돼 있어 즉시 통과
```

**"B 시작"은 약 0초 시점(A의 sleep 직후)에 출력됨.** `create_task`로 등록된 Task는 현재 코루틴이 `await`로 제어권을 반환하는 순간 실행 기회를 얻는다. C2에서 Task가 "즉시 실행된다"고 이해했다면 이 문제도 맞출 수 있었음.

---

### P3 — process_all 코드의 문제점 | **70 / 100**

> "코루틴이 실행 안 된다. 누군가가 다시 실행해줘야 한다."

핵심은 맞음. 조금 더 구체적으로:

- 코루틴 객체만 리스트에 쌓고 반환 → 호출자도 결과값이 아닌 코루틴 객체 리스트를 받음
- 올바른 수정: `await process_item(item)` 또는 `asyncio.create_task(process_item(item))`로 실행해야 함
- 한꺼번에 동시 실행하려면 `return await asyncio.gather(*[process_item(item) for item in items])`

"async를 붙이는 의미도 없다"는 표현은 약간 부정확함 — async는 의미 있지만 내부에서 await/create_task를 써야 한다는 게 포인트.

---

## 총점

| 문항 | 점수 |
|------|------|
| C1   | 65   |
| C2   | 60   |
| C3   | 95   |
| P1   | 100  |
| P2   | 15   |
| P3   | 70   |
| **평균** | **68 / 100** |

---

## 학습 후 개념 교정 기록

### 몰랐던 것 → 이해한 것

---

**1. `await` = 프로그램 전체가 멈춘다?**

```
몰랐던 것:
  await task_a 하면 5초 동안 아무것도 실행 안 된다.

이해한 것:
  await task_a 하면 "현재 코루틴(main)만" 대기한다.
  이벤트 루프는 계속 돌아가며 다른 Task를 실행한다.

  main: await task_a → 잠듦
  루프: A 실행 → sleep → B 실행 → B 완료 → A 완료
  main: 재개
```

---

**2. `create_task` 하면 즉시 실행된다?**

```
몰랐던 것:
  create_task(A()) 하는 순간 A가 실행된다.

이해한 것:
  create_task는 ready queue에 "등록"만 한다.
  실제 실행은 현재 코루틴이 어떤 await든 만나서 제어권을 반환할 때.

  create_task(A())   → ready queue에 A 등록 (실행 안 됨)
  create_task(B())   → ready queue에 B 등록 (실행 안 됨)
  await task_a       → 첫 await. 여기서 루프가 A, B 실행 시작.
```

---

**3. `await task_a`가 A를 실행시킨다?**

```
몰랐던 것:
  await task_a가 A를 실행시키는 명령이다.

이해한 것:
  await task_a는 "A가 완료되면 나를 재개해줘" + 제어권 반환이다.
  A가 실행되는 이유는 await task_a가 첫 번째 await였기 때문.
  사이에 다른 await가 있었다면 거기서 이미 A가 실행됐을 것.
```

---

**4. 제어권과 코루틴이 뭔지 몰랐다**

```
이해한 것:
  제어권  = 지금 CPU가 실행 중인 코드의 주인
  코루틴  = await 지점에서 멈추고 재개할 수 있는 함수
  루프    = 제어권을 누구한테 줄지 결정하는 관리자

  일반 함수: 시작 ───────────────── 끝  (중단 불가)
  코루틴:    시작 ──await──(대기)── 끝  (중간에 멈추고 재개 가능)
```

---

**5. `await`의 정확한 의미**

```
몰랐던 것:
  await = 이거 끝날 때까지 기다려라

이해한 것:
  await = 이 함수를 루프에 넘겨서 관리하게 하고
        + 완료되면 나(현재 코루틴)를 재개해줘

  그래서 await와 create_task의 차이:

  await A()         → 루프에 넘기고, A 끝날 때까지 내가 대기
  create_task(A())  → 루프에 넘기고, 나는 계속 실행

  둘 다 "루프에 관리 맡긴다"는 건 같고,
  "현재 코루틴이 기다리느냐 안 기다리느냐"의 차이.
```

---

## 학습 중 질문 기록

**Q. 나는 당연히 `await`가 "await 붙은 코드는 끝날 때까지 기다려라"인 줄 알았는데 잘못 이해한 거야?**

반만 맞고 반은 틀렸다.

**"await = 이게 끝날 때까지 기다려라"** — 맞음.

그런데 **"누가 기다리느냐"** 가 핵심이다.

- **현재 코루틴(main)** 이 기다리는 것
- **이벤트 루프 전체** 가 멈추는 게 아님

```python
async def main():
    task_a = asyncio.create_task(A())  # 루프에 등록
    task_b = asyncio.create_task(B())  # 루프에 등록
    await task_a   # ← main이 여기서 대기. 루프는 계속 돌아감.
    await task_b
```

`await task_a` 시점에 일어나는 일:

```
main    → "나는 task_a 끝날 때까지 기다릴게" → 제어권 반환
루프    → task_a 실행: "A 시작" 출력 → sleep(5) → 제어권 반환
루프    → task_b 실행: "B 시작" 출력   ← 이때 B가 실행됨 (0초 시점)
루프    → 5초 후 task_a 재개: "A 완료"
main    → await task_b → 이미 완료돼 있어서 즉시 통과
```

`await`는 "**내가** 여기서 멈추고 루프에 제어권을 돌려준다"는 의미이고, 루프는 그 틈에 다른 Task를 실행한다.

비유: 카페에서 음료 주문하고 기다리는 동안 직원이 다른 손님 주문도 처리한다. 내가 기다리는 동안 카페 전체가 멈추는 게 아님.

---

## 종합 피드백

**1챕터(49점) → 2챕터(68점): 19점 상승.** Coroutine/Future/Task 구조 자체는 잘 흡수했음.

**여전히 약한 부분 — P2:** `create_task`로 등록된 Task가 **언제 실행 기회를 얻는가**에 대한 이해가 아직 부족함. 이벤트 루프는 `await task_a`처럼 현재 코루틴이 제어권을 반환하는 순간 다른 Task를 실행한다. "main이 기다린다 = 루프 전체가 멈춘다"는 오해를 아직 갖고 있음. 3챕터(블로킹) 공부할 때 이 개념이 다시 나올 것이므로 그때 확실히 잡아둘 것.
