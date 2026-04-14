- 생성 완료
Table USERS {
  USER_ID bigint [pk] // 회원 PK
  NAME varchar // 회원 이름 또는 닉네임
  EMAIL varchar // 대표 이메일
  BIRTH_DATE date // 생년월일
  STATUS varchar // 회원 상태
  CREATED_AT datetime // 생성일시
  UPDATED_AT datetime // 수정일시
}

- 생성 완료
Table AUTH_ACCOUNTS {
  AUTH_ID bigint [pk] // 인증방식 PK
  USER_ID bigint [ref: > USERS.USER_ID] // 회원 FK
  PROVIDER varchar // local, google, kakao, naver
  PROVIDER_USER_ID varchar // 소셜 제공자 고유 ID
  LOGIN_ID varchar // 일반 로그인 아이디
  PASSWORD_HASH varchar // 일반 로그인 비밀번호 해시
  CREATED_AT datetime // 생성일시
}

Table PLANS {
  PLAN_ID bigint [pk] // 요금제 PK
  PLAN_NAME varchar // 요금제명
  DESCRIPTION text // 요금제 설명
  PRICE decimal // 가격
  BILLING_CYCLE varchar // monthly, yearly 등
  CREATED_AT datetime // 생성일시
}

Table USER_SUBSCRIPTIONS {
  SUBSCRIPTION_ID bigint [pk] // 회원 구독 PK
  USER_ID bigint [ref: > USERS.USER_ID] // 회원 FK
  PLAN_ID bigint [ref: > PLANS.PLAN_ID] // 요금제 FK
  STATUS varchar // 구독 상태
  PRICE_AT_PURCHASE decimal // 구독 시점의 가격
  STARTED_AT datetime // 구독 시작일시 (= 생성일시)
  ENDED_AT datetime // 청구 주기 기준 예정 종료일시
  CANCELED_AT datetime // 중간 해지 일시 (null이면 해지 안 함)
}

Table USER_IDEAS {
  IDEA_ID bigint [pk] // 사용자 원본 아이디어 PK
  USER_ID bigint [ref: > USERS.USER_ID] // 회원 FK
  TITLE varchar // 아이디어 제목
  CONTENT text // 아이디어 원문
  STATUS varchar // 아이디어 상태
  CREATED_AT datetime // 생성일시
  UPDATED_AT datetime // 수정일시
}

Table IDEA_ANALYSES {
  ANALYSIS_ID bigint [pk] // 아이디어 분석 PK
  IDEA_ID bigint [ref: > USER_IDEAS.IDEA_ID] // 아이디어 FK
  ANALYSIS_TYPE varchar // 시장분석, 경쟁사분석 등
  RESULT_SUMMARY text // 분석 요약
  RESULT_RAW text // AI 분석 원문
  CREATED_AT datetime // 생성일시
}

Table IDEA_NOTES {
  NOTE_ID bigint [pk] // 아이디어 노트 PK
  IDEA_ID bigint [ref: > USER_IDEAS.IDEA_ID] // 아이디어 FK
  USER_ID bigint [ref: > USERS.USER_ID] // 회원 FK
  TITLE varchar // 노트 제목
  CONTENT json // 노트 내용
  CREATED_AT datetime // 생성일시
  UPDATED_AT datetime // 수정일시
}

Table MARKET_RAW_SOURCES {
  RAW_SOURCE_ID bigint [pk] // 시장정보 원본 PK
  SOURCE_NAME varchar // 출처명
  SOURCE_URL text // 원본 링크
  SOURCE_TYPE varchar // 뉴스, 블로그, 리포트 등
  RAW_CONTENT text // 수집 원문
  COLLECTED_AT datetime // 수집일시
}

Table MARKET_EXTRACTS {
  EXTRACT_ID bigint [pk] // 정제 데이터 PK
  RAW_SOURCE_ID bigint [ref: > MARKET_RAW_SOURCES.RAW_SOURCE_ID] // 원본 FK
  TOPIC varchar // 추출 주제
  SUMMARY json // 정제 요약
  EXTRACTED_DATA text // 추출 결과
  CREATED_AT datetime // 생성일시
}

Table COMPETITORS {
  COMPETITOR_ID bigint [pk] // 경쟁사 PK
  NAME varchar // 회사/서비스명
  DESCRIPTION text // 서비스 설명
  TARGET_CUSTOMER text // 타겟 고객
  PRICE_POLICY text // 기본 가격정책
  CREATED_AT datetime // 생성일시
  UPDATED_AT datetime // 수정일시
}

Table COMPETITOR_FEATURES {
  FEATURE_ID bigint [pk] // 경쟁사 기능 PK
  COMPETITOR_ID bigint [ref: > COMPETITORS.COMPETITOR_ID] // 경쟁사 FK
  FEATURE_NAME varchar // 기능명
  FEATURE_DESCRIPTION text // 기능 설명
  CREATED_AT datetime // 생성일시
}

Table COMPETITOR_POLICIES {
  POLICY_ID bigint [pk] // 경쟁사 시점별 정책 PK
  COMPETITOR_ID bigint [ref: > COMPETITORS.COMPETITOR_ID] // 경쟁사 FK
  POLICY_DATE date // 기준일
  POSITIONING text // 현재 포지션
  POLICY_SUMMARY text // 현재 정책/방향 요약
  CREATED_AT datetime // 생성일시
}

Table IDEA_COMPETITOR_COMPARISONS {
  COMPARISON_ID bigint [pk] // 아이디어-경쟁사 비교 PK
  IDEA_ID bigint [ref: > USER_IDEAS.IDEA_ID] // 아이디어 FK
  COMPETITOR_ID bigint [ref: > COMPETITORS.COMPETITOR_ID] // 경쟁사 FK
  COMPARISON_RESULT text // 비교 결과
  CREATED_AT datetime // 생성일시
}

Table TRENDS {
  TREND_ID bigint [pk] // 트렌드 PK
  TOPIC varchar // 트렌드 주제
  TREND_DATE date // 기준일
  TREND_SCORE decimal // 트렌드 점수
  SUMMARY text // 요약
  SOURCE varchar // 출처
  CREATED_AT datetime // 생성일시
}

Table DAILY_TOP_SEARCHES {
  TOP_SEARCH_ID bigint [pk] // 일별 인기 검색어 PK
  SEARCH_DATE date // 집계일
  TOPIC varchar // 검색 주제
  SEARCH_COUNT bigint // 검색 횟수
  CREATED_AT datetime // 생성일시
}