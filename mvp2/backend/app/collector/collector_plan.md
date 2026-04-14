# Collector 설계 계획

## 역할
경쟁사 정보, 시장 데이터, 트렌드를 자동 수집·분석해서 DB에 저장하는 백그라운드 시스템.
FastAPI 메인 서버와 같은 프로세스 안에서 APScheduler로 실행.

---

## 폴더 구조

```
app/collector/
│
├── collector_plan.md          ← 이 파일
│
├── __init__.py
├── scheduler.py               ← APScheduler 등록. FastAPI startup에 연결.
│
├── crawlers/                  ← 외부 데이터 수집 (저장은 안 함, 원본 반환만)
│   ├── __init__.py
│   ├── news_crawler.py        ← 뉴스/블로그 크롤링 (경쟁사명 + 키워드 기반)
│   ├── competitor_crawler.py  ← 경쟁사 공식 사이트 크롤링 (기본정보, 기능, 가격 등)
│   └── trends_crawler.py     ← Google Trends / 네이버 DataLab API 호출
│
├── processors/                ← 수집된 원본을 AI로 처리해서 DB에 저장
│   ├── __init__.py
│   ├── market_processor.py    ← RAW 뉴스 → MARKET_RAW_SOURCES 저장 + AI로 MARKET_EXTRACTS 생성
│   ├── policy_detector.py     ← 뉴스에서 경쟁사 정책 변경 감지 → COMPETITOR_POLICIES 저장
│   └── analysis_generator.py ← COMPETITOR_ANALYSES 생성 (AI 종합 분석 + 임베딩)
│
└── queue/                     ← 이벤트 트리거 기반 재분석 큐
    ├── __init__.py
    └── reanalysis_queue.py    ← "정책 변경 N건 이상" 감지 시 재분석 대상 적재
```

---

## 스케줄 구조

### 매일 실행 (daily_job)
```
1. news_crawler      → 뉴스/블로그 수집 (경쟁사명 + 관련 키워드)
2. market_processor  → 수집된 뉴스를 MARKET_RAW_SOURCES 저장
                       AI로 CONTENT_TYPE 분류 (PAIN_POINT / MARKET_DATA / STARTUP_STORY)
                       유의미한 내용 → MARKET_EXTRACTS 생성
3. policy_detector   → 뉴스에서 경쟁사 정책 변경 감지
                       변경 확인 시 → COMPETITOR_POLICIES 새 행 추가
                       30일 내 변경 3건 이상인 경쟁사 → reanalysis_queue 적재
4. trends_crawler    → Google Trends / 네이버 DataLab API 호출 → TRENDS 저장
```

### 분기 실행 (quarterly_job)
```
1. competitor_crawler  → 전 경쟁사 공식 사이트 크롤링
                         COMPETITORS 기본정보 갱신 (변경 시 UPDATE)
                         COMPETITOR_FEATURES 갱신 (변경 시 새 행)
2. analysis_generator  → 전 경쟁사 AI 종합 분석
                         COMPETITOR_ANALYSES 새 행 생성
                         임베딩 벡터 생성 → pgvector 저장 (RAG용)
```

### 이벤트 트리거 (event_job) — 매일 daily_job 직후 실행
```
1. reanalysis_queue 확인
2. 큐에 경쟁사 있으면 → analysis_generator로 해당 경쟁사만 즉시 재분석
3. 큐 비움
```

---

## 주요 라이브러리

| 역할 | 라이브러리 |
|------|-----------|
| 스케줄러 | `APScheduler` (AsyncIOScheduler) |
| HTTP 요청 | `httpx` (async) |
| HTML 파싱 | `BeautifulSoup4` |
| JS 렌더링 사이트 | `Playwright` (필요한 경우만) |
| AI 처리 | `anthropic` (Claude API) |
| 임베딩 | `anthropic` or `openai` embeddings → `pgvector` |
| DB 세션 | SQLAlchemy AsyncSession (기존 app/db.py 재사용) |

---

## 각 파일 역할 상세

### scheduler.py
- APScheduler `AsyncIOScheduler` 초기화
- `daily_job`, `quarterly_job`, `event_job` 등록
- FastAPI `startup` 이벤트에서 `scheduler.start()` 호출
- `shutdown` 이벤트에서 `scheduler.shutdown()` 호출

```python
# main.py 연결 예시
@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(engine)
    scheduler.start()

@app.on_event("shutdown")
async def on_shutdown():
    scheduler.shutdown()
```

---

### crawlers/news_crawler.py
- 입력: 경쟁사명 리스트 + 정책 키워드 리스트
- 출력: `[{ title, url, content, source_type, published_at }]` 원본 리스트
- 저장은 하지 않음 (processor에서 저장)
- 중복 방지: URL 해시를 확인해서 이미 수집된 URL은 skip

---

### crawlers/competitor_crawler.py
- 입력: COMPETITORS 테이블에 등록된 경쟁사 website 목록
- 출력: `{ name, description, target_customer, features[], price_info }` 파싱 결과
- 저장은 하지 않음

---

### crawlers/trends_crawler.py
- Google Trends API (`pytrends`) 또는 네이버 DataLab API 호출
- 입력: 토픽 키워드 목록, TOPIC_TYPE
- 출력: `[{ topic, topic_type, trend_date, trend_score, source }]`
- trends_crawler는 이미 정제된 데이터라 바로 TRENDS 테이블에 저장까지 담당

---

### processors/market_processor.py
- `news_crawler` 결과를 받아서:
  1. MARKET_RAW_SOURCES에 원본 저장
  2. Claude API로 CONTENT_TYPE 분류 + 유의미 여부 판단
  3. 유의미하면 EXTRACT_TYPE, PAIN_AREA, SUMMARY 생성 → MARKET_EXTRACTS 저장
  4. 중복 없는 뉴스만 처리 (RAW_SOURCE_ID 기준)

---

### processors/policy_detector.py
- `news_crawler` 결과 + POLICY_TYPES(is_active=true) 목록을 Claude에 넘겨서:
  - "이 뉴스가 특정 경쟁사의 특정 정책 유형 변경에 해당하는가?" 판단
  - 해당하면 POLICY_DATA 구조 생성 → COMPETITOR_POLICIES 새 행 추가
  - 직전 같은 policy_type_id 행의 POLICY_DATA와 해시 비교 → 동일하면 skip
- 30일 내 변경 건수 집계 → 임계치 초과 경쟁사를 reanalysis_queue에 추가

---

### processors/analysis_generator.py
- 입력: competitor_id (단건 or 전체)
- 해당 경쟁사의 COMPETITOR_FEATURES + COMPETITOR_POLICIES + 최근 뉴스 취합
- Claude API로 STRENGTH, WEAKNESS, CHARACTERISTIC(market_share, growth, keywords) 생성
- COMPETITOR_ANALYSES 새 행 저장
- 임베딩 생성 (description + features + strength/weakness 합산 텍스트) → pgvector 저장
  - RAG에서 아이디어와 유사도 검색할 때 사용

---

### queue/reanalysis_queue.py
- 메모리 내 set 또는 DB 별도 테이블로 관리 (competitor_id 목록)
- `policy_detector`가 적재, `event_job`이 소비
- 재분석 완료 시 해당 id 제거

---

## 변경 감지 전략 (중복 저장 방지)

| 테이블 | 판단 방법 |
|--------|----------|
| MARKET_RAW_SOURCES | SOURCE_URL 해시 중복 체크 |
| COMPETITOR_POLICIES | 직전 같은 policy_type_id 행의 POLICY_DATA JSON 해시 비교 |
| COMPETITOR_FEATURES | 직전 행의 feature_name + feature_desc 해시 비교 |
| COMPETITORS | 필드별 비교 후 변경된 필드만 UPDATE |
| TRENDS | TOPIC + TREND_DATE 복합 unique → 중복 시 upsert |

---

## 추후 고려사항
- 크롤링 실패 시 재시도 로직 (지수 백오프)
- 수집 로그 테이블 (언제 어떤 경쟁사를 크롤했는지 추적)
- 경쟁사 목록 관리 — 관리자 대시보드에서 추가/삭제 가능하게
- Playwright 필요 사이트는 별도 worker로 분리 (무거움)
