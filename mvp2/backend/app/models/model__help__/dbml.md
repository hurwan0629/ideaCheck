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
  IDEA_ID    bigint      [pk]
  USER_ID    bigint      [not null]
  TITLE      varchar(255) [not null]
  CONTENT    jsonb       [not null]
  STATUS     idea_status [not null, default: 'DRAFT']
  CREATED_AT timestamptz [not null]
  UPDATED_AT timestamptz [not null]
}

Table USER_SUBSCRIPTIONS {
  SUBSCRIPTION_ID bigint              [pk]
  USER_ID         bigint              [not null]
  PLAN_ID         bigint              [not null]
  STATUS          subscription_status [not null, default: 'ACTIVE']
  PRICE_AT_PURCHASE decimal(10,2)     [not null]
  STARTED_AT      timestamptz         [not null]
  ENDED_AT        timestamptz
  CANCELED_AT     timestamptz
}

Table IDEA_ANALYSES {
  ANALYSIS_ID    bigint      [pk]
  IDEA_ID        bigint      [not null, unique]
  RESULT_SUMMARY jsonb
  RESULT_RAW     text
  CREATED_AT     timestamptz [not null]

  Note: '아이디어 1개당 행 1개. AI가 생성하는 분석 데이터.'
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
// Collection Domain
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

Table COMPETITOR_ANALYSIS {
  ANALYSIS_ID     bigint      [pk]
  COMPETITOR_ID   bigint      [not null]
  ANALYSIS_DATE   date        [not null]
  STRENGTHS       jsonb
  WEAKNESSES      jsonb
  CHARACTERISTICS jsonb
  CREATED_AT      timestamptz [not null]

  Note: 'AI 생성 분석. UPDATE 없이 새 행 추가. 최신은 ANALYSIS_DATE DESC LIMIT 1.'
}

Table COMPETITOR_FEATURES {
  FEATURE_ID          bigint       [pk]
  COMPETITOR_ID       bigint       [not null]
  FEATURE_NAME        varchar(255) [not null]
  FEATURE_DESCRIPTION text
  CREATED_AT          timestamptz  [not null]

  Note: '자주 안 바뀌는 기능 정보. 변경 시 새 행 추가.'
}

Table COMPETITOR_POLICIES {
  POLICY_ID     bigint      [pk]
  COMPETITOR_ID bigint      [not null]
  POLICY_DATE   date        [not null]
  POLICY_DATA   jsonb
  CREATED_AT    timestamptz [not null]

  Note: 'POLICY_DATE: 기업 발표일. CREATED_AT: 수집일. UPDATE 없이 이력 보존.'
}

Table MARKET_RAW_SOURCES {
  RAW_SOURCE_ID bigint       [pk]
  SOURCE_NAME   varchar(255) [not null]
  SOURCE_URL    text
  SOURCE_TYPE   source_type  [not null]
  RAW_CONTENT   text
  COLLECTED_AT  timestamptz  [not null]
}

Table MARKET_EXTRACTS {
  EXTRACT_ID    bigint       [pk]
  RAW_SOURCE_ID bigint       [not null]
  TOPIC         varchar(255) [not null]
  SUMMARY       jsonb
  EXTRACTED_DATA text
  CREATED_AT    timestamptz  [not null]
}

Table TRENDS {
  TREND_ID     bigint        [pk]
  TOPIC        varchar(255)  [not null]
  TREND_DATE   date          [not null]
  TREND_SCORE  decimal(10,2)
  SUMMARY      text
  SOURCE       varchar(255)
  CREATED_AT   timestamptz   [not null]

  Note: 'Google Trends / 네이버 데이터랩 등에서 정제된 데이터를 직접 수집.'
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
Ref: AUTH_ACCOUNTS.USER_ID        > USERS.USER_ID
Ref: USER_IDEAS.USER_ID           > USERS.USER_ID
Ref: USER_SUBSCRIPTIONS.USER_ID   > USERS.USER_ID
Ref: USER_SUBSCRIPTIONS.PLAN_ID   > PLANS.PLAN_ID
Ref: IDEA_ANALYSES.IDEA_ID        - USER_IDEAS.IDEA_ID   // 1:1
Ref: IDEA_NOTES.USER_ID           > USERS.USER_ID

// Collection Domain
Ref: COMPETITOR_ANALYSIS.COMPETITOR_ID  > COMPETITORS.COMPETITOR_ID
Ref: COMPETITOR_FEATURES.COMPETITOR_ID  > COMPETITORS.COMPETITOR_ID
Ref: COMPETITOR_POLICIES.COMPETITOR_ID  > COMPETITORS.COMPETITOR_ID
Ref: MARKET_EXTRACTS.RAW_SOURCE_ID      > MARKET_RAW_SOURCES.RAW_SOURCE_ID
```
