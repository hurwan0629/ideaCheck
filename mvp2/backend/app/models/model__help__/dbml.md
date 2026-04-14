// 2026-04-14 — feedback.md 논의 반영 업데이트

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

Enum content_type {
  PAIN_POINT     // 사회 문제, 일상 불편함
  MARKET_DATA    // 시장 규모, 성장률 수치
  STARTUP_STORY  // 문제를 겨냥한 스타트업 사례
  ETC
}

Enum extract_type {
  PAIN_POINT    // 불편함/문제 추출
  MARKET_SIZE   // 시장 규모/성장률 추출
  STARTUP_CASE  // 스타트업 사례 추출
}

Enum topic_type {
  SOCIAL    // 쇼츠 유행, 소비 패턴 등 사회/문화
  BUSINESS  // 산업 동향, 투자, 규제 등 비즈니스
  TECH      // 신기술, AI/SaaS 등 기술
}

Enum recommendation_type {
  GO              // 진입 가능, 차별화 포인트 유효
  GO_WITH_CAUTION // 진입 가능하나 리스크 존재
  PIVOT           // 방향 전환하면 가능
  RETHINK         // 근본적 재검토 필요
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
  PROVIDER_USER_ID varchar(255)
  LOGIN_ID         varchar(255)  [unique]
  PASSWORD_HASH    varchar(255)
  CREATED_AT       timestamptz   [not null]
}

Table USER_IDEAS {
  IDEA_ID    bigint       [pk]
  USER_ID    bigint       [not null]
  TITLE      varchar(255) [not null]
  CONTENT    jsonb        [not null, note: '린 캔버스 형태. core_idea 필수, 나머지 null 허용(=고민중). { core_idea, target_customer, business_model, differentiation, problem_solved, why_use_us, tags }']
  STATUS     idea_status  [not null, default: 'DRAFT']
  CREATED_AT timestamptz  [not null]
  UPDATED_AT timestamptz  [not null]
}

Table USER_SUBSCRIPTIONS {
  SUBSCRIPTION_ID   bigint              [pk]
  USER_ID           bigint              [not null]
  PLAN_ID           bigint              [not null]
  STATUS            subscription_status [not null, default: 'ACTIVE']
  PRICE_AT_PURCHASE decimal(10,2)       [not null]
  STARTED_AT        timestamptz         [not null]
  ENDED_AT          timestamptz
  CANCELED_AT       timestamptz
}

Table IDEA_ANALYSES {
  ANALYSIS_ID         bigint              [pk]
  IDEA_ID             bigint              [not null, unique]
  RECOMMENDATION_TYPE recommendation_type [not null, note: 'UI 색상/아이콘 분기용. GO/GO_WITH_CAUTION/PIVOT/RETHINK']
  RESULT_SUMMARY      jsonb               [note: '{ entry_feasibility_score(0-100), direction, differentiation[{point,valid,reason}], matched_competitors[{id,similarity,reason}], risks, suggestions, market_context }']
  RESULT_RAW          text
  CREATED_AT          timestamptz         [not null]

  Note: '아이디어 1개당 행 1개. RAG로 COMPETITOR_ANALYSES + MARKET_EXTRACTS 참조하여 AI 생성.'
}

Table IDEA_NOTES {
  NOTE_ID    bigint       [pk]
  USER_ID    bigint       [not null]
  TITLE      varchar(255) [not null]
  CONTENT    jsonb
  CREATED_AT timestamptz  [not null]
  UPDATED_AT timestamptz  [not null]
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
// Collection Domain — 관리 테이블
// ==========================================

Table FEATURE_CATEGORIES {
  CATEGORY_ID   bigint       [pk]
  NAME          varchar(100) [not null, unique]
  DESCRIPTION   text
  IS_ACTIVE     boolean      [not null, default: true, note: 'false = 신규 수집 중단. 절대 하드 DELETE 안 함.']
  DEPRECATED_AT timestamptz  [note: 'IS_ACTIVE = false 로 바꾼 시점']
  CREATED_AT    timestamptz  [not null]

  Note: '크롤러/AI가 COMPETITOR_FEATURES 채울 때 참조. 관리자 대시보드에서 추가/비활성화.'
}

Table POLICY_TYPES {
  POLICY_TYPE_ID bigint       [pk]
  NAME           varchar(100) [not null, unique]
  DESCRIPTION    text
  IS_ACTIVE      boolean      [not null, default: true, note: 'false = 신규 수집 중단. 절대 하드 DELETE 안 함.']
  DEPRECATED_AT  timestamptz  [note: 'IS_ACTIVE = false 로 바꾼 시점']
  CREATED_AT     timestamptz  [not null]

  Note: '크롤러/AI가 COMPETITOR_POLICIES 채울 때 참조. 관리자 대시보드에서 추가/비활성화.'
}

// ==========================================
// Collection Domain — 경쟁사
// ==========================================

Table COMPETITORS {
  COMPETITOR_ID   bigint       [pk]
  NAME            varchar(255) [not null]
  TYPE            varchar(50)  [not null]
  DESCRIPTION     text
  TARGET_CUSTOMER text
  WEBSITE         varchar(255)
  CREATED_AT      timestamptz  [not null]
  UPDATED_AT      timestamptz  [not null]
}

Table COMPETITOR_FEATURES {
  FEATURE_ID    bigint       [pk]
  COMPETITOR_ID bigint       [not null]
  CATEGORY_ID   bigint       [note: 'FEATURE_CATEGORIES FK. null 허용 (미분류 기능)']
  FEATURE_NAME  varchar(255) [not null]
  FEATURE_DESC  jsonb        [note: '{ description, detail }']
  CREATED_AT    timestamptz  [not null]

  Note: '변경 시 새 행 추가. CATEGORY_ID는 is_active=true 카테고리만 신규 수집 시 사용.'
}

Table COMPETITOR_POLICIES {
  POLICY_ID      bigint [pk]
  COMPETITOR_ID  bigint [not null]
  POLICY_TYPE_ID bigint [note: 'POLICY_TYPES FK. null 허용 (미분류 정책)']
  POLICY_DATE    date   [not null, note: '기업 발표일']
  POLICY_DATA    jsonb  [note: '유형별 자유형. 예) 가격: {tier, base_price} / 현지화: {target_region, language}']
  CREATED_AT     timestamptz [not null, note: '수집일']

  Note: '변경 시 새 행 추가 (이력 보존). POLICY_TYPE_ID는 is_active=true 유형만 신규 수집 시 사용.'
}

Table COMPETITOR_ANALYSES {
  ANALYSIS_ID    bigint [pk]
  COMPETITOR_ID  bigint [not null]
  ANALYSIS_DATE  date   [not null]
  STRENGTH       jsonb  [note: '["가격 경쟁력", "넓은 사용자층"]']
  WEAKNESS       jsonb  [note: '["느린 업데이트", "모바일 UX 약함"]']
  CHARACTERISTIC jsonb  [note: '{ market_share:{estimated_pct,confidence,basis}, growth:{yoy_pct,trend,confidence,basis}, keywords }']
  CREATED_AT     timestamptz [not null]

  Note: 'AI 생성. UPDATE 없이 새 행 추가. 최신은 ANALYSIS_DATE DESC LIMIT 1. confidence: low|medium|high.'
}

// ==========================================
// Collection Domain — 시장/트렌드
// ==========================================

Table MARKET_RAW_SOURCES {
  RAW_SOURCE_ID bigint       [pk]
  SOURCE_NAME   varchar(255) [not null]
  SOURCE_URL    text
  SOURCE_TYPE   source_type  [not null, note: '수집 매체 (NEWS/BLOG/REPORT/COMMUNITY/ETC)']
  CONTENT_TYPE  content_type [not null, note: '수집 내용 성격 (PAIN_POINT/MARKET_DATA/STARTUP_STORY/ETC)']
  RAW_CONTENT   text
  COLLECTED_AT  timestamptz  [not null]
}

Table MARKET_EXTRACTS {
  EXTRACT_ID     bigint       [pk]
  RAW_SOURCE_ID  bigint       [not null]
  EXTRACT_TYPE   extract_type [not null]
  TOPIC          varchar(255) [not null]
  PAIN_AREA      varchar(100) [note: '불편함/문제 영역. EXTRACT_TYPE=PAIN_POINT 일 때 주로 사용. 예: 세무, 물류, 고용']
  SUMMARY        jsonb        [note: 'PAIN_POINT: {insight, keywords, sentiment} / STARTUP_CASE: {company, problem_targeted, outcome, keywords}']
  EXTRACTED_DATA text
  CREATED_AT     timestamptz  [not null]
}

Table TRENDS {
  TREND_ID    bigint        [pk]
  TOPIC       varchar(255)  [not null]
  TOPIC_TYPE  topic_type    [not null, note: 'SOCIAL/BUSINESS/TECH — 필터링용']
  TREND_DATE  date          [not null]
  TREND_SCORE decimal(10,2) [note: 'source 내부 상대값(0-100). source간 직접 비교 불가.']
  SUMMARY     text
  SOURCE      varchar(255)  [note: 'google_trends / naver_datalab 등']
  CREATED_AT  timestamptz   [not null]

  Note: 'Google Trends / 네이버 데이터랩 API에서 이미 정제된 값을 받아 저장. RAW 테이블 없음.'
}

Table IDEA_TOPIC_STATS {
  STAT_ID    bigint       [pk]
  STAT_DATE  date         [not null]
  TOPIC      varchar(255) [not null]
  IDEA_COUNT bigint       [not null, default: 0]
  CREATED_AT timestamptz  [not null]
}

// ==========================================
// Refs
// ==========================================

// User Domain
Ref: AUTH_ACCOUNTS.USER_ID          > USERS.USER_ID
Ref: USER_IDEAS.USER_ID             > USERS.USER_ID
Ref: USER_SUBSCRIPTIONS.USER_ID     > USERS.USER_ID
Ref: USER_SUBSCRIPTIONS.PLAN_ID     > PLANS.PLAN_ID
Ref: IDEA_ANALYSES.IDEA_ID          - USER_IDEAS.IDEA_ID    // 1:1
Ref: IDEA_NOTES.USER_ID             > USERS.USER_ID

// Collection — 관리 테이블
Ref: COMPETITOR_FEATURES.CATEGORY_ID   > FEATURE_CATEGORIES.CATEGORY_ID
Ref: COMPETITOR_POLICIES.POLICY_TYPE_ID > POLICY_TYPES.POLICY_TYPE_ID

// Collection — 경쟁사
Ref: COMPETITOR_ANALYSES.COMPETITOR_ID > COMPETITORS.COMPETITOR_ID
Ref: COMPETITOR_FEATURES.COMPETITOR_ID > COMPETITORS.COMPETITOR_ID
Ref: COMPETITOR_POLICIES.COMPETITOR_ID > COMPETITORS.COMPETITOR_ID

// Collection — 시장
Ref: MARKET_EXTRACTS.RAW_SOURCE_ID     > MARKET_RAW_SOURCES.RAW_SOURCE_ID