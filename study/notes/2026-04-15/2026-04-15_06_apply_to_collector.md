# 06. collector에 적용

> 04에서 결론 낸 것: 함수마다 세션 → processor 함수가 db를 파라미터로 받는 구조

---

## database.py 위치

```
mvp2/backend/app/
  database.py       ← engine + SessionLocal 여기에
  main.py
  models/
  collector/
    jobs/
      daily.py
    processors/
      market_processor.py
      policy_detector.py
      analysis_generator.py
```

---

## database.py

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/sym_db")

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,   # 커넥션이 살아있는지 쿼리 전에 체크
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# FastAPI 라우터용 (Depends에서 씀)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

`pool_pre_ping=True` — 오래된 커넥션이 끊겨 있으면 자동으로 재연결.
새벽 3시 job이라 밤새 커넥션이 죽어있을 수 있어서 필요.

---

## jobs/daily.py — 세션 열고 processor에 전달

```python
# app/collector/jobs/daily.py
from app.database import SessionLocal
from app.collector.crawlers.news_crawler import crawl_news
from app.collector.crawlers.trends_crawler import crawl_trends
from app.collector.processors.market_processor import process_market_news
from app.collector.processors.policy_detector import detect_policy_changes
from app.collector.queue.reanalysis_queue import consume_reanalysis_queue


def daily_job():
    _run_news_pipeline()
    _run_trends()
    _consume_queue()


def _run_news_pipeline():
    raw_news = crawl_news()   # DB 불필요, 크롤링만

    db = SessionLocal()
    try:
        process_market_news(db, raw_news)
        detect_policy_changes(db, raw_news)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[daily] news pipeline 실패: {e}")
        raise
    finally:
        db.close()


def _run_trends():
    trend_data = crawl_trends()   # DB 불필요, 크롤링만

    db = SessionLocal()
    try:
        save_trends(db, trend_data)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[daily] trends 실패: {e}")
    finally:
        db.close()


def _consume_queue():
    consume_reanalysis_queue()   # 내부에서 세션 직접 관리
```

**왜 단계마다 세션을 따로 여나:**
- 뉴스 저장 성공 후 트렌드에서 실패해도 뉴스는 보존
- 각 단계가 독립적 → 실패가 전파 안 됨

---

## processors/market_processor.py — db를 파라미터로 받음

```python
# app/collector/processors/market_processor.py
from sqlalchemy.orm import Session
from app.models.market_raw_source import MarketRawSource
from app.models.market_extract import MarketExtract
import anthropic

client = anthropic.Anthropic()


def process_market_news(db: Session, raw_news: list[dict]):
    for item in raw_news:
        # 중복 체크
        exists = db.query(MarketRawSource).filter(
            MarketRawSource.url == item["url"]
        ).first()
        if exists:
            continue

        # 원본 저장
        raw = MarketRawSource(
            competitor_id=item.get("competitor_id"),
            title=item["title"],
            url=item["url"],
            content=item["content"],
            source_type="NEWS",
        )
        db.add(raw)
        db.flush()   # id 확보 (commit은 아직 안 함)

        # Claude로 분류
        category = _classify_with_claude(item["content"])
        if category is None:
            continue

        # 분류 결과 저장
        extract = MarketExtract(
            raw_source_id=raw.id,
            category=category,
            summary=item["content"][:500],
        )
        db.add(extract)

    # commit은 caller(daily_job)에서


def _classify_with_claude(content: str) -> str | None:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=50,
        messages=[{
            "role": "user",
            "content": f"다음 뉴스를 PAIN_POINT / MARKET_SIZE / STARTUP_CASE 중 하나로 분류. 해당 없으면 NONE.\n\n{content[:1000]}"
        }]
    )
    result = response.content[0].text.strip()
    return None if result == "NONE" else result
```

**`db.flush()` 쓰는 이유:**
`raw.id`가 `MarketExtract`의 외래키로 필요한데,
`commit()` 전에 flush를 하면 DB에 INSERT SQL이 나가서 id가 채워짐.
(트랜잭션은 아직 열려있음)

---

## processors/policy_detector.py — 세션으로 policy_types 조회

```python
# app/collector/processors/policy_detector.py
from sqlalchemy.orm import Session
from app.models.policy_type import PolicyType
from app.models.competitor_policy import CompetitorPolicy
from app.collector.queue.reanalysis_queue import add_to_queue
from datetime import datetime, timedelta
import anthropic

client = anthropic.Anthropic()


def detect_policy_changes(db: Session, raw_news: list[dict]):
    # POLICY_TYPES에서 policy_props 조회
    policy_types = db.query(PolicyType).filter(PolicyType.is_active == True).all()

    for item in raw_news:
        for pt in policy_types:
            policy_data = _detect_policy_in_article(item["content"], pt)
            if policy_data is None:
                continue

            # INSERT (UPDATE 없음 — 이력 보존)
            record = CompetitorPolicy(
                competitor_id=item.get("competitor_id"),
                policy_type_id=pt.id,
                policy_data=policy_data,
            )
            db.add(record)

        # 30일 내 변경 3회 이상이면 재분석 큐
        _check_reanalysis_threshold(db, item.get("competitor_id"))


def _check_reanalysis_threshold(db: Session, competitor_id: int):
    if competitor_id is None:
        return
    cutoff = datetime.now() - timedelta(days=30)
    count = db.query(CompetitorPolicy).filter(
        CompetitorPolicy.competitor_id == competitor_id,
        CompetitorPolicy.created_at >= cutoff,
    ).count()
    if count >= 3:
        add_to_queue(competitor_id)


def _detect_policy_in_article(content: str, policy_type) -> dict | None:
    props = policy_type.policy_props   # ["tier", "base_price", ...]
    props_str = ", ".join(props)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (
                f"다음 기사에서 '{policy_type.name}' 정책 변경을 감지해줘.\n"
                f"감지되면 다음 필드를 포함한 JSON으로 응답: {props_str}\n"
                f"없으면 NONE.\n\n{content[:1500]}"
            )
        }]
    )
    text = response.content[0].text.strip()
    if text == "NONE":
        return None
    import json
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
```

---

## 구조 요약

```
daily_job()
  ↓
_run_news_pipeline()
  ├─ crawl_news()                    # 크롤링 (DB 없음)
  ├─ db = SessionLocal()             # 세션 열기
  ├─ process_market_news(db, ...)    # db 주입
  ├─ detect_policy_changes(db, ...) # db 주입
  └─ db.commit() / db.close()       # 커밋 + 반납

_run_trends()
  ├─ crawl_trends()                  # 크롤링 (DB 없음)
  ├─ db = SessionLocal()
  ├─ save_trends(db, ...)
  └─ db.commit() / db.close()
```

크롤러(crawler)는 DB 모름 — 순수하게 데이터만 가져옴.
프로세서(processor)는 db를 파라미터로 받아서 저장 담당.
커밋은 job 함수에서 — processor는 add/flush만.
