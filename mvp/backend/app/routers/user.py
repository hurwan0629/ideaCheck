# ============================================================
# routers/user.py — 로그인한 유저 관련 API
#
# URL:
#   GET /user/reports  → 내 리포트 목록
#   GET /user/usage    → 이번 달 사용량 조회
#   GET /user/profile  → 프로필 + 구독 플랜 조회
#
# 세 가지 모두 로그인이 필요하다.
# ============================================================

from fastapi import APIRouter, HTTPException, Header
from app.services import report as report_svc
from app.db.supabase import get_client
from datetime import datetime, timezone

router = APIRouter()


@router.get("/reports")
async def get_reports(authorization: str | None = Header(default=None)):
    """
    로그인한 유저의 리포트 목록을 최신순으로 반환한다.
    대시보드 페이지에서 사용한다.
    """
    user_id = _extract_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    return await report_svc.get_user_reports(user_id)


@router.get("/usage")
async def get_usage(authorization: str | None = Header(default=None)):
    """
    이번 달 사용량을 조회한다.
    무료 플랜 유저의 한도 초과 여부를 확인할 때 사용한다.

    처리 방식:
    - 이번 달 1일 00:00 이후의 usage_logs를 모두 가져온다
    - action별로 카운트해서 반환한다
    """
    user_id = _extract_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    db = get_client()
    now = datetime.now(timezone.utc)
    # 이번 달 1일 00:00:00 UTC
    month_start = now.replace(day=1, hour=0, minute=0, second=0).isoformat()

    # 이번 달 이후의 usage_logs만 조회
    res = (
        db.table("usage_logs")
        .select("action")
        .eq("user_id", user_id)
        .gte("created_at", month_start)  # gte = greater than or equal (>=)
        .execute()
    )
    logs = res.data or []

    return {
        "month": now.strftime("%Y-%m"),
        "analyze_count": sum(1 for l in logs if l["action"] == "analyze"),
        "pdf_download_count": sum(1 for l in logs if l["action"] == "pdf_download"),
    }


@router.get("/profile")
async def get_profile(authorization: str | None = Header(default=None)):
    """
    유저 프로필과 구독 플랜을 반환한다.
    설정 페이지와 헤더의 플랜 표시에 사용한다.
    """
    user_id = _extract_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    db = get_client()
    res = db.table("profiles").select("*").eq("id", user_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")
    return res.data


def _extract_user_id(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ")
    try:
        res = get_client().auth.get_user(token)
        return res.user.id if res.user else None
    except Exception:
        return None
