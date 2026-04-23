# SYM Frontend — Next.js

**Search Your Market** 서비스의 프론트엔드 앱입니다.  
Next.js 15 App Router + TypeScript + Tailwind CSS로 구성되어 있습니다.

---

## 기술 스택

| 항목 | 사용 기술 | 이유 |
|------|-----------|------|
| 프레임워크 | Next.js 15 (App Router) | 파일 기반 라우팅, SSR/SSG 지원 |
| 언어 | TypeScript | 타입 안전성, 자동완성 |
| 스타일링 | Tailwind CSS v3 | 유틸리티 퍼스트, 빠른 개발 |
| HTTP 클라이언트 | Axios | 인터셉터, 에러 처리 편의성 |
| 쿠키 관리 | js-cookie | 브라우저 쿠키 읽기/쓰기 |

---

## 디렉토리 구조

```
frontend/
├── app/                        ← Next.js App Router (파일 = 라우트)
│   ├── globals.css             ← 전역 스타일, CSS 변수, Tailwind 지시어
│   ├── layout.tsx              ← 루트 레이아웃 (Navbar + main + Footer)
│   ├── page.tsx                ← / 랜딩 페이지
│   ├── login/
│   │   └── page.tsx            ← /login 로그인/회원가입
│   ├── find-idea/
│   │   └── page.tsx            ← /find-idea 4단계 아이디어 구상 위저드
│   ├── analyze/
│   │   └── page.tsx            ← /analyze 아이디어 분석 + 결과 보기
│   ├── trend/
│   │   └── page.tsx            ← /trend 요즘 트렌드
│   ├── market-share/
│   │   └── page.tsx            ← /market-share 시장 점유율
│   ├── popular-keywords/
│   │   └── page.tsx            ← /popular-keywords 인기 검색어
│   ├── mypage/
│   │   └── page.tsx            ← /mypage 마이페이지
│   └── pricing/
│       └── page.tsx            ← /pricing 요금제
│
├── components/                 ← 재사용 컴포넌트
│   └── layout/
│       ├── Navbar.tsx          ← 상단 네비게이션 바
│       └── Footer.tsx          ← 하단 푸터
│
├── lib/                        ← 유틸리티 / 공통 로직
│   ├── api.ts                  ← Axios 인스턴스 + 도메인별 API 함수
│   └── auth.ts                 ← JWT 토큰/유저 쿠키 관리 헬퍼
│
├── next.config.ts              ← /api/* → http://localhost:8000 프록시
├── tailwind.config.ts          ← Tailwind 커스텀 색상, 폰트
├── tsconfig.json               ← TypeScript 설정 (@/* 경로 별칭)
├── postcss.config.js           ← PostCSS (Tailwind 빌드에 필요)
└── package.json                ← 의존성 목록, 스크립트
```

---

## 설치 및 실행

### 1. 패키지 설치

```bash
cd frontend
npm install
```

### 2. 개발 서버 실행

```bash
npm run dev
```

- 앱 주소 : `http://localhost:3000`
- API 요청 : `/api/*` → `http://localhost:8000/api/*` (자동 프록시)
  - 백엔드 서버가 `localhost:8000`에서 실행 중이어야 함

### 3. 프로덕션 빌드

```bash
npm run build
npm start
```

---

## 페이지별 상세 설명

### `/` — 랜딩 페이지 (`app/page.tsx`)

서비스 소개 및 진입 페이지입니다.

**구성:**
- **히어로 섹션**: 다크 그라디언트 배경 + 핵심 메시지
  - [아이디어 구상하기] → `/find-idea`
  - [지금 분석하기] → `/analyze`
- **통계 섹션**: 누적 분석 건수, 분석된 경쟁사 수 등
- **기능 소개 섹션**: AI 분석, 경쟁사 분석, 트렌드 리포트

---

### `/login` — 로그인/회원가입 (`app/login/page.tsx`)

탭으로 로그인과 회원가입을 전환합니다.

**로그인 탭:**
- 이메일 + 비밀번호 폼
- 비밀번호 분실 링크 (미구현 표시)
- Google / 카카오 소셜 로그인 버튼 (UI만)

**회원가입 탭:**
- 이름, 이메일, 비밀번호, 비밀번호 확인
- 비밀번호 불일치 시 클라이언트 측 에러 표시
- 서버 에러(이미 사용 중인 이메일 등)는 상단 에러 박스에 표시

**성공 시:** `saveAuth(token, user)` 호출 → 쿠키 저장 → `/mypage` 이동

---

### `/find-idea` — 아이디어 구상 (`app/find-idea/page.tsx`)

4단계 위저드(wizard) 형태로 선호도를 수집한 뒤 AI가 맞춤 아이디어를 추천합니다.

**단계:**
1. **관심 분야** — 복수 선택 (식음료, IT, 커머스 등 9가지)
2. **선호 방식** — 사업 형태 + 고객층 선택
3. **여건 확인** — 초기 자본, 팀 규모, 기술 수준
4. **아이디어 추천** — AI가 생성한 4개 카드 표시 (시장 적합도 포함)

**주의:** 로그인하지 않은 상태에서 "아이디어 추천받기" 클릭 시 `/login`으로 이동  
**AI 오류 시:** 하드코딩된 샘플 아이디어 4개를 폴백(fallback)으로 표시

---

### `/analyze` — 아이디어 분석 (`app/analyze/page.tsx`)

비즈니스 아이디어를 입력하면 AI가 SWOT, 경쟁사, 차별화 전략을 분석해줍니다.

**입력 섹션:**
- 기본 정보: 서비스명, 카테고리, 한 줄 소개, 해결 문제
- 비즈니스 모델: 타겟 고객, 수익 모델, 가치 제안, 가격, 자본
- 추가 정보: 알고 있는 경쟁사, 기타

**결과 섹션 (분석 완료 후):**
- **리포트 헤더**: 서비스명 + 요약 + 태그
- **SWOT 분석**: 4분면 그리드 (강점/약점/기회/위협)
- **시장 가능성 평가**: 5개 지표별 점수 + 프로그레스 바
- **경쟁사 분석**: 위협 수준별 배지 + 메타정보 + 차별화 포인트
- **차별화 전략**: 번호 순서가 있는 전략 목록

**로딩 중:** 전체 화면 오버레이 + 스피너 표시  
**FREE 플랜 한도 초과 시:** alert으로 안내 메시지 표시

---

### `/trend` — 요즘 트렌드 (`app/trend/page.tsx`)

현재 인기 있는 아이템 및 키워드 트렌드를 카드 형태로 보여줍니다.

**구성:**
- 다크 히어로 바 + 업데이트 시각 표시
- 카테고리 필터 버튼 (전체, 식음료, IT/테크, 라이프스타일 등)
- **1위(HOT)**: 전체 너비 가로 레이아웃 카드
- **2위 이하**: 3열 그리드 카드

**데이터:** 백엔드 `/api/trends/`에서 조회. 실패 시 하드코딩 폴백 사용

---

### `/market-share` — 시장 점유율 (`app/market-share/page.tsx`)

국내 주요 산업의 시장 점유율을 시각화합니다.

**구성:**
- 산업 탭 (IT/테크, 식음료, 핀테크, 헬스케어)
- **도넛 차트**: CSS `conic-gradient`로 순수 CSS 구현
- **바 차트**: 기업별 점유율 + 전분기 대비 증감
- **성장/위축 세그먼트**: 2열 미니 카드

**데이터 미준비 탭**: "준비 중" 플레이스홀더 표시

---

### `/popular-keywords` — 인기 검색어 (`app/popular-keywords/page.tsx`)

사용자들이 많이 검색하는 사업 아이디어 키워드를 보여줍니다.

**구성:**
- **태그 클라우드**: 인기도에 따라 5단계 크기/색상
- **카테고리별 키워드**: IT, 식음료, 헬스, 교육 — 상대적 인기도 바
- **사이드바 실시간 랭킹**: 1~10위 + 상승/하락/유지/NEW 배지

**개인정보 안내**: 구체적 수치는 표시하지 않고 상대적 수준만 표시

---

### `/mypage` — 마이페이지 (`app/mypage/page.tsx`)

로그인 필요 페이지. 비로그인 시 `/login`으로 리다이렉트.

**구성:**
- **프로필 배너**: 아바타, 이름, 이메일, 플랜 배지 + 이번 달 통계
- **분석 히스토리 탭**: 분석 카드 목록 (점수 표시, 삭제 가능)
- **아이디어 노트 탭**: 노트 목록 (상태 배지, 분석하기 버튼, 삭제)
  - "+ 새 아이디어 적어두기" 인라인 폼으로 빠른 추가
- **사이드바**:
  - 이번 달 사용량 프로그레스 바 (분석 횟수 / 아이디어 개수)
  - FREE 플랜이면 PRO 업그레이드 안내
  - 계정 설정 (이름/이메일/비밀번호 변경, 계정 탈퇴)

---

### `/pricing` — 요금제 (`app/pricing/page.tsx`)

FREE / PRO 플랜 비교 페이지.

**구성:**
- **월간/연간 토글**: 연간 선택 시 가격 자동 변경 (5,900 → 4,917원)
- **플랜 카드**: FREE(흰 배경), PRO(다크 그라디언트 + "가장 인기" 배지)
- **상세 비교 표**: 기능별 FREE/PRO 지원 여부
- **FAQ**: 아코디언 형식 (클릭 시 답변 열기/닫기)

---

## 공통 스타일 시스템 (`app/globals.css`)

CSS 변수로 색상 팔레트를 정의하고, Tailwind `@layer components`로 자주 사용하는 스타일을 클래스화합니다.

### CSS 변수 (색상)
```css
--primary       : #2563eb  /* 메인 파란색 (버튼, 링크) */
--primary-dark  : #1d4ed8  /* 호버 상태 파란색 */
--accent        : #06b6d4  /* 강조 청록색 (로고, 뱃지) */
--nav-bg        : #1e293b  /* 네비게이션 다크 배경 */
--dark          : #0f172a  /* 가장 어두운 텍스트 */
--bg            : #f8fafc  /* 페이지 기본 배경 (연한 회색) */
--border        : #e2e8f0  /* 테두리 색상 */
--text          : #334155  /* 일반 텍스트 */
--text-light    : #64748b  /* 보조 텍스트 (흐린 회색) */
```

### 공통 컴포넌트 클래스
```css
.btn-primary     /* 파란 채워진 버튼 */
.btn-secondary   /* 테두리 버튼 */
.card            /* 흰 배경 + 테두리 + 둥근 모서리 카드 */
.section-title   /* 섹션 제목 */
.form-label      /* 폼 레이블 */
.form-input      /* 인풋 필드 */
.nav-link        /* 네비게이션 링크 */
.tag             /* 파란 라벨 태그 */
```

---

## API 연동 구조

```
컴포넌트
  └─ import { analyzeAPI } from "@/lib/api"
       └─ api.post("/analyze/idea", data)
            └─ Axios 인스턴스 (baseURL="/api")
                 └─ next.config.ts 프록시
                      └─ http://localhost:8000/api/analyze/idea
```

### 인터셉터 동작
- **요청 시**: `Cookies.get("token")` → `Authorization: Bearer ...` 헤더 자동 추가
- **401 응답 시**: 쿠키 삭제 → `/login` 자동 리다이렉트

---

## 경로 별칭 (`tsconfig.json`)

`@/`는 프로젝트 루트(`frontend/`)를 가리킵니다.

```typescript
// 아래 두 줄은 동일
import api from "../../../lib/api";
import api from "@/lib/api";  ← 이걸 사용
```

---

## 개발 팁

### 백엔드 없이 테스트하기
각 페이지는 백엔드 API 호출 실패 시 하드코딩된 샘플 데이터(폴백)를 표시합니다.  
`/trend`, `/popular-keywords`, `/market-share`는 백엔드 없이도 UI 확인 가능합니다.

### 새 페이지 추가하기
`app/` 하위에 폴더 + `page.tsx` 파일만 만들면 자동으로 라우트가 생성됩니다:
```
app/new-feature/page.tsx → /new-feature 경로로 접근 가능
```

### Tailwind 커스텀 색상 사용
`tailwind.config.ts`에 정의된 색상을 클래스로 사용:
```tsx
<div className="bg-primary text-accent border-nav-bg">...</div>
```

### "use client" 지시어
- React 훅(`useState`, `useEffect`) 사용 시 파일 상단에 반드시 선언
- 쿠키 접근, 라우터 사용 시에도 필요
- 없으면 Next.js가 서버 컴포넌트로 처리 → 훅 사용 불가
