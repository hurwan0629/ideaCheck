# 2026-04-13 02:03:38 - 지금 orm 모델 만들어두긴 했는데 이상한 부분이 보였던거같아서 점검 한번 하려함

AUTH_ACCOUNTS - 문제 없어보임. USERS과 1:N 형태로 관계를 맺어 여러 로그인 방식으로 하나의 계정에 접속 가능하게 되어있음

COMPETITOR_FEATURES - 약간 이상한게 competitor_features말고 COMPETITOR_POLICIES와 COMPETITORS과 겹치는 부분이 존재하는거같음. 아마 설계할 때에는 안변하는 것들과 트렌드나 바뀔 수 있는 부분을 나눠서 설계했던거같은데 뭔가 오류가 난 느낌

COMPETITOR_POLICIES - 위와 비슷하긴 한데 뭘 생각하고 만들었는지 기억이 잘 안남. 아마 트렌드에 따라 어떤식으로 정책을 바꾸었는지 기록하려고 한건가?

COMPETITORS - 이건 아마 대표 사앹를 저장하려 한건데 이걸 COMPETITOR_FEATURES와 합쳐서 안변하는 걸로 만들어야하는건가?

DAILY_TOP_SEARCHES - 이건 확실하게 인기 검색어보다는 사용자가 낸 아이디어를 기록하는 공간으로 두려고 했었음. 예를 들어 면도를 쉽게 해주는 알라미 라고 한다면 "라이프사이클" 관련 검색량이 많다고 기록하는 느낌으로 하려고 했었는데 뭔가 하다보니까 조금 더 섬세한 설정이 필요할듯. 너무 포괄적이면 서비스 기능 품질이 떨어질 수 있으려나?

IDEA_ANALYSES - 사용자가 낸 USER_IDEAS를 기반으로 분석된 데이터를 JSON 형태로 저장하려고 함. 원래 TEXT로 되어있었지만 이번에 ORM 모델 생성중 즉석으로 바꿈. JSONB가 더 좋은거같아서

IDEA_COMPETITOR_COMPARISIONS - 사용자가 낸 아이디어의 경쟁사 분석을 위해 만든건데 이것도 IDEA_ANALYSES과 합쳐야할지 고민중. 경쟁사1, 경쟁사2, 경쟁사3 ... 형태로 만들어서 경쟁사의 약점/강점/특징 등을 뽑아서 사용자에게 카드 형태로 보여줄 생각이였음.

IDEA_NOTES - 이건 명확하게 사용자가 아직 쓰지 않은 아이디어 저장용으로 만든 테이블임 지금 보기에는 큰 문제는 없어보임

MARKET_EXTRACTS - 요즘 시장 상태 (예를 들어 IT시장이 커지는 중)를 분석하기 위해 MARKET_RAW_SOURCES로 부터 정제한 데이터. 동일하게 TEXT 대신 JSONB 채택

MARKET_RAW_SOURCES - 위에 말했듯 시장 점유율 등 확인용으로 수집한 데이터 저장 공간. 이건 SOURCE_TYPE를 왜 만든건지 잘 모르겠음. 뭔가 더 분류할 필요가 있나? 이건 TEXT로 가는게 맞을듯

PLANS - 일반적으로 사용자들이 선택할 수 있는 요금제 리스트용 테이블. 일단 요금제는 무료/유료로만 ㅏㅁㄴ들 생각이였는데 PRICE 테이블을 없애야하나? 계산법을 대신 넣어야하나? 아니면 PRICE도 ENUM으로 만들어야하나?

TRENDS - 사용자들이 요즘 트렌드 확인 가능하게 하기 위해 트렌드 정보 수집하는 공간. 그런데 이것도 RAW데이터와 정제 데이터로 나눠야할거같기도 하고

USER_IDEAS - 사용자가 사업 분석을 위해 주는 데이터. 자유 글쓰기가 아닌 폼을 제공할 것이기 때문에 text -> json으로 content 타입을 바꾸었다. status는 문제있는 아이디어를 거절하고, 사용자가 저장했는지 등을 분석하기 위해 만든 컬럼. updated_at이 필요한지는 잘 모르겠다.

USER_SUBSCRIPTIONS - 사용자가 구독한 상태를 저장하기 위해 사용한 데이터. 그냥 필요한거같다. 적절한듯?




# 2026-04-13 02:21:56 - 클로드의 의견

---

## 전체적인 평가

설계 방향 자체는 맞다. 특히 RAW → EXTRACT 분리, AUTH_ACCOUNTS로 소셜 로그인 분리, IDEA_ANALYSES에 JSONB 채택한 판단은 좋은 선택이다. 아래는 테이블별 구체적인 의견.

---

## COMPETITORS / COMPETITOR_FEATURES / COMPETITOR_POLICIES — 관계 정리

네 고민이 맞다. 현재 세 테이블의 역할이 겹친다.

**권장 구조:**

```
COMPETITORS         → 경쟁사 기본 정보 (이름, 설명, 타겟 고객) — 잘 안 바뀜
COMPETITOR_FEATURES → 경쟁사가 제공하는 기능 목록 — 비교적 안 바뀜
COMPETITOR_POLICIES → 시점별 정책/포지셔닝 변화 — 자주 바뀜
```

- `COMPETITORS.PRICE_POLICY (text)` → 이건 COMPETITOR_POLICIES로 옮기거나 삭제하는 게 맞다. "기본 가격정책"이 Text면 나중에 검색/비교가 어렵다.
- `COMPETITORS.TYPE`을 ORM에서 `IT/FINANCE` Enum으로 만들었는데, 이건 도메인이 늘어날 때 마이그레이션이 필요해지는 구조다. `String(50)`으로 두고 API 레벨에서 검증하는 게 더 유연하다.

**결론:** 세 테이블 분리는 유지하되, COMPETITORS에서 PRICE_POLICY 컬럼을 제거하고 COMPETITOR_POLICIES에 통합하는 걸 추천.

---

## IDEA_ANALYSES — ANALYSIS_TYPE 컬럼 누락

tables.md에는 `ANALYSIS_TYPE varchar`가 있는데 ORM(idea_analyses.py)에서 빠졌다. 이게 없으면 "시장분석인지 경쟁사분석인지"를 구분할 방법이 없다. IDEA_COMPETITOR_COMPARISONS를 IDEA_ANALYSES와 합치려면 이 컬럼이 더 중요해진다.

**IDEA_COMPETITOR_COMPARISONS 합칠지 말지:**
- 합치는 게 맞다고 본다. `ANALYSIS_TYPE = "competitor_comparison"` 하나로 처리하면 API도 단순해지고, 프론트에서 카드 형태로 렌더링할 때도 RESULT_RAW JSONB 안에 `{competitors: [{name, strengths, weaknesses}]}` 구조로 넣으면 충분하다.
- 단, 합칠 경우 IDEA_COMPETITOR_COMPARISONS의 `COMPETITOR_ID` FK가 사라진다. 나중에 "특정 경쟁사가 몇 번 비교됐는지" 쿼리가 필요하다면 분리 유지.

---

## DAILY_TOP_SEARCHES — 목적 재정의 필요

현재 이름(`DAILY_TOP_SEARCHES`)과 네가 생각한 용도("아이디어 카테고리별 검색 빈도")가 안 맞는다.

**두 가지 선택지:**

1. **이름 바꾸기** → `IDEA_TOPIC_STATS` 또는 `TOPIC_DAILY_STATS`로 변경. `SEARCH_COUNT`도 `IDEA_COUNT`나 `SUBMIT_COUNT`로 명확히.
2. **용도 재정의** → 실제로 "사용자들이 어떤 주제로 아이디어를 많이 냈는지" 집계 테이블로 쓰려면 `USER_IDEAS` 기반으로 집계 배치를 돌리는 구조가 되어야 한다.

이름이 의도를 반영 못 하면 나중에 팀원(또는 미래의 나)이 혼란스럽다. 지금 바꾸는 게 제일 쉬운 타이밍.

---

## MARKET_RAW_SOURCES — SOURCE_TYPE의 역할

`SOURCE_TYPE (news, blog, report 등)`은 정제 단계에서 신뢰도 가중치를 다르게 주거나, 특정 타입만 필터링해서 정제할 때 유용하다. 예: 리포트는 높은 신뢰도, 블로그는 낮은 신뢰도.

지금 당장 그 로직이 없다면 넣어둬도 무방하다 — 있어서 해가 될 건 없다. `RAW_CONTENT`는 TEXT가 맞다 (원문 전체를 JSONB로 쓸 이유가 없음).

---

## TRENDS — RAW/EXTRACT 분리 여부

`TRENDS`를 RAW/EXTRACT로 나누는 건 **지금 당장은 오버엔지니어링**이다.

- 트렌드 데이터를 외부 API(Google Trends, 네이버 데이터랩 등)에서 바로 정제해서 받아온다면 RAW가 따로 필요 없다.
- 직접 크롤링해서 원문을 저장한 뒤 별도로 정제하는 파이프라인을 만들 계획이라면 `TREND_RAW_SOURCES` 추가가 맞다.

MVP 단계에서는 현재 단일 테이블 구조로 가고, 파이프라인 복잡도가 올라갈 때 분리 검토 추천.

---

## PLANS — PRICE 컬럼 처리

무료/유료 두 가지만 있을 거라면:

- `PRICE decimal` 유지하되, 무료 플랜은 `0.00`으로 넣으면 된다. ENUM으로 만들 필요 없다.
- `BILLING_CYCLE`도 무료 플랜은 `NULL` 허용하거나 `NONE` Enum 값을 추가하면 된다.
- 현재 ORM에서 `BILLING_CYCLE`이 `nullable=False`인데, 무료 플랜에 billing_cycle이 강제되면 INSERT할 때 문제가 생긴다. `nullable=True`로 바꾸거나 `NONE` Enum 추가 필요.
- `plans.py`에 오타 있음: `PRIMIUM = "PREMIUM"` → Enum 키 이름을 `PREMIUM`으로 맞춰야 한다.

---

## USER_IDEAS — updated_at 필요 여부

필요하다. 사용자가 폼을 수정할 가능성이 있고, "마지막 수정 시점"은 분석 캐시 무효화나 정렬에 유용하다. 그냥 두는 게 맞다.

---

## 요약 액션 아이템

| 우선순위 | 항목 |
|---|---|
| 높음 | `IDEA_ANALYSES`에 `ANALYSIS_TYPE` 컬럼 추가 |
| 높음 | `PLANS.billing_cycle` nullable=True 또는 NONE Enum 추가, 오타 수정 |
| 높음 | `DAILY_TOP_SEARCHES` 테이블명/컬럼명 목적에 맞게 재정의 |
| 중간 | `COMPETITORS.PRICE_POLICY` 제거 → COMPETITOR_POLICIES로 이동 |
| 중간 | `COMPETITORS.TYPE` Enum → String 변경 (유연성) |
| 낮음 | IDEA_COMPETITOR_COMPARISONS 합칠지 최종 결정 |
| 낮음 | TRENDS RAW 분리는 MVP 이후로 보류 |

---

---

# 2026-04-13 02:38:42 - 허완 변경 사항 및 추가 질문

일단 공통 질문을 해보면 컬럼이름을 [테이블]_[컬럼명] 으로 통일하는게 좋을지 아니면 그냥 [커럼명] 만 쓰면 될지 고민된다. 그리고 ENUM이 도메인 레벨에서의 제약 아니였나? 이건 유연한게 아닌 이유가 궁금하다. DB에서 제약조건 안넣고 ORM 모델에 ENUM을 넣으면 문제가 생기나?

AUTH_ACCOUNT - PROVIDER 종류가 늘어날 수 도 있는데 이건 감안하고 ENUM으로 두는게 맞을까?

COMPETITOR_FEATURES - 이거 말한데로 자주 안바뀌는 경쟁사의 기능을 저장할 예정

COMPETITOR_POLICY - 이건 아마 분기마다 바뀌거나 할만한 정보를 저장할 예정. POLICY_DATE와 CREATED_AT 를 구분할 예정. POSITIONING를 통해 저장할 예정. 가격정책도 여기 SUMMARY 등에 넣을 생각인데 컬럼을 따로 만들지, JSON형태로 바꿀지 고민중

COMPETITORS - 이건 말한데로 기업 철학, 타겟, 카테고리 등같이 설정할 예정. 이건 회사가 바뀌면 컬럼 추가 안하고 UPDATE 할 예정

IDEA_ANALYSIS - 사용자 아이디어 분석인데 이것도 DETAIL은 그대로 저장하고 SUMMARY에 분석된 데이터를 저장하는 용도로 사용하는게 좋을거같단 생각함. 이거 경쟁사 분석이랑 합치기 전에 생각한게 만약에 사용자 아이디어1 에 대해서 분석할 때 경쟁사 3개와 비교한다면 [일반 분석, 경쟁사1, 경쟁사2, 경쟁사3] 으로 데이터 행이 4개가 추가되는 방식이 되는건가? 그러면 경쟁사 분석 타입에는 RESULT_SUMMARY에 JSON타입으로 {COMPETITOR_ID: 1234, ANALYSIS: {...}} 와 같이 해도 되지 않을까

IDEA_COMPETITOR_COMPARISIONS - 이건 위에꺼 채택되면 삭제할 예정

IDEA_NOTES - 말한데로 갈 예정.

IDEA_TOPIC_STATS - 이것도 말한데로 매일 00시에 이전날꺼 집계해서 매일 저장하면 되지 않을까 생각중

MARKET_EXTRACTS - 이거ㅓㄴ 현재 파일 그대로 가는거 생각중

MARKET_RAW_SOURCES - 이것도 테이블 형태는 이대로 가도 좋을거같은데 SOURCE_TYPE 종류는 어떤걸로 할지 생각해야할듯

PLANS - BILLING_CYCLE에 NONE(영구) 추가

TRENDS - 말한대로 정제된 데이터를 가져오는걸로 할까 생각했는데 생각해보니까 만드는 서비스에 요즘 트렌드 뉴스같은것도 보여줄까 했는데 어떻게 하면 좋을지 고민중.

USER_IDEAS, USER_SUBSCRIPTIONS - 모두 틀이 정해져있는 기능이라 더 코멘트 없음
---

# 2026-04-13 - 클로드 의견 (2차)

## 공통: 컬럼명 네이밍 컨벤션

`[테이블]_[컬럼명]` 방식은 쓰지 않아도 된다. PK/FK처럼 다른 테이블에서 참조될 컬럼은 `IDEA_ID`, `USER_ID`처럼 테이블명 접두사를 붙이는 게 관행이지만, 나머지는 `NAME`, `STATUS`, `CREATED_AT` 그냥 쓰면 된다. 모든 컬럼에 접두사 붙이면 `COMPETITORS.COMPETITOR_NAME` 같이 중복이 된다. 현재 방식 그대로 유지.

---

## 공통: ENUM — DB 제약 vs ORM만

SQLAlchemy에서 `SqlEnum(MyEnum)`을 쓰면 PostgreSQL에 실제로 `CREATE TYPE ... AS ENUM (...)` DDL이 생긴다. **DB 레벨 제약이 맞다.** 다만 나중에 값을 추가/삭제할 때 `ALTER TYPE` 마이그레이션이 필요하다.

만약 컬럼을 `String(50)`으로 두고 Python Enum만 정의하면 → DB에는 제약 없이 ORM 통할 때만 검증된다. 직접 SQL INSERT나 마이그레이션 스크립트로 bypass하면 잘못된 값이 들어갈 수 있다.

정리하면:
- **ENUM 써야 하는 경우**: 값이 거의 안 바뀌고, 잘못된 값이 들어가면 치명적인 곳 → `AUTH_ACCOUNTS.PROVIDER`, `USER_IDEAS.STATUS`, `ANALYSIS_TYPE`, `BILLING_CYCLE`
- **String이 나은 경우**: 값이 늘어날 가능성이 높은 곳 → `COMPETITORS.TYPE` (업종/카테고리는 계속 늘어날 수 있음)

---

## AUTH_ACCOUNTS — PROVIDER ENUM 유지 여부

ENUM 유지가 맞다. 소셜 로그인 제공자는 서비스 초기에 정해지면 크게 늘지 않고, 인증 관련 컬럼이라 잘못된 값이 들어가면 로그인 자체가 망가진다. 나중에 Apple 로그인 추가할 때 마이그레이션 한 번 감수하면 된다.

그리고 현재 ORM에 `NAVER`가 빠져있다. tables.md에는 있으니 추가 필요.

---

## COMPETITOR_POLICIES — POSITIONING + POLICY_SUMMARY JSONB 통합

JSONB로 바꾸는 게 맞다. 가격정책 + 포지션 + 전략 방향을 Text 하나에 자유 텍스트로 넣으면 나중에 파싱/비교가 불가능해진다. 권장 구조:

```json
{
  "price": {"tier": "freemium", "base_price": "월 9,900원"},
  "positioning": "중소기업 타겟 올인원 SaaS",
  "strategy": "가격 경쟁력으로 대기업 제품 대체"
}
```

`POSITIONING` 별도 컬럼은 JSONB 안으로 흡수하면 된다. 단, 포지셔닝으로 필터링/검색이 필요하다면 별도 컬럼이 유리하다. MVP에서는 검색 조건이 될 가능성이 낮으니 통합 권장.

결론: `POSITIONING text` + `POLICY_SUMMARY text` → `POLICY_DATA jsonb` 하나로 통합.

---

## IDEA_ANALYSES — 행 4개 방식

맞다. 아이디어1 분석 시 테이블 상태:

| ANALYSIS_ID | IDEA_ID | ANALYSIS_TYPE | RESULT_SUMMARY |
|---|---|---|---|
| 1 | 1 | GENERAL | {"market_size": "...", "feasibility": "..."} |
| 2 | 1 | COMPETITOR | {"competitor_id": 100, "analysis": {...}} |
| 3 | 1 | COMPETITOR | {"competitor_id": 101, "analysis": {...}} |
| 4 | 1 | COMPETITOR | {"competitor_id": 102, "analysis": {...}} |

이 방식의 장점: 경쟁사 추가/재분석이 행 하나만 추가하면 되고, API도 단순해진다.

한 가지 고려사항: `competitor_id`가 JSONB 안에 들어가면 FK 제약을 걸 수 없어서 데이터 정합성이 약해진다. 나중에 경쟁사가 삭제됐을 때 고아 데이터가 생길 수 있다. 만약 이게 신경 쓰인다면 `IDEA_ANALYSES`에 `COMPETITOR_ID bigint nullable` 컬럼을 하나 추가하는 방법이 있다. GENERAL 타입이면 NULL, COMPETITOR 타입이면 실제 ID. 선택사항.

---

## IDEA_TOPIC_STATS — 배치 집계

매일 00시에 전날 USER_IDEAS 기준으로 집계하는 방식 좋다. 현재 파일의 컬럼명이 아직 옛날 이름(TOP_SEARCH_ID, SEARCH_DATE, SEARCH_COUNT)으로 되어 있어서 테이블명(IDEA_TOPIC_STATS)이랑 안 맞는다. STAT_ID, STAT_DATE, IDEA_COUNT로 맞춰주면 된다.

---

## TRENDS — 뉴스 표시 기능

두 방향이 있다.

**방향 A: MARKET_EXTRACTS 활용** (권장)
이미 MARKET_RAW_SOURCES → MARKET_EXTRACTS 파이프라인이 있으니 SOURCE_TYPE = NEWS인 것들을 뉴스 섹션으로 보여주면 된다. 추가 테이블/컬럼 없이 기존 파이프라인 재활용.

**방향 B: TRENDS에 플래그 추가**
IS_FEATURED boolean 컬럼 추가. 단순하지만 트렌드 데이터와 뉴스 데이터를 같은 테이블에 섞는 구조가 된다.

MVP에서는 방향 A 권장. TRENDS는 지표성 데이터(점수, 주제, 날짜)에 집중하고, 뉴스 콘텐츠는 MARKET_EXTRACTS에서 가져오는 게 역할이 더 명확하다.

---

## 남은 수정 사항 정리

| 파일 | 수정 내용 |
|---|---|
| auth_accounts.py | NAVER = "NAVER" 추가 |
| competitor_policies.py | POSITIONING + POLICY_SUMMARY → POLICY_DATA jsonb 통합 |
| idea_topic_stats.py | 컬럼명 STAT_ID, STAT_DATE, IDEA_COUNT로 정리 |
| idea_competitor_comparisons.py | 삭제 |
| idea_notes.py | JSON → JSONB (PostgreSQL 최적화) |

# 허완

그런데 회사 강/약점은 정책이 바뀔때마다 바뀔 수 있는데 COMPETITORS와 COMPETITOR_FEATURES는 COMPETITOR_POLICIES에 비해 비교적 덜 바뀔텐데 COMPETITOR_POLICIES에
컬럼을 추가하거나 COMPETITORS_ANALYSIS테이블을 추가하는건 어떨까

---

# 2026-04-13 - 클로드 의견 (3차) — 경쟁사 테이블 4개 구조안

## 역할 정리

```
COMPETITORS          → 기업 기본 정보. 거의 안 바뀜. UPDATE로 관리.
COMPETITOR_FEATURES  → 기능 목록. 기능 추가/제거 시 행 추가.
COMPETITOR_POLICIES  → 정책/포지셔닝 변화 이력. 분기마다 새 행 추가.
COMPETITOR_ANALYSIS  → 강/약점/특징. 아이디어 매칭용 참조 데이터. 주기적 갱신.
```

---

## 테이블 구조안

```
Table COMPETITORS {
  COMPETITOR_ID  bigint       [pk]
  NAME           varchar(255) // 회사/서비스명
  TYPE           varchar(50)  // 업종 카테고리 (IT, 핀테크, 헬스케어 등) — String으로 유연하게
  DESCRIPTION    text         // 서비스 한줄 설명
  TARGET_CUSTOMER text        // 타겟 고객군
  WEBSITE        varchar(255) // 공식 사이트 (크롤링 출처 추적용)
  CREATED_AT     datetime
  UPDATED_AT     datetime
}

Table COMPETITOR_FEATURES {
  FEATURE_ID          bigint       [pk]
  COMPETITOR_ID       bigint       [ref: > COMPETITORS.COMPETITOR_ID]
  FEATURE_NAME        varchar(255) // 기능명
  FEATURE_DESCRIPTION text         // 기능 설명
  CREATED_AT          datetime
  // 기능이 바뀌면 UPDATE 대신 새 행 추가 (이력 보존)
}

Table COMPETITOR_POLICIES {
  POLICY_ID     bigint [pk]
  COMPETITOR_ID bigint [ref: > COMPETITORS.COMPETITOR_ID]
  POLICY_DATE   date   // 정책 기준일 (기업이 발표한 날짜)
  POLICY_DATA   jsonb  // {"price": {...}, "positioning": "...", "strategy": "..."}
  CREATED_AT    datetime
  // POLICY_DATE와 CREATED_AT 분리: 기업이 발표한 시점 vs 우리가 수집한 시점
}

Table COMPETITOR_ANALYSIS {
  ANALYSIS_ID   bigint [pk]
  COMPETITOR_ID bigint [ref: > COMPETITORS.COMPETITOR_ID]
  ANALYSIS_DATE date   // 분석 기준일
  STRENGTHS     jsonb  // ["가격 경쟁력", "넓은 사용자층"]
  WEAKNESSES    jsonb  // ["느린 업데이트", "모바일 UX 약함"]
  CHARACTERISTICS jsonb // {"market_share": "중위권", "growth": "성장중", "keywords": [...]}
  CREATED_AT    datetime
  // 아이디어 매칭 시 ANALYSIS_DATE 기준 최신 행을 참조
  // COMPETITOR_POLICIES와 달리 AI가 생성하는 분석 데이터
}
```

---

## IDEA_ANALYSES 변경 (ANALYSIS_TYPE 제거)

경쟁사 분석을 COMPETITOR_ANALYSIS에 사전 저장하면 IDEA_ANALYSES는 단순해진다.

```
Table IDEA_ANALYSES {
  ANALYSIS_ID    bigint [pk]
  IDEA_ID        bigint [ref: > USER_IDEAS.IDEA_ID]
  // ANALYSIS_TYPE 제거
  RESULT_SUMMARY jsonb  // {"direction": "...", "differentiation": [...], "matched_competitors": [100, 101, 102]}
  RESULT_RAW  jsonb  // AI 분석 전문
  CREATED_AT     datetime
}
```

AI 흐름:
1. 사용자 아이디어 제출
2. COMPETITOR_ANALYSIS에서 유사 경쟁사 매칭
3. 매칭된 경쟁사 기반으로 차별화 포인트 + 방향성 생성
4. IDEA_ANALYSES에 행 1개 저장 (RESULT_SUMMARY에 matched_competitors 리스트 포함)

---

## 고려사항

- COMPETITOR_POLICIES (사람이 수집/크롤링) vs COMPETITOR_ANALYSIS (AI 생성) — 데이터 출처가 다르기 때문에 분리가 맞다
- COMPETITOR_ANALYSIS의 `ANALYSIS_DATE`로 "가장 최신 분석" 쿼리: `ORDER BY ANALYSIS_DATE DESC LIMIT 1`
- STRENGTHS/WEAKNESSES를 jsonb 배열로 두면 나중에 키워드 기반 매칭(`@>` 연산자)도 가능 