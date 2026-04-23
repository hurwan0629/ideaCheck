# 모르는 개념 목록

> 대화 중 나온 것들 중 공부가 필요해 보이는 것들.
> 공부하면 지우거나 취소선 처리.

---

- **TLS Fingerprinting (JA3/JA4)**: TLS 핸드셰이크 패턴으로 클라이언트가 Python인지 브라우저인지 식별하는 기술. User-Agent 위장해도 이걸로 봇 감지 가능 (2026-04-16 발견)
- **navigator.webdriver**: headless 브라우저임을 JS에서 감지할 수 있는 브라우저 플래그. `true`면 자동화 도구로 판단됨 (2026-04-16 발견)
- **SQLAlchemy dirty tracking**: ORM 객체 필드 변경 시 자동으로 dirty 상태로 마킹, commit 시 UPDATE 쿼리 자동 생성. 명시적 update 호출 불필요 (2026-04-16 발견)
- **httpx.Client 커넥션 풀**: Client를 싱글턴으로 유지하면 TCP 연결을 재사용. 매번 새로 만들면 연결을 매번 새로 맺음 (2026-04-16 발견)
- **Playwright networkidle**: 네트워크 요청이 500ms 동안 없을 때 로딩 완료로 판단하는 wait 조건 (2026-04-16 발견)
- **Playwright wait_until 옵션들**: domcontentloaded / load / networkidle 차이 및 각각 어떤 상황에 써야 하는지 (2026-04-17 발견)
- **httpx vs Playwright 크롤링 선택 기준**: 정적 사이트엔 httpx, JS 렌더링 필요하면 Playwright — 판단 기준과 _needs_js 같은 휴리스틱 패턴 (2026-04-17 발견)
