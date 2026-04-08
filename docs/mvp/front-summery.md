# 프론트엔드 파일 구조 & 역할 정리

> 프레임워크: **Next.js 16** (App Router)  
> 언어: **TypeScript**  
> 스타일: **Tailwind CSS**

---

## 전체 폴더 구조 한눈에 보기

```
frontend/
├── app/                  ← 📄 페이지 파일 모음 (URL = 폴더 이름)
├── components/           ← 🧩 재사용 UI 조각 모음
├── lib/                  ← 🔧 공통 유틸 함수 모음
├── store/                ← 🗂️ 전역 상태 저장소
└── public/               ← 🖼️ 이미지 등 정적 파일
```

---

## app/ — 페이지 파일들

> Next.js는 **폴더 이름 = URL** 입니다.  
> 예: `app/analyze/page.tsx` → 브라우저에서 `/analyze` 로 접속하면 이 파일이 보임

| 파일 경로 | 접속 URL | 역할 |
|-----------|----------|------|
| `app/page.tsx` | `/` | **랜딩 페이지** — 서비스 소개 + CTA 버튼 |
| `app/layout.tsx` | 전체 공통 | **루트 레이아웃** — 모든 페이지를 감싸는 HTML 껍데기 (폰트, 배경색 등) |
| `app/analyze/page.tsx` | `/analyze` | **아이디어 입력 페이지** — 3단계 위저드 폼으로 분석 요청 |
| `app/report/[id]/page.tsx` | `/report/abc123` | **리포트 결과 페이지** — 분석 결과를 탭으로 보여줌. `[id]`는 리포트 고유번호 |
| `app/dashboard/page.tsx` | `/dashboard` | **내 리포트 목록** — 로그인한 유저의 분석 히스토리 |
| `app/pricing/page.tsx` | `/pricing` | **요금제 페이지** — Free/Lite/Pro 플랜 비교 |
| `app/login/page.tsx` | `/login` | **로그인 페이지** — 이메일 + 비밀번호 로그인 |
| `app/signup/page.tsx` | `/signup` | **회원가입 페이지** — 이메일 회원가입. `?plan=lite` 처럼 쿼리로 플랜 연동 |
| `app/settings/page.tsx` | `/settings` | **계정 설정 페이지** — 프로필, 구독 관리 |
| `app/trends/page.tsx` | `/trends` | **시장 트렌드 페이지** — 아이디어가 없는 유저에게 트렌드 정보 제공 |

### layout.tsx가 하는 일
```
브라우저 요청
      ↓
layout.tsx (HTML 뼈대, 폰트, 배경색 설정)
      ↓
각 page.tsx (실제 내용)
```
모든 페이지가 layout.tsx 안에 들어가기 때문에, 배경색 같은 공통 설정은 여기서 한 번만 해도 됩니다.

---

## components/ — UI 조각들

> 여러 페이지에서 **반복해서 쓰는 UI**를 따로 분리해놓은 파일들입니다.  
> "레고 블록"이라고 생각하면 됩니다.

### components/wizard/ — 아이디어 입력 위저드

| 파일 | 역할 |
|------|------|
| `StepIndicator.tsx` | 상단 "1 → 2 → 3" 진행 표시바. 현재 몇 번째 단계인지 시각적으로 보여줌 |
| `StepForm.tsx` | 단계별 입력 폼. step=0이면 주제 입력, step=1이면 타겟/수익모델 입력, step=2면 요약 확인 |

### components/report/ — 분석 결과 관련

| 파일 | 역할 |
|------|------|
| `StreamingText.tsx` | AI가 답변을 생성하는 동안 글자가 타이핑되듯 나타나는 컴포넌트 |
| `ReportView.tsx` | 리포트 전체를 렌더링하는 메인 컴포넌트. 아래 컴포넌트들을 조립함 |
| `CompetitorTable.tsx` | 경쟁사 목록을 표(table)로 보여줌 (이름, 설명, 강점, 약점) |
| `ActionList.tsx` | "지금 당장 해야 할 일" 목록을 번호 리스트로 보여줌 |
| `ReportCard.tsx` | 대시보드에서 리포트 하나를 카드 형태로 보여줌 (클릭하면 상세 페이지로 이동) |

---

## lib/ — 공통 유틸 함수들

> 페이지나 컴포넌트에서 **반복 사용하는 로직**을 모아둔 폴더입니다.  
> "도구 상자"라고 생각하면 됩니다.

| 파일 | 역할 | 쉬운 설명 |
|------|------|-----------|
| `api.ts` | 백엔드 API 호출 함수 | `fetch()`를 감싸서 에러처리를 자동으로 해주는 래퍼 |
| `stream.ts` | SSE 스트리밍 읽기 | AI 답변이 조금씩 오는 것을 받아서 콜백으로 넘겨주는 함수 |
| `auth.ts` | Supabase 로그인/가입 | `signIn()`, `signUp()`, `signOut()` 함수 모음 |
| `format.ts` | 데이터 변환 | 백엔드 JSON 응답을 화면에 보여주기 좋은 형태로 바꿔주는 함수 |

### SSE(Server-Sent Events)가 뭔가요?
```
일반 fetch:  클라이언트 → 요청 → 서버 → 한 번에 응답
SSE:         클라이언트 → 요청 → 서버 → 데이터를 조금씩 여러 번 보냄
```
AI가 글을 생성하면서 실시간으로 타이핑 효과를 내려면 SSE가 필요합니다.

---

## store/ — 전역 상태 저장소

| 파일 | 역할 |
|------|------|
| `store/wizard.ts` | 아이디어 입력 위저드의 폼 데이터(topic, target 등)와 현재 단계(step)를 전역으로 관리 |

### 왜 전역 상태가 필요한가요?
위저드는 여러 컴포넌트에 걸쳐 있는데, 1단계에서 입력한 내용을 3단계에서도 써야 합니다.  
props로 계속 전달하면 복잡해지므로 Zustand 전역 저장소에 저장해 어디서든 꺼내 씁니다.

---

## 데이터 흐름 전체 그림

```
유저가 /analyze 접속
      ↓
StepIndicator + StepForm (단계별 입력)
      ↓ 제출
lib/stream.ts → POST /analyze (백엔드)
      ↓ SSE 스트림
StreamingText (타이핑 효과로 실시간 표시)
      ↓ 완료
router.push('/report/{id}')
      ↓
ReportView → CompetitorTable + ActionList + ...
```

---

## 자주 헷갈리는 것들

**Q. "use client"는 왜 파일 맨 위에 쓰나요?**  
Next.js는 기본적으로 서버에서 렌더링합니다. `useState`, `onClick` 같이 브라우저에서만 동작하는 코드가 있으면 `"use client"`를 써서 "이 파일은 브라우저에서 실행해"라고 알려줘야 합니다.

**Q. `async function Page()`는 뭔가요?**  
서버 컴포넌트는 `async`를 쓸 수 있어서, 컴포넌트 안에서 직접 `await fetch()`로 데이터를 가져올 수 있습니다. useEffect 없이 서버에서 데이터를 미리 받아서 HTML을 만들어 보내줍니다.

**Q. `PageProps<'/report/[id]'>`는 뭔가요?**  
Next.js 16의 새 타입 헬퍼입니다. `/report/[id]` 페이지의 `params`(= `{ id: string }`)와 `searchParams` 타입을 자동으로 추론해줍니다. Next.js 14에서 직접 타입을 쓰던 방식보다 편리합니다.
