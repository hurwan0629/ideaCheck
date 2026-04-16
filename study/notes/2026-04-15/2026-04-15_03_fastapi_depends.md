# 03. FastAPI 의존성 주입 (Depends)

---

## Spring DI와 뭐가 다른가

**Spring Boot:**
```java
@Service
public class UserService {
    @Autowired
    private UserRepository repo;   // 컨테이너가 빈 주입
}
```
- 앱 시작 시 컨테이너가 빈 그래프 분석 → 싱글톤 객체 생성 → 주입
- 런타임엔 이미 다 연결되어 있음
- 스코프: 기본 싱글톤, `@RequestScope`로 요청마다 새 인스턴스

**FastAPI:**
```python
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    ...
```
- 컨테이너 없음. 빈 그래프 없음.
- 요청이 올 때마다 `get_db()` 함수를 **직접 실행**해서 값 생성
- 스코프: 기본이 요청 단위 (Spring의 `@RequestScope`와 같음)

**핵심 차이:**
```
Spring  → 컨테이너가 객체를 미리 만들어두고 주입
FastAPI → 요청마다 함수를 실행해서 그 반환값을 주입
```

---

## Depends() 동작 방식

```python
def get_something():
    return "hello"

@app.get("/")
def route(value: str = Depends(get_something)):
    print(value)  # "hello"
```

FastAPI가 `/` 요청을 받으면:
1. `route` 함수의 파라미터 목록 분석
2. `Depends(get_something)` 발견 → `get_something()` 실행
3. 반환값 `"hello"` → `value`에 주입
4. `route(value="hello")` 실행

---

## 의존성 체인 (Depends가 Depends를 받는 경우)

```python
def get_token(request: Request):
    return request.headers.get("Authorization")

def get_current_user(token: str = Depends(get_token)):
    return decode_token(token)

@app.get("/profile")
def profile(user = Depends(get_current_user)):
    return user
```

FastAPI가 알아서 체인 따라 실행:
```
profile 요청 →
  get_current_user 실행 필요 →
    get_token 실행 필요 →
      token 반환
    → user 반환
  → profile(user=...) 실행
```

Spring의 `@Service → @Repository` 계층 구조랑 비슷하지만,
Spring은 컨테이너가 미리 연결하고, FastAPI는 요청마다 실행한다는 차이.

---

## Generator 함수를 Depends에 쓰는 이유

```python
def get_db():
    db = SessionLocal()
    try:
        yield db        # 여기서 라우터 함수로 db 전달
    finally:
        db.close()      # 라우터 함수 끝나면 여기 실행
```

`yield`를 쓰면 FastAPI가 이렇게 처리:
```
1. get_db() 실행 → yield 전까지 실행 (db 생성)
2. db를 라우터 함수에 주입
3. 라우터 함수 실행 (응답 생성)
4. 응답 반환 후 → yield 이후 finally 실행 (db.close())
```

**왜 이게 필요한가:**
일반 함수(`return db`)로는 라우터 함수가 끝난 후에 close()를 실행할 방법이 없다.
`yield`를 쓰면 FastAPI가 라우터 함수 전후로 코드를 쪼개서 실행해준다.

**Spring 비유:**
```
Spring @Transactional AOP → 메서드 전후에 begin/commit/rollback 자동 삽입
FastAPI yield Depends    → yield 전후에 setup/teardown 자동 실행
```

---

## 파라미터에 주입되는 흐름

```python
@app.get("/items")
def get_items(
    db: Session = Depends(get_db),         # DB 세션
    current_user = Depends(get_current_user),  # 인증 유저
    q: str = None,                          # 쿼리 파라미터 (Depends 아님)
):
    ...
```

FastAPI는 파라미터 타입과 `Depends` 유무를 보고 자동 분류:
- `Depends(...)` → 의존성 함수 실행해서 주입
- 나머지 → 쿼리파라미터 / 경로파라미터 / 바디 등으로 처리

---

## 정리

| | Spring DI | FastAPI Depends |
|---|---|---|
| 주입 시점 | 앱 시작 시 (빈 컨테이너) | 요청마다 함수 실행 |
| 스코프 기본값 | 싱글톤 | 요청 단위 |
| 설정 방법 | @Bean, @Component | 함수 정의 + Depends() |
| 정리 (teardown) | @PreDestroy, DisposableBean | yield 이후 코드 |
| 의존성 체인 | @Autowired 계층 | Depends(Depends(...)) |
