```dbml
// ==========================================
// Enums
// ==========================================

Enum user_status {
  ACTIVE
  INACTIVE
  BANNED
}

Enum auth_provider {
  LOCAL
  GOOGLE
  KAKAO
}

Enum idea_status {
  DRAFT
  ACTIVE
  ARCHIVED
}

Enum recommendation_type {
  GO              [note: '진입 가능, 차별화 포인트 유효']
  GO_WITH_CAUTION [note: '진입 가능하나 리스크 존재']
  PIVOT           [note: '방향 전환 시 가능']
  RETHINK         [note: '근본적 재검토 필요']
}

Enum subscription_status {
  ACTIVE
  CANCELED
  EXPIRED
  PAUSED
}

Enum plan_name {
  FREE
  PREMIUM
}

Enum billing_cycle {
  NONE
  MONTHLY
  YEARLY
}

Enum source_type {
  NEWS
  BLOG
  REPORT
  COMMUNITY
  ETC
}

Enum extract_type {
  PAIN_POINT   [note: '창업자가 문제를 발견하는 용도']
  MARKET_SIZE  [note: '시장 크기 파악용']
  STARTUP_CASE [note: '선례 참고용']
}

Enum topic_type {
  SOCIAL   [note: '쇼츠 유행, 소비 패턴 등 사회/문화 트렌드']
  BUSINESS [note: '산업 동향, 투자, 규제 등 비즈니스 트렌드']
  TECH     [note: '신기술, AI/SaaS 등 기술 트렌드']
}

// ==========================================
// User Domain
// ==========================================

Table USERS {
  USER_ID         bigint        [pk]
  USER_NAME       varchar(100)  [not null]
  USER_EMAIL      varchar(255)  [not null, unique]
  USER_BIRTH_DATE date
  USER_STATUS     user_status   [not null, default: 'ACTIVE']
  USER_CREATED_AT timestamptz   [not null]
  USER_UPDATED_AT timestamptz   [not null]
}

Table AUTH_ACCOUNTS {
  AUTH_ID          bigint        [pk]
  USER_ID          bigint        [not null]
  PROVIDER         auth_provider [not null]
  PROVIDER_USER_ID varchar(255)  [note: '소셜 제공자 고유 ID. 소셜 로그인 시 사용']
  LOGIN_ID         varchar(255)  [unique, note: '일반 로그인 아이디. LOCAL 방식일 때만 사용']
  PASSWORD_HASH    varchar(255)  [note: '일반 로그인 비밀번호 해시. LOCAL 방식일 때만 사용']
  CREATED_AT       timestamptz   [not null]
}

Table USER_IDEAS {
  IDEA_ID    bigint       [pk]
  USER_ID    bigint       [not null]
  TITLE      varchar(255) [not null]
  CONTENT    jsonb        [not null, note: '린 캔버스 형태. core_idea 필수, 나머지 null 허용(UI에서 고민중 표시).
{
  "core_idea": "소상공인 세금 신고 앱",
  "target_customer": null,
  "business_model": null,
  "differentiation": null,
  "problem_solved": null,
  "why_use_us": null,
  "tags": ["세무", "B2B"]
}']
  STATUS     idea_status  [not null, default: 'DRAFT']
  CREATED_AT timestamptz  [not null]
  UPDATED_AT timestamptz  [not null]
}

Table IDEA_ANALYSES {
  ANALYSIS_ID       bigint              [pk]
  IDEA_ID           bigint              [not null, unique]
  RECOMMENDATION_TYPE recommendation_type [not null, note: 'UI 색상/아이콘 분기용. GO=초록, GO_WITH_CAUTION=노랑, PIVOT=주황, RETHINK=빨강']
  RESULT_SUMMARY    jsonb               [note: '분석 결과 구조화 데이터.
{
  "scores": {
    "market_growth": 88,
    "competition_intensity": 62,
    "entry_barrier": 45,
    "profitability": 74,
    "differentiation_potential": 91
  },
  "swot": {
    "strength": ["AI 개인화 추천", "정기구독 락인 효과"],
    "weakness": ["콜드스타트 문제", "초기 물류비"],
    "opportunity": ["1인 가구 증가", "건강식 트렌드"],
    "threat": ["대기업 진입", "구독 피로도"]
  },
  "direction": "시장 타이밍이 좋고 차별화 가능성이 높음.",
  "matched_competitors": [
    {
      "id": 100,
      "name": "마켓컬리",
      "similarity": 0.87,
      "threat_level": "HIGH",
      "diff_point": "구독 모델 없음. AI 맞춤 기능 없음."
    }
  ],
  "suggestions": ["AI 식단 개인화 고도화", "1인 가구 특화 포지셔닝"],
  "risks": ["대기업 진입 가능성", "구독 피로도 증가"],
  "market_context": ["1인 가구 600만 돌파", "건강식 시장 연 15% 성장"]
}']
  RESULT_RAW        text                [note: 'Claude AI 분석 원문 전체. 구조화 실패 시 fallback용']
  CREATED_AT        timestamptz         [not null]

  Note: '아이디어 1개당 행 1개 (1:1). 재분석 시 기존 행 UPDATE.'
}

Table IDEA_NOTES {
  NOTE_ID    bigint       [pk]
  USER_ID    bigint       [not null]
  TITLE      varchar(255) [not null]
  CONTENT    jsonb        [note: '자유 형태 메모. 구조 없음. 에디터 블록 구조 저장 가능']
  CREATED_AT timestamptz  [not null]
  UPDATED_AT timestamptz  [not null]
}

Table USER_SUBSCRIPTIONS {
  SUBSCRIPTION_ID bigint              [pk]
  USER_ID         bigint              [not null]
  PLAN_ID         bigint              [not null]
  STATUS          subscription_status [not null, default: 'ACTIVE']
  PRICE_AT_PURCHASE decimal(10,2)     [not null, note: '구독 시점의 가격 스냅샷. PLANS.PRICE 변경과 무관하게 보존']
  STARTED_AT      timestamptz         [not null]
  ENDED_AT        timestamptz         [note: '청구 주기 기준 예정 종료일. 해지와 무관']
  CANCELED_AT     timestamptz         [note: '중간 해지 일시. 해지 안 했으면 null']
}

// ==========================================
// Service Domain
// ==========================================

Table PLANS {
  PLAN_ID       bigint        [pk]
  PLAN_NAME     plan_name     [not null]
  DESCRIPTION   text
  PRICE         decimal(10,2) [not null]
  BILLING_CYCLE billing_cycle [not null, default: 'NONE']
  CREATED_AT    timestamptz   [not null]
}

// ==========================================
// Collection Domain
// ==========================================

Table FEATURE_CATEGORIES {
  CATEGORY_ID   bigint       [pk]
  NAME          varchar(100) [not null, unique, note: '예: 세무, 회계, HR, 결제']
  DESCRIPTION   text
  IS_ACTIVE     boolean      [not null, default: true]
  DEPRECATED_AT timestamptz  [note: 'IS_ACTIVE = false 로 바꾼 시점. 하드 DELETE 절대 금지']
  CREATED_AT    timestamptz  [not null]

  Note: '크롤러/AI가 COMPETITOR_FEATURES 채울 때 참조. IS_ACTIVE=true 항목만 신규 수집에 사용.'
}

Table POLICY_TYPES {
  POLICY_TYPE_ID bigint       [pk]
  NAME           varchar(100) [not null, unique, note: '예: 가격 정책, 현지화, 세대 겨냥, 채널 전략']
  DESCRIPTION    text
  POLICY_PROPS   jsonb        [note: '이 유형의 POLICY_DATA가 가져야 할 필드 목록. 크롤러/AI가 POLICY_DATA 채울 때 참조.
예: ["tier", "base_price", "enterprise_contact"]
→ COMPETITOR_POLICIES.POLICY_DATA는 이 목록의 key만 사용해야 함.']
  IS_ACTIVE      boolean      [not null, default: true]
  DEPRECATED_AT  timestamptz  [note: 'IS_ACTIVE = false 로 바꾼 시점. 하드 DELETE 절대 금지']
  CREATED_AT     timestamptz  [not null]

  Note: '크롤러/AI가 COMPETITOR_POLICIES 채울 때 참조. POLICY_PROPS로 POLICY_DATA 구조를 강제. deprecated된 유형도 이력 분석 가능하게 보존.'
}

Table COMPETITORS {
  COMPETITOR_ID   bigint       [pk]
  NAME            varchar(255) [not null]
  TYPE            varchar(50)  [not null, note: '업종 카테고리. 예: IT, 핀테크, 헬스케어']
  DESCRIPTION     text         [note: '서비스 한줄 설명. 공식 사이트 크롤링']
  TARGET_CUSTOMER text         [note: '타겟 고객군. 공식 사이트 크롤링']
  WEBSITE         varchar(255) [note: '공식 사이트. 크롤링 출처 추적용']
  CREATED_AT      timestamptz  [not null]
  UPDATED_AT      timestamptz  [not null]

  Note: '기본 정보. 거의 안 바뀜. 바뀌면 UPDATE로 관리. pgvector 임베딩 대상(RAG 유사도 검색용).'
}

Table COMPETITOR_ANALYSES {
  ANALYSIS_ID   bigint [pk]
  COMPETITOR_ID bigint [not null]
  ANALYSIS_DATE date   [not null, note: '분석 기준일']
  STRENGTH      jsonb  [note: '강점 리스트.
["가격 경쟁력", "넓은 사용자층", "강력한 브랜드"]']
  WEAKNESS      jsonb  [note: '약점 리스트.
["느린 업데이트", "모바일 UX 약함", "고객센터 부재"]']
  CHARACTERISTIC jsonb [note: '시장 포지셔닝 수치. confidence: low=추정/medium/high=실수치. UI에서 low면 추정치 라벨 표시.
{
  "market_share": {
    "estimated_pct": "10-20%",
    "confidence": "low",
    "basis": "앱 리뷰 수, 언론 노출 빈도 기반 추정"
  },
  "growth": {
    "yoy_pct": null,
    "trend": "up",
    "confidence": "medium",
    "basis": "최근 6개월 기사 빈도 증가"
  },
  "keywords": ["SaaS", "B2B", "중소기업"]
}']
  CREATED_AT    timestamptz [not null]

  Note: 'AI 생성 분석. UPDATE 없이 새 행 추가. 최신은 ANALYSIS_DATE DESC LIMIT 1.'
}

Table COMPETITOR_FEATURES {
  FEATURE_ID    bigint       [pk]
  COMPETITOR_ID bigint       [not null]
  CATEGORY_ID   bigint       [note: 'FEATURE_CATEGORIES FK. IS_ACTIVE=true 카테고리만 신규 수집 시 사용']
  FEATURE_NAME  varchar(255) [not null]
  FEATURE_DESC  jsonb        [note: '기능 상세.
{
  "description": "세금 신고서를 자동으로 작성하고 제출합니다",
  "detail": "국세청 API 연동, 부가세/소득세 지원"
}']
  CREATED_AT    timestamptz  [not null]

  Note: '경쟁사 주요 기능 목록. 변경 시 UPDATE 없이 새 행 추가(이력 보존).'
}

Table COMPETITOR_POLICIES {
  POLICY_ID      bigint [pk]
  COMPETITOR_ID  bigint [not null]
  POLICY_TYPE_ID bigint [note: 'POLICY_TYPES FK. IS_ACTIVE=true 유형만 신규 수집 시 사용']
  POLICY_DATE    date   [not null, note: '기업이 해당 정책을 발표/적용한 날짜']
  POLICY_DATA    jsonb  [note: 'POLICY_TYPES.POLICY_PROPS에 정의된 필드 목록을 key로 사용.
크롤러/AI가 해당 policy_type의 policy_props를 읽고 그 구조에 맞게 채움.
예) 가격 정책(policy_props=["tier","base_price","enterprise_contact"]): {"tier": "freemium", "base_price": "월 9,900원", "enterprise_contact": null}
예) 현지화(policy_props=["region","launch_date","localized_features"]): {"region": "동남아", "launch_date": "2024-03", "localized_features": ["베트남어 지원"]}
확인 불가한 필드는 null로 채움.']
  CREATED_AT     timestamptz [not null, note: '수집일시. POLICY_DATE와 다름']

  Note: '시기마다 바뀌는 정책/포지셔닝 이력. UPDATE 없이 새 행 추가(이력 보존).'
}

Table MARKET_RAW_SOURCES {
  RAW_SOURCE_ID bigint      [pk]
  TITLE         varchar(500) [not null, note: '기사 제목']
  SOURCE_URL    text         [note: '원본 링크']
  SOURCE_TYPE   source_type  [not null, note: '수집 매체 분류 (NEWS/BLOG/REPORT/COMMUNITY/ETC)']
  RAW_CONTENT   text         [note: '수집 원문 전체. 재처리 가능하도록 보존']
  PUBLISHED_AT  timestamptz  [note: '기사 발행일. 크롤러가 제공하는 경우 저장']
  COLLECTED_AT  timestamptz  [not null]

  Note: '크롤링/API 수집 원본 저장소. 원본은 절대 삭제하지 않음. 내용 분류(content_type)는 AI 분석 후 MARKET_EXTRACTS.EXTRACT_TYPE에 저장.'
}

Table MARKET_EXTRACTS {
  EXTRACT_ID     bigint       [pk]
  RAW_SOURCE_ID  bigint       [not null]
  EXTRACT_TYPE   extract_type [not null]
  TOPIC          varchar(255) [not null, note: '추출 주제. 예: 세무 자동화, 소상공인 재고 관리']
  PAIN_AREA      varchar(100) [note: '불편함 영역. 예: 세무, 물류, 고용. PAIN_POINT 타입 시 주로 사용']
  EXTRACTED_DATA jsonb        [note: 'AI가 반환한 JSON 그대로 저장. 유형별 구조 다름.
PAIN_POINT:   {"insight": "중소기업 사장 67%가 세무 혼자 처리, 월 8시간 소요", "keywords": ["세무", "중소기업"], "sentiment": "negative"}
MARKET_SIZE:  {"size": "약 3조원", "growth_rate": "연 15%", "source": "한국IDC 2024", "keywords": ["세무SaaS", "B2B"]}
STARTUP_CASE: {"company": "ㅇㅇ스타트업", "problem_targeted": "소상공인 재고 관리", "outcome": "Series A 50억", "keywords": ["재고", "B2B SaaS"]}']
  CREATED_AT     timestamptz  [not null]
}

Table TRENDS {
  TREND_ID    bigint        [pk]
  TOPIC       varchar(255)  [not null, note: '트렌드 주제. 예: 세무 자동화, AI 챗봇']
  TOPIC_TYPE  topic_type    [not null, note: '필터링용. 창업자에게 비즈니스만 보기 등 제공']
  TREND_DATE  date          [not null, note: '기준일']
  TREND_SCORE decimal(10,2) [note: 'source 내부 상대값(0-100). source 간 직접 비교 불가. 시각화 시 source별 분리']
  SUMMARY     text          [note: '트렌드 요약 설명']
  SOURCE      varchar(255)  [note: '출처. 예: google_trends, naver_datalab']
  CREATED_AT  timestamptz   [not null]

  Note: 'RAW 테이블 없이 바로 저장. Google Trends/네이버 DataLab이 이미 정제된 점수값 반환하기 때문.'
}

Table IDEA_TOPIC_STATS {
  STAT_ID    bigint       [pk]
  STAT_DATE  date         [not null, note: '집계일']
  TOPIC      varchar(255) [not null, note: '아이디어 카테고리. 예: 세무, 물류, 헬스케어']
  IDEA_COUNT bigint       [not null, default: 0, note: '해당 날짜에 해당 토픽으로 분석 요청된 아이디어 수']
  CREATED_AT timestamptz  [not null]

  Note: '사용자 아이디어 분석 요청을 카테고리화하여 집계. 인기 검색어 화면에서 사용.'
}

// ==========================================
// Refs
// ==========================================

// User Domain
Ref: AUTH_ACCOUNTS.USER_ID         > USERS.USER_ID
Ref: USER_IDEAS.USER_ID            > USERS.USER_ID
Ref: IDEA_ANALYSES.IDEA_ID         - USER_IDEAS.IDEA_ID
Ref: IDEA_NOTES.USER_ID            > USERS.USER_ID
Ref: USER_SUBSCRIPTIONS.USER_ID    > USERS.USER_ID
Ref: USER_SUBSCRIPTIONS.PLAN_ID    > PLANS.PLAN_ID

// Collection Domain
Ref: COMPETITOR_ANALYSES.COMPETITOR_ID  > COMPETITORS.COMPETITOR_ID
Ref: COMPETITOR_FEATURES.COMPETITOR_ID  > COMPETITORS.COMPETITOR_ID
Ref: COMPETITOR_FEATURES.CATEGORY_ID    > FEATURE_CATEGORIES.CATEGORY_ID
Ref: COMPETITOR_POLICIES.COMPETITOR_ID  > COMPETITORS.COMPETITOR_ID
Ref: COMPETITOR_POLICIES.POLICY_TYPE_ID > POLICY_TYPES.POLICY_TYPE_ID
Ref: MARKET_EXTRACTS.RAW_SOURCE_ID      > MARKET_RAW_SOURCES.RAW_SOURCE_ID
```
