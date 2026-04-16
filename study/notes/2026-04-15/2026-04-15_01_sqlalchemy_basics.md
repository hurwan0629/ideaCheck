# 01. SQLAlchemy 기본 구조

---

## Engine — DB 커넥션 풀

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:password@localhost/dbname",
    pool_size=5,        # 커넥션 풀 크기
    max_overflow=10,    # 풀 초과 시 임시 커넥션 최대 수
)
```

**Spring 비유:**
```
SQLAlchemy Engine  ≈  Spring의 DataSource (HikariCP)
```

- DB 주소, 인증 정보, 커넥션 풀을 들고 있는 객체
- 앱 전체에서 하나만 만들고 공유 (싱글톤)
- 실제 쿼리를 직접 실행하진 않음 — 커넥션을 빌려줄 뿐

---

## Session — 작업 단위

```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    user = session.get(User, 1)
    user.name = "변경"
    session.commit()
```

**Spring 비유:**
```
SQLAlchemy Session  ≈  JPA EntityManager
```

- DB와 대화하는 실제 창구
- 내부에 **1차 캐시(identity map)** 가짐 — 같은 id로 조회하면 DB 안 가고 캐시에서 반환
- `commit()` 전까지 변경사항은 메모리에만 있음
- `close()` 하면 캐시 비우고 커넥션 풀에 반납

---

## Engine → SessionFactory → Session 흐름

```
create_engine()
    ↓
sessionmaker(bind=engine)   ← SessionFactory (설정 묶음)
    ↓
SessionLocal()              ← 실제 Session 인스턴스 생성
    ↓
db.query(...) / db.add() / db.commit()
    ↓
db.close()                  ← 커넥션 풀 반납
```

**Spring 비유:**
```
create_engine()          ≈  DataSource 설정
sessionmaker()           ≈  EntityManagerFactory
SessionLocal() (호출)    ≈  entityManagerFactory.createEntityManager()
db.close()               ≈  entityManager.close()
```

---

## 왜 sessionmaker가 중간에 있나

`Session(engine)`을 매번 직접 써도 되지만,
sessionmaker는 **설정(autocommit, autoflush 등)을 한 번만 정의**하고 재사용하는 팩토리.

```python
# 매번 설정 넘기기 (불편)
Session(engine, autocommit=False, autoflush=False)

# sessionmaker로 설정 고정 (편함)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
db = SessionLocal()  # 설정 이미 박혀있음
```

---

## 정리

| 개념 | 역할 | Spring 대응 |
|---|---|---|
| `create_engine()` | DB 주소 + 커넥션 풀 | DataSource |
| `sessionmaker()` | Session 설정 묶음 | EntityManagerFactory |
| `Session` / `SessionLocal()` | 실제 쿼리 창구 | EntityManager |
| `session.commit()` | 트랜잭션 커밋 | `@Transactional` 끝에 자동 커밋 |
| `session.close()` | 커넥션 풀 반납 | `em.close()` |
