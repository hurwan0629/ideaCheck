# 06. APScheduler — 이벤트 루프 위의 스케줄링
> 학습 목표: APScheduler가 이벤트 루프에 어떻게 붙는지, 각 옵션이 왜 필요한지 이해한다.
> 선행 학습: 01~05 전부

---

## 0. 왜 알아야 하나

APScheduler는 단순히 "설정만 하면 되는 도구"가 아니다.
이벤트 루프 위에 올라타는 구조를 이해해야:
- 스케줄러 시작 시점을 올바르게 판단
- 잡이 오래 걸릴 때 서버에 미치는 영향 파악
- 옵션들을 상황에 맞게 설정

---

## 1. APScheduler가 이벤트 루프에 붙는 방식

### scheduler.start() 내부

```python
scheduler.start()
# 내부적으로:
# 1. asyncio.get_running_loop() → 현재 실행 중인 루프 참조 획득
# 2. loop.call_soon(self._dispatch_jobs) 등록
#    = 루프에 "매 tick마다 잡 체크 함수 실행해줘" 요청
```

이것이 05에서 "lifespan yield 이전에 start()해야 한다"는 이유다.
루프가 없는 상태에서 `start()`를 호출하면 `get_running_loop()`가 실패하거나
별도 스레드에서 새 루프를 만들어 동작하게 된다.

### 잡 실행 흐름 (이벤트 루프 관점)

```
이벤트 루프 타임라인:

[HTTP 처리] → [대기] → [HTTP 처리] → [대기] → [HTTP 처리] ...
                ↑                       ↑
         매 tick마다 스케줄러가 체크    03:00 도달 → 잡 실행

스케줄러 tick 동작:
  1. "지금 실행할 잡 있나?" 확인
  2. 있으면: asyncio.ensure_future(daily_job())
             = daily_job을 Task로 만들어 루프에 등록
  3. daily_job이 Task로 루프에서 실행됨
     → daily_job 안의 await마다 다른 요청 처리 가능
```

---

## 2. 스케줄러 종류 — 왜 AsyncIOScheduler인가

```python
# AsyncIOScheduler (이 프로젝트에서 사용)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 동작: asyncio 이벤트 루프 안에서 실행
# async def 잡 지원: YES
# FastAPI 루프와 공유: YES
# 별도 스레드: NO
```

```python
# BackgroundScheduler (동기 앱에서 사용)
from apscheduler.schedulers.background import BackgroundScheduler

# 동작: 별도 백그라운드 스레드에서 실행
# async def 잡 지원: NO (동기 함수만)
# FastAPI 루프와 공유: NO
# 별도 스레드: YES
```

**FastAPI에서 BackgroundScheduler를 쓰면:**
- 잡 함수가 동기여야 함
- `async def daily_job()`은 실행 불가
- 스레드 간 데이터 공유 시 동기화 필요

→ FastAPI + async 잡은 무조건 `AsyncIOScheduler`

---

## 3. Trigger 종류

### CronTrigger — 특정 시각 반복

```python
from apscheduler.triggers.cron import CronTrigger

# 매일 03:00
CronTrigger(hour=3, minute=0)

# 분기 1회 (1, 4, 7, 10월 1일 04:00)
CronTrigger(month="1,4,7,10", day=1, hour=4, minute=0)

# 매주 월요일 09:00
CronTrigger(day_of_week="mon", hour=9, minute=0)

# 30분마다
CronTrigger(minute="*/30")
```

### IntervalTrigger — 일정 간격 반복

```python
from apscheduler.triggers.interval import IntervalTrigger

# 6시간마다
IntervalTrigger(hours=6)

# 30분마다
IntervalTrigger(minutes=30)

# 첫 실행을 10초 후에 시작하고 이후 1시간마다
IntervalTrigger(hours=1, start_date=datetime.now() + timedelta(seconds=10))
```

---

## 4. add_job() 핵심 옵션 — 원리와 이유

### replace_existing

```python
scheduler.add_job(..., id="daily_job", replace_existing=True)
```

**문제:** 앱을 재시작하면 `setup_scheduler()`가 다시 실행되어 `add_job()`이 다시 호출됨.

```
1회 실행: id="daily_job" 등록
재시작:   id="daily_job" 또 등록 시도

replace_existing=False (기본): ConflictingIdError 발생
replace_existing=True:         기존 잡을 새 설정으로 조용히 교체
```

개발 중 재시작이 잦으므로 필수.

---

### misfire_grace_time

```python
scheduler.add_job(..., misfire_grace_time=3600)
```

**문제:** 잡이 실행되어야 할 시각에 서버가 다운되어 있으면?

```
설정: 매일 03:00, misfire_grace_time=3600 (1시간)

시나리오 1: 02:50 다운 → 03:45 재시작
  → 03:45 - 03:00 = 45분 경과 < 1시간 → 즉시 실행

시나리오 2: 02:50 다운 → 05:10 재시작
  → 05:10 - 03:00 = 130분 경과 > 1시간 → 건너뜀

misfire_grace_time=None → 시간 무관하게 항상 실행
```

`replace_existing`은 "중복 등록" 문제, `misfire_grace_time`은 "놓친 실행" 문제.
완전히 다른 상황을 다루는 옵션이다.

---

### max_instances

```python
scheduler.add_job(..., max_instances=1)
```

**문제:** 잡 실행 시간 > 실행 주기이면?

```
설정: 매일 03:00, max_instances=1

시나리오: daily_job이 3시간 걸림 (API 10000건 처리)
  03:00 → 1번째 인스턴스 시작
  다음날 03:00 → 1번째 아직 실행 중

max_instances=1:
  → 이미 1개 실행 중이므로 새 인스턴스 시작 안 함 (건너뜀)
  → 경고 로그: "Execution of job skipped: maximum number of instances reached"

max_instances 미설정 (기본 1):
  → 기본값이 1이므로 동일 동작
  → 명시적으로 써두는 것이 의도를 드러냄
```

---

### coalesce

```python
scheduler.add_job(..., coalesce=True)
```

**문제:** 서버가 오래 다운되어 여러 번 실행을 놓쳤으면?

```
설정: 매일 03:00, coalesce=True

시나리오: 월~목 서버 다운, 금요일 재시작
  놓친 실행: 월, 화, 수, 목 (4회)

coalesce=True:  가장 최근 1번만 실행 (목요일 것만)
coalesce=False: 4번 연속 실행
```

뉴스/트렌드 수집처럼 "오늘 최신 데이터"가 목적이면 `coalesce=True`가 적합.
회계 정산처럼 "날짜별로 모두 처리"가 목적이면 `coalesce=False`.

---

## 5. 이 프로젝트 최종 권장 설정

```python
def setup_scheduler():
    scheduler.add_job(
        daily_job,
        CronTrigger(hour=3, minute=0),
        id="daily_job",
        replace_existing=True,        # 재시작 시 중복 방지
        misfire_grace_time=3600,      # 1시간 이내 지연 허용
        max_instances=1,              # 동시 실행 방지 (명시적)
        coalesce=True,                # 밀린 건 최근 1회만
    )

    scheduler.add_job(
        quarterly_job,
        CronTrigger(month="1,4,7,10", day=1, hour=4, minute=0),
        id="quarterly_job",
        replace_existing=True,
        misfire_grace_time=86400,     # 분기 작업: 하루 이내 지연 허용
        max_instances=1,
        coalesce=True,
    )
```

---

## 6. 잡 에러 처리 — 스케줄러는 죽지 않는다

```python
async def daily_job():
    raw_news = await crawl_news()
    await process_market_news(raw_news)   # 여기서 예외 발생
    await detect_policy_changes(raw_news)  # 실행 안 됨
    await crawl_trends()                   # 실행 안 됨
```

예외 발생 시:
- **스케줄러 자체는 멈추지 않는다** → 다음 날 03:00에 정상 실행
- **해당 잡의 그 회차만 중단** → 이후 단계 스킵

```python
# 방어적 설계: 단계별 독립 실행
async def daily_job():
    try:
        raw_news = await crawl_news()
    except Exception as e:
        logger.error(f"crawl_news 실패: {e}")
        return  # 뉴스 없으면 이하 처리 의미 없으므로 전체 중단

    results = await asyncio.gather(
        process_market_news(raw_news),
        detect_policy_changes(raw_news),
        return_exceptions=True,       # 하나 실패해도 다른 건 계속
    )
    for r in results:
        if isinstance(r, Exception):
            logger.error(f"처리 실패: {r}")

    # trends와 queue는 독립적이므로 위 실패와 무관하게 실행
    await asyncio.gather(
        crawl_trends(),
        consume_reanalysis_queue(),
        return_exceptions=True,
    )
```

---

## 이해도 측정

### 개념 문항

**C1.** `AsyncIOScheduler`와 `BackgroundScheduler`의 핵심 차이를 FastAPI 관점에서 설명해봐요.

```
답: asyncio는 fastapi와 이벤트 루프를 공유하는 스케줄러, background는 별도 스레드 스케줄러
```

**C2.** `replace_existing`과 `misfire_grace_time`은 각각 어떤 상황에서 동작하는 옵션인지 구분해서 설명해봐요.

```
답: replace_existing: a작업 실행중 b작업 시간 되면 b작업 할지(True)말지(False). misfire_grace_time: a시간에 해야할 작업을 서버가 꺼져있어도 몇초까지 허용해줄지
```

**C3.** `coalesce=True`가 적합한 잡과 `coalesce=False`가 적합한 잡의 예시를 이 프로젝트 기준으로 들어봐요.

```
답: True면 밀린걸 한다, False면 버린다 인데 여기에서는 데이터 수집도 있고 정보 전달도 있으니까 일단 매일 하는 뉴스크롤링을 기준으로 말하면 max_instance=2 정도로 두고, misfire_grace_time을 3일정도로 두면 좋을거같아
```

---

### 코드 감각 문항

**P1.** 아래 코드에서 문제점을 찾고 수정해봐요.

```python
# main.py
from app.collector.scheduler import scheduler, setup_scheduler

scheduler.start()     # 모듈 로드 시점에 바로 시작

app = FastAPI()

@app.on_event("startup")
def on_startup():
    setup_scheduler()
```

```
문제점: 별도의 스레드 루프가 생겨서 나중에 충돌이 있을 수 있음
수정 후: lifespan 함수를 생성해서 직접 주입해주기
```

**P2.** 아래 상황에 맞는 `misfire_grace_time` 값을 설정하고 이유를 써봐요.

```
quarterly_job: 분기 1회 실행, 서버 장애가 최대 3일 지속될 수 있음
daily_job:     매일 실행, 새벽 3시 실행이 목적, 아침 9시 이전이면 의미 있음
```

```
quarterly_job misfire_grace_time = 60*60*24*3.5  이유: 넉넉잡아 3.5일 
daily_job misfire_grace_time = 60*60*6      이유: 6시간까지 오차 허용
```

**P3.** 아래 `daily_job`을 `gather`와 에러 처리를 활용해서 개선해봐요.
(각 단계의 독립성을 고려해서)

```python
async def daily_job():
    raw_news = await crawl_news()
    await process_market_news(raw_news)
    await detect_policy_changes(raw_news)
    await crawl_trends()
    await consume_reanalysis_queue()
```

```python
# 개선 후:
async def daily_job():
  try:
    raw_news = await crawl_news()
  except:
    # 크롤링 실패
    return
  # 트렌드 먼저 시작
  crawl_task = asyncio.create_task(crawl_trends())
  # 뉴스기반 분석
  await asyncio.gather(
    process_market_news(raw_news),
    detect_policy_changes(raw_news),
    return_exceptions=True # 간섭 방지
  )
  # 작업 종료 (이벤트루프에서 제거)
  await crawl_task
  # 마무리 분석 업데이트
  await consume_reanalysis_queue()
```

```
답: # 개선 후 에 기재되어있음
```

---

## 채점 결과

**전체 점수: 72/100**

### 개념 문항 (C1~C3): 16/30

**C1 — 95점**
정확함. "이벤트 루프 공유 여부 + 별도 스레드 여부"를 핵심으로 잘 잡음.

**C2 — 35점**
`replace_existing` 설명이 `max_instances`와 혼동됨.
> replace_existing은 "실행 중 충돌"이 아니라 **"같은 id로 add_job() 다시 호출할 때 중복 등록 방지"** 옵션
> 재시작 시 `setup_scheduler()`가 다시 실행되면 같은 id 잡이 또 등록되는 문제를 막는 것

`misfire_grace_time` 설명은 정확함.

**C3 — 20점**
True/False가 반대로 이해됨.
> coalesce=**True**: 밀린 것 중 **최근 1번만** 실행 (나머지 버림)
> coalesce=**False**: 밀린 것 **전부** 실행

질문은 "각각 어떤 잡에 적합하냐"였는데 max_instances/misfire_grace_time 설정 얘기로 빠짐.

---

### 코드 문항 (P1~P3): 56/70

**P1 — 85점**
문제점, 해결 방향 모두 정확. 구체적인 코드가 없는 점만 아쉬움.

**P2 — 90점**
quarterly_job 3.5일, daily_job 6시간 모두 합리적이고 이유도 맞음.

**P3 — 85점**
논리 구조가 탄탄함. `crawl_trends`를 `create_task`로 미리 시작하는 판단이 특히 좋음.

두 가지만 개선하면 100점:
```python
# 1. except는 로깅 포함하는 게 좋음
except Exception as e:
    logger.error(f"crawl_news 실패: {e}")
    return

# 2. gather 결과를 체크 안 하면 실패 여부를 모름
results = await asyncio.gather(
    process_market_news(raw_news),
    detect_policy_changes(raw_news),
    return_exceptions=True,
)
for r in results:
    if isinstance(r, Exception):
        logger.error(f"처리 실패: {r}")
```

---

### 총평

코드 감각은 5번보다 더 올랐음. P3 구조 설계가 특히 좋았어.

**이번 약점은 개념 C2, C3:**
- `replace_existing` = 중복 등록 방지 (재시작 시)
- `coalesce=True` = 밀린 것 버리고 최근 1번만

이 두 개만 다시 짚고 가면 돼.
