# MVP3 Working Guide

이 폴더는 `SearchYourIdea`의 MVP3 작업 공간이다.
이전 MVP, MVP2에서 구조가 흔들렸던 경험을 반영해서, 이번에는 설계 기준과 작업 방식을 먼저 고정하고 구현한다.

이 문서는 다른 세션에서 다시 들어와도 같은 기준으로 작업하기 위한 운영 문서다.

## 1. 이 프로젝트의 최우선 목표

이 프로젝트에는 중요한 목표가 2개 있다.

1. 실제로 배포 가능한 MVP를 만든다.
2. 작업 과정에서 작성자가 직접 배우면서 이해할 수 있어야 한다.

즉, "빨리 돌아가는 코드"만 만드는 것이 목표가 아니다.
구조를 이해하면서 직접 수정 가능한 상태로 만드는 것이 중요하다.

---

## 2. 기준 문서 읽는 순서

MVP3의 설계 기준은 아래 3개 문서다.

1. `plan/backend_structure.md`
   - 백엔드 디렉토리 구조
   - `api`, `scheduler`, `common` 책임 분리

2. `plan/search_your_idea_mvp.dbml`
   - MVP 기준 데이터 모델
   - 어떤 데이터를 저장하는지

3. `plan/backend_run_guide.md`
   - 실제 실행 순서
   - 수동 테스트 / 자동 테스트 흐름

권장 읽는 순서는:

`backend_structure.md -> search_your_idea_mvp.dbml -> backend_run_guide.md`

이 순서로 보면:

- 먼저 구조를 이해하고
- 그 다음 저장 데이터 모델을 보고
- 마지막으로 실행 방법을 이해할 수 있다

---

## 3. 현재 고정된 설계 결정

현재 MVP3는 아래 결정을 기준으로 진행한다.

- 백엔드는 `api`, `scheduler`, `common` 3영역으로 나눈다.
- 실제 업무 로직은 `common`에 모은다.
- 크롤링은 사용자 요청마다 하지 않고 배치 작업으로 수행한다.
- MVP DB 구조는 `ideas`, `analysis_results`, `competitors`, `collected_news`를 기본으로 한다.
- 사용자 인증은 MVP에서 제외하고, 작성자 정보는 `ideas`에 함께 둔다.
- 분석 결과에 사용한 경쟁사/뉴스는 `analysis_results` 내부 JSONB 스냅샷으로 저장한다.

이 기준은 구현 중 임의로 자주 바꾸지 않는다.
구조 변경이 필요하면 먼저 이유를 문서에 남기고 바꾼다.

---

## 4. 작업 원칙

이 프로젝트는 학습을 겸해서 진행하므로 아래 원칙을 지킨다.

- 한 번에 큰 기능을 다 만들지 않는다.
- 항상 작은 단위로 구현하고 바로 실행 확인한다.
- 새 개념은 기능과 같이 배운다.
- 추상화는 늦게 하고, 동작 확인은 빨리 한다.
- 구조를 설명할 수 없는 코드는 쉽게 추가하지 않는다.

예를 들어:

- FastAPI 앱 실행
- DB 연결
- `POST /ideas`
- `POST /analysis/{idea_id}`
- `GET /analysis/{idea_id}/latest`

이런 식으로 단계별로 진행한다.

---

## 5. 학습 중심 작업 방식

이 프로젝트는 "AI가 전부 만들어주는 방식"으로 진행하지 않는다.
아래 방식으로 진행한다.

1. 이번 단계 목표를 작게 정한다.
2. 왜 이 구조를 쓰는지 짧게 이해한다.
3. 최소 코드만 만든다.
4. 직접 실행해서 확인한다.
5. 다음 단계로 넘어가기 전에 한 번 스스로 수정해본다.

각 작업은 가능하면 아래 4개를 같이 남긴다.

- 목적
- 완료 기준
- 학습 포인트
- 직접 확인할 것

---

## 6. 지금 단계의 추천 구현 우선순위

배포와 학습을 같이 만족하려면 아래 순서가 가장 안전하다.

1. 백엔드 폴더 골격 만들기
2. FastAPI 앱과 `GET /health` 만들기
3. SQLAlchemy 연결
4. ORM 모델 작성
5. Alembic migration 연결
6. `POST /ideas` 구현
7. `POST /analysis/{idea_id}` 구현
8. `GET /analysis/{idea_id}/latest` 구현
9. scheduler 골격 추가
10. 크롤러와 분석 로직 확장

핵심은 처음부터 전부 만들지 않는 것이다.
배포 1차 목표는 "아이디어 저장 + 분석 저장/조회"까지다.

---

## 7. 다른 세션에서 작업할 때 지켜야 할 것

다른 세션에서 이 폴더를 다시 읽을 때는 아래 순서를 먼저 따른다.

1. 이 `README.md`를 읽는다.
2. `plan/backend_structure.md`를 읽는다.
3. `plan/search_your_idea_mvp.dbml`를 읽는다.
4. `plan/backend_run_guide.md`를 읽는다.
5. `plan/todo.md`에서 현재 진행 단계와 다음 작업을 확인한다.

새 세션에서는 먼저 설계 문서를 다시 쓰지 않는다.
기존 기준을 읽고, 현재 TO-DO 기준으로 이어서 작업한다.

---

## 8. 구현 중 판단 기준

구현 중 어떤 선택이 애매하면 아래 기준으로 판단한다.

- 이 변경이 배포를 더 빠르게 만드는가?
- 이 변경이 작성자의 이해를 더 쉽게 만드는가?
- 지금 당장 필요한 복잡성인가?
- 문서 기준과 충돌하지 않는가?

위 질문에 `아니오`가 많으면 지금은 하지 않는다.

---

## 9. 문서 운영 규칙

- 설계 기준 변경 전에는 먼저 이유를 기록한다.
- 작업 시작 전에는 `plan/todo.md`의 현재 단계부터 확인한다.
- 작업이 끝나면 TO-DO 상태를 갱신한다.
- 새 기능을 넣고 싶어지면 먼저 MVP 범위를 넘는지 확인한다.

---

## 10. 현재 작업 상태

현재까지 완료된 상태:

- `mvp3/plan/` 기준 문서 3개 확정
- `mvp3/plan/todo.md` 작성
- `backend/` 폴더 골격 생성
- `docker-compose.yml` 초안 작성 및 PostgreSQL 설정 오타 수정
- `common/core/config.py`, `common/core/database.py` 생성
- scheduler 관련 진입점/잡 파일 생성
- repository, service, client, model, schema 파일 뼈대 생성

아직 안 끝난 핵심 상태:

- `GET /health` 엔드포인트 없음
- FastAPI 라우터 연결 미완료
- DB 실제 연결 확인 전
- ORM 모델 내용 미작성
- Alembic 미연결

현재 주의할 점:

- 설계 문서에는 `api/`, `tests/`라고 적혀 있지만 현재 구현은 `app/`, `test/`로 시작함
- 다음 구현 전에 이 네이밍을 유지할지, 문서 기준으로 맞출지 한 번 결정하는 것이 좋다
- 설정 키는 문서에 따라 `LLM_API_KEY`로 적힌 곳이 있지만 현재 코드는 `OPENAI_API_KEY`를 사용 중이다

---

## 11. 다음 세션용 작업 재개 메모

다음 세션에서 바로 이어서 작업하려면 아래 맥락을 기준으로 보면 된다.

- 목표 1: 실제 배포 가능한 MVP 만들기
- 목표 2: 작성자가 배우면서 직접 이해할 수 있게 만들기
- 현재 단계: "구조 생성"은 대부분 끝났고, 이제 "최소 실행 확인" 단계로 넘어가는 시점
- 바로 다음 기술 목표: FastAPI 라우팅, health check, 실행 확인
- 지금은 기능 확장보다 "실제로 부팅되는 최소 서버"를 먼저 만드는 것이 우선

다음 세션에서 우선 확인할 파일:

- `mvp3/README.md`
- `mvp3/plan/todo.md`
- `mvp3/backend/app/main.py`
- `mvp3/backend/app/router.py`
- `mvp3/backend/common/core/config.py`
- `mvp3/backend/common/core/database.py`

다음 세션의 바로 다음 작업 순서:

1. `plan/todo.md` 확인
2. `backend/app/main.py`와 `backend/app/router.py` 확인
3. `GET /health` 추가
4. FastAPI 서버 실행
5. `/health` 200 확인

---

## 12. 한 줄 요약

MVP3는 "배포 가능한 작은 구조"를 만들면서, 작성자가 FastAPI, SQLAlchemy, Alembic, scheduler 구조를 직접 이해할 수 있도록 단계별로 구현하는 프로젝트다.
