# MVP 개발 아키텍처: ValidAI

---

## 1. UI/UX 화면 구성

```
[랜딩] /
  → 서비스 소개 + CTA("무료로 검증하기")

[검증 입력] /validate
  → 텍스트 입력창 ("서비스 아이디어를 설명해주세요")
  → 옵션 선택: 타겟 / 수익모델 / 카테고리 (유료)
  → "분석 시작" 버튼

[결과] /result/[id]
  → 스트리밍 보고서 (섹션별 순차 표시)
    - 아이디어 요약
    - 경쟁사 분석 (카드 리스트)
    - 강점/약점
    - (유료) 시장규모 / 개선방향 / 출처
  → PDF 다운로드 버튼 (유료)

[히스토리] /dashboard  ← 로그인 필요
  → 과거 분석 목록

[인증] /login, /signup
```

---

## 2. API 엔드포인트 (FastAPI)

| Method | Path | 기능 | 인증 |
|--------|------|------|------|
| POST | `/api/v1/validate` | 분석 시작, report_id 반환 | 선택 |
| GET | `/api/v1/validate/{id}/stream` | SSE 스트리밍 결과 | 선택 |
| GET | `/api/v1/reports/{id}` | 저장된 보고서 조회 | 필요 |
| GET | `/api/v1/reports` | 내 보고서 목록 | 필요 |
| GET | `/api/v1/reports/{id}/pdf` | PDF 생성 다운로드 | 유료 |
| POST | `/api/v1/auth/signup` | 회원가입 | - |
| POST | `/api/v1/auth/login` | 로그인 (JWT) | - |
| GET | `/api/v1/users/me` | 내 정보 + 플랜 | 필요 |
| POST | `/api/v1/payments/checkout` | Stripe 결제 세션 생성 | 필요 |
| POST | `/api/v1/payments/webhook` | Stripe 웹훅 처리 | - |

---

## 3. 프로젝트 구조

### Next.js (프론트엔드)
```
frontend/
├── app/
│   ├── page.tsx              # 랜딩
│   ├── validate/
│   │   └── page.tsx          # 입력 폼
│   ├── result/[id]/
│   │   └── page.tsx          # 결과 (SSE 스트리밍)
│   ├── dashboard/
│   │   └── page.tsx          # 히스토리
│   └── (auth)/
│       ├── login/page.tsx
│       └── signup/page.tsx
├── components/
│   ├── ValidateForm.tsx
│   ├── ReportViewer.tsx      # 스트리밍 렌더러
│   ├── CompetitorCard.tsx
│   └── PlanGate.tsx          # 유료 기능 잠금 UI
├── lib/
│   ├── api.ts                # fetch 래퍼
│   └── auth.ts               # JWT 관리
└── middleware.ts              # 인증 라우트 보호
```

### FastAPI (백엔드)
```
backend/
├── main.py
├── api/
│   ├── validate.py           # 핵심 분석 엔드포인트
│   ├── reports.py
│   ├── auth.py
│   └── payments.py
├── services/
│   ├── analysis_service.py   # RAG + Claude 호출 오케스트레이션
│   ├── rag_service.py        # Pinecone 검색
│   ├── claude_service.py     # Claude API 래퍼
│   └── pdf_service.py        # PDF 생성
├── models/
│   ├── user.py
│   ├── report.py
│   └── payment.py
├── db/
│   └── session.py            # SQLAlchemy + Supabase
└── core/
    ├── config.py
    └── security.py           # JWT
```

---

## 4. DB ERD

```
users
  id            UUID PK
  email         VARCHAR UNIQUE
  password_hash VARCHAR
  plan          ENUM('free','starter','pro')
  usage_count   INT DEFAULT 0        -- 이번 달 사용 횟수
  created_at    TIMESTAMP

reports
  id            UUID PK
  user_id       UUID FK → users.id (nullable, 비로그인 허용)
  input_idea    TEXT
  input_options JSONB                -- 타겟, 카테고리 등
  status        ENUM('pending','processing','done','error')
  result        JSONB                -- 보고서 전체 내용
  plan_tier     ENUM('free','paid')  -- 생성 당시 플랜
  created_at    TIMESTAMP

competitors                          -- 보고서당 경쟁사 목록
  id            UUID PK
  report_id     UUID FK → reports.id
  name          VARCHAR
  url           VARCHAR
  summary       TEXT
  source_url    VARCHAR              -- 출처

payments
  id            UUID PK
  user_id       UUID FK → users.id
  stripe_session_id VARCHAR
  amount        INT
  status        ENUM('pending','paid','cancelled')
  plan          ENUM('starter','pro')
  created_at    TIMESTAMP
```

---

## 5. 핵심 분석 흐름

```
POST /validate
  1. usage_count 체크 (무료: 월 3회)
  2. report 레코드 생성 (status=pending)
  3. 백그라운드 태스크 시작 → report_id 즉시 반환

GET /validate/{id}/stream  (SSE)
  1. RAG: Pinecone에서 유사 서비스 벡터 검색
  2. 외부 API: Crunchbase / 뉴스 크롤러 조회
  3. Claude API 스트리밍 호출 (구조화 프롬프트)
  4. 섹션 완성될 때마다 SSE event 전송
  5. 완료 시 reports.result 저장, status=done
```
