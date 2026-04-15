# SYM (Search Your Market) — 개발 여정

> 포트폴리오용 기록. "이런 고민을 했다"는 흔적을 남기기 위한 문서.
> 기술적 결정 + 삽질 과정 + 왜 이렇게 했는지를 담음.

---

## 서비스 한줄 요약

창업자들의 시작을 쉽게 해준다.
아이디어를 입력하면 AI가 경쟁사/시장 데이터 기반으로 실현 가능성을 분석해주는 서비스.

---

## 전체 여정

### 1차 — 바이브코딩 (`/mvp` 폴더)

AI 도움 받아서 빠르게 만들어보려 했는데 구조가 너무 복잡해짐.
코드를 이해 못한 채로 진행하다 막힘.

### 2차 — MVP 재시도

FastAPI를 선택했는데 기초 개념이 없으니까 막히는 부분마다 왜 그런지 몰랐음.
asyncio, lifespan, SQLAlchemy 등 모르는 게 너무 많았음.

### 3차 — mvp2 (현재 진행 중)

처음부터 개념을 이해하면서 짜기로 방향을 바꿈.

- `mvp2/backend/study/` — FastAPI, asyncio, APScheduler 등 개념 공부 기록
- `mvp2/backend/my_level.md` — 현재 기술 수준 현황판
- `mvp2/backend/work.md` — 설계 고민 + 대화 로그 전체

현재 상태: DB 모델 완성, 서비스 구조/사용자 여정 확정, 파이프라인 설계 진행 중.

---

## 관련 폴더

| 폴더 | 설명 |
|------|------|
| `mvp2/backend/study/` | FastAPI/asyncio 등 개념 공부 노트 |
| `mvp2/backend/my_level.md` | 현재 기술 수준 (세션마다 업데이트) |
| `mvp2/backend/study/session_log.md` | 공부 세션 로그 |
| `mvp2/backend/work.md` | 설계 대화 로그 전체 (날것 그대로) |
| `devlog/` | 포트폴리오용 개발일지 (이 폴더) |
| `prototype/` | UI 프로토타입 HTML |
