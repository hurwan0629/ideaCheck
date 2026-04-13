2026-04-13 21:48:27 - 테이블의 존재 이유 설명

# user - 회원 관련
- USERS: 회원
- AUTH_ACCOUNTS: 등록된 회원의 로그인 방식

- IDEA_NOTES: 사용자가 마이페이지에 기록한 아이디어
- USER_IDEAS: 사용자가 분석 요청한 아이디어
  - CONTENT (jsonb): 사용자가 직접 입력한 아이디어 원문
    # { "text": "...", "tags": ["핀테크", "B2B"] }
- IDEA_ANALYSES: 사용자가 분석 요청한 아이디어에 대해서 분석
  - RESULT_SUMMARY (jsonb): AI가 생성한 분석 요약 + 매칭 경쟁사 리스트
    # { "direction": "...", "differentiation": ["...", "..."], "matched_competitors": [100, 101] }
  - RESULT_RAW (text): AI가 생성한 분석 원문 전체

- USER_SUBSCRIPTIONS: 구독한 사용자와 그 기간 또는 상태,해지 및 취소 정보

# service - 서비스 자체에 대한 정보
- PLANS: 사용자가 선택 가능한 요금제

# collection - 데이터 수집용 테이블
" 크게 [경쟁사, 트렌드, 주요 사업 관심사] 로 이루어져있다.
1. 경쟁사 (사업분석)
- COMPETITORS: 가장 근본적인 경쟁사 정의로 바뀌지 않을만한 것(경쟁사 철학, 카테고리)
  - DESCRIPTION (text): 서비스 한줄 설명 — 공식 사이트 또는 소개 페이지 크롤링
  - TARGET_CUSTOMER (text): 타겟 고객군 — 공식 사이트 또는 소개 페이지 크롤링

- COMPETITOR_FEATURES: 그 다음으로 잘 바뀌지 않는것 (제공 기능)
  - FEATURE_DESCRIPTION (text): 기능 설명 — 공식 사이트 기능 소개 페이지 크롤링

- COMPETITOR_POLICIES: 트렌드나 시기마다 바뀌는 트렌드관련 (홍보, 마케팅 등등)
  - POLICY_DATA (jsonb): 시점별 가격/포지셔닝/전략 — 공식 사이트 및 뉴스 크롤링
    # { "price": {"tier": "freemium", "base_price": "월 9,900원"}, "positioning": "...", "strategy": "..." }

- COMPETITOR_ANALYSES: 위 3가지를 종합하여 분석한 경쟁사 정보 (특징, 강/약점, 차별화 포인트 등)
  - STRENGTH (jsonb): AI가 생성한 강점 리스트
    # ["가격 경쟁력", "넓은 사용자층"]
  - WEAKNESS (jsonb): AI가 생성한 약점 리스트
    # ["느린 업데이트", "모바일 UX 약함"]
  - CHARACTERISTIC (jsonb): AI가 생성한 포지셔닝/시장 특성
    # { "market_share": "중위권", "growth": "성장중", "keywords": ["SaaS", "B2B"] }

2. 시장 분포
- MARKET_RAW_SOURCES: 크롤링, api 등을 이용하여 가져온 데이터들 저장용
  - RAW_CONTENT (text): 수집 원문 전체 — 뉴스/블로그/리포트 크롤링 또는 API 응답 원문

- MARKET_EXTRACTS: 위 데이터에서 유의미한 데이터 뽑은 것들
  - SUMMARY (jsonb): AI가 추출한 핵심 요약
    # { "insight": "...", "keywords": ["..."], "sentiment": "positive" }
  - EXTRACTED_DATA (text): AI가 추출한 본문 발췌

3. 트렌드
- TRENDS: 구글, 네이버 등에서 정제된 데이터 추출용
  - TREND_SCORE (decimal): 트렌드 점수 — Google Trends / 네이버 DataLab API
  - SUMMARY (text): 트렌드 요약 — API 응답 또는 AI 요약

4. 요즘 상황
- IDEA_TOPIC_STATS: 사용자가 분석 요청한 아이디어를 카테고리화하여 집계한 통계
  - IDEA_COUNT (bigint): 해당 날짜에 해당 토픽으로 분석 요청된 아이디어 수 — USER_IDEAS 기반 집계
