# SearchYourIdea Backend Structure

SearchYourIdea MVP 백엔드는 `api`, `scheduler`, `common` 3개 영역으로 나눈다.

- `api`: 사용자 요청 처리
- `scheduler`: 정기 작업 실행
- `common`: 두 영역이 함께 사용하는 공통 로직

이 구조를 쓰는 이유는 API 서버와 스케줄러는 실행 방식이 다르지만, 실제 업무 로직은 많이 공유하기 때문이다.

---

# 디렉토리 구조

```text
backend/
  api/
    main.py
    router.py
    v1/
      ideas.py
      analysis.py
      crawler.py
      health.py
  scheduler/
    main.py
    jobs/
      crawl_news.py
      crawl_competitors.py
    schedule_runner.py
  common/
    core/
      config.py
      database.py
      logging.py
    models/
      idea.py
      analysis_result.py
      competitor.py
      collected_news.py
    schemas/
      idea.py
      analysis.py
      crawler.py
      common.py
    repositories/
      idea_repository.py
      analysis_repository.py
      competitor_repository.py
      news_repository.py
    services/
      idea_service.py
      analysis_service.py
      crawler_service.py
    clients/
      llm_client.py
      crawler_client.py
    utils/
      time.py
      json.py
  tests/
```

---

# 역할 정리

## `api/`

HTTP 요청을 처리한다.

- 요청 받기
- 입력 검증
- 서비스 호출
- 응답 반환

여기에는 실제 크롤링 로직이나 분석 로직을 길게 두지 않는다.

## `scheduler/`

정기 작업 실행만 담당한다.

- 어떤 job을 언제 돌릴지 관리
- job 시작
- 공통 서비스 호출

즉, 스케줄러는 "언제 실행할지"를 담당하고 "실제 일을 처리하는 곳"은 아니다.

## `common/`

실제 업무 로직을 둔다.

- DB 모델
- repository
- service
- 외부 API client

API와 scheduler는 둘 다 이 공통 영역을 사용한다.

---

# 중요한 기준

실제 크롤링 로직은 `scheduler/` 안에 두지 않는다.
`common/services/crawler_service.py`에 둔다.

이유는 아래와 같다.

- 스케줄러가 호출할 수 있어야 함
- 테스트용 API도 호출할 수 있어야 함
- 같은 로직을 두 군데에 복붙하지 않기 위해

즉 구조는 아래처럼 본다.

```text
api/v1/crawler.py
  -> common/services/crawler_service.py

scheduler/jobs/crawl_news.py
  -> common/services/crawler_service.py
```

---

# 요청 흐름

## 아이디어 분석 요청

```text
api
-> common/services/analysis_service
-> common/repositories + common/clients
-> database / llm
```

예:

1. 사용자가 아이디어를 생성한다
2. 사용자가 분석 요청을 보낸다
3. `analysis_service`가 아이디어, 뉴스, 경쟁사를 조회한다
4. `llm_client`를 호출한다
5. 결과를 저장한다
6. 응답을 반환한다

## 뉴스 정기 수집

```text
scheduler
-> common/services/crawler_service
-> common/clients/crawler_client
-> common/repositories
-> database
```

예:

1. `schedule_runner`가 정해진 시간에 job 실행
2. `crawl_news.py`가 `crawler_service` 호출
3. `crawler_client`가 외부 뉴스 데이터를 가져옴
4. `crawler_service`가 정제 후 저장

---

# crawler 라우터가 있는 이유

`api/v1/crawler.py`는 정기 크롤링용이 아니다.
수동 실행이나 상태 조회용이다.

예:

- 수집 테스트
- 관리자 수동 재실행
- 최근 크롤링 상태 확인

즉 역할은 아래처럼 나뉜다.

- 자동 실행: `scheduler/`
- 수동 실행: `api/v1/crawler.py`
- 실제 크롤링 처리: `common/services/crawler_service.py`

---

# 파일별 핵심 책임

## `api/main.py`

- FastAPI 앱 시작점

## `api/router.py`

- 버전별 라우터 등록

## `scheduler/main.py`

- 스케줄러 시작점

## `scheduler/schedule_runner.py`

- 잡 등록
- 실행 주기 설정

## `scheduler/jobs/crawl_news.py`

- 뉴스 수집 job 실행 파일
- 내부에서 `crawler_service` 호출

## `scheduler/jobs/crawl_competitors.py`

- 경쟁사 수집 job 실행 파일
- 내부에서 `crawler_service` 호출

## `common/services/analysis_service.py`

- 사용자 아이디어 분석 흐름 처리

## `common/services/crawler_service.py`

- 뉴스/경쟁사 수집
- 파싱
- 정제
- 저장

## `common/clients/llm_client.py`

- LLM 호출

## `common/clients/crawler_client.py`

- 외부 사이트 요청
- HTML/API 응답 수집

---

# 왜 이 구조가 좋은가

- API와 scheduler의 역할이 명확하게 분리됨
- 공통 로직 위치가 분명함
- `scheduler`가 `common/services/crawler_service.py`를 자연스럽게 사용할 수 있음
- 테스트용 API와 정기 배치가 같은 로직을 재사용할 수 있음
- 나중에 API 서버와 스케줄러를 따로 배포해도 구조가 유지됨

---

# 한 줄 정리

SearchYourIdea 백엔드는 `api`와 `scheduler`를 실행 단위로 나누고, 실제 업무 로직은 `common`에 모으는 구조가 가장 덜 헷갈리고 재사용하기 쉽다.
