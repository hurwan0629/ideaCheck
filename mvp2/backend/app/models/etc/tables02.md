# Tables v2
> ORM 기준 최종 테이블 정의 및 DB 제약조건
> 업데이트: 2026-04-13

---

## 폴더 구조

```
models/
├── user/        사용자 정보 (계정, 아이디어, 구독)
├── service/     서비스 기능 (요금제)
└── collection/  데이터 수집 (경쟁사, 시장, 트렌드)
```

---

## [user] 사용자 정보

### USERS
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| USER_ID | bigint | PK | |
| USER_NAME | varchar(100) | NOT NULL | 이름 또는 닉네임 |
| USER_EMAIL | varchar(255) | NOT NULL, UNIQUE | 대표 이메일 |
| USER_BIRTH_DATE | date | nullable | 생년월일 |
| USER_STATUS | enum | NOT NULL, DEFAULT 'ACTIVE' | ACTIVE / INACTIVE / BANNED |
| USER_CREATED_AT | timestamptz | NOT NULL, DEFAULT now() | |
| USER_UPDATED_AT | timestamptz | NOT NULL | |

---

### AUTH_ACCOUNTS
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| AUTH_ID | bigint | PK | |
| USER_ID | bigint | NOT NULL, FK → USERS.USER_ID | |
| PROVIDER | enum | NOT NULL | LOCAL / GOOGLE / KAKAO ⚠️ NAVER 누락 |
| PROVIDER_USER_ID | varchar(255) | nullable | 소셜 제공자 고유 ID |
| LOGIN_ID | varchar(255) | nullable, UNIQUE | 일반 로그인 아이디 |
| PASSWORD_HASH | varchar(255) | nullable | bcrypt 해시 |
| CREATED_AT | timestamptz | NOT NULL, DEFAULT now() | |

> 관계: USERS 1 : N AUTH_ACCOUNTS (하나의 계정에 여러 로그인 방식)

---

### USER_IDEAS
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| IDEA_ID | bigint | PK | |
| USER_ID | bigint | NOT NULL, FK → USERS.USER_ID | |
| TITLE | varchar(255) | NOT NULL | |
| CONTENT | jsonb | NOT NULL | 폼 입력 구조화 데이터 |
| STATUS | enum | NOT NULL, DEFAULT 'DRAFT' | DRAFT / ACTIVE / ARCHIVED |
| CREATED_AT | timestamptz | NOT NULL, DEFAULT now() | |
| UPDATED_AT | timestamptz | NOT NULL, AUTO UPDATE | |

---

### IDEA_ANALYSES
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| ANALYSIS_ID | bigint | PK | |
| IDEA_ID | bigint | NOT NULL, FK → USER_IDEAS.IDEA_ID | |
| RESULT_SUMMARY | jsonb | nullable | 방향성, 차별화 포인트, 매칭 경쟁사 ID 리스트 |
| RESULT_RAW | text | nullable | AI 분석 원문 |
| CREATED_AT | timestamptz | NOT NULL, DEFAULT now() | |

> 아이디어 1개당 행 1개. 경쟁사 비교는 COMPETITOR_ANALYSIS 참조.
> RESULT_SUMMARY 예시: `{"direction": "...", "differentiation": [...], "matched_competitors": [100, 101]}`

---

### IDEA_NOTES
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| NOTE_ID | bigint | PK | |
| IDEA_ID | bigint | NOT NULL, FK → USER_IDEAS.IDEA_ID | |
| USER_ID | bigint | NOT NULL, FK → USERS.USER_ID | |
| TITLE | varchar(255) | NOT NULL | |
| CONTENT | json | nullable | ⚠️ JSONB로 변경 권장 |
| CREATED_AT | timestamptz | NOT NULL, DEFAULT now() | |
| UPDATED_AT | timestamptz | NOT NULL, AUTO UPDATE | |

---

### USER_SUBSCRIPTIONS
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| SUBSCRIPTION_ID | bigint | PK | |
| USER_ID | bigint | NOT NULL, FK → USERS.USER_ID | |
| PLAN_ID | bigint | NOT NULL, FK → PLANS.PLAN_ID | |
| STATUS | enum | NOT NULL, DEFAULT 'ACTIVE' | ACTIVE / CANCELED / EXPIRED / PAUSED |
| PRICE_AT_PURCHASE | decimal(10,2) | NOT NULL | 구독 시점의 가격 |
| STARTED_AT | timestamptz | NOT NULL, DEFAULT now() | 구독 시작일시 (= 생성일시) |
| ENDED_AT | timestamptz | nullable | 청구 주기 기준 예정 종료일시 |
| CANCELED_AT | timestamptz | nullable | 중간 해지 일시 (null이면 해지 안 함) |

---

## [service] 서비스 기능

### PLANS
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| PLAN_ID | bigint | PK | |
| PLAN_NAME | enum | NOT NULL | FREE / PREMIUM |
| DESCRIPTION | text | nullable | |
| PRICE | numeric(10,2) | NOT NULL | 무료 플랜은 0.00 |
| BILLING_CYCLE | enum | NOT NULL, DEFAULT 'NONE' | NONE / MONTHLY / YEARLY |
| CREATED_AT | timestamptz | NOT NULL, DEFAULT now() | |

---

## [collection] 데이터 수집

### COMPETITORS
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| COMPETITOR_ID | bigint | PK | |
| NAME | varchar(255) | NOT NULL | |
| TYPE | varchar(50) | NOT NULL | 업종 카테고리. Enum 아닌 String (확장성) |
| DESCRIPTION | text | nullable | |
| TARGET_CUSTOMER | text | nullable | |
| WEBSITE | varchar(255) | nullable | 크롤링 출처 추적용 |
| CREATED_AT | timestamptz | NOT NULL, DEFAULT now() | |
| UPDATED_AT | timestamptz | NOT NULL, AUTO UPDATE | |

> 변경 시 UPDATE로 관리 (이력 불필요)

---

### COMPETITOR_FEATURES
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| FEATURE_ID | bigint | PK | |
| COMPETITOR_ID | bigint | NOT NULL, FK → COMPETITORS.COMPETITOR_ID | |
| FEATURE_NAME | varchar(255) | NOT NULL | |
| FEATURE_DESCRIPTION | text | nullable | |
| CREATED_AT | timestamptz | NOT NULL, DEFAULT now() | |

> 기능 변경 시 UPDATE 대신 새 행 추가 (이력 보존)

---

### COMPETITOR_POLICIES
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| POLICY_ID | bigint | PK | |
| COMPETITOR_ID | bigint | NOT NULL, FK → COMPETITORS.COMPETITOR_ID | |
| POLICY_DATE | date | NOT NULL | 기업이 정책을 발표한 날짜 |
| POLICY_DATA | jsonb | nullable | 가격정책, 포지셔닝, 전략 통합 |
| CREATED_AT | timestamptz | NOT NULL, DEFAULT now() | 수집(크롤링)한 날짜 |

> 변경 시 새 행 추가 (이력 보존). POLICY_DATE ≠ CREATED_AT
> POLICY_DATA 예시: `{"price": {"tier": "freemium"}, "positioning": "...", "strategy": "..."}`

---

### COMPETITOR_ANALYSIS
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| ANALYSIS_ID | bigint | PK | |
| COMPETITOR_ID | bigint | NOT NULL, FK → COMPETITORS.COMPETITOR_ID | |
| ANALYSIS_DATE | date | NOT NULL | 분석 기준일 |
| STRENGTHS | jsonb | nullable | 강점 배열. 예: `["가격 경쟁력", "넓은 사용자층"]` |
| WEAKNESSES | jsonb | nullable | 약점 배열. 예: `["느린 업데이트"]` |
| CHARACTERISTICS | jsonb | nullable | `{"market_share": "중위권", "keywords": [...]}` |
| CREATED_AT | timestamptz | NOT NULL, DEFAULT now() | |

> AI가 생성하는 분석 데이터 (COMPETITOR_POLICIES는 사람이 수집).
> 최신 분석 조회: `ORDER BY ANALYSIS_DATE DESC LIMIT 1`
> 변경 시 새 행 추가 (이력 보존)

---

### MARKET_RAW_SOURCES
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| RAW_SOURCE_ID | bigint | PK | |
| SOURCE_NAME | varchar(255) | NOT NULL | 출처명 |
| SOURCE_URL | text | nullable | 원본 링크 |
| SOURCE_TYPE | enum | NOT NULL | NEWS / BLOG / REPORT / COMMUNITY / ETC |
| RAW_CONTENT | text | nullable | 수집 원문 |
| COLLECTED_AT | timestamptz | NOT NULL, DEFAULT now() | |

---

### MARKET_EXTRACTS
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| EXTRACT_ID | bigint | PK | |
| RAW_SOURCE_ID | bigint | NOT NULL, FK → MARKET_RAW_SOURCES.RAW_SOURCE_ID | |
| TOPIC | varchar(255) | NOT NULL | 추출 주제 |
| SUMMARY | jsonb | nullable | 정제 요약 |
| EXTRACTED_DATA | text | nullable | 추출 결과 전문 |
| CREATED_AT | timestamptz | NOT NULL, DEFAULT now() | |

> SOURCE_TYPE = NEWS인 항목을 서비스 내 뉴스 섹션으로 표시 (별도 테이블 불필요)

---

### TRENDS
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| TREND_ID | bigint | PK | |
| TOPIC | varchar(255) | NOT NULL | 트렌드 주제 |
| TREND_DATE | date | NOT NULL | 기준일 |
| TREND_SCORE | numeric(10,2) | nullable | |
| SUMMARY | text | nullable | |
| SOURCE | varchar(255) | nullable | Google Trends, 네이버 데이터랩 등 |
| CREATED_AT | timestamptz | NOT NULL, DEFAULT now() | |

> Google Trends / 네이버 데이터랩 등 외부 API에서 정제된 데이터를 직접 수신.
> RAW 테이블 없음.

---

### IDEA_TOPIC_STATS
| 컬럼 | 타입 | 제약조건 | 비고 |
|---|---|---|---|
| STAT_ID | bigint | PK | |
| STAT_DATE | date | NOT NULL | 집계 기준일 (전날) |
| TOPIC | varchar(255) | NOT NULL | USER_IDEAS에서 추출한 주제 |
| IDEA_COUNT | bigint | NOT NULL, DEFAULT 0 | 해당 주제로 제출된 아이디어 수 |
| CREATED_AT | timestamptz | NOT NULL, DEFAULT now() | |

> 매일 00시 배치로 전날 USER_IDEAS 집계.
> ⚠️ ORM 파일에 오타 있음: 컬럼명 `"IDEA_COUNT로"` → `"IDEA_COUNT"` 수정 필요

---

## 테이블 관계 요약

```
USERS ──< AUTH_ACCOUNTS
USERS ──< USER_IDEAS ──< IDEA_ANALYSES
                    └──< IDEA_NOTES
USERS ──< USER_SUBSCRIPTIONS >── PLANS

COMPETITORS ──< COMPETITOR_FEATURES
           ──< COMPETITOR_POLICIES
           ──< COMPETITOR_ANALYSIS

MARKET_RAW_SOURCES ──< MARKET_EXTRACTS
```

---

## 미해결 항목 (⚠️)

| 파일 | 문제 | 조치 |
|---|---|---|
| `user/auth_accounts.py` | `NAVER` Enum 값 누락 | `NAVER = "NAVER"` 추가 |
| `user/idea_notes.py` | `JSON` → `JSONB` 미변경 | PostgreSQL 최적화를 위해 변경 권장 |
| `collection/idea_topic_stats.py` | 컬럼명 오타 `"IDEA_COUNT로"` | `"IDEA_COUNT"` 로 수정 필요 |
