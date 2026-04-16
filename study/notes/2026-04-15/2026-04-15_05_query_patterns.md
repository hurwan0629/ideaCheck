# 05. 실제 쿼리 패턴

> 우리 프로젝트 모델 기준으로 실제 쓸 패턴만 정리

---

## SELECT

```python
# 전체 조회
competitors = db.query(Competitor).all()

# 조건 조회
competitor = db.query(Competitor).filter(Competitor.id == 1).first()

# 여러 조건
news_list = db.query(MarketRawSource).filter(
    MarketRawSource.competitor_id == 1,
    MarketRawSource.is_processed == False,
).all()

# 없으면 None (first()는 없으면 None 반환)
policy = db.query(CompetitorPolicy).filter(...).first()
if policy is None:
    ...

# 최신 1개 (이력 테이블에서 자주 씀)
latest_policy = (
    db.query(CompetitorPolicy)
    .filter(CompetitorPolicy.competitor_id == competitor_id)
    .order_by(CompetitorPolicy.created_at.desc())
    .first()
)
```

---

## INSERT

```python
# 인스턴스 만들고 add → commit
news = MarketRawSource(
    competitor_id=1,
    title="제목",
    url="https://...",
    content="본문",
    source_type="NEWS",
)
db.add(news)
db.commit()
print(news.id)     # 있음 — commit 후 expired → 접근 시 lazy reload로 자동 SELECT
# db.refresh(news) 는 명시적으로 즉시 SELECT 원할 때만. 없어도 됨.
```

**주의:** `db.add()` 직후에는 `news.id`가 None — 아직 DB INSERT 전이라 id 미할당.
`db.flush()` 또는 `db.commit()` 후엔 DB가 id를 채워주므로 접근 가능.

---

## UPDATE

```python
# 방법 1: 객체 가져와서 필드 수정
competitor = db.query(Competitor).filter(Competitor.id == 1).first()
competitor.name = "새 이름"
competitor.updated_at = datetime.now()
db.commit()
# → SQLAlchemy가 변경된 필드만 UPDATE SQL 생성
```

```python
# 방법 2: 직접 UPDATE 쿼리 (대량 업데이트에 유리)
db.query(MarketRawSource).filter(
    MarketRawSource.id.in_([1, 2, 3])
).update({"is_processed": True}, synchronize_session=False)
db.commit()
```

우리 프로젝트에서는 대부분 방법 1로 충분.

---

## DELETE

```python
# 객체 가져와서 삭제
old_record = db.query(SomeModel).filter(SomeModel.id == 1).first()
if old_record:
    db.delete(old_record)
    db.commit()
```

우리 프로젝트는 이력 보존 정책이라 DELETE보다 상태 컬럼 변경을 주로 씀.

---

## 우리 프로젝트에서 실제 쓸 패턴들

### 뉴스 저장 (daily_job)
```python
def save_raw_news(db: Session, raw_news: list[dict]):
    for item in raw_news:
        # 중복 URL 체크
        exists = db.query(MarketRawSource).filter(
            MarketRawSource.url == item["url"]
        ).first()
        if exists:
            continue

        record = MarketRawSource(
            competitor_id=item["competitor_id"],
            title=item["title"],
            url=item["url"],
            content=item["content"],
            source_type="NEWS",
        )
        db.add(record)

    db.commit()
```

### 정책 저장 (UPDATE 없이 INSERT만)
```python
def save_policy(db: Session, competitor_id: int, policy_type_id: int, data: dict):
    record = CompetitorPolicy(
        competitor_id=competitor_id,
        policy_type_id=policy_type_id,
        policy_data=data,   # JSONB
    )
    db.add(record)
    db.commit()
```

### 트렌드 upsert (있으면 업데이트, 없으면 삽입)
```python
from sqlalchemy.dialects.postgresql import insert

def upsert_trend(db: Session, keyword: str, score: int):
    stmt = insert(Trend).values(keyword=keyword, score=score)
    stmt = stmt.on_conflict_do_update(
        index_elements=["keyword"],
        set_={"score": score, "updated_at": datetime.now()}
    )
    db.execute(stmt)
    db.commit()
```

### 정책 타입 + policy_props 조회 (policy_detector에서)
```python
policy_types = db.query(PolicyType).filter(PolicyType.is_active == True).all()

for pt in policy_types:
    props = pt.policy_props   # list (JSONB) — ["tier", "base_price", ...]
    ...
```

### 30일 내 정책 변경 카운트 (reanalysis_queue 판단)
```python
from datetime import datetime, timedelta

cutoff = datetime.now() - timedelta(days=30)
count = db.query(CompetitorPolicy).filter(
    CompetitorPolicy.competitor_id == competitor_id,
    CompetitorPolicy.created_at >= cutoff,
).count()

if count >= 3:
    add_to_queue(competitor_id)
```

---

## 자주 실수하는 것

```python
# 실수: commit 없이 add만 하고 끝냄
db.add(record)
# db.commit() 빠짐 → DB에 안 들어감

# 실수: refresh 없이 id 사용
db.add(record)
db.commit()
print(record.id)   # OK — commit 후엔 id 채워짐
                   # refresh() 없어도 SQLAlchemy가 자동으로 가져오는 경우 많음
                   # 명시적으로 쓰고 싶으면 db.refresh(record) 추가
```
