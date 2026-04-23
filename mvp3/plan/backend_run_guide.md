# SearchYourIdea Backend Run Guide

이 문서는 SearchYourIdea 백엔드를 실제로 실행하고 테스트하는 순서를 정리한 설명서다.
다른 폴더에서 프로젝트를 다시 만들거나 옮겨도 흐름을 그대로 참고할 수 있게 작성한다.

기준 구조:

- `api`: 사용자 요청 처리
- `scheduler`: 정기 크롤링 실행
- `common`: 공통 로직
- `tests`: 테스트 코드

즉, 실행 단위는 보통 2개다.

- API 프로세스 1개
- Scheduler 프로세스 1개

---

# 1. 실행 전에 필요한 것

최소 준비물:

- PostgreSQL
- Python 가상환경
- FastAPI
- SQLAlchemy
- pytest
- 크롤링용 라이브러리
- LLM 호출용 라이브러리

필수 환경 변수 예시:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/searchyouridea
LLM_API_KEY=your_key_here
```

필요하면 아래도 추가할 수 있다.

```env
NEWS_CRAWL_INTERVAL=daily
COMPETITOR_CRAWL_INTERVAL=quarterly
```

---

# 2. 전체 실행 순서

백엔드를 돌릴 때 기본 순서는 아래와 같다.

1. DB 실행
2. API 서버 실행
3. API 기본 확인
4. Scheduler 실행
5. 수동 테스트
6. 자동 테스트

---

# 3. DB 실행

먼저 PostgreSQL이 떠 있어야 한다.

해야 하는 것:

- DB 서버 실행
- 사용할 데이터베이스 생성
- `DATABASE_URL` 연결 확인

예:

```text
DB 이름: searchyouridea
```

ORM이나 migration 도구를 붙인 뒤에는 테이블 생성까지 확인한다.

---

# 4. API 서버 실행

API 서버는 사용자 요청을 처리한다.

역할:

- 아이디어 저장
- 분석 요청
- 분석 결과 조회
- 필요하면 수동 크롤링 실행

실행 예시:

```bash
uvicorn api.main:app --reload
```

또는 프로젝트 구조에 따라:

```bash
python -m api.main
```

중요:

- 이 프로세스는 웹 요청을 기다리는 서버다
- 정기 크롤링을 자동 실행하는 역할은 아니다

---

# 5. Scheduler 실행

Scheduler는 정해진 시간마다 크롤링 job을 실행한다.

역할:

- 뉴스 크롤링 시작
- 경쟁사 크롤링 시작
- 정해진 주기 관리

실행 예시:

```bash
python -m scheduler.main
```

이 프로세스는 API 서버와 별개로 돌아간다.

즉 보통은 아래처럼 2개를 따로 켠다.

```text
터미널 1: API 서버 실행
터미널 2: Scheduler 실행
```

---

# 6. 구조상 실제 호출 흐름

## 사용자 분석 요청

```text
api
-> common/services/analysis_service
-> common/repositories + common/clients
-> DB / LLM
```

## 정기 뉴스 수집

```text
scheduler
-> jobs/crawl_news
-> common/services/crawler_service
-> common/clients/crawler_client
-> common/repositories
-> DB
```

즉 실제 크롤링 로직은 `scheduler`가 아니라 `common/services/crawler_service`에 있다.
`scheduler`는 "언제 실행할지"를 담당한다.

---

# 7. 수동 테스트 순서

처음에는 자동 테스트보다 수동 테스트가 더 빠르다.
아래 순서로 확인하면 된다.

## 1. health 확인

```http
GET /health
```

확인할 것:

- 서버 응답 여부
- 기본 라우팅 정상 여부

## 2. 아이디어 생성

```http
POST /ideas
```

확인할 것:

- DB 저장 성공
- 응답 값에 `idea_id` 포함 여부

## 3. 분석 요청

```http
POST /analysis/{idea_id}
```

확인할 것:

- 아이디어 조회 성공
- LLM 호출 성공
- 분석 결과 저장 성공

## 4. 분석 결과 조회

```http
GET /analysis/{idea_id}/latest
```

확인할 것:

- 최근 분석 결과 조회 가능 여부
- `result_json` 구조 확인

## 5. 수동 크롤링 확인

수동 실행 API를 둘 경우:

```http
POST /crawler/news/run
POST /crawler/competitors/run
```

확인할 것:

- 외부 데이터 수집 여부
- DB 저장 여부
- 실패 시 에러 메시지 확인

---

# 8. 자동 테스트에서 하는 것

`tests/`에서는 API, 서비스, DB 접근이 의도대로 동작하는지 확인한다.

주요 테스트 종류:

- API 테스트
- 서비스 테스트
- 리포지토리 테스트

## API 테스트 예시

- health 응답 확인
- 아이디어 생성 API 확인
- 분석 결과 조회 API 확인

## 서비스 테스트 예시

- 분석 요청 흐름 확인
- 크롤링 결과 정제 확인
- 실패 처리 확인

## 리포지토리 테스트 예시

- 아이디어 저장/조회 확인
- 뉴스 저장/조회 확인
- 경쟁사 저장/조회 확인

---

# 9. pytest 실행 예시

전체 테스트:

```bash
pytest
```

파일별 실행:

```bash
pytest tests/test_health.py
pytest tests/test_ideas.py
pytest tests/test_analysis.py
```

초기 MVP에서는 아래 3개가 우선순위가 높다.

- 아이디어 저장 테스트
- 분석 결과 저장/조회 테스트
- 크롤링 데이터 저장 테스트

---

# 10. 개발 중 추천 실행 순서

실제로 개발할 때는 아래 순서가 가장 무난하다.

1. DB 실행
2. API 서버 실행
3. `GET /health` 확인
4. 아이디어 생성 API 확인
5. 분석 API 확인
6. Scheduler 실행
7. 크롤링 로그 확인
8. pytest 실행

---

# 11. 한 줄 정리

SearchYourIdea 백엔드는 보통 `DB -> API 서버 -> Scheduler -> 수동 테스트 -> pytest` 순서로 실행하고 확인한다.
