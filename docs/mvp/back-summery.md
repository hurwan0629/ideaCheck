# 백엔드 파일 구조 & 역할 정리

> 프레임워크: **FastAPI** (Python)  
> 실행 서버: **Uvicorn**  
> AI: **OpenAI gpt-4o-mini** (추후 Claude로 전환 예정)  
> 검색: **Tavily API** (실시간 웹 검색)  
> DB: **Supabase** (PostgreSQL)

---

## 전체 폴더 구조 한눈에 보기

```
backend/
└── app/
    ├── main.py          ← 🚪 서버 입구 (앱 설정, 라우터 등록)
    ├── routers/         ← 🛣️ URL 경로별 요청 처리
    ├── services/        ← ⚙️ 실제 비즈니스 로직 (AI, 검색, DB저장)
    ├── models/          ← 📋 데이터 형태 정의 (타입 검사용)
    └── db/              ← 🗄️ 데이터베이스 연결
```

---

## 요청이 처리되는 순서

```
브라우저/프론트
      ↓ HTTP 요청
   main.py           ← 서버 실행 + 라우터 연결
      ↓
  routers/           ← "이 URL은 이 함수가 담당"
      ↓
  services/          ← 실제 작업 수행 (검색, AI 호출, DB 저장)
      ↓
  db/ + 외부 API     ← Supabase, OpenAI, Tavily
      ↓ 응답
브라우저/프론트
```

---

## main.py — 서버의 입구

가장 먼저 실행되는 파일입니다. 해야 할 일:
1. FastAPI 앱 객체 생성
2. CORS 설정 (프론트엔드가 다른 포트에서 요청해도 허용)
3. 각 라우터(routers/)를 앱에 연결

```
uvicorn app.main:app --reload
         ↑
    이 명령어로 서버를 실행합니다
```

**CORS가 뭔가요?**  
브라우저는 보안상 다른 주소로 요청을 보내면 막습니다.  
프론트(`localhost:3000`)에서 백엔드(`localhost:8000`)로 요청 보낼 때 허용해주는 설정입니다.

---

## routers/ — URL 경로 담당자들

> "어떤 URL 요청이 오면 어떤 함수를 실행할지" 연결하는 파일들입니다.

| 파일 | 담당 URL | 역할 |
|------|----------|------|
| `analyze.py` | `POST /analyze` | 아이디어 분석 요청 받고 SSE 스트림으로 결과 반환 |
| `report.py` | `GET /report/{id}`, `DELETE /report/{id}` | 특정 리포트 조회 및 삭제 |
| `user.py` | `GET /user/reports`, `/user/usage`, `/user/profile` | 로그인한 유저의 리포트 목록, 사용량, 프로필 조회 |
| `trends.py` | `GET /trends` | 주제 없는 유저를 위한 시장 트렌드 스냅샷 |
| `webhook.py` | `POST /webhook/stripe` | Stripe 결제 이벤트 수신 후 구독 상태 DB 업데이트 |

### analyze.py가 하는 일 (핵심 흐름)

```
POST /analyze 요청 수신
      ↓
① search.py → Tavily로 경쟁사/시장 정보 검색
      ↓
② ai.py → 검색 결과 + 유저 입력을 OpenAI에게 전달
      ↓
③ AI 응답을 조금씩 SSE로 프론트에 전달 (타이핑 효과)
      ↓
④ 분석 완료되면 report.py → Supabase DB에 저장
      ↓
⑤ report_id를 프론트에 전달 → /report/{id}로 이동
```

### Webhook이 뭔가요?
Stripe(결제 서비스)가 "구독 결제 완료됨", "구독 취소됨" 같은 이벤트를 우리 서버로 자동으로 보내줍니다.  
우리는 그 이벤트를 받아서 DB의 구독 상태를 업데이트합니다.

---

## services/ — 실제 일을 하는 파일들

> 라우터는 "요청을 받아서 서비스에 넘기는" 역할만 하고,  
> 실제 로직은 서비스 파일에서 처리합니다.  
> 이렇게 분리하면 나중에 수정하기 쉬워집니다.

| 파일 | 역할 |
|------|------|
| `search.py` | Tavily API로 웹 검색. `search_competitors(topic)`, `search_market_trends(topic)` 제공 |
| `ai.py` | OpenAI API 호출. 시스템 프롬프트 + 검색 결과를 조합해서 JSON 분석 결과를 스트리밍으로 생성 |
| `report.py` | Supabase reports 테이블에 저장/조회/삭제하는 함수들 모음 |

### ai.py의 프롬프트 구조

```
[시스템 프롬프트]
"당신은 스타트업 아이디어 검증 전문가입니다.
JSON 형식으로 분석하세요: summary, competitors, market_size, action_plan, sources"

[유저 입력 + 검색 결과]
"아이디어: AI 시장조사 SaaS
타겟: 개발자 창업자
시장 조사 데이터:
- VenturusAI: AI startup idea validator...
- ..."
```

AI는 이 내용을 보고 구조화된 JSON을 만들어서 조금씩 반환합니다.

---

## models/ — 데이터 형태 정의

> Python은 타입이 느슨하지만, **Pydantic**을 쓰면 데이터의 형태를 미리 정의해서  
> 잘못된 데이터가 들어오면 자동으로 에러를 냅니다.

| 파일 | 정의하는 것 |
|------|------------|
| `models/report.py` | `AnalyzeInput` (요청 데이터), `ReportResult` (분석 결과), `ReportRow` (DB 행) |
| `models/user.py` | `UserProfile` (유저 프로필), `UsageStats` (사용량 통계) |

### 예시
```python
class AnalyzeInput(BaseModel):
    topic: str          # 필수: 아이디어 주제
    target: str | None  # 선택: 타겟 유저
    revenue_model: str | None  # 선택: 수익 모델
```
`topic`을 안 보내면 FastAPI가 자동으로 422 에러를 반환합니다.  
라우터에서 직접 검사할 필요가 없어서 코드가 깔끔해집니다.

---

## db/ — 데이터베이스 연결

| 파일 | 역할 |
|------|------|
| `db/supabase.py` | Supabase 클라이언트를 한 번만 만들어서 재사용 (싱글턴 패턴) |

**싱글턴이 뭔가요?**  
DB 연결은 비용이 크기 때문에 요청마다 새로 만들지 않고,  
처음 한 번만 만들고 계속 같은 객체를 돌려씁니다.

---

## requirements.txt — 필요한 패키지 목록

```
fastapi      ← 웹 프레임워크
uvicorn      ← 서버 실행기
openai       ← AI API 호출
tavily-python ← 웹 검색 API
supabase     ← DB 클라이언트
stripe       ← 결제 webhook 처리
pydantic     ← 데이터 타입 검사
python-dotenv ← .env 파일에서 환경변수 읽기
```

---

## .env.example — 환경 변수 목록

실제 API 키는 절대 코드에 직접 쓰면 안 됩니다.  
`.env` 파일에 따로 보관하고, `.env.example`은 "이런 키가 필요하다"는 안내용입니다.

```
OPENAI_API_KEY=      ← OpenAI 키
TAVILY_API_KEY=      ← Tavily 검색 키
SUPABASE_URL=        ← Supabase 프로젝트 URL
SUPABASE_SERVICE_KEY= ← Supabase 서비스 키 (서버에서만 사용)
STRIPE_SECRET_KEY=   ← Stripe 결제 키
STRIPE_WEBHOOK_SECRET= ← Stripe webhook 검증용
FRONTEND_URL=        ← CORS 허용할 프론트 주소
```

---

## API 전체 목록

| 메서드 | URL | 인증 필요 | 설명 |
|--------|-----|-----------|------|
| POST | `/analyze` | 선택 | 아이디어 분석 (SSE 스트림) |
| GET | `/report/{id}` | X | 리포트 조회 |
| DELETE | `/report/{id}` | O | 리포트 삭제 |
| GET | `/user/reports` | O | 내 리포트 목록 |
| GET | `/user/usage` | O | 이번 달 사용량 |
| GET | `/user/profile` | O | 프로필 + 구독 플랜 |
| GET | `/trends` | X | 시장 트렌드 스냅샷 |
| POST | `/webhook/stripe` | Stripe 서명 | 구독 이벤트 수신 |
| GET | `/health` | X | 서버 상태 확인 |
