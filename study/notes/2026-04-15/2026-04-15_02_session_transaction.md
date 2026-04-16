# 02. SessionLocal + 트랜잭션

---

## SessionLocal 만들기

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,   # 직접 commit() 호출해야 반영됨
    autoflush=False,    # commit() 전에 자동으로 DB에 flush하지 않음
)
```

`autocommit=False` — Spring JPA 기본값과 동일. 명시적으로 `commit()`을 불러야 트랜잭션 반영.

---

## 세션 여는 3가지 방법

### 방법 1: 수동 (try-finally)
```python
db = SessionLocal()
try:
    db.add(something)
    db.commit()
except Exception:
    db.rollback()
    raise
finally:
    db.close()   # 반드시 실행됨
```

### 방법 2: 컨텍스트 매니저 (with문)
```python
with SessionLocal() as db:
    db.add(something)
    db.commit()
# with 블록 끝나면 자동으로 close()
# 단, rollback은 자동 아님 — 예외 처리 따로 필요
```

### 방법 3: begin() 포함 컨텍스트 매니저
```python
with SessionLocal() as db:
    with db.begin():        # 트랜잭션 시작
        db.add(something)
    # begin() 블록 끝나면 자동 commit 또는 rollback
# 세션도 자동 close
```

**우리 프로젝트(collector)에서 쓸 방식:** 방법 1 또는 2. collector는 단순하게 명시적으로 쓰는 게 낫다.

---

## commit / rollback / close 각 역할

```python
db.add(obj)       # 세션 내 1차 캐시에 추가 (DB엔 아직 안 감)
db.flush()        # 1차 캐시 → DB로 SQL 전송 (트랜잭션은 열린 채)
db.commit()       # 트랜잭션 확정 → DB에 영구 반영
db.rollback()     # 트랜잭션 취소 → DB 변경사항 없던 일로
db.close()        # 세션 종료 → 커넥션 풀에 커넥션 반납
```

**순서가 중요:**
```
add → (flush 자동) → commit   ← 정상 흐름
add → 예외 발생  → rollback → close   ← 에러 흐름
```

---

## 왜 finally에서 close() 해야 하나

```python
db = SessionLocal()
try:
    db.commit()
finally:
    db.close()   # 예외가 나든 안 나든 반드시 실행
```

`close()` 안 하면 커넥션이 풀로 안 돌아간다.
풀 크기(pool_size)가 5이면 close() 5번 빠지면 더 이상 DB 연결 못 함.

**Spring 비유:**
```
Spring @Transactional → AOP가 메서드 감싸서 try-finally 자동 처리
SQLAlchemy → 직접 try-finally 써야 함 (또는 컨텍스트 매니저)
```

---

## autoflush 이해

```python
db = SessionLocal()  # autoflush=False

user = User(name="홍길동")
db.add(user)

# autoflush=True였으면 여기서 SELECT 전에 자동으로 INSERT SQL 날아감
result = db.query(User).filter(User.name == "홍길동").first()

db.commit()
```

`autoflush=False`로 설정한 이유:
- 의도하지 않은 시점에 SQL이 나가는 걸 방지
- 명시적으로 `flush()` 또는 `commit()` 호출할 때만 DB에 반영

---

## 정리

| 메서드 | 하는 일 | 안 하면 |
|---|---|---|
| `db.add(obj)` | 1차 캐시에 올림 | 세션이 obj를 모름 |
| `db.commit()` | DB에 영구 반영 | 재시작하면 사라짐 |
| `db.rollback()` | 변경 취소 | 반쯤 들어간 데이터 남음 |
| `db.close()` | 커넥션 반납 | 풀 고갈 |
