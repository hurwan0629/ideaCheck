# 01. asyncio 이벤트 루프 내부 동작
> 학습 목표: 이벤트 루프가 "어떻게" 단일 스레드로 여러 작업을 처리하는지 원리를 이해한다.
> 선행 지식: 동시성/병렬성 구분, 스레드/프로세스 차이 (이미 알고 있음)

---

## 0. 왜 알아야 하나

이벤트 루프 원리를 모르면 이런 실수를 한다:
- `async def` 안에 블로킹 코드 넣고 왜 느린지 모름
- `await` 없이도 동시에 실행될 거라고 착각
- 스케줄러가 왜 "루프에 붙어야" 하는지 이해 못함

---

## 1. 이벤트 루프 이전 — 전통적인 서버의 문제

```
전통적인 동기 서버 (스레드 기반):
  요청 1 → 스레드 1 생성 → DB 대기 (스레드 1이 멈춤)
  요청 2 → 스레드 2 생성 → DB 대기 (스레드 2가 멈춤)
  요청 N → 스레드 N 생성 → ...

문제:
  - 스레드 1000개 = 메모리 수 GB 소비
  - 스레드 대부분이 "그냥 기다리는 중"
  - 스레드 생성/전환 비용이 큼
```

핵심 통찰: **"기다리는 동안 그 스레드가 다른 걸 하면 안 되나?"**

---

## 2. OS의 I/O 다중화 — 이벤트 루프의 실제 엔진

이벤트 루프가 가능한 이유는 OS 커널이 제공하는 **I/O 다중화(I/O Multiplexing)** 덕분이다.

### OS에게 맡기는 방식

```
기존: 스레드가 직접 소켓에서 데이터 기다림 (블로킹)
새방식: OS에게 "이 소켓들 중 하나라도 데이터 오면 알려줘" 라고 등록
        그 동안 스레드는 다른 일 가능
        OS가 준비된 소켓 목록 알려주면 그때 처리
```

OS별 구현:
- Linux: `epoll`
- macOS: `kqueue`
- Windows: `IOCP`

Python asyncio는 내부적으로 이 OS 기능 위에서 동작한다.

---

## 3. 이벤트 루프의 실제 구조

```
이벤트 루프 내부:

  ┌─────────────────────────────────────────┐
  │  Ready Queue (즉시 실행 가능한 콜백들)    │
  │  [콜백A, 콜백B, 콜백C, ...]              │
  └─────────────────────────────────────────┘

  ┌─────────────────────────────────────────┐
  │  I/O Waiting (OS에 등록된 I/O 대기들)    │
  │  [소켓1 읽기대기, 소켓2 쓰기대기, ...]   │
  └─────────────────────────────────────────┘

  ┌─────────────────────────────────────────┐
  │  Timer Queue (시간 기반 대기들)           │
  │  [3초 후 실행, 60초 후 실행, ...]         │
  └─────────────────────────────────────────┘
```

### 루프 한 번의 iteration (의사 코드)

```python
while True:
    # 1. Ready Queue에서 꺼내서 실행
    while ready_queue:
        callback = ready_queue.popleft()
        callback()   # 실행. await 만나면 여기서 멈추고 다음 콜백으로

    # 2. OS에게 "I/O 준비된 거 있어?" 물어봄 (epoll/kqueue)
    #    timeout: 다음 타이머까지 남은 시간
    io_events = os_poll(timeout=next_timer_delay)

    # 3. 준비된 I/O → Ready Queue에 추가
    for event in io_events:
        ready_queue.append(event.callback)

    # 4. 만료된 타이머 → Ready Queue에 추가
    for timer in expired_timers():
        ready_queue.append(timer.callback)
```

---

## 4. 실제 실행 흐름 — 타임라인

```python
async def A():
    await asyncio.sleep(1)
    print("A 완료")

async def B():
    await asyncio.sleep(2)
    print("B 완료")

asyncio.run(asyncio.gather(A(), B()))
```

```
시간(ms)  이벤트루프 상태              Ready Queue          Timer Queue
0         A 시작                      [A코루틴]            []
0         A: await sleep(1) 도달      []                   [1000ms→A재개]
0         B 시작 (gather가 동시 등록)  [B코루틴]            [1000ms→A재개]
0         B: await sleep(2) 도달      []                   [1000ms→A재개, 2000ms→B재개]
0         Ready Queue 비었음, OS poll
1000      타이머 만료 → A Ready Queue  [A재개콜백]           [2000ms→B재개]
1000      A 재개 → "A 완료" 출력       []                   [2000ms→B재개]
2000      타이머 만료 → B Ready Queue  [B재개콜백]           []
2000      B 재개 → "B 완료" 출력       []                   []
```

**핵심:** A가 sleep(1)에서 "1초 후 나 깨워줘" 라고 타이머 등록하고 제어권 반환 → 그 동안 B 실행.

---

## 5. GIL과 asyncio의 관계

Python은 GIL(Global Interpreter Lock) 때문에 **CPU 작업은 진짜 병렬 실행이 안 된다.**

```
멀티스레드라도:
  스레드 A: [CPU계산 중]
  스레드 B: [GIL 기다리는 중] ← 동시에 실행 못함

asyncio:
  어차피 단일 스레드이므로 GIL 문제 없음
  I/O 대기 동안 다른 코루틴 실행 = GIL 영향 없음
  CPU 계산은 여전히 1개만 실행됨
```

**결론:**
- I/O 작업 (네트워크, DB, 파일): asyncio로 충분히 빠름
- CPU 작업 (계산, 이미지 처리): asyncio 효과 없음 → multiprocessing 필요

---

## 6. asyncio.run() — 진입점

```python
asyncio.run(main())
```

내부 동작:
```
1. 새 이벤트 루프 생성
2. main() 코루틴을 Task로 등록
3. 루프 시작 (위의 while True 시작)
4. main()이 완료되면 루프 종료
5. 루프 정리 (미완료 Task 취소 등)
```

FastAPI/Uvicorn은 `asyncio.run()`을 직접 호출하지 않고
uvicorn 자체가 루프를 만들고 관리한다. (다음 챕터에서)

---

## 이해도 측정

### 개념 문항

**C1.** 이벤트 루프가 단일 스레드인데도 여러 I/O 작업을 동시에 처리할 수 있는 이유를 "OS 역할"을 포함해서 설명해봐요.

```
답: OS에서 지원하는 멀티플렉싱을 통해서 3단 구조 [ReadyQueue, (Socket, Timer)]을 기반으로 완료된 이벤트에 대해 등록된 콜백이 동작하는 방식입니다.
```

**C2.** asyncio가 I/O에는 효과적이지만 CPU 계산에는 효과 없는 이유를 설명해봐요.

```
답: Python의 기본 내장 GIL가 뮤텍스 락을 통해 cpu를 하나씩만 사용가능하게 만들기 때문입니다.
```

**C3.** Ready Queue와 I/O Waiting의 차이가 뭔가요?

```
답: Ready Queue는 I/O Waiting에서 종료된 이벤트를 받아 실행할 콜백 함수를 저장해놓은 자료구조입니다.
```

---

### 코드 감각 문항

**P1.** 아래 코드의 출력 순서를 예측해봐요.

```python
import asyncio

async def task(name, delay):
    print(f"{name} 시작")
    await asyncio.sleep(delay)
    print(f"{name} 완료")

async def main():
    await asyncio.gather(
        task("A", 2),
        task("B", 1),
        task("C", 3),
    )

asyncio.run(main())
```

```
예측: A시작 -> B시작 -> C시작 -> B완료 -> A완료 -> C완료
```

**P2.** 아래 코드는 왜 total 3초가 아니라 6초 걸리나요?

```python
async def main():
    await task("A", 2)   # 2초
    await task("B", 1)   # 1초
    await task("C", 3)   # 3초
```

```
답: Timer Zone에서 동시에 실행되며 먼저 끝나는것을 OS가 알려주며 해당 코드를 실행하기 때문입니다.
```

**P3.** 이벤트 루프 관점에서 `await asyncio.sleep(0)` 이 의미하는 게 뭔가요? (힌트: 타이머 0초)

```
답: 즉시 실행하라? (정확히는 자발적 양보)
```

---