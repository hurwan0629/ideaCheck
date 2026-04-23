# 사용자
일단 전체적인 프로젝트 개요는 아래와 같다.

목표 - 창업 아이디어에 대해서 가능성 검증 및 이유 등을 분석해주는 사이트

타깃 - 바이브 코딩을 통해 개발이 빨라진 지금, 빠른 시작을 위해서 아이디어 및 설계를 빠르게 할 수 있게 해주는 프로그램이 필요한 개발자들

기능:
- 매일 뉴스 크롤링 및 저장 후 현재 트렌드, 경쟁사 상태, 시장 상태 업데이트
- 분기별 경쟁사 크롤링을 통해 경쟁사 추가/삭제/수정와 특징, 장단점 업데이트
- 사용자 입력 아이디어 입력 폼 또는 설문을 통해 원하는 아이디어 받기 및 분석 (비슷한 경쟁사 보여주기, 차별화 포인트 알려주기 또는 리스트 등 알려주기)
- 아이디어 없는 사용자에게 아이디어 어느정도 잡아주는 기능
- 현재 트렌드 보여주기 (주요 뉴스 또는 유행 등)
- 요즘 떠오르는 스타트업, 시장 점유율 등등 보여주기
- 마이 페이지에서 아이디어 분석 기록 등 보여주기

---

# 설계 관점에서 지금 부족한 점

지금 문서는 "무엇을 만들고 싶은지"는 보이지만, "어떻게 설계할지"는 아직 부족하다.

## 1. 문제 정의가 아직 추상적임

- 사용자가 정확히 어떤 상황에서 이 서비스를 쓰는지 더 구체화가 필요하다.
- 예: "아이디어는 있는데 시장성이 불안한 개발자", "아이디어가 아예 없는 개발자", "경쟁사 조사를 빠르게 하고 싶은 1인 개발자"

## 2. 기능 우선순위가 없음

- 현재는 좋은 기능들이 많이 적혀 있지만, MVP와 나중 기능이 섞여 있다.
- 설계 연습에서는 먼저 "최소 기능"을 정해야 구조가 선명해진다.

## 3. 사용자 흐름이 없음

- 사용자가 처음 들어와서 무엇을 누르고, 어떤 입력을 하고, 어떤 결과를 보는지가 문서에 없다.
- 설계에서는 기능 목록보다 사용자 흐름이 먼저 정리되는 편이 좋다.

## 4. 데이터 구조가 없음

- 어떤 데이터를 저장해야 하는지 정리되어 있지 않다.
- 예: 사용자, 아이디어, 분석 결과, 뉴스, 경쟁사, 트렌드 리포트

## 5. 시스템 구성요소 분리가 없음

- 프론트엔드, 백엔드, 크롤러, 분석 로직, 스케줄러, 데이터베이스를 어떻게 나눌지 정해져 있지 않다.
- 이 부분이 있어야 "소프트웨어 설계" 연습이 된다.

## 6. 비기능 요구사항이 없음

- 실시간 분석이 필요한지
- 하루 1회 갱신이면 되는지
- 분석 결과를 몇 초 안에 보여줘야 하는지
- 사용자 수가 늘어나면 어디가 병목이 될지

이런 항목이 아직 빠져 있다.

---

# 지금 단계에서의 판단

현재 상태는 "서비스 아이디어 초안"으로는 괜찮다.

하지만 아직 "설계 문서 초안"이라고 보기에는 아래 항목이 더 필요하다.

- MVP 정의
- 사용자 시나리오
- 핵심 엔티티 정의
- 시스템 컴포넌트 분리
- 데이터 흐름
- 기술 선택 이유

---

# 다음에 하면 좋은 것

## 1. MVP부터 줄이기

처음부터 모든 기능을 설계하지 말고, 아래 3개 정도만 남기는 것이 좋다.

- 사용자가 아이디어를 입력한다
- 시스템이 유사 경쟁사와 차별화 포인트를 분석한다
- 결과를 저장하고 다시 볼 수 있다

이 정도면 핵심 가치가 보인다.

## 2. 사용자 시나리오 3개 작성하기

예시:

1. 사용자는 창업 아이디어를 입력한다.
2. 시스템은 관련 시장/경쟁사 정보를 기반으로 분석 결과를 생성한다.
3. 사용자는 결과에서 경쟁사, 차별점, 리스크를 확인한다.
4. 사용자는 결과를 저장하고 나중에 다시 본다.

이런 식으로 실제 흐름을 먼저 적는 연습이 필요하다.

## 3. 핵심 데이터 정의하기

최소한 아래 정도는 먼저 적어보면 좋다.

- User
- Idea
- AnalysisResult
- Competitor
- TrendReport

각각에 대해 "무슨 정보를 가지는가"를 적어보면 설계가 훨씬 구체화된다.

## 4. 시스템을 컴포넌트로 나누기

초기 버전은 아래 정도로 나누면 충분하다.

- Frontend
- API Server
- Analysis Service
- Crawler
- Scheduler
- Database

여기서 각 컴포넌트의 역할을 1~2줄씩 적으면 설계 연습이 된다.

## 5. 데이터 흐름 1개 그리기

가장 먼저 그릴 흐름 추천:

`사용자 아이디어 입력 -> API 서버 -> 분석 서비스 -> DB 조회/저장 -> 결과 반환`

이 흐름 하나만 그려도 서버/DB/분석 책임 분리가 보이기 시작한다.

## 6. 기술 선택 근거 적기

예:

- 왜 모놀리식으로 시작할지
- 왜 RDB를 쓸지
- 왜 크롤링은 배치 작업으로 둘지
- 왜 분석 요청은 동기/비동기 중 무엇으로 할지

기술 이름보다 "왜 그렇게 선택했는지"를 적는 연습이 중요하다.

---

# 추천 학습 연결 포인트

현재 체크리스트에서 이 문서와 바로 연결되는 항목은 시스템 설계 기초 영역이다.

특히 아래를 같이 보면 좋다.

- 서버와 클라이언트 구조
- 캐시를 어디에 둘 수 있는지
- 메시지 큐가 필요한 상황
- 단일 장애 지점(SPOF)
- 모놀리식과 마이크로서비스 차이
- 트래픽 증가 시 병목 지점 찾기

---

# 바로 다음 실습 과제

다음 문서 작성 목표는 아래 순서가 좋다.

1. 이 서비스의 MVP를 3기능으로 줄이기
2. 사용자 시나리오 3개 쓰기
3. 핵심 엔티티 5개 정의하기
4. 컴포넌트 구조 초안 적기
5. 데이터 흐름 1개 그리기

---

# 한 줄 정리

지금 문서는 아이디어 정리 단계까지는 괜찮고, 다음부터는 기능 추가보다 "요구사항 분해 -> 데이터 정의 -> 컴포넌트 분리 -> 흐름 설계" 순서로 연습하는 것이 좋다.

----

# 실습

일단 MVP 3개 기능
- 데이터 크롤링
- 사용자 아이디어 받기
- 사용자 아이디어 분석

사용자 시나리오
- 바이브 코딩을 시작하는데 주제를 정하기 어려워하는 개발자 -> 아이디어 조사 및 폼 제출 -> 아이디어 분석 -> 아이디어 보강 -> 작업 시작
- 과제를 하려는데 뭔가 주제가 잡히지 않는 학생 -> 아이디어 분석 -> 아이디어 확인 및 검증 -> 작업 시작

핵심 엔티티
- 사용자 정보
- 크롤링한 경쟁사 정보
- 크롤링한 시장 데이터
- 사용자가 제출한 아이디어 (RAW)
- 사용자의 아이디어 분석 결과

컴포넌트 구조
- backend(fastapi)
  - app/
    - main.py
    - database.py
    - router/
      - mvp.py (모든 요청은 한곳에서 받기)
    - models/
      - orm모델.py
    - schemas/
      - 작업_별_dto
    - service/
      - collector/ (데이터 수집기)
      - analyzer/ (사용자 아이디어 분석기)
      - common/ (기본 crud)
    - repositories/
      - 테이블별_repo.py
- frontend(next)
  - / (루트, 메인페이지)
  - /idea (사용자 아이디어 입력)
  - /analyze (사용자 아이디어 분석 결과)

데이터 흐름
1. 뉴스, 경쟁사종류 크롤링
2. 뉴스와 ai를 통한 경졍사 강/약점 및 특징 분석 -> 저장
3. 사용자 아이디어 입력받기
4-1. 아이디어와 관련된 경쟁사들 분석
4-2. 아이디어와 관련된 뉴스들 분석
5. ai가 최종적으로 가능성 판단 및 근거 제출

```
- 초기에는 API 수가 적고 변경 가능성이 높으므로 라우터를 mvp.py 하나로 단순화한다.
- 추후 기능이 확장되면 ideas, analysis, trend 등 책임 기준으로 분리한다.
- 크롤링은 사용자 요청 시점마다 수행하지 않고 스케줄링 기반 배치 작업으로 수행한다.
- 그 이유는 응답 시간을 줄이고, 외부 데이터 의존성을 낮추고, 분석 결과에 근거 데이터를 포함하기 위해서다.
- 이 서비스의 핵심 가치는 단순 AI 의견이 아니라 최신 뉴스/경쟁사 정보에 근거한 설득력 있는 분석 결과 제공에 있다.
```

# 할일
```
1. ERD 초안
- 어떤 데이터를 저장할지 확정
- 엔티티 간 관계 정리
- 지금 네 경우 최소:
  User, Idea, AnalysisResult, Competitor, CollectedNews, 필요하면 TrendReport

2. 프로젝트 모듈 설계
- 어떤 책임을 어떤 계층이 가지는지 정리
- 예:
  router -> service -> repository -> model
  collector, analyzer는 별도 서비스 성격으로 분리

3. 파일 구조 설계
- 실제 구현 전에 디렉토리와 파일 역할 정의
- 여기서 중요한 건 “파일 이름”보다 “책임 경계”입니다

4. 주요 데이터 흐름 다시 점검
- 배치 크롤링 흐름
- 사용자 분석 요청 흐름
- 결과 저장/조회 흐름
- 이 3개가 구조와 맞는지 확인

5. 비기능 요구사항 한 줄씩 추가
- 크롤링 주기
- 분석 응답 시간 목표
- 장애 시 fallback
- 외부 API 실패 시 처리 방식
```

# DataBase ERD
USERS
- USER_ID         BIGINT        PK NOT NULL
- USER_NAME       VARCHAR(100)  NOT NULL
- USER_EMAIL      VARCHAR(100)  NOT NULL
- USER_PHONE      VARCHAR(11) 

IDEA - 사용자 아이디어
- IDEA_ID         BIGINT        PK
- USER_ID         BIGINT        FK
- IDEA_NAME       VARCHAR(255)  NOT NULL
- IDEA_CONTENT    JSONB         NOT NULL


ANALYSIS_RESULT - 아이디어 분석 결과
- RESULT_ID       BIGINT        PK
- IDEA_ID         BIGINT        FK  NOT NULL
- MARKET_POTENTIAL ENUM         NOT NULL
- COMPETITOR_ID   JSONB [competitor1_id: , competitor2_id: , ...]
- ANALYZE_RESULT  JSONB {차별점: , 약점, 등등}
- ANALYZE_RAW_RESULT  TEXT      NOT NULL

COMPETITOR
- COMPETITOR_ID   BIGINT  PK
- FEATURE         JSONB {강점, 약점, 카테고리, 기업 규모, 성장률, 등등} NOT NULL

COLLECTED_NEWS
- NEWS_ID         BIGINT        PK
- URL             VARCHAR(255)  NOT NULL
- CONTENT         TEXT          NOT NULL


# 분석 흐름
## 스케줄링
- 매일: 뉴스 크롤링 -> 1. 뉴스 저장   2. 경쟁사 경쟁사 분석
- 매분기: 경쟁사 크롤링 (경쟁사 추가 및 수정)

## 사용자 분석 요청
1. 사용자의 아이디어 입력
2. AI가 사용자의 아이디어를 스타트업 아이디어 + 경쟁사 + 뉴스들과 함께 분석 -> 결과 저장 -> 조회

# 모듈 책임
- router: 요청 받는 엔드포인트
- service: 분석 및 크롤링 로직을 맡는 공간
- repository: DB에 접근하는 계층
- model: 데ㅣ에터 저장소

# 비기능 요구사항
- 그냥 그럴싸해 보이는게 아니라 실제로 사용자에게 도움이 되어야함
- 로딩 시간은 10초 이상 넘어가면 안됨
- API 실패 시 이유 명확하게 알려줘서 이후에 해결 가능하게 만들기
- 어느정도의 분석은 사용자 요청 전에 준비된 상태가 되어있어야함 (경쟁사 분석 또는 시장 상황 등 사용자 아이디어 없이 할 수 있는 분석들)

---

# 의견

지금 문서는 아이디어 수준을 넘어서 설계 초안으로 꽤 발전했다.
특히 아래 4가지는 방향이 좋다.

- 크롤링을 사용자 요청마다 하지 않고 배치로 분리한 점
- FastAPI backend / Next frontend로 큰 축을 먼저 나눈 점
- 사용자 분석 요청 흐름과 스케줄링 흐름을 따로 본 점
- 응답 시간과 실패 처리 같은 비기능 요구사항을 적기 시작한 점

다만 지금 상태에서 실제 구현으로 넘어가면 먼저 막힐 가능성이 큰 부분도 보인다.

## 1. AnalysisResult에 competitor id를 JSON으로 넣는 것은 비추천

현재 구조:

- `COMPETITOR_ID JSONB [competitor1_id, competitor2_id, ...]`

이 방식은 처음엔 편해 보이지만 나중에 아래 문제가 생긴다.

- FK 제약을 걸기 어렵다
- 어떤 경쟁사가 어떤 분석 결과에 몇 번 연결됐는지 조회가 불편하다
- 경쟁사 삭제/수정 시 영향 범위 추적이 어렵다

더 나은 방식:

- `analysis_result` 테이블은 분석 결과 자체만 저장
- `analysis_result_competitor` 연결 테이블을 따로 둠

예:

- `analysis_result`
- `analysis_result_competitor`
  - `result_id`
  - `competitor_id`
  - `reason_summary`
  - `rank_order`

이렇게 두면 "이 분석 결과에서 어떤 경쟁사를 근거로 사용했는지"가 명확해진다.

## 2. 뉴스와 경쟁사가 분석 결과의 근거로 연결되어야 함

이 서비스의 핵심 가치는 "그럴싸한 AI 답변"이 아니라 "뉴스/경쟁사 데이터에 근거한 분석"이다.
그런데 현재 ERD에는 분석 결과와 뉴스의 연결이 없다.

그래서 아래가 필요하다.

- `analysis_result_news`
  - `result_id`
  - `news_id`
  - `reason_summary`

- `analysis_result_competitor`
  - `result_id`
  - `competitor_id`
  - `reason_summary`

이 구조가 있으면 이후 화면에서도 아래처럼 보여줄 수 있다.

- 이 분석에 사용된 뉴스 3건
- 이 아이디어와 유사한 경쟁사 5개
- 각 경쟁사가 왜 선택되었는지 요약

## 3. JSONB는 보조 용도로만 쓰는 것이 좋음

지금은 `IDEA_CONTENT`, `ANALYZE_RESULT`, `FEATURE`를 JSONB로 넣었는데, 전부 JSON으로 두면 나중에 검색과 정렬이 어려워진다.

권장 방식:

- 자주 조회하거나 필터링할 값은 일반 컬럼으로 분리
- 구조가 자주 바뀌는 원본 응답이나 추가 메타데이터만 JSONB로 저장

예를 들면:

`idea`
- `idea_id`
- `user_id`
- `title`
- `problem`
- `target_user`
- `solution_summary`
- `raw_input_json`

`competitor`
- `competitor_id`
- `name`
- `category`
- `summary`
- `strength_json`
- `weakness_json`
- `source_url`

`analysis_result`
- `result_id`
- `idea_id`
- `market_potential`
- `summary`
- `risks_json`
- `differentiation_json`
- `raw_llm_response`

## 4. Competitor와 CollectedNews에도 메타데이터가 더 필요함

현재는 최소 구조로는 괜찮지만 실제 활용에는 정보가 부족하다.

추가를 추천하는 필드:

`competitor`
- `name`
- `homepage_url`
- `category`
- `business_model`
- `country`
- `collected_at`
- `updated_at`

`collected_news`
- `title`
- `source_name`
- `published_at`
- `url`
- `summary`
- `content`
- `collected_at`

특히 뉴스는 `published_at`이 없으면 최신성 판단이 어렵다.

## 5. User가 꼭 필요한지 먼저 결정하는 것이 좋음

초기 MVP에서는 로그인 없이도 분석 기능만 먼저 제공할 수 있다.
그래서 선택지는 두 가지다.

1. 로그인 없이 시작
- `user_id` nullable
- 분석 경험을 빠르게 검증 가능

2. 로그인 포함해서 시작
- 분석 기록 저장, 마이페이지 구현이 쉬움
- 대신 인증 설계가 추가됨

MVP 목적이 빠른 검증이라면 처음에는 익명 허용도 나쁘지 않다.

## 6. 비기능 요구사항은 측정 가능한 문장으로 바꾸는 것이 좋음

현재 문장 중 좋은 방향도 있지만 일부는 측정이 어렵다.

예를 들어:

- "실제로 사용자에게 도움이 되어야함"

이 문장은 제품 목표로는 좋지만 시스템 요구사항으로는 애매하다.

아래처럼 바꾸면 더 설계 문서답다.

- 아이디어 분석 API 응답 목표: 10초 이내
- 뉴스 수집 배치 주기: 하루 1회
- 경쟁사 수집 배치 주기: 분기 1회
- 외부 API 실패 시 최대 2회 재시도
- 분석 실패 시 사용자에게 실패 원인과 재시도 가능 여부를 반환

## 7. 모듈 책임은 조금만 더 구체화하면 좋음

현재 구조는 맞다.
다만 `service` 안에서도 책임을 한 번 더 나누면 더 선명해진다.

예:

- `router`
  - 요청/응답 처리
  - validation 실패 응답

- `service`
  - 유스케이스 조합
  - 분석 요청 흐름 제어

- `repository`
  - DB CRUD

- `collector`
  - 외부 사이트/뉴스 수집
  - 수집 결과 정제

- `analyzer`
  - 경쟁사/뉴스/아이디어를 조합해 LLM 분석 요청
  - 분석 결과 후처리

## 내가 추천하는 최소 ERD 초안

`users`
- `user_id`
- `name`
- `email`
- `phone`
- `created_at`

`ideas`
- `idea_id`
- `user_id`
- `title`
- `problem`
- `target_user`
- `solution_summary`
- `raw_input_json`
- `created_at`

`analysis_results`
- `result_id`
- `idea_id`
- `market_potential`
- `summary`
- `raw_llm_response`
- `created_at`

`competitors`
- `competitor_id`
- `name`
- `category`
- `summary`
- `feature_json`
- `source_url`
- `collected_at`

`collected_news`
- `news_id`
- `title`
- `source_name`
- `published_at`
- `url`
- `summary`
- `content`
- `collected_at`

`analysis_result_competitor`
- `result_id`
- `competitor_id`
- `reason_summary`
- `rank_order`

`analysis_result_news`
- `result_id`
- `news_id`
- `reason_summary`

## 한 줄 의견

전체 방향은 좋고, 이제부터는 기능을 더 늘리기보다 "관계형으로 저장할 것"과 "JSON으로 남길 것"을 구분하는 연습을 하면 설계 품질이 훨씬 좋아진다.

---

# MVP 테이블 컬럼 초안

현재 방향 기준으로는 `users` 테이블 없이 `ideas`에 작성자 정보를 함께 두고, `analysis_results`가 분석 결과를 저장하며, `competitors`와 `collected_news`는 분석용 참조 데이터로 두는 구조가 가장 단순하다.

## 1. ideas

- `idea_id` `BIGINT PK`
- `nickname` `VARCHAR(50) NOT NULL`
- `email` `VARCHAR(100) NULL`
- `title` `VARCHAR(255) NOT NULL`
- `problem` `TEXT NOT NULL`
- `target_user` `TEXT NULL`
- `solution_summary` `TEXT NOT NULL`
- `status` `VARCHAR(30) NOT NULL`
- `raw_input_json` `JSONB NULL`
- `created_at` `TIMESTAMP NOT NULL`
- `updated_at` `TIMESTAMP NOT NULL`

설명:

- `ideas`는 사용자 제출 기록 역할도 같이 한다.
- `nickname`, `email`은 별도 `users` 없이도 MVP 운영이 가능하도록 둔다.
- `problem`, `target_user`, `solution_summary`는 화면 표시와 분석 입력에 자주 쓰이므로 컬럼으로 둔다.
- 설문 전체 원본이나 추가 입력값은 `raw_input_json`에 둔다.

`raw_input_json` 예시 틀:

```json
{
  "idea_background": "",
  "expected_users": [],
  "pain_points": [],
  "reference_services": [],
  "additional_notes": ""
}
```

## 2. analysis_results

- `result_id` `BIGINT PK`
- `idea_id` `BIGINT FK NOT NULL`
- `market_potential` `VARCHAR(20) NOT NULL`
- `summary` `TEXT NOT NULL`
- `strength_summary` `TEXT NULL`
- `weakness_summary` `TEXT NULL`
- `differentiation_summary` `TEXT NULL`
- `risk_summary` `TEXT NULL`
- `recommended_action` `TEXT NULL`
- `related_competitors_json` `JSONB NULL`
- `related_news_json` `JSONB NULL`
- `raw_llm_response` `TEXT NOT NULL`
- `created_at` `TIMESTAMP NOT NULL`

설명:

- `analysis_results`는 최종 분석 결과를 저장한다.
- 경쟁사/뉴스는 현재 MVP 기준으로는 별도 연결 테이블 대신 JSONB로 스냅샷처럼 보관한다.
- 다만 최종 요약값은 화면 표시와 비교가 쉽도록 일반 컬럼으로 뺀다.

`related_competitors_json` 예시 틀:

```json
[
  {
    "competitor_id": 0,
    "name": "",
    "category": "",
    "reason": "",
    "rank": 0
  }
]
```

`related_news_json` 예시 틀:

```json
[
  {
    "news_id": 0,
    "title": "",
    "source_name": "",
    "published_at": "",
    "reason": ""
  }
]
```

`raw_llm_response`와 별도로 추가 메타데이터가 필요하면 아래처럼 확장할 수 있다.

`analysis_meta_json` 예시 틀:

```json
{
  "model": "",
  "prompt_version": "",
  "analysis_started_at": "",
  "analysis_finished_at": ""
}
```

## 3. competitors

- `competitor_id` `BIGINT PK`
- `name` `VARCHAR(255) NOT NULL`
- `category` `VARCHAR(100) NOT NULL`
- `summary` `TEXT NULL`
- `homepage_url` `VARCHAR(255) NULL`
- `business_model` `VARCHAR(100) NULL`
- `target_market` `VARCHAR(255) NULL`
- `feature_json` `JSONB NULL`
- `source_url` `VARCHAR(255) NULL`
- `collected_at` `TIMESTAMP NOT NULL`
- `updated_at` `TIMESTAMP NOT NULL`

설명:

- 경쟁사는 최소한 `name`, `category`는 일반 컬럼으로 둔다.
- 강점/약점/세부 특징은 수집 소스마다 형태가 달라질 수 있으므로 `feature_json`으로 둔다.

`feature_json` 예시 틀:

```json
{
  "strengths": [],
  "weaknesses": [],
  "features": [],
  "company_size": "",
  "growth_stage": "",
  "notes": ""
}
```

## 4. collected_news

- `news_id` `BIGINT PK`
- `title` `VARCHAR(255) NOT NULL`
- `source_name` `VARCHAR(100) NOT NULL`
- `url` `VARCHAR(255) NOT NULL`
- `published_at` `TIMESTAMP NOT NULL`
- `summary` `TEXT NULL`
- `content` `TEXT NOT NULL`
- `category` `VARCHAR(100) NULL`
- `collected_at` `TIMESTAMP NOT NULL`

설명:

- 뉴스는 최신성 판단이 중요하므로 `published_at`이 꼭 있어야 한다.
- `summary`는 크롤링 후 요약본, `content`는 원문 저장 역할로 생각하면 된다.

## 관계 정리

- `ideas 1 : N analysis_results`
- `competitors`는 분석 시 참조하는 수집 데이터
- `collected_news`도 분석 시 참조하는 수집 데이터
- 현재 MVP에서는 분석 시점에 사용한 경쟁사/뉴스를 `analysis_results`의 JSONB에 스냅샷처럼 저장한다

## JSONB 사용 기준 정리

- SQL 조건 검색이나 정렬이 자주 필요한 값은 일반 컬럼으로 둔다
- 구조가 자주 바뀌거나 원본 보존 목적의 값은 JSONB로 둔다
- MVP에서는 지나치게 정규화하지 말고, 조회 패턴이 분명해지면 그때 분리 테이블을 고려한다

---

# MVP 테이블 컬럼 초안 2안

이 안은 더 단순한 MVP 기준이다.
핵심 컬럼만 남기고, 분석 결과나 입력 상세는 JSONB로 묶어서 저장하는 방향이다.

## ideas

- `idea_id` `BIGINT PK`
- `nickname` `VARCHAR(50) NOT NULL`
- `email` `VARCHAR(100) NULL`
- `title` `VARCHAR(255) NOT NULL`
- `problem` `TEXT NOT NULL`
- `target_user` `TEXT NULL`
- `solution_summary` `TEXT NOT NULL`
- `raw_input_json` `JSONB NULL`
- `created_at` `TIMESTAMP NOT NULL`
- `updated_at` `TIMESTAMP NOT NULL`

정리:

- `status`는 현재 MVP에서는 제외한다
- `problem`, `target_user`, `solution_summary`는 일단 컬럼으로 유지한다
- 나중에 폼 구조가 바뀌거나 추가 입력이 생기면 `raw_input_json`에 넣는다
- 이후 조회 패턴이 단순하면 이 값들도 JSONB로 더 합칠 수 있다

`raw_input_json` 예시 틀:

```json
{
  "idea_background": "",
  "expected_users": [],
  "pain_points": [],
  "reference_services": [],
  "additional_notes": ""
}
```

## analysis_results

- `result_id` `BIGINT PK`
- `idea_id` `BIGINT FK NOT NULL`
- `market_potential` `VARCHAR(20) NOT NULL`
- `result_json` `JSONB NOT NULL`
- `related_competitors_json` `JSONB NULL`
- `related_news_json` `JSONB NULL`
- `raw_llm_response` `TEXT NOT NULL`
- `created_at` `TIMESTAMP NOT NULL`

정리:

- `strength_summary`, `weakness_summary`, `differentiation_summary`, `risk_summary`, `recommended_action`은 하나의 `result_json`으로 합친다
- 경쟁사/뉴스는 여전히 별도 관계 테이블 없이 JSON list로 둔다
- `rank`는 기준이 애매하면 일단 넣지 않아도 된다
- 이후 정말 우선순위 기준이 필요할 때만 추가하면 된다

`result_json` 예시 틀:

```json
{
  "strengths": [],
  "weaknesses": [],
  "differentiation": [],
  "risks": [],
  "recommended_actions": [],
  "summary": ""
}
```

`related_competitors_json` 예시 틀:

```json
[
  {
    "competitor_id": 0,
    "reason": ""
  }
]
```

`related_news_json` 예시 틀:

```json
[
  {
    "news_id": 0,
    "reason": ""
  }
]
```

## competitors

- `competitor_id` `BIGINT PK`
- `name` `VARCHAR(255) NOT NULL`
- `category` `VARCHAR(100) NOT NULL`
- `summary` `TEXT NULL`
- `homepage_url` `VARCHAR(255) NULL`
- `business_model` `VARCHAR(100) NULL`
- `target_market` `VARCHAR(255) NULL`
- `feature_json` `JSONB NULL`
- `source_url` `VARCHAR(255) NULL`
- `collected_at` `TIMESTAMP NOT NULL`
- `updated_at` `TIMESTAMP NOT NULL`

정리:

- `business_model`은 `B2B`, `B2C`, `SaaS`, `Marketplace` 같은 운영 방식 분류다
- `target_market`은 어떤 고객층/시장에 집중하는지 적는 값이다
- 세부 강점/약점/특징은 `feature_json`에 둔다

`feature_json` 예시 틀:

```json
{
  "strengths": [],
  "weaknesses": [],
  "features": [],
  "notes": ""
}
```

## collected_news

- `news_id` `BIGINT PK`
- `title` `VARCHAR(255) NOT NULL`
- `source_name` `VARCHAR(100) NOT NULL`
- `url` `VARCHAR(255) NOT NULL`
- `published_at` `TIMESTAMP NOT NULL`
- `summary` `TEXT NULL`
- `content` `TEXT NOT NULL`
- `category` `VARCHAR(100) NULL`
- `collected_at` `TIMESTAMP NOT NULL`

정리:

- `summary`는 뉴스 원문 전체를 분석에 바로 쓰기 어려울 때 사용할 요약본이다
- 필요하면 추후 `analysis_summary_json` 같은 별도 필드를 둘 수 있지만, 현재 MVP에서는 `summary`로 충분하다

## 2안 관계 정리

- `ideas 1 : N analysis_results`
- `competitors`와 `collected_news`는 참조 데이터
- 분석 시 사용한 경쟁사/뉴스 목록은 `analysis_results` 내부 JSONB에 보관한다
