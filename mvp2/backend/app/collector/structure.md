# collector 구조

## 폴더 구조

```
collector/
  scheduler.py          ← 스케줄러 인스턴스 + job 등록
  jobs/
    daily.py            ← 매일 오전 3시 실행
    quarterly.py        ← 분기 1회 실행 (1/4/7/10월 1일 오전 4시)
  crawlers/
    news_crawler.py     ← 뉴스 수집 (httpx + BeautifulSoup)
    trends_crawler.py   ← 트렌드 점수 수집 (Google Trends, 네이버 DataLab)
    competitor_crawler.py ← 경쟁사 사이트 수집 (httpx 또는 Playwright)
  processors/
    market_processor.py ← 뉴스 저장 + Claude로 분류
    policy_detector.py  ← 경쟁사 정책 변경 감지
    analysis_generator.py ← 경쟁사 종합 분석 + 임베딩 생성
  queue/
    reanalysis_queue.py ← 재분석 대기열 (메모리 set)
```

---

## 실행 흐름

### daily_job (매일 오전 3시)

```
crawl_news()
  └→ 경쟁사 키워드로 뉴스 검색 → 본문 파싱 → list[dict] 반환

process_market_news(raw_news)
  └→ MARKET_RAW_SOURCES 저장
  └→ Claude Sonnet으로 분류 (PAIN_POINT / MARKET_SIZE / STARTUP_CASE)
  └→ 유의미한 것만 MARKET_EXTRACTS 저장

detect_policy_changes(raw_news)
  └→ DB에서 POLICY_TYPES + policy_props 조회
  └→ Claude Haiku에게 정책 유형별 policy_props 전달 → POLICY_DATA 필드 지정
  └→ 변경 있으면 COMPETITOR_POLICIES 저장 (이력 보존, UPDATE 없음)
  └→ 30일 내 변경 3회 이상 → reanalysis_queue에 추가

crawl_trends()
  └→ Google Trends + 네이버 DataLab → TRENDS 저장 (upsert)

consume_reanalysis_queue()
  └→ 큐에 쌓인 경쟁사 즉시 재분석 (generate_analysis_for_one 단건 호출)
```

### quarterly_job (분기 1회)

```
crawl_competitors()
  └→ 경쟁사 공식 사이트 크롤링
  └→ COMPETITORS, COMPETITOR_FEATURES 갱신

generate_analyses_for_all()
  └→ 전 경쟁사 generate_analysis_for_one() 순차 호출
  └→ Claude Sonnet으로 강점/약점/특성 분석
  └→ COMPETITOR_ANALYSES 저장 (이력 보존)
  └→ 임베딩 생성 → pgvector 저장 (RAG용)
```

---

## 설계 결정

### 왜 전부 def (동기)인가

AsyncIOScheduler는 `def` 함수를 받으면 내부적으로 스레드풀(run_in_executor)에서 실행한다.
이벤트 루프와 분리되므로 블로킹 걱정 없음.

실행 주기가 최소 하루 1번 + 새벽 3시이므로 비동기로 얻을 이점이 없다.
단순하게 동기로 전부 통일.

### 크롤러 방식 분기

| 사이트 유형 | 방식 |
|---|---|
| 정적 HTML | httpx.Client + BeautifulSoup |
| JS 렌더링 필요 | playwright.sync_api.sync_playwright |

Playwright도 `sync_api`가 있어서 async 없이 사용 가능.

### 재분석 큐가 set인 이유

같은 경쟁사가 하루에 여러 번 큐에 들어와도 1번만 처리하면 된다.
set의 중복 제거 특성이 딱 맞음.
단점은 서버 재시작 시 초기화. MVP에선 허용, 추후 Redis로 교체 가능.

### policy_detector가 저장할 때 UPDATE 없이 INSERT인 이유

정책은 히스토리가 중요하다. "언제 가격이 바뀌었는지"를 추적하려면 새 행을 쌓아야 함.
최신 정책은 `ORDER BY created_at DESC LIMIT 1`로 조회.

---

## 각 파일 연결 관계

```
scheduler.py
  → jobs/daily.py
  → jobs/quarterly.py

jobs/daily.py
  → crawlers/news_crawler.py
  → processors/market_processor.py
  → processors/policy_detector.py   → queue/reanalysis_queue.py
  → crawlers/trends_crawler.py
  → queue/reanalysis_queue.py       → processors/analysis_generator.py

jobs/quarterly.py
  → crawlers/competitor_crawler.py
  → processors/analysis_generator.py
```
