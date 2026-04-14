2026-04-14 — feedback.md 논의 반영 업데이트

# user — 회원 관련
- USERS: 회원
- AUTH_ACCOUNTS: 등록된 회원의 로그인 방식

- IDEA_NOTES: 사용자가 마이페이지에 자유롭게 기록한 아이디어 메모
- USER_IDEAS: 사용자가 분석 요청한 아이디어
  - TITLE: 아이디어 제목 (필수)
  - CONTENT (jsonb): 린 캔버스 형태. core_idea 필수, 나머지 null 허용 (UI에서 "고민중" 표시)
    # {
    #   "core_idea": "...",          // 필수
    #   "target_customer": null,     // null = 고민중
    #   "business_model": null,
    #   "differentiation": null,
    #   "problem_solved": null,
    #   "why_use_us": null,
    #   "tags": []
    # }
    분석 시 AI가 null 항목에 대해 보완 제안 or 질문으로 유도.

- IDEA_ANALYSES: 사용자 아이디어 AI 분석 결과 (아이디어 1개당 1행)
  - RECOMMENDATION_TYPE: GO / GO_WITH_CAUTION / PIVOT / RETHINK — UI 색상/아이콘 분기
  - RESULT_SUMMARY (jsonb): 분석 요약 + 매칭 경쟁사
    # {
    #   "entry_feasibility_score": 72,    // 0-100, AI 근거 기반
    #   "direction": "...",
    #   "differentiation": [{ "point": "...", "valid": true, "reason": "..." }],
    #   "matched_competitors": [{ "id": 100, "similarity": 0.87, "reason": "..." }],
    #   "risks": ["..."],
    #   "suggestions": ["..."],
    #   "market_context": ["..."]         // MARKET_EXTRACTS 기반 시장 맥락
    # }
  - RESULT_RAW (text): AI 분석 원문 전체
  경쟁사 매칭은 pgvector RAG로 수행. 전체 DB 안 넘기고 유사도 Top-K만 LLM context에 전달.

- USER_SUBSCRIPTIONS: 구독한 사용자와 그 기간, 상태, 해지/취소 정보

# service — 서비스 자체 정보
- PLANS: 사용자가 선택 가능한 요금제

# collection — 데이터 수집용 테이블
" 크게 [관리 테이블 / 경쟁사 / 시장·트렌드] 로 이루어져 있다.

## 0. 관리 테이블 (소프트 딜리트 패턴)
- FEATURE_CATEGORIES: 경쟁사 기능 카테고리 목록. 관리자 대시보드에서 추가/비활성화.
  - IS_ACTIVE = false + DEPRECATED_AT 기록으로만 관리. 절대 하드 DELETE 안 함.
  - 크롤러/AI는 IS_ACTIVE = true 카테고리만 참조해서 신규 데이터 생성.
  - 예: "세무", "회계", "HR", "결제"

- POLICY_TYPES: 경쟁사 정책 유형 목록. 관리자 대시보드에서 추가/비활성화.
  - IS_ACTIVE = false + DEPRECATED_AT 기록으로만 관리. 절대 하드 DELETE 안 함.
  - deprecated된 유형도 히스토리 분석 가능 (예: "세대 겨냥 마케팅이 2년 전엔 유행")
  - 예: "가격 정책", "현지화", "세대 겨냥", "채널 전략"

## 1. 경쟁사 (사업 분석)
- COMPETITORS: 경쟁사 기본 정보. 잘 안 바뀌는 것들 (철학, 카테고리, 타겟).
  - DESCRIPTION (text): 서비스 한줄 설명 — 공식 사이트 크롤링
  - TARGET_CUSTOMER (text): 타겟 고객군 — 공식 사이트 크롤링
  - pgvector 임베딩 대상 (RAG 유사도 검색용)

- COMPETITOR_FEATURES: 경쟁사 주요 기능 목록.
  - CATEGORY_ID: FEATURE_CATEGORIES FK. 카테고리 기준으로 기능 분류.
  - FEATURE_DESC (jsonb): { description, detail }
  - 변경 시 새 행 추가.

- COMPETITOR_POLICIES: 시기마다 바뀌는 정책/포지셔닝 이력.
  - POLICY_TYPE_ID: POLICY_TYPES FK. 유형별로 정책 분류.
  - POLICY_DATA (jsonb): 유형별 자유형 (가격/현지화/세대 겨냥 등 필드가 다름)
  - POLICY_DATE: 기업 발표일. CREATED_AT: 수집일. 변경 시 새 행 추가.

- COMPETITOR_ANALYSES: 위 3가지 종합 AI 분석. RAG 매칭 시 참조.
  - STRENGTH (jsonb): ["가격 경쟁력", "넓은 사용자층"]
  - WEAKNESS (jsonb): ["느린 업데이트", "모바일 UX 약함"]
  - CHARACTERISTIC (jsonb): 시장 포지셔닝 수치 (confidence 포함)
    # {
    #   "market_share": { "estimated_pct": "10-20%", "confidence": "low", "basis": "..." },
    #   "growth": { "yoy_pct": null, "trend": "up", "confidence": "medium", "basis": "..." },
    #   "keywords": ["SaaS", "B2B"]
    # }
    confidence: low(추정) | medium | high(실수치). UI에서 low면 "추정치" 라벨 표시.

## 2. 시장 분포
- MARKET_RAW_SOURCES: 크롤링/API로 수집한 원본 데이터.
  - SOURCE_TYPE: 수집 매체 분류 (NEWS/BLOG/REPORT/COMMUNITY/ETC)
  - CONTENT_TYPE: 수집 내용 성격 분류
    - PAIN_POINT: 사회 문제, 일상 불편함 관련 기사 (창업 기회 발견용)
    - MARKET_DATA: 시장 규모, 성장률 수치 (시장 크기 파악용)
    - STARTUP_STORY: 문제 해결 스타트업 사례 (선례 참고용)

- MARKET_EXTRACTS: 원본에서 AI로 추출한 유의미한 정보.
  - EXTRACT_TYPE: PAIN_POINT / MARKET_SIZE / STARTUP_CASE
  - PAIN_AREA: 불편함 영역 (세무, 물류, 고용 등). PAIN_POINT 타입 시 주로 사용.
  - SUMMARY (jsonb): 유형별 구조
    # PAIN_POINT:   { insight, keywords, sentiment }
    # STARTUP_CASE: { company, problem_targeted, outcome, keywords }

## 3. 트렌드
- TRENDS: Google Trends / 네이버 데이터랩 등에서 정제된 데이터 직접 수집.
  - TOPIC_TYPE: SOCIAL(사회/문화) / BUSINESS(산업·투자) / TECH(기술) — 필터링용
  - TREND_SCORE (decimal): source 내부 상대값 (0-100). source간 직접 비교 불가.
  - SOURCE: 출처 명시 (google_trends, naver_datalab 등)

## 4. 사용자 동향
- IDEA_TOPIC_STATS: 분석 요청 아이디어를 카테고리화하여 집계한 통계
  - IDEA_COUNT: 해당 날짜에 해당 토픽으로 분석 요청된 아이디어 수
