추천 아키텍처
1) MVP 단계 아키텍처
A. FastAPI App

역할:

로그인
아이디어 생성/조회
분석 요청 접수
분석 결과 조회
노트/마이페이지
트렌드/인기검색 조회
B. Worker

역할:

크롤링 실행
외부 데이터 수집
분석 파이프라인 실행
경쟁사 비교
일일 배치 집계
C. PostgreSQL

역할:

사용자/구독/아이디어/분석/노트
수집 원본/정제 데이터
트렌드/검색 집계 저장
D. Redis

역할:

작업 큐
캐시
rate limit
최근 조회 데이터 캐싱
가장 현실적인 디렉토리 구조

아래 구조가 네 서비스에 잘 맞아.

app/
├── main.py
├── core/
│   ├── config.py
│   ├── security.py
│   ├── logging.py
│   ├── exceptions.py
│   └── constants.py
│
├── api/
│   ├── deps.py
│   └── v1/
│       ├── router.py
│       ├── auth.py
│       ├── users.py
│       ├── plans.py
│       ├── ideas.py
│       ├── analysis.py
│       ├── trends.py
│       ├── market.py
│       ├── notes.py
│       ├── mypage.py
│       └── admin.py
│
├── schemas/
│   ├── common.py
│   ├── auth.py
│   ├── user.py
│   ├── plan.py
│   ├── idea.py
│   ├── analysis.py
│   ├── trend.py
│   ├── market.py
│   └── note.py
│
├── models/
│   ├── base.py
│   ├── user.py
│   ├── auth_account.py
│   ├── plan.py
│   ├── subscription.py
│   ├── user_idea.py
│   ├── idea_analysis.py
│   ├── idea_note.py
│   ├── market_raw_source.py
│   ├── market_extract.py
│   ├── competitor.py
│   ├── competitor_feature.py
│   ├── competitor_policy.py
│   ├── idea_competitor_comparison.py
│   ├── trend.py
│   └── daily_top_search.py
│
├── db/
│   ├── session.py
│   ├── base.py
│   └── migrations/
│
├── repositories/
│   ├── user_repository.py
│   ├── plan_repository.py
│   ├── idea_repository.py
│   ├── analysis_repository.py
│   ├── trend_repository.py
│   ├── market_repository.py
│   └── note_repository.py
│
├── services/
│   ├── auth_service.py
│   ├── plan_service.py
│   ├── idea_service.py
│   ├── analysis_service.py
│   ├── trend_service.py
│   ├── market_service.py
│   ├── mypage_service.py
│   └── note_service.py
│
├── analyzers/
│   ├── idea/
│   │   ├── suggestion_engine.py
│   │   ├── swot_analyzer.py
│   │   ├── market_score_analyzer.py
│   │   ├── competitor_matcher.py
│   │   ├── strategy_generator.py
│   │   └── pipeline.py
│   │
│   └── market/
│       ├── trend_scorer.py
│       ├── category_classifier.py
│       └── keyword_ranker.py
│
├── collectors/
│   ├── base.py
│   ├── kosis_collector.py
│   ├── publicdata_collector.py
│   ├── google_trends_collector.py
│   ├── naver_datalab_collector.py
│   ├── bigkinds_collector.py
│   ├── kstartup_collector.py
│   ├── dart_collector.py
│   ├── kipris_collector.py
│   └── appstore_collector.py
│
├── extractors/
│   ├── raw_source_parser.py
│   ├── competitor_extractor.py
│   ├── pricing_extractor.py
│   ├── trend_extractor.py
│   └── summary_extractor.py
│
├── tasks/
│   ├── celery_app.py
│   ├── analysis_tasks.py
│   ├── collection_tasks.py
│   ├── trend_tasks.py
│   └── maintenance_tasks.py
│
├── integrations/
│   ├── llm_client.py
│   ├── payment_client.py
│   ├── oauth_google.py
│   ├── oauth_kakao.py
│   ├── oauth_naver.py
│   └── news_client.py
│
├── utils/
│   ├── time.py
│   ├── hashing.py
│   ├── text.py
│   ├── retry.py
│   └── pagination.py
│
└── tests/
    ├── test_auth.py
    ├── test_ideas.py
    ├── test_analysis.py
    ├── test_trends.py
    └── test_collectors.py
폴더 역할을 쉽게 말하면
api/

라우터만 둔다.
여기서는 “요청 받기 / 응답 반환”만 한다.

예:

/ideas
/analyses
/trends
services/

비즈니스 흐름 담당.

예:

아이디어 저장
분석 요청 생성
작업 큐 전달
분석 결과 조합

즉 “실제 일 처리”.

repositories/

DB 접근 전담.

예:

아이디어 저장
분석 결과 조회
경쟁사 목록 조회
analyzers/

네 서비스의 핵심 로직.

예:

SWOT 분석
시장성 점수 계산
경쟁사 유사도 계산
전략 제안 생성
collectors/

외부 데이터 수집 전담.

예:

KOSIS
Google Trends
네이버 데이터랩
BIG KINDS
DART
tasks/

오래 걸리는 작업 비동기 처리.

예:

분석 요청 들어오면 worker가 수행
매일 00:00 인기 검색어 집계
트렌드 데이터 새로 수집
API는 어떻게 나누면 좋냐

네 페이지 설계를 기준으로 하면 이렇게 자르는 게 깔끔해.

1. Auth / User
POST   /api/v1/auth/signup
POST   /api/v1/auth/login
POST   /api/v1/auth/social/google
POST   /api/v1/auth/social/kakao
GET    /api/v1/users/me
PATCH  /api/v1/users/me
2. Pricing / Subscription
GET    /api/v1/plans
POST   /api/v1/subscriptions
GET    /api/v1/subscriptions/me
3. Find Idea
POST   /api/v1/ideas/recommend

입력:

관심 산업
고객층
자본금
팀 여부
기술 보유 여부
최근 불편함
취미
참여도 등

출력:

추천 주제
기능 아이디어
분석 필요 여부

이건 USER_IDEAS에 바로 저장 안 하고,
처음엔 임시 추천 결과로만 줘도 돼.

4. Idea CRUD
POST   /api/v1/ideas
GET    /api/v1/ideas
GET    /api/v1/ideas/{idea_id}
PATCH  /api/v1/ideas/{idea_id}
DELETE /api/v1/ideas/{idea_id}
5. Analyze Idea
POST   /api/v1/analyses
GET    /api/v1/analyses/{analysis_id}
GET    /api/v1/ideas/{idea_id}/analyses

여기서 중요한 건:
POST /analyses는 즉시 분석 완료 응답보다
작업 생성 + status 반환 형태가 더 안전해.

예:

{
  "analysis_id": 101,
  "status": "queued"
}

이후:

GET /api/v1/analyses/101

응답:

{
  "analysis_id": 101,
  "status": "completed",
  "result": {
    "swot": {...},
    "market_score": {...},
    "competitors": [...]
  }
}
6. Trends / Market
GET /api/v1/trends
GET /api/v1/trends/top
GET /api/v1/market-share
GET /api/v1/popular-keywords
GET /api/v1/index/summary
7. Notes / Mypage
GET    /api/v1/mypage
GET    /api/v1/mypage/history
GET    /api/v1/notes
POST   /api/v1/notes
PATCH  /api/v1/notes/{note_id}
DELETE /api/v1/notes/{note_id}