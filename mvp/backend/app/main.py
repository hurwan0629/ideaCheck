# ============================================================
# main.py — 서버의 입구 파일
#
# 역할:
#   1. FastAPI 앱 객체를 만든다
#   2. CORS 설정 (프론트가 다른 포트에서 요청해도 허용)
#   3. 각 기능별 라우터를 앱에 연결한다
#
# 실행 방법:
#   uvicorn app.main:app --reload
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# routers 폴더의 각 기능 파일을 가져온다
from app.routers import analyze, report, user, trends, webhook

# .env 파일에 있는 환경변수(API 키 등)를 불러온다
load_dotenv()

# FastAPI 앱 객체 생성
app = FastAPI(title="IdeaCheck API", version="0.1.0")

# ── CORS 설정 ──────────────────────────────────────────────
# 브라우저는 보안상 다른 주소(포트)로 요청을 막는다.
# 예) 프론트(localhost:3000) → 백엔드(localhost:8000) 요청을 허용하기 위해 필요.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, DELETE 등 모두 허용
    allow_headers=["*"],   # Authorization 헤더 등 모두 허용
)

# ── 라우터 연결 ────────────────────────────────────────────
# 각 라우터 파일에 정의된 URL들을 앱에 등록한다.
# tags는 /docs 페이지에서 API를 그룹으로 묶어 보여주는 용도.
app.include_router(analyze.router, tags=["analyze"])
app.include_router(report.router, prefix="/report", tags=["report"])  # /report/... 로 시작
app.include_router(user.router, prefix="/user", tags=["user"])        # /user/... 로 시작
app.include_router(trends.router, tags=["trends"])
app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])  # /webhook/... 로 시작


# ── 헬스체크 ───────────────────────────────────────────────
# 서버가 살아있는지 확인하는 단순 엔드포인트.
# Railway 같은 배포 플랫폼이 서버 상태를 확인할 때 사용.
@app.get("/health")
def health():
    return {"status": "ok"}
