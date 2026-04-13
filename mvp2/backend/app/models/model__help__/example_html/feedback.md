# COMPETITORS
- DISCRIPTION 괜찮음
- TARGET CUSTOMER
- WEBSITE 좋음

# COMPETITORS_FEATURES
- 보니까 주요 기능이 여러개 있을 상황이 있으니 그냥 TEXT->JSONB가 나으려나? 이것도 어짜피 기능을 통한 검색기능은 아직 없으니까 나중에 필요하면 기능을 좀 더 분류화 시키는걸로 하고 지금은 그냥 JSONB로 갈까

생각해 보니까 역추적도 쉬워야하는구나
예를 들어 사용자가 IT서비스로 선택하면 COMPETITORS.TYPE로 검색이 되지만
TARGET_CUSTOMER을 검색하면 일일히 거대한 데이터베이스를 AI가 하나하나 뒤지긴 좀 어렵지 않나?
RAG를 쓰면 편한가?
아무튼 이런식으로 역으로 검색하기 위해선 조치가 필요해보임

# COMPETITOR_POLICIES
이런식으로 좀 타임라인으로 보니까 좀 좋긴 하다.
그런데 꼭 PRICE라던가 가격적인 포지셔닝 말고도, 현지화, 세대겨냥 등등 다각화해서 볼 수 있으면 좋겠네.

# COMPETITOR_ANALYSES
전체적으로 좋은거같음 UI도 예쁘고 
그런데 점유율이나 성장도는 조금 더 수치적으로 보여주면 좋겠네.
시장 N%나 5년대비 N%성장, 전년대비 M%성장 이런느낌으로. 
키워드는 좋고.

---

이런거 SaaS나 핀테크, B2B같은거 설명해주는 기능도 간단하게 만들어도 괜찮겠다.
경쟁사 총평으로는 괜찮지만 이게 진짜 사업 진입 판단용이나 분석용으로 괜찮을지 살짝 고민드는정도 (데이터 분석하면 좀 더 나아지려나?)

---
# MARKET_RAW_SOURCES
일단 진행 방식 자체는 괜찮음. 실제 크롤링 데이터는 더 많을 예정이고.

# MARKET_EXTRACTS
오해없이 하기위해. RAW_SOURCE_ID는 MARKET_RAW_SOURCES의 ID가 될 예정
솔직히 정보가 창업자들에게 아이디어나 진입각 확인용으로 정보를 제공하려는건데 이게 도움이 될지 잘 모르겠네.

---
# TRENDS
어짜피 다른것들하고 섞어서 이야기할거니까 괜찮긴한데
이게 사업적인 트렌드만 나오고 진짜 약간 사소한거부터 (쇼츠, 유행), 비즈니스적인거까지 여러가지 있으면 좋겠어.

--- 
# USER_IDEAS
사용자 아이디어 받을 때에도
이렇게 간단히 말고, 비즈니스 캔버스나 린 캔버스 느낌으로
카테고리, 비즈니스 모델, 차별화 포인트, 타겟 고객, 아이디어 제목, 구체적인 해결 방안, 우리 서비스를 사용할 이유 등등 좀더 구체적으로 끄집어 낼 수 있으면 좋겠어.

# IDEA_ANALYSES
일단 사업 진입 가능성같은걸 보여줘야하고,
비슷한 사업의 특징과 장단점. (아까 분석한 경쟁사들을 기반으로)
차별화 포인트 괜찮은지, 안괜찮은지와 그 이유, 해결책 등을 보여주고, 실질적인 도움을 줄 수 있어야해.

---
---

# Claude 의견

## COMPETITOR_FEATURES — TEXT → JSONB 방향 동의

JSONB가 맞음. 이유는 단순히 저장용이 아니라 나중에 "세금 자동화 기능 있는 경쟁사만 필터링" 같은 기능이 생길 때 TEXT면 손 못 댐.
다만 JSONB로 바꾸면 어떤 key를 쓸지 최소 기준을 정해두지 않으면 경쟁사마다 필드가 다 달라서 나중에 집계가 어려워짐.
예) `{ "name": "세금 신고 자동화", "description": "...", "category": "세무" }` 정도 최소 스키마 합의 필요.

## 역추적 검색 (RAG 질문) — 맞는 방향

TARGET_CUSTOMER나 DESCRIPTION을 텍스트 검색으로 뒤지는 건 한계 있음. RAG가 정답.
실용적 방법: pgvector 확장으로 COMPETITORS.DESCRIPTION, TARGET_CUSTOMER를 임베딩 벡터로 저장하고,
사용자 아이디어 입력 시 벡터 유사도 검색으로 관련 경쟁사를 뽑는 파이프라인.
COMPETITOR_ANALYSES.matched_competitors가 현재 ID 배열인데, 이걸 유사도 점수와 함께 저장하면
(`[{"id": 100, "score": 0.87}, ...]`) 나중에 "왜 이 경쟁사가 매칭됐는지" 근거도 생김.

## COMPETITOR_POLICIES — 다각화 동의, 단 일관성 주의

POLICY_DATA(jsonb)가 자유형이라 현지화, 세대 겨냥 등 필드 추가는 자유롭게 가능함.
다만 필드가 완전 자유형이면 크롤러나 AI가 시점마다 다른 key를 쓸 수 있어서
쿼리할 때 `policy_data->>'price'` 이런 게 있는 row도 있고 없는 row도 있는 상황이 생김.
해결책: 필수 key 목록을 내부 문서나 Enum으로 정의해두고, 추가 필드는 자유롭게.

## COMPETITOR_ANALYSES — 수치화 강하게 동의

"중위권", "성장중" 같은 텍스트는 AI한테는 쉽지만 프론트에서 차트 그리거나 비교할 때 쓸모없음.
`market_share`는 `{ "rank": 3, "estimated_pct": "15-20%" }` 식으로,
`growth`는 `{ "yoy_pct": 38, "trend": "up" }` 식으로 수치 기반으로 바꾸길 권장.
단, 실제 수치 데이터 소스(뉴스, 리포트)가 명확히 있을 때만 넣는 게 맞음. 없으면 AI가 추측값 넣게 되는데 그건 더 위험.

## MARKET_EXTRACTS — 창업자 유용성 고민 공유

솔직히 "이 시장이 38% 성장했다"는 정보가 창업자한테 직접 도움이 되려면
USER_IDEAS와 연결이 돼야 함. 예) "당신 아이디어가 속한 B2B SaaS 시장은 현재 이런 상황입니다" 식으로.
현재 구조에선 MARKET_EXTRACTS가 IDEA_ANALYSES와 연결되는 고리가 없음.
IDEA_ANALYSES.RESULT_SUMMARY에 관련 market extract ID나 요약을 포함시키는 방향이 자연스러울 것.

## TRENDS — 스코어 정규화 기준 불명확

Google Trends는 0-100 상대값, 네이버 DataLab도 0-100인데 이 둘이 같은 스케일이 아닐 수 있음.
TREND_SCORE를 그냥 decimal로 저장하면 나중에 "Google 88 vs 네이버 88은 같은 의미인가?" 혼란 생김.
SOURCE 컬럼이 있으니 시각화할 때 source별로 따로 보여주거나,
TREND_SCORE를 source 내부 상대값임을 명시하는 게 좋겠음.

사소한 트렌드 (쇼츠, 유행) + 비즈니스 트렌드 섞는 방향은 좋은데,
TOPIC_TYPE 같은 컬럼으로 분류해두면 나중에 필터링이 편함. 예) `"social"`, `"business"`, `"tech"`.

## USER_IDEAS — 린 캔버스 방향 완전 동의, 단 이탈률 고려

구체적으로 끄집어내는 건 분석 품질에 직결되니 맞는 방향.
근데 한 페이지에 다 물어보면 사용자가 중간에 이탈할 수 있음.
추천: 단계형 입력 (Step 1: 제목 + 핵심 아이디어 → Step 2: 타겟/차별화/모델 등 상세).
CONTENT jsonb도 이에 맞게 확장 필요:
```json
{
  "title": "...",
  "core_idea": "...",
  "target_customer": "...",
  "business_model": "...",
  "differentiation": "...",
  "problem_solved": "...",
  "tags": ["..."]
}
```
필수값은 title + core_idea 정도로 최소화하고 나머지는 optional.

## IDEA_ANALYSES — 진입 가능성 수치화 제안

"진입 가능성"이 텍스트로만 나오면 신뢰도 낮아 보임.
RESULT_SUMMARY에 스코어 필드 추가 제안:
```json
{
  "entry_feasibility_score": 72,
  "direction": "...",
  "differentiation": ["..."],
  "matched_competitors": [{"id": 100, "similarity": 0.87}],
  "risks": ["..."],
  "suggestions": ["..."]
}
```
`entry_feasibility_score`는 AI가 근거 기반으로 생성한 0-100 점수 + 근거 요약.
사용자 입장에서 숫자 하나가 있으면 "이 서비스가 내 아이디어를 진지하게 분석했구나" 체감이 올라감.

## 전체적으로

구조 자체는 잘 잡혀있음. 데이터 흐름 (수집 → 추출 → 분석 → 사용자 제공)이 명확하고,
jsonb로 AI 출력 저장하는 패턴도 실용적.
다음 단계에서 크롤러/스케줄러 설계할 때 COMPETITOR_ANALYSES, MARKET_EXTRACTS 재생성 주기를 어떻게 할지 (전체 재생성 vs 변경분만) 미리 생각해두면 좋을 것 같음.

---
---

# 사용자(허완) 
일단 내용을 정리해보면
- COMPETITOR_FEATURES는 JSONB 틀을 정해놓고 포멧대로 채우자
- RAG 만들면 좋고, 사업 형태와 규모, 타겟, 강단점 등에 대해서 벡터 유사도 검색을 통해 빠른 출력이 가능하게 하여 토큰 사용을 줄이는 방식을 사용 가능하다. (+분석 후 이 회사는 ㅇㅇ 부분에서 비슷합니다 또는 확장까지 가능)
- COMPETITOR_POLICIES에서 정책같은 경우에는 새로운 형태가 자주 나올 수 있기도 하니까 변경하기 좋은 형태가 좋을거같음. 아마 POLICIES전용 테이블을 만들어서 관리자 대시보드에서 정책 키워드같은거 추가/삭제 가능하게 해도 좋을까?
- COMPETITOR_ANALYSES에서 말한대로 수치화에 필요한 소스를 찾는게 쉬운일은 아닐거같은데 어떻게 타협하면 좋을지. 아니면 좋은 방법이 있을까?
- MARKET_EXTRACTS에서 창업자 관련 유용성의 경우에는 사용자의 아이디어 기반으로 한다기 보다는 지금 HTML에 적혀져 있는 내용이 "ㅇㅇ비즈니스가 성공했습니다." 같은 정보는 뭔가 크게 쓸모있나 싶어서 조금 더 의미있는 내용, 사회문제나 일상 속 불편함을 나타내는 기사들을 스크랩하는건 어떨지 싶어. 아니면 그걸 겨냥한 스타트업 사례라던가. 아마 너랑 내가 생각하는 핀트가 약간 어긋난거같은데 맞아?
- TRENDS - 스코어 정규화는 중요한거같긴 한데 이건 구조적으로 분리해서 따로 고민할 수 있는 내용인거같아서 일단 후순위로 둬야할거같아.
- 린 캔버스같은 경우에는 일단 말한대로 이탈은 막아야하고 좀 더 간결하고 고민없이 할 수 있는 흐름을 만들어야지. 예를 들어 "타겟 고객은?" 했는데 고민해야한다면 또 머리아파지니까 그냥 "고민중" 이라는 선택지를 만든다던가. 그리고 나중에 AI가 제안하는 형식으로
- IDEA_ANALYSES에서도 진입 가능성을 이야기 할 때 당연히 이유도 함께 말해야하고, 예를 들면 "비슷한 경쟁사가 있긴한데 차별화 포인트로 접근성이 좋다는 점에서 실행가능" 같이 설명하면 좋을거같고 안되는 경우에도 이유만 말하지 않고 차별화 방식을 제안하거나 어떤부분을 차별화 하면 좋을지나 왜 안되는지, 개선사항을 찾는 방법도 알려줘야할거같아.

---
---

# Claude 의견 2

## COMPETITOR_FEATURES JSONB 틀 — 확정하기 전 한 가지만

틀 정해두는 방향 맞음. 근데 틀을 코드에 하드코딩하지 말고 POLICY_TYPES 테이블처럼 "feature 카테고리 목록" 테이블을 두는 게 낫다고 생각함 (아래 COMPETITOR_POLICIES 항목이랑 같은 맥락). AI가 크롤링 후 채울 때 이 목록 기준으로 매핑하게 하면, 나중에 새 카테고리 추가해도 코드 안 건드려도 됨.

최소 확정 스키마 예시:
```json
{
  "features": [
    { "category": "세무", "name": "세금 신고 자동화", "description": "..." },
    { "category": "회계", "name": "자동 장부 정리", "description": "..." }
  ]
}
```
`category` 값이 DB 테이블에서 관리되는 enum이면 일관성 보장됨.

## RAG — 아키텍처 방향 정리

맞는 방향이고, 구체적으로 어떻게 흐를지 정리하면:

1. 크롤러가 경쟁사 수집 → COMPETITORS + COMPETITOR_FEATURES 저장
2. 백그라운드 워커가 description + features 합쳐서 임베딩 생성 → pgvector에 저장
3. 사용자가 아이디어 입력하면 → 아이디어 텍스트 임베딩 → 유사도 Top-K 경쟁사 추출
4. LLM한테는 전체 DB 안 넘기고, 유사도 뽑힌 경쟁사 정보만 context로 전달 → 토큰 절감

"이 회사는 ㅇㅇ 부분에서 비슷합니다" 설명은 4번 단계에서 LLM이 유사도 근거 포함해서 생성하면 됨.
IDEA_ANALYSES.RESULT_SUMMARY에 `matched_competitors: [{"id": 100, "similarity": 0.87, "reason": "..."}]` 저장해두면 나중에 UI에서 근거 표시도 가능.

## COMPETITOR_POLICIES — 관리자 대시보드 방식 동의, 구조 제안

맞는 접근. 테이블 구조 제안:

```
POLICY_TYPES (관리자가 관리)
- id
- name         -- "가격 정책", "현지화", "세대 겨냥"
- description
- is_active    -- 비활성화 가능하게

COMPETITOR_POLICIES (기존)
- policy_type_id → POLICY_TYPES.id (FK 추가)
- policy_data (jsonb) -- 해당 타입에 맞는 세부 내용
```

이렇게 하면 관리자가 대시보드에서 "세대 겨냥" 타입 추가하면 크롤러/AI가 다음 수집 사이클부터 해당 타입으로 데이터 채울 수 있음. 코드 배포 없이 정책 유형 확장 가능.

## COMPETITOR_ANALYSES 수치화 타협안

실제 수치 소스 확보가 어렵다는 거 맞음. 현실적인 타협 방법:

**1단계 (지금): AI 추정값 + 신뢰도 표기**
```json
{
  "market_share": { "estimated_pct": "10-20%", "confidence": "low", "basis": "앱 리뷰 수, 언론 노출 빈도 기반 추정" },
  "growth": { "yoy_pct": null, "trend": "up", "confidence": "medium", "basis": "최근 6개월 기사 빈도 증가" }
}
```
수치가 없으면 null, 있으면 채우되 confidence + basis 필수. UI에서 "추정치" 라벨 붙이면 신뢰도 문제 완화.

**2단계 (나중에 데이터 소스 생기면):** Crunchbase, CB Insights, Statista 등 API 연결하거나, IR 자료 크롤링으로 실수치 대체.

지금 당장 null 허용해두고 구조만 잡아두면 나중에 채워넣기 쉬움.

## MARKET_EXTRACTS — 핀트 어긋난 거 맞음, 방향 전환 동의

맞음, 어긋났음. 내가 처음 상정한 건 "시장 규모, 성장률" 같은 macro 데이터였는데, 허완이 말하는 건 **"왜 이 시장에 기회가 있는가"를 보여주는 근거** — 즉 사회 문제, 불편함 사례, 그걸 해결하려는 스타트업 동향 같은 qualitative 내용임.

이게 창업자한테 훨씬 더 유용함. "B2B SaaS 시장 38% 성장" 보다 "중소기업 세무 처리에 평균 월 8시간 낭비, 직원 없이 혼자 처리하는 사장 비중 67%" 같은 게 아이디어 검증에 직결됨.

테이블 방향 수정 제안:
```
MARKET_RAW_SOURCES
- source_type: "news", "startup_case", "report", "social_complaint"  ← 타입 추가
- content_type: "pain_point", "market_data", "startup_story"          ← 내용 성격 분류

MARKET_EXTRACTS
- extract_type: "pain_point" | "market_size" | "startup_case"        ← 기존 내용과 병행
- pain_area: "세무", "물류", "고용" 등                               ← 불편함 영역 분류
```

"ㅇㅇ비즈니스 성공" 류는 startup_case로 수집하되 활용도 낮으면 우선순위 낮추고,
사회 문제 / 불편함 기사를 pain_point 타입으로 우선 수집하는 방향.

## USER_IDEAS 린 캔버스 — "고민중" 옵션 + AI 제안 흐름 구체화

"고민중" 선택지 좋은 아이디어. DB에는 `null`로 저장하고 UI에서 "고민중"으로 표시.
분석 요청 시 AI가 입력된 항목 기반으로 빈 항목을 채워주거나 질문하는 방식으로:

흐름 예시:
- Step 1: 아이디어 제목 + 핵심 내용 (필수, 짧게)
- Step 2: 타겟/차별화/모델 (선택지 또는 "고민중")
- 분석 시작 → AI가 "타겟 고객을 아직 정하지 않으셨네요. [소상공인 / 스타트업 / 일반인 / 직접 입력] 중 어떤 분들이 떠오르세요?" 형태로 보완 유도

CONTENT jsonb에 `"status": "draft" | "complete"` 필드 추가해두면 분석 전 완성도 체크도 가능.

## IDEA_ANALYSES — "실행 불가" 도 건설적으로

완전 동의. 결과 출력 방식 기준 정리:

| 상황 | 출력 내용 |
|------|-----------|
| 진입 가능 | 이유 + 어떤 차별화 포인트가 유효한지 |
| 진입 가능하나 위험 | 가능한 이유 + 리스크 + 리스크 완화 방법 |
| 진입 어려움 | 안 되는 이유 + 어떤 방향으로 틀면 가능한지 + 차별화 제안 |
| 포화/레드오션 | 니치 타겟 제안 또는 접근 방식 전환 제안 |

RESULT_SUMMARY에 `"recommendation_type": "go" | "go_with_caution" | "pivot" | "rethink"` 같은 필드 추가하면 UI에서 색상/아이콘 분기도 쉬워짐.

