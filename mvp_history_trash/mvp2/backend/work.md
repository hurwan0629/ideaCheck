# 작업 노트
> 여기서 이야기하자. 이해한 구조, 현재 상태, 다음 할 일 순으로.

---

## 서비스 한줄 요약

사용자가 창업 아이디어를 입력하면 → AI가 경쟁사/시장 데이터 기반으로 실현 가능성을 분석해주는 서비스.
"Find Your Market Service"

---

## 전체 구조 이해

크게 두 흐름이 존재한다.

```
[자동 수집 파이프라인]          [사용자 요청 처리]
APScheduler                    FastAPI 라우터 (아직 없음)
    ↓                               ↓
daily_job (매일 03:00)          사용자가 아이디어 입력
    ├── crawl_news()            → UserIdea 저장
    ├── process_market_news()   → IdeaAnalysis 생성 (pgvector RAG)
    ├── detect_policy_changes() → 경쟁사 Top-K 매칭 후 Claude 분석
    ├── crawl_trends()
    └── consume_reanalysis_queue()

quarterly_job (분기 1회)
    ├── crawl_competitors()
    └── generate_analyses_for_all()
```

백엔드가 하는 일: **데이터를 모으고 → AI로 가공해서 → DB에 쌓아두는 것**
사용자 요청이 오면 그 데이터를 꺼내서 분석 결과를 만드는 것.

---

## DB 테이블 구조 이해

### user 그룹 (사용자 관련)
```
USERS ─┬── AUTH_ACCOUNTS     (소셜 로그인 등 로그인 방식)
       ├── USER_IDEAS         (분석 요청한 아이디어, 린 캔버스 형태 JSONB)
       │     └── IDEA_ANALYSES    (아이디어 AI 분석 결과, RECOMMENDATION_TYPE: GO/PIVOT 등)
       ├── IDEA_NOTES         (자유 메모)
       └── USER_SUBSCRIPTIONS (구독 정보)
```

### collection 그룹 (자동 수집 데이터)
```
경쟁사:
COMPETITORS ─┬── COMPETITOR_FEATURES   (기능 목록, FEATURE_CATEGORIES FK)
             ├── COMPETITOR_POLICIES   (정책 이력, POLICY_TYPES FK)
             └── COMPETITOR_ANALYSES   (종합 AI 분석 + 임베딩 벡터)

시장:
MARKET_RAW_SOURCES ── MARKET_EXTRACTS  (원본 → AI 추출)

트렌드:
TRENDS                 (Google Trends, 네이버 DataLab)
IDEA_TOPIC_STATS       (사용자 아이디어 카테고리 통계)

관리 테이블 (소프트 딜리트):
FEATURE_CATEGORIES, POLICY_TYPES
```

### service 그룹
```
PLANS (요금제)
```

---

## 핵심 설계 포인트

**1. 아이디어 분석 시 RAG 사용**
- 경쟁사 300개를 통째로 Claude에 넘기면 토큰 폭발
- COMPETITOR_ANALYSES에 임베딩 벡터 저장 (pgvector)
- 아이디어 입력 → 임베딩 → 유사도 Top-K 경쟁사만 Claude에 전달
- 임베딩 API는 아직 더미 (`[0.0] * 1536`)

**2. 수집과 분석 분리**
- `crawl_news()`: 뉴스 원본만 가져옴 (저장 X)
- `process_market_news()`: 저장 + AI 분류 담당
- 역할 분리로 재처리 가능 (원본은 MARKET_RAW_SOURCES에 항상 보존)

**3. 정책 변경 감지 → 재분석 큐**
- 뉴스에서 경쟁사 정책 변경 감지
- 변경 많은 경쟁사는 `reanalysis_queue`(set)에 추가
- daily_job 마지막에 `consume_reanalysis_queue()`로 처리

**4. 관리 테이블 소프트 딜리트**
- FEATURE_CATEGORIES, POLICY_TYPES는 절대 하드 DELETE 안 함
- IS_ACTIVE = false + DEPRECATED_AT 기록으로만 관리
- 히스토리 분석 보존 목적

---

## 현재 상태 (코드 기준)

| 영역 | 상태 |
|------|------|
| models/ | 전체 완성. DB 테이블 정의 완료 |
| config.py | 완성. .env에서 DATABASE_URL 읽음 |
| db.py | 완성. 동기 SQLAlchemy 엔진, SessionLocal, get_db() |
| main.py | 뼈대만. lifespan 있는데 스케줄러 연결 안 됨. 라우터 없음 |
| collector/scheduler.py | 완성. daily_job, quarterly_job 구조 완성 |
| collector/crawlers/ | 더미. 실제 API 연동 없음 (네이버 뉴스 API 등) |
| collector/processors/ | 더미. Claude 호출 구조는 있는데 DB 저장 부분 TODO |
| collector/queue/ | 미확인 |
| API 라우터 | 없음 |

**main.py에 버그 있음:**
```python
# 현재 — lifespan을 정의했지만 app에 연결 안 함
app = FastAPI()  # lifespan 빠짐

# 그리고 잘못된 import 경로 2개
from mvp2.backend.app.models.user.idea_analyses import IdeaAnalysis   # 절대경로 잘못됨
from mvp2.backend.app.models.collection.competitor_analyses import CompetitorAnalysis
```

---

## 다음에 할 것들 (우선순위 미정)

- [ ] main.py 버그 수정 (lifespan 연결, import 경로)
- [ ] main.py에 스케줄러 연결 (lifespan 안에서 setup_scheduler + start)
- [ ] collector/queue/reanalysis_queue.py 확인
- [ ] DB 저장 로직 구현 (processors의 TODO 채우기)
- [ ] API 라우터 설계 + 구현
- [ ] 임베딩 API 연동 (pgvector RAG 실제 작동)

---

---

# 대화 로그

---

## 2026-04-15

### [나] 앞으로 대화 내용 모두 work.md에 적어줘. 몇 가지 현황:
- `app/collector/` 폴더는 어제 구조 눈으로 보려고 빠르게 만들어달라고 한 거라 다시 짜야함
- pgvector/RAG가 뭘 위한 기술인지는 아는데 원리나 사용법은 거의 모름
- 파이프라인 설계를 좀 더 해봐야 함
- 프론트와의 상호작용이나 최종 목표를 명확히 해야 함
- 주 목표: "창업자들의 시작을 쉽게 해준다. 아이디어 탐색 및 분석, 정보 제공"
- 어떤 방식으로 해줄지 명확한 정의가 필요함

### [Claude] 정리

**collector 관련**
맞음. 어제 만든 collector 코드는 구조 파악용이라 실제로 쓸 수 있는 상태가 아님.
pgvector/RAG는 지금 당장 몰라도 됨 — 수집/저장 파이프라인이 먼저고, RAG는 사용자 아이디어 분석 단계에서 나오는 이야기라 그때 같이 공부하면 됨.

**지금 가장 먼저 정의해야 할 것**
코드보다 앞서야 할 게 있음. 서비스가 "어떻게" 작동하는지가 안 정해지면 라우터도, 파이프라인도 설계를 못 함.

아래 질문들에 대한 답이 있어야 다음 단계로 갈 수 있음:

**Q1. 사용자 여정이 어떻게 되나?**
지금 모델을 보면 이 정도 흐름이 보이는데, 맞는지:
```
회원가입/로그인
  → 아이디어 입력 (린 캔버스, core_idea만 필수)
  → 분석 결과 확인 (GO / PIVOT 등 + 경쟁사 매칭 + 시장 맥락)
  → 아이디어 수정 후 재분석? 또는 새 아이디어 추가?
  → 마이페이지에서 내 아이디어 목록 관리
```
탐색 기능도 있는 건지? (로그인 없이 트렌드/시장 정보 둘러보는 것)

**Q2. 분석은 언제 트리거되나?**
- 사용자가 "분석 요청" 버튼 누를 때 즉시 처리?
- 아니면 배치로 처리?
- 재분석은? (아이디어 수정 후 다시 분석)

**Q3. 구독/요금제는 어떤 방식?**
- 무료: 분석 N회/월, 유료: 무제한?
- 분석 결과 상세도가 달라지는 방식?

**Q4. 프론트에 뭘 보여주나?**
`model__help__/example_html/` 폴더에 HTML 예시 파일들이 있음 (index, competitor, idea_analysis, market, trends).
이게 UI 초안이면 같이 보면서 정하면 좋을 것 같음.

이 4가지가 정해지면 → 파이프라인 설계 + 라우터 설계 바로 들어갈 수 있음.

### [나]
일단 기본 흐름은 거의 frontend/ 폴더의 prototype html구조와 비슷하긴 한데 

# 헤더
- 좌측: 로고
- 중앙: 시장분포, 트렌드, 많이 나온 아이디어보기
- 우측: 요금제, [로그인/로그아웃], 마이페이지

# body
- 아이디어가 없다면? 아이디어 탐색하러 가기
- 아이디어 분석하기

# 푸터
- 일반적인 형태로

---

이런느낌으로 갈거고 헤더 중앙의 기능은 게스트도 사용 가능하게. (물론 유료 사용자에게 더 많은 제공)

그리고 게스트도 아이디어 탐색 & 아이디어 분석 기능 사용 가능하게 할지 아니면 그냥 auth를 통해 간편 로그인을 강제로 시킬지 고민중이야. (이탈 가능성과 관리중에서 타협해야할거같아. 나는 로그인 필수가 관리에도 용이하고 무료사용자용 토큰 관리할때도 편할거같아.)

그리고 무료 사용자에 대해서 유료 사용자와 보여주는 화면을 다르게 하는게 아니라 같은 포멧을 보여주지만 블러처리해서 이런이런 정보를 더 받을 수 있어요 같이 하는거지.

그리고 아이디어 수정 후 재분석같은 경우에는 좀 자잘한 비용이 들거같긴한데 필수적인거같기도 해서 어느정도 채팅을 통한 조언 -> 수정 루프를 해야할거같아. (다시 분석하는건 비용이 들거같긴한데 사업 모델 바꾸는건 자주 있을 수 있으니까(구상시기에는) 어쩔 수 없는거같아.(우리 서비스의 중심이니까))

분석 트리거라는게 뭐에대한건지 모르겠지만
- 사용자 아이디어: 사용자가 분석 요청 누를때 처리하게 하는걸로 생각중이야.
- 트렌드, 경쟁사 등: 주기적으로 기업들 강/약점, 차별화 포인트, 특징 등 정리할 예정

너가 본 model__help__/ 는 내가 테이블에 json의 속성들 좀 정리하고싶어서 시각화한거고 일단 가장 내 생각하고 가까운건 루트폴더의 /prototype/ 폴더에있어.

### [Claude] prototype 읽고 정리

**서비스 정체성 확정**
- 서비스명: **SYM (Search Your Market)**
- 슬로건: "당신의 아이디어, 시장에서 검증하세요"
- 핵심: 아이디어 입력 → AI가 SWOT + 경쟁사 + 차별화 전략까지 리포트로

---

**페이지 구성 (prototype 기준)**
```
index.html          — 랜딩. 두 갈래: 아이디어 탐색 / 아이디어 분석
analyze-idea.html   — 핵심 기능. 입력 → 분석 결과 리포트
find-idea.html      — 아이디어 없는 사람용 (관심사 기반 구상 도움)
trend.html          — 요즘 트렌드
market-share.html   — 시장 점유율
popular-keywords.html — 인기 검색어
login.html          — 로그인
pricing.html        — 요금제
mypage.html         — 내 아이디어 목록, 분석 이력
```

헤더 중앙 3개(트렌드/시장점유율/인기검색어)는 게스트 접근 가능.
핵심 기능(아이디어 분석)은 로그인 필요 방향으로 가닥 잡는 중.

---

**분석 결과 화면 → DB 매핑**

prototype의 analyze-idea 결과 화면을 보면 IDEA_ANALYSES.RESULT_SUMMARY가 뭘 담아야 하는지 명확해짐:

```
결과 화면 항목                    DB 매핑
─────────────────────────────────────────
SWOT 4분면                     → result_summary.swot (현재 모델엔 없음, 추가 필요)
시장 가능성 점수 5개             → result_summary.entry_feasibility_score 외 4개 (현재 1개뿐)
경쟁사 카드 (강도 배지 포함)      → result_summary.matched_competitors
차별화 전략 리스트               → result_summary.suggestions
종합 코멘트                      → result_summary.direction
```

**→ RESULT_SUMMARY JSONB 구조 수정이 필요할 수 있음**
현재 모델의 `entry_feasibility_score` 하나만으론 화면의 5개 점수(성장성/경쟁강도/진입장벽/수익성/차별화)를 못 담음.

---

**정리된 사용자 여정**
```
[게스트]
  → 랜딩 접근
  → 트렌드/시장분포/인기검색어 둘러보기 (로그인 불필요)
  → 아이디어 분석 클릭 → 로그인 요구 (간편 로그인)

[로그인 후]
  → 아이디어 입력 (린 캔버스 형태, core_idea 필수 나머지 선택)
  → "AI 분석 시작하기" 클릭 → 즉시 처리 (동기 or 로딩 UX)
  → 결과: SWOT + 점수 + 경쟁사 카드 + 차별화 전략
  → 무료 유저: 일부 블러 + "업그레이드하면 더 볼 수 있어요"
  → 분석 저장 → 마이페이지에서 이력 관리
  → 채팅 조언 → 아이디어 수정 → 재분석 (루프)
```

---

**아직 결정 안 된 것들**

1. **로그인 강제 여부** - 너는 강제 쪽으로 기울어 있음. 합리적 선택. 결정하면 확정 기록.

2. **find-idea.html 범위** - "관심사 기반으로 아이디어 구상 도움"인데 어떤 방식인지 미정.
   - 단순 탐색 (트렌드/시장 데이터 보여주기)?
   - AI 대화로 아이디어 도출?
   - MVP에 포함할 건지?

3. **분석 결과 JSONB 구조 확정** - 화면 보고 수정 필요. 지금 모델이랑 prototype이 안 맞는 부분 있음.

4. **무료 유저 제한 범위** - 블러 처리할 항목 구체화 (경쟁사 몇 개까지? 차별화 전략 몇 개까지?)

5. **재분석 채팅 기능** - 별도 채팅 UI가 필요한 건지, 그냥 수정 후 재분석 버튼인지.

---

**다음 작업 순서 제안**

지금 결정 가능한 것들 먼저 확정하고 코드로 들어가는 게 맞음:
1. 로그인 강제 여부 확정
2. find-idea MVP 범위 확정
3. RESULT_SUMMARY JSONB 구조 확정
4. 그 다음에 → main.py 버그 수정 + 라우터 설계 시작


### [나]
로그인 방식 내가 말한거에 큰 문제 없으면 이대로 갈게

일단 find-idea.html에서는 단계별로 
1. 당신의 관심사는? -> 선택지: AI, 금융, 라이프스타일, ..., 기타[직접입력]
2. 당신의 팀 규모는?
3. 자금은?
...
이런 느낌으로 가려하고있어.

jsonb는 이제 제대로 정할 필요 있어. 지금 fastapi 등 공부하기 전에 딱 그거하던 단계였어. 일단 지금 /model/에 대충 예시 있긴한데 아마 그것들 다 정리(삭제)하고 다시 파일 하나에서 정리해야할거같아. (dbml폴더같은 데에서)

무료 제한범위는 경쟁사 하나만 보여주거나 **당신에게 추천하는 차별화 전략** -> 밑에 블러하기 라던가. 그런방식으로?
일단 초반에는 무료로 다 풀어야할거같으니까 이걸 나중에 plan테이블에서 허용하는 기능이라던가 plan별 허용 기능 관리하는 테이블이 필요할거같기도 해. 일단 지금은 mvp니까 없이가자

재분석 채팅은 내가 ai 비용에 대한 감각이 없어서 좀 햇갈리네. 그런데 채팅 ui는 필요할거같아. 간단하게. 아마 그냥 gpt api말고 rag기반의 우리 ai 이용하는게 좋을거같아.

### [Claude] RAG 설명 + 작업 내역

**RAG 오해 정정 — 네 이해가 맞음**

RAG라고 해서 뭔가 복잡한 별도 시스템이 있는 게 아님.
네가 말한 흐름이 정확히 RAG임:

```
사용자 아이디어 입력
  → 아이디어 텍스트를 숫자 벡터로 변환 (임베딩)
  → pgvector에서 "이 벡터랑 가장 가까운 경쟁사" Top-K 조회
  → 그 경쟁사들의 DB 데이터 (COMPETITORS + COMPETITOR_ANALYSES) SELECT
  → Claude 프롬프트에 경쟁사 데이터 + 아이디어 같이 넣어서 분석 요청
  → Claude가 비교 분석 결과 반환
```

"RAG 컨텍스트"라고 했던 게 바로 이 "Claude 프롬프트에 넣는 경쟁사 DB 데이터".
그 텍스트가 길수록 토큰 비용이 올라간다는 의미였음.

경쟁사 300개 전부 넣으면 토큰 폭발 → pgvector로 유사한 Top-5~10만 골라서 넣는 것.

채팅도 동일한 원리:
```
사용자 질문
  → 질문 관련 경쟁사/시장 데이터 DB에서 SELECT
  → Claude 프롬프트에 [이전 대화 이력 + DB 데이터 + 질문] 넣기
  → Claude 답변
```
GPT API 따로 쓸 필요 없이 동일하게 Claude API 쓰면 됨.

---

**완료한 작업**

1. **DBML 통합** (`app/history/dbml.md`)
   - 모든 테이블 + enum 완성
   - JSONB 컬럼마다 `note:` 달아서 dbdiagram.io에서 메모로 확인 가능
   - RESULT_SUMMARY 새 구조 반영 (scores 5개 + swot 추가)
   - FEATURE_CATEGORIES, POLICY_TYPES 테이블 추가 (기존 DBML에 누락)
   - 모든 Ref 정리

2. **모델 파일 주석 제거** (17개 파일)
   - 모든 `"""Table..."""` docstring 제거
   - 인라인 `# 설명` 주석 제거
   - 나중에 DBML 기반으로 일괄 재작성 예정

---

**다음**
- [ ] main.py 버그 수정 (lifespan 연결, import 경로 2개)
- [ ] 그 다음 단계 논의

### [Claude] 결정 사항 정리 + JSONB 구조 제안

**확정된 것들**

| 항목 | 결정 |
|------|------|
| 로그인 | 강제 (간편 로그인). 분석/탐색 전 로그인 필요 |
| find-idea | 단계별 설문 (관심사 → 팀규모 → 자금 → ...) → 아이디어 추천 |
| 무료 제한 | MVP에서는 전부 오픈. 나중에 PLAN 기반 제한 추가 |
| 채팅 | 단순 채팅 UI. Claude API + RAG (DB 기반 컨텍스트) |
| JSONB 정리 | 기존 model__help__ 예시들 정리 후 dbml 폴더에 통합 |

---

**RESULT_SUMMARY JSONB 구조 제안**

prototype 화면 기준으로 현재 모델이랑 맞게 수정 제안:

```json
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
  "direction": "시장 타이밍이 좋고 차별화 가능성이 높음. 초기 물류 파트너십이 핵심 변수.",
  "matched_competitors": [
    {
      "id": 100,
      "name": "마켓컬리",
      "similarity": 0.87,
      "threat_level": "HIGH",
      "diff_point": "구독 모델 없음. AI 맞춤 기능 없음."
    }
  ],
  "suggestions": [
    "AI 식단 개인화 고도화",
    "1인 가구 특화 포지셔닝"
  ],
  "risks": ["대기업 진입 가능성", "구독 피로도 증가"],
  "market_context": ["1인 가구 600만 돌파", "건강식 시장 연 15% 성장"]
}
```

현재 모델 대비 변경점:
- `entry_feasibility_score` (숫자 1개) → `scores` (5개 항목)로 교체
- `swot` 추가 (현재 없음)
- `differentiation` 리스트 삭제 → `suggestions`에 통합 (역할 겹침)
- `matched_competitors`에 `name`, `threat_level` 추가

RECOMMENDATION_TYPE (GO / GO_WITH_CAUTION / PIVOT / RETHINK) 은 scores 평균이나 AI 판단으로 결정 — 별도 컬럼 유지 맞음.

---

**채팅 비용 감각**

참고용으로만: Claude Haiku 기준 약 1000토큰 = $0.001 (0.1원대).
채팅 한 턴(질문+RAG컨텍스트+답변)에 보통 2000~5000토큰이면 턴당 0.3~0.5원 수준.
근데 RAG 컨텍스트(경쟁사 정보 등)가 길어지면 금방 10배로 뜀.
→ 채팅은 Haiku로, 최초 분석은 Sonnet으로 하는 모델 분리가 합리적.

---

**다음 할 것 (확정)**

1. `app/models/history/dbml.md` or 새 파일에 JSONB 구조 문서화
2. `idea_analyses.py` RESULT_SUMMARY 주석 위 구조로 업데이트
3. main.py 버그 2개 수정 (lifespan 연결, import 경로)
4. 라우터 설계 시작

지금 바로 2번 → 3번 순서로 들어갈 수 있음. 할까?

### [나]
일단 result_summary jsonb는 구조 좋은거같아. 
jsonb하고 text 타입은 여러개 있으니까 그것들 다 비슷하게 작업하면 좋을거같아. jsonb와 text형태에 따라 크롤링 방식이 다 바뀌고 서비스 형태도 바뀌니까 잘 작업 해야해.

그런데 scores 5개 항목도 완전 정해진건 아니기도 하고 하긴 한데 지금 결과창은 일단 좀 만족스러워.

채팅 비용 관련해서 RAG컨텍스트라는게 뭔지 모르겠네? RAG가 우리가 정보 정리해서 벡터로 저장해놓으면 사용자 아이디어 -> 설정된 로직을 통해 근접한 점수 파일 확인. 이런 느낌 아닌가? 그리고 경쟁사 정보는 DB에서 바로 select 해서 가져오는거고. ai가 그냥 경쟁사x사용자_아이디어 비교해서 좀 차별점 보여주는거고
하는거 아니야?

일단 dbml 전체 jsonb까지 정리 가능한 형태로 만들어주고(dbdiagram에서 봤을 때 메모지로 확인 가능하게), 모든 orm모델들에서 주석들 일단 삭제해줘. 나중에 dbml기반으로 다시 일괄적으로 주석 입히게

### [Claude] RAG 설명 + 작업 완료

**RAG 오해 정정 — 네 이해가 맞음**

RAG라고 해서 별도 시스템이 있는 게 아님. 네가 말한 흐름이 정확히 RAG임:

```
사용자 아이디어 입력
  → 아이디어 텍스트를 벡터로 변환 (임베딩)
  → pgvector에서 "이 벡터랑 가장 가까운 경쟁사" Top-K 조회
  → 그 경쟁사들 DB에서 SELECT (COMPETITORS + COMPETITOR_ANALYSES)
  → Claude 프롬프트에 [경쟁사 데이터 + 아이디어] 같이 넣어서 분석 요청
  → Claude 비교 분석 결과 반환
```

"RAG 컨텍스트"가 바로 프롬프트에 넣는 경쟁사 DB 데이터 텍스트.
그 텍스트가 길수록(경쟁사 많이 넣을수록) 토큰 비용 올라감.
→ 300개 전부 넣으면 폭발 → pgvector로 유사한 Top-5~10만 골라서 넣는 것.

채팅도 동일: [이전 대화 + 관련 DB 데이터 + 질문] → Claude 답변.
GPT 따로 쓸 필요 없이 동일하게 Claude API 사용.

---

**완료한 작업**

1. **DBML 통합** (`app/history/dbml.md`)
   - 모든 테이블 + enum 완성
   - JSONB 컬럼마다 `note:` 달아서 dbdiagram.io에서 메모지로 확인 가능
   - RESULT_SUMMARY 새 구조 반영 (scores 5개 + swot 추가)
   - FEATURE_CATEGORIES, POLICY_TYPES 테이블 추가 (기존에 누락됐던 것)
   - 모든 Ref 정리

2. **모델 파일 주석 제거** (17개 파일)
   - 모든 `"""Table..."""` docstring 제거
   - 인라인 `#` 주석 제거
   - 나중에 DBML 기반으로 일괄 재작성 예정

---

**다음**
- [ ] main.py 버그 수정 (lifespan 연결, import 경로 2개)

### [나]
```
# COMPETITORS
일단 이건 정적이고 변하지 않는 고정된 데이터니까 문제 없는거같고
TARGET_CUSTOMER도 결국 카테고리화 할거지만 생각해보면 카테고리로 정리할만큼 정규화 된 부분도 아닌거같아서 RAG(벡터화)가 더 적절한거같다. DISCRIPTION도 동일하게

# Feature_Categoreis
일단 ai가 news등 크롤링 -> FREATURE_CATEGORIES 읽고나서 
A, B, C 가 ACTIVE면 그거 형태로 분석해서 나누는거고, 나중에 검색할 때 쓰려나? 일단 나중에 이거 FEATURE 형태 기반으로 검색하려면 언제 DEPRECATE, ACTIVE 했는지 시계열로 기록하는게 좋아보이긴 하는데 일단 MVP니까 그렇게까지 안해도 될듯. (필요하면 나중에 JSON하나씩 뜯어서 기록하면 되니까)
일단 이대로 가면 될듯

# POLICY_TYPES
이것도 정ㅊ개 유형이라 많이 생성은 안될거같은데 따로 관리하는게 좋긴 할거같음. 그런데 POLICY_TYPES에 JSONB하나 추가해서 
POLICY_TYPES=1 를 쓰는 COMPETITOR_POLICIES의 POLICY_DATA의 JSONB에 들어갈 속성을 POLICY_TYPES의 POLICY_PROPS에 맞춰서 설정하는것도 좋을듯.
다시 설명해면
POLICY_TYPES.ID=1에 POLICY_TYPES.POLICY_PROPS=[position, price, reason] 이런식으로 COMPETITOR_POLICIES의 POLICY_DATA 형태를 만들어주는게 좋을거같은데 어때?

# COMPETITOR_ANALYSES
이건 어짜피 많이 바뀔테니까 이대로 둬도 되려나? 뭔가 틀이 딱 정해져서 조금 불편하긴 했는데 어짜피 RAW데이터에 가까운건 3개가 더 있으니까. 어떻게 생각해?

# IDEA_TOPIC_STATS
이건 뭐 사용자 정보 기록용이니까 알아서 하게 두면 되는거고. 거의 LOG 집계테이블이니까

# TRENDS
이것도 그냥 복붙용 테이블이니까 넘어갈게. 
그런데 요즘 트렌드 뉴스도 보여주긴해야하는데 이걸 MARKET_RAW_SOURCES.SOURCE_URL을 통해 보여주는건가?

# MARKET_RAW_SOURCES
이건 그 자체로 괜찮은듯

# MARKET_EXTRACTS
이것ㄷ 좋은듯. EXTRACT_TYPE는 이 뉴스의 요점, TOPIC는 어떤 주제인지(부정/긍정이 아니라 업종 카테고리라던가, 운영방식이라던가, 새 기술 발견등일거같고.
EXTRACTED_DATA는 뭐ㅓ지? 정제된 RAW_CONTENT인건가? 아니면 JSONB로 만들어도 될거같은데.

# USERS & AUTH_ACCOUNTS
이건 그대로.

# IDEA_NOTES 
이것도 굿

# USER_IDEAS
이거 나중에 포멧 바뀔 수 있는데 그냥 따로 설정 안하는걸로 갈게.
큰변화니까 자주 바뀌진 않을듯.

# USER_SUBSCRIPTIONS
이거 USERS : USER_SUBSCRIPTIONS가 1:N인게 맞나? 이거 1:1 아니야? 한 유저가 반드시 하나의 구독(무료/유료)를 해야하잖아.

# 추가 코멘트
이거 FEATURE_CATEGORIES와 POLICY_TYPES는 옵셔널이라 나와있는데 이거 이렇게 가야하나? 아니면 디폴트 값을만들어서 active상태 없으면 할거 만들어줘야하나?
```

### [Claude] 테이블별 응답

**COMPETITORS** — 동의. DESCRIPTION, TARGET_CUSTOMER는 카테고리화보다 RAG가 맞음. "B2B SaaS, 중소기업 세무" 같은 자유 텍스트가 벡터 유사도에 더 적합.

**FEATURE_CATEGORIES** — 이대로. MVP에서 시계열 추적까지 필요 없음.

**POLICY_TYPES — POLICY_PROPS 아이디어 좋음. 추가하자.**

네 아이디어대로:
```
POLICY_TYPES
  id=1, name="가격 정책", policy_props=["tier", "base_price", "enterprise_contact"]
  id=2, name="현지화",    policy_props=["target_region", "languages"]
  id=3, name="세대 겨냥", policy_props=["target_generation", "channel", "message"]
```
크롤러/AI가 정책 수집할 때 `policy_props`를 읽고 그 필드에 맞게 `POLICY_DATA`를 채움.
→ `policy_types.py`에 `POLICY_PROPS jsonb` 컬럼 추가 + DBML 업데이트 필요.

**COMPETITOR_ANALYSES** — 이대로 둬도 됨.
STRENGTH / WEAKNESS / CHARACTERISTIC은 AI 생성 요약 데이터. 원본은 COMPETITORS, COMPETITOR_FEATURES, COMPETITOR_POLICIES 3개에 다 있음. 분석 틀이 바뀌면 새 행 추가하면 그만이라 유연함.

**TRENDS** — 트렌드 뉴스 링크 보여주는 건 MARKET_RAW_SOURCES.SOURCE_URL로 가능. "요즘 트렌드" 페이지는 TRENDS 점수 + MARKET_EXTRACTS 요약 + SOURCE_URL 링크 조합으로 구성하면 됨.

**MARKET_EXTRACTS — EXTRACTED_DATA는 text 유지.**
SUMMARY가 이미 JSONB (구조화된 핵심 요약). EXTRACTED_DATA는 SUMMARY 생성이 실패했을 때 쓸 수 있는 원문 발췌 텍스트 (fallback). 굳이 JSONB로 만들 필요 없음.

**USER_SUBSCRIPTIONS — 1:N이 맞음.**
지금은 1명에 구독 1개처럼 느껴지지만, 이력이 생김:
```
user_id=1, plan=FREE,    status=EXPIRED,  started=1월, ended=3월
user_id=1, plan=PREMIUM, status=ACTIVE,   started=3월
```
"현재 구독"은 `WHERE status='ACTIVE'`로 1개만 가져오면 됨. 이력 보존 때문에 1:N.

**FEATURE_CATEGORIES / POLICY_TYPES nullable 문제 — 시드 데이터로 해결.**
`CATEGORY_ID`, `POLICY_TYPE_ID`가 nullable인 건 DB 레벨에서 강제 안 한다는 것.
크롤러 입장에서 "active인 카테고리가 하나도 없다"면 분류를 못 함.
→ 앱 최초 실행 시 기본 카테고리/정책 유형을 seed 데이터로 INSERT하면 해결.
MVP에선 직접 DB에 넣어도 됨. 나중에 어드민 API로 관리.

---

**변경 필요한 것**
- [x] `policy_types.py`에 `POLICY_PROPS jsonb` 컬럼 추가
- [x] DBML에 해당 컬럼 + note 추가
- [x] main.py 버그 수정 (lifespan 연결, import 경로)

### [Claude] main.py + policy_types.py 수정 완료

**수정 내용**

1. **`policy_types.py`** — `POLICY_PROPS jsonb` 컬럼 추가
   ```python
   from typing import Any
   from sqlalchemy.dialects.postgresql import JSONB
   
   policy_props: Mapped[list[Any] | None] = mapped_column("POLICY_PROPS", JSONB, nullable=True)
   ```
   예시: `policy_props=["tier", "base_price", "enterprise_contact"]`
   크롤러가 이 목록을 읽고 COMPETITOR_POLICIES.POLICY_DATA의 JSONB 필드를 채움.

2. **`main.py`** 버그 3가지 수정
   - import 경로 2개 수정 (`mvp2.backend.app.models...` → `app.models...`)
   - 누락된 import 2개 추가 (`FeatureCategory`, `PolicyType`) — 이게 없으면 `Base.metadata.create_all()`이 두 테이블을 생성하지 않음
   - lifespan 연결은 이미 되어 있었음 (`app = FastAPI(lifespan=lifespan)` 확인)

---

**다음 할 것**

다음 단계 선택지:
1. **스케줄러 연결** — main.py lifespan에 APScheduler 붙이기
2. **API 라우터 설계** — 어떤 엔드포인트가 필요한지 설계부터
3. **다른 공부** — SQLAlchemy 세션 관리, FastAPI 의존성 주입 등

어떻게 할지?