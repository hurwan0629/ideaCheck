# MVP3 TO-DO

이 문서는 MVP3 구현용 작업 체크리스트다.
목표는 2개다.

1. 실제 배포 가능한 MVP 만들기
2. 작업 과정에서 구조와 개념을 학습하기

완료 표시 규칙:

- `[ ]` 아직 시작 전
- `[~]` 진행 중
- `[x]` 완료

---

## 0. 작업 기준 고정

- [x] 기준 문서 3개 확정
  - `backend_structure.md`
  - `search_your_idea_mvp.dbml`
  - `backend_run_guide.md`
- [x] MVP3 작업 원칙 문서 작성
  - `mvp3/README.md`
- [x] 구현 시작 전 폴더 구조 최종 확인

학습 포인트:

- 설계 문서와 구현 기준을 분리해서 관리하는 이유

완료 기준:

- 이후 세션에서도 어떤 문서를 기준으로 읽어야 하는지 바로 알 수 있어야 함

---

## 1. 백엔드 프로젝트 골격 만들기

- [x] `backend/` 루트 디렉토리 생성
- [~] `api/`, `scheduler/`, `common`, `tests/` 생성
  - 현재 구현은 `api/` 대신 `app/`, `tests/` 대신 `test/`
- [x] 각 디렉토리의 역할에 맞는 초기 파일 생성
- [x] FastAPI 앱 시작점 생성
  - 현재 구현 파일: `backend/app/main.py`
- [x] 라우터 등록 구조 생성
  - 현재 구현 파일: `backend/app/router.py`
- [x] `scheduler/main.py` 시작점 생성

학습 포인트:

- FastAPI 프로젝트를 왜 계층별로 나누는지
- 실행 단위와 업무 로직을 왜 분리하는지

완료 기준:

- 구조가 `backend_structure.md`와 크게 맞아야 함

현재 메모:

- 구조 뼈대는 생성 완료
- 네이밍은 문서와 완전히 일치하지 않음
- 다음에 `app`을 유지할지 `api`로 바꿀지 한 번 결정 필요

---

## 2. FastAPI 최소 실행 확인

- [ ] `GET /health` 엔드포인트 추가
- [ ] 로컬에서 FastAPI 서버 실행
- [ ] `/health` 200 응답 확인

학습 포인트:

- FastAPI 엔트리포인트
- 라우터 등록 방식
- 요청과 응답의 흐름

완료 기준:

- 서버가 정상 기동되고 health check가 동작해야 함

현재 메모:

- 아직 라우터 연결과 health 구현 전
- 다음 세션의 첫 작업은 여기부터 시작

---

## 3. 환경 변수와 설정 구조 만들기

- [x] `common/core/config.py` 생성
- [x] `DATABASE_URL`, API 키 설정 정의
- [x] `.env.example` 초안 작성
- [ ] 환경 변수 없을 때의 실패 메시지 기준 정리

학습 포인트:

- 설정을 코드에 하드코딩하면 왜 위험한지
- 설정 모듈이 왜 필요한지

완료 기준:

- 앱이 설정값을 한 곳에서 읽도록 정리되어야 함

현재 메모:

- 현재 코드는 `OPENAI_API_KEY` 사용 중
- 일부 문서에는 `LLM_API_KEY`로 적혀 있으므로 나중에 이름 통일 필요

---

## 4. DB 연결과 SQLAlchemy 기본 구조

- [x] `common/core/database.py` 생성
- [x] SQLAlchemy engine / session 구조 추가
- [x] Base 선언 위치 정리
- [ ] DB 연결 테스트 가능한 상태 만들기

학습 포인트:

- engine
- session
- declarative base
- 요청 단위 세션 관리

완료 기준:

- 앱에서 DB 세션을 만들 수 있어야 함

현재 메모:

- DB 연결 파일은 있음
- 실제 연결 확인은 아직 안 함
- 이름 정리 필요 여부 확인 (`Mvp2Database` 같은 이전 이름 잔재)

---

## 5. ORM 모델 만들기

- [x] `Idea` 모델 파일 생성
- [x] `AnalysisResult` 모델 파일 생성
- [x] `Competitor` 모델 파일 생성
- [x] `CollectedNews` 모델 파일 생성
- [ ] DBML과 모델 차이 검토
- [ ] 모델 필드 실제 작성

학습 포인트:

- DBML과 ORM 모델의 대응 관계
- 컬럼과 JSONB를 나누는 기준
- FK가 필요한 곳과 필요 없는 곳

완료 기준:

- DBML 기준 핵심 테이블 4개가 코드에 반영되어야 함

현재 메모:

- 파일만 있고 실제 모델 구현은 아직 비어 있음

---

## 6. Alembic 연결

- [ ] Alembic 초기화
- [ ] migration 설정 연결
- [ ] 첫 migration 생성
- [ ] DB에 테이블 생성 확인

학습 포인트:

- ORM 모델만으로 끝나지 않는 이유
- migration이 필요한 이유
- schema 변경 이력 관리 방식

완료 기준:

- migration으로 테이블 생성이 가능해야 함

---

## 7. 아이디어 입력 기능

- [x] `schemas/idea.py` 파일 생성
- [x] `repositories/idea_repository.py` 파일 생성
- [x] `services/idea_service.py` 파일 생성
- [ ] 아이디어 라우터 파일 생성
- [ ] `POST /ideas` 구현
- [ ] 저장 결과로 `idea_id` 반환

학습 포인트:

- router -> service -> repository 흐름
- DTO와 ORM 모델 차이
- 입력 검증과 DB 저장의 책임 분리

완료 기준:

- API 호출로 아이디어가 DB에 저장되어야 함

현재 메모:

- 뼈대 파일은 있음
- 실제 구현은 아직 전

---

## 8. 분석 결과 저장/조회 기능

- [x] `schemas/analysis.py` 파일 생성
- [x] `repositories/analysis_repository.py` 파일 생성
- [x] `services/analysis_service.py` 파일 생성
- [x] `clients/llm_client.py` 파일 생성
- [ ] `POST /analysis/{idea_id}` 구현
- [ ] `GET /analysis/{idea_id}/latest` 구현

학습 포인트:

- 유스케이스 중심 서비스 구성
- 외부 클라이언트 분리 이유
- 분석 결과 스냅샷 저장 방식

완료 기준:

- 아이디어 기준으로 분석 결과 생성 및 최신 결과 조회가 가능해야 함

주의:

- 처음에는 LLM 실제 연결보다 저장/조회 흐름을 먼저 완성

---

## 9. 크롤링 참조 데이터 구조 만들기

- [x] `repositories/competitor_repository.py` 파일 생성
- [x] `repositories/news_repository.py` 파일 생성
- [x] `clients/crawler_client.py` 파일 생성
- [x] `services/crawler_service.py` 파일 생성

학습 포인트:

- 외부 데이터 수집 로직을 API 로직과 분리하는 이유
- 수집과 저장을 별도 책임으로 나누는 방법

완료 기준:

- 크롤링 로직을 붙일 준비가 된 구조가 있어야 함

현재 메모:

- 현재는 빈 뼈대 수준

---

## 10. Scheduler 골격 만들기

- [x] `scheduler/schedule_runner.py` 작성
- [x] `jobs/crawl_news.py` 작성
- [x] `jobs/crawl_competitors.py` 작성
- [ ] scheduler 프로세스 실행 구조 확인

학습 포인트:

- API 서버와 배치 프로세스의 차이
- "언제 실행할지"와 "무엇을 할지"의 책임 분리

완료 기준:

- scheduler가 `crawler_service`를 호출할 수 있는 구조여야 함

---

## 11. 테스트 추가

- [ ] `tests/test_health.py`
- [ ] `tests/test_ideas.py`
- [ ] `tests/test_analysis.py`
- [ ] repository 또는 service 레벨 기본 테스트 추가

학습 포인트:

- 테스트를 왜 가장 바깥 API만 보는 방식으로 끝내면 안 되는지
- 최소 테스트 범위를 어디까지 잡을지

완료 기준:

- 핵심 흐름 3개는 자동 테스트로 확인 가능해야 함

핵심 흐름:

- health 응답
- idea 저장
- analysis 저장/조회

---

## 12. 배포 준비

- [ ] 실행 환경 변수 정리
- [ ] production 실행 명령 정리
- [ ] DB migration 적용 절차 정리
- [ ] 배포 전 체크리스트 작성

학습 포인트:

- 로컬 실행과 배포 실행의 차이
- 환경 변수, DB, migration이 배포에서 왜 중요한지

완료 기준:

- 최소한 백엔드 단독 배포가 가능한 상태여야 함

---

## 13. 비기능 요구사항 점검

- [ ] 분석 API 응답 목표 10초 기준 점검
- [ ] 외부 API 실패 시 에러 메시지 기준 정리
- [ ] 재시도 여부와 fallback 기준 정리
- [ ] 크롤링 주기 설정값 정리

학습 포인트:

- 기능 요구사항과 비기능 요구사항의 차이
- 사용자 입장에서 장애 메시지가 왜 중요한지

완료 기준:

- 실패했을 때도 어디가 문제인지 알 수 있어야 함

---

## 14. 현재 MVP 범위 밖 항목

아래는 당장은 하지 않는다.

- [ ] 로그인/인증
- [ ] 마이페이지 고도화
- [ ] 고급 추천 알고리즘
- [ ] 완전한 트렌드 대시보드
- [ ] 과한 정규화
- [ ] 너무 이른 비동기 최적화

이유:

- 현재 목표는 배포 가능한 MVP와 학습 가능한 구조 확보이기 때문

---

## 15. 이번 작업 방식 규칙

각 단계는 아래 형식으로 진행한다.

1. 이번 단계 목표 확인
2. 왜 필요한지 짧게 이해
3. 최소 구현
4. 직접 실행
5. 직접 한 번 수정
6. 다음 단계로 이동

이 규칙은 구현 속도보다 이해도를 높이기 위한 것이다.

---

## 16. 바로 다음 추천 작업

현재 가장 먼저 할 일:

- [x] `backend/` 폴더 골격 생성
- [x] FastAPI 앱 생성
- [ ] `GET /health` 동작 확인

바로 다음 순서:

1. `backend/app/router.py` 정리
2. `health` 라우터 파일 생성
3. `app/main.py`에 라우터 연결
4. FastAPI 실행
5. `/health` 200 확인

여기까지 끝나면 다음 단계로 DB 연결 확인을 진행한다.
