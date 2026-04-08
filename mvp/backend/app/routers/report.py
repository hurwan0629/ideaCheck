# ============================================================
# routers/report.py — 리포트 조회/삭제
#
# URL:
#   GET    /report/{id}  → 리포트 하나 조회 (비로그인도 가능)
#   DELETE /report/{id}  → 리포트 삭제 (본인만 가능)
# ============================================================

from fastapi import APIRouter, HTTPException, Header
from app.services import report as report_svc

router = APIRouter()


@router.get("/{report_id}")
async def get_report(report_id: str):
    """
    report_id에 해당하는 리포트를 조회한다.
    /report/[id] 페이지에서 호출한다.
    로그인 없이도 접근 가능 (공유 링크 기능을 위해).
    """
    report = await report_svc.get_report(report_id)
    if not report:
        # HTTP 404: 리소스를 찾을 수 없음
        raise HTTPException(status_code=404, detail="리포트를 찾을 수 없습니다.")
    return report


@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    authorization: str | None = Header(default=None),
):
    """
    리포트를 삭제한다.
    본인 리포트만 삭제 가능하므로 로그인이 필요하다.
    """
    user_id = _extract_user_id(authorization)
    if not user_id:
        # HTTP 401: 인증 필요
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    deleted = await report_svc.delete_report(report_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="리포트를 찾을 수 없습니다.")
    return {"ok": True}


def _extract_user_id(authorization: str | None) -> str | None:
    """TODO: JWT 검증 후 user_id 반환"""
    return None
