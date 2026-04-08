# [표기해야할 것 리스트]

# UI/UX 
- 화면 분위기
- 화면에 있는 요소들
- 로딩 방식 (과 기타 디테일)

# 웹 서비스 아키텍처
## 프론트
- 컴포넌트 종류
- lib 함수 종류
- 상태 관리 방식
- 화면 url표기방식

## 백엔드
- 프로젝트 구조
- 흐름 방식
- API등과 기능

## DB
- 제약조건 너무 빡세지 않게, 조건 검수는 서버 도메인 레벨에서 관리

## 
- 모든 요소가 유지보수 하기 쉬운 형태로 높은 결합도와 낮은 응집도를 지킬것

---

# [설계]

## UI/UX

**화면 분위기**
- 다크 톤 베이스 (배경 #0F0F0F ~ #1A1A1A), 포인트: 인디고/퍼플 계열
- 미니멀 SaaS 스타일 — 여백 넉넉, 카드 기반 레이아웃 (Linear, Vercel Dashboard 참고)

**화면 요소**
- 랜딩: 히어로 + CTA + 샘플 리포트 미리보기
- 입력: 멀티스텝 위저드 (주제 → 타겟 → 수익모델 → 분석 시작)
- 리포트: 탭 구조 (요약 / 경쟁사 / 시장규모 / 액션플랜)
- 대시보드: 리포트 히스토리 카드 목록

**로딩 방식**
- 분석 중: 스트리밍 텍스트 출력 (SSE 타이핑 효과) + 단계별 진행 표시바
- 스켈레톤 UI로 레이아웃 선점 후 데이터 채움

---

## 웹 서비스 아키텍처

### 프론트 (Next.js 14 App Router / Vercel)

**URL 구조**
```
/                   랜딩
/analyze            아이디어 입력 위저드
/report/[id]        리포트 상세
/dashboard          내 리포트 목록 (로그인 필요)
/pricing            요금제
/login              로그인
/signup             회원가입
/settings           계정 정보 + 구독 관리
/trends             주제 없을 때 시장 트렌드 탐색
```

**컴포넌트 구조**
```
app/
  (public)/         히어로, 기능 소개, 가격표
  analyze/          AnalyzeWizard (멀티스텝 폼)
  report/[id]/      ReportView, ReportTabs, StreamingText
  dashboard/        ReportCard, ReportList
components/
  ui/               Button, Card, Input, Badge (shadcn 기반)
  report/           CompetitorTable, TamChart, ActionList
  wizard/           StepIndicator, StepForm
```

**lib 함수**
```
lib/
  api.ts        백엔드 fetch 래퍼 (에러 핸들링 포함)
  stream.ts     SSE 스트리밍 읽기 유틸
  auth.ts       Supabase 인증 헬퍼
  format.ts     리포트 데이터 → 렌더링용 포맷 변환
```

**상태 관리**
- 서버 상태: React Query (리포트 fetch/캐싱)
- 위저드 폼: Zustand 스토어 1개
- 인증: Supabase Auth + Context

---

### 백엔드 (FastAPI / Railway)

**프로젝트 구조**
```
app/
  routers/
    analyze.py    POST /analyze → SSE 스트림 반환
    report.py     GET /report/{id}
    user.py       GET /user/reports
  services/
    search.py     Tavily 검색 + 결과 파싱
    ai.py         OpenAI API 호출 (gpt-4o-mini → 추후 Claude 전환)
    report.py     분석 오케스트레이션
  models/         Pydantic 스키마
  db/             Supabase 클라이언트
```

**요청 흐름**
```
POST /analyze
  → 입력 검증
  → Tavily 검색 (경쟁사 3~5개, 시장 뉴스)
  → 검색결과 + 유저입력 → 프롬프트 조합
  → OpenAI 스트리밍 호출
  → SSE 청크 → 프론트 전달
  → 완료 시 reports 테이블 저장
```

**주요 API**
| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | /analyze | 분석 시작 (SSE 스트림) |
| GET | /report/{id} | 리포트 조회 |
| DELETE | /report/{id} | 리포트 삭제 |
| GET | /user/reports | 내 리포트 목록 |
| GET | /user/usage | 이번 달 사용량 조회 |
| GET | /user/profile | 프로필 + 구독 플랜 조회 |
| GET | /trends | 트렌드 시장 스냅샷 (무료, 주제 없는 유저용) |
| POST | /webhook/stripe | Stripe 구독 이벤트 수신 |

---

### DB (Supabase / PostgreSQL)

```sql
-- 유저: Supabase Auth 기본 테이블 사용 (auth.users)

profiles (
  id            uuid PRIMARY KEY REFERENCES auth.users, -- Supabase Auth 유저 ID와 1:1 매핑
  display_name  text,                                   -- 화면에 표시할 닉네임
  plan          text DEFAULT 'free',                    -- 현재 구독 플랜: 'free' | 'lite' | 'pro'
  created_at    timestamptz DEFAULT now()               -- 가입 일시
)

subscriptions (
  id                  uuid PRIMARY KEY,                 -- 구독 레코드 ID
  user_id             uuid REFERENCES profiles(id),     -- 구독 중인 유저
  stripe_customer_id  text,                             -- Stripe 고객 ID (결제 수단 연결용)
  stripe_sub_id       text,                             -- Stripe 구독 객체 ID (상태 동기화용)
  plan                text,                             -- 구독 플랜: 'lite' | 'pro'
  status              text,                             -- 구독 상태: 'active' | 'canceled' | 'past_due'
  current_period_end  timestamptz                       -- 현재 결제 주기 만료일 (만료 여부 판단용)
)

reports (
  id          uuid PRIMARY KEY,                         -- 리포트 고유 ID (공유 링크 /report/{id} 에 사용)
  user_id     uuid,                                     -- 생성한 유저 (null = 비로그인 무료 분석)
  input       jsonb,                                    -- 유저 입력 원문 (서비스명, 타겟, 수익모델 등)
  result      jsonb,                                    -- AI 분석 결과 (경쟁사, 시장규모, 액션플랜 등)
  plan        text,                                     -- 생성 시점 플랜 (결과 범위 확인용)
  created_at  timestamptz DEFAULT now()                 -- 리포트 생성 일시
)

usage_logs (
  id          uuid PRIMARY KEY,                         -- 로그 레코드 ID
  user_id     uuid REFERENCES profiles(id),             -- 행동을 수행한 유저
  action      text,                                     -- 행동 종류: 'analyze' | 'pdf_download'
  created_at  timestamptz DEFAULT now()                 -- 행동 발생 일시 (월별 사용량 집계 기준)
)
-- 제약조건은 서버에서 처리, DB는 타입/NOT NULL 최소화
```