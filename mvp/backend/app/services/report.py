# ============================================================
# services/report.py — 리포트 DB 처리 서비스
#
# Supabase reports 테이블에 대한 CRUD 작업을 담당한다.
# (Create, Read, Update, Delete)
#
# 사용 위치: routers/analyze.py, routers/report.py, routers/user.py
# ============================================================

import uuid
import json
from app.db.supabase import get_client
from app.models.report import AnalyzeInput, ReportRow


async def save_report(
    input_data: AnalyzeInput,
    result: dict,
    plan: str,
    user_id: str | None = None,
) -> str:
    """
    분석이 완료된 리포트를 DB에 저장하고 report_id를 반환한다.

    인자:
      input_data : 유저가 입력한 데이터 (AnalyzeInput)
      result     : AI 분석 결과 딕셔너리
      plan       : 생성 시점의 플랜 ('free', 'lite', 'pro')
      user_id    : 로그인한 유저의 ID (비로그인이면 None)

    반환: 생성된 리포트의 UUID 문자열
    """
    db = get_client()
    report_id = str(uuid.uuid4())  # 고유한 ID 생성

    db.table("reports").insert({
        "id": report_id,
        "user_id": user_id,
        "input": input_data.model_dump(),  # Pydantic 모델 → dict 변환
        "result": result,
        "plan": plan,
    }).execute()

    return report_id


async def get_report(report_id: str) -> ReportRow | None:
    """
    report_id로 특정 리포트를 조회한다.
    없으면 None을 반환한다.
    """
    db = get_client()
    res = db.table("reports").select("*").eq("id", report_id).single().execute()
    return ReportRow(**res.data) if res.data else None


async def get_user_reports(user_id: str) -> list[ReportRow]:
    """
    특정 유저의 모든 리포트를 최신순으로 조회한다.
    대시보드 페이지에서 사용한다.
    """
    db = get_client()
    res = (
        db.table("reports")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)  # 최신 리포트가 먼저 오도록 정렬
        .execute()
    )
    return [ReportRow(**r) for r in res.data]


async def delete_report(report_id: str, user_id: str) -> bool:
    """
    리포트를 삭제한다.
    보안을 위해 user_id도 같이 확인해서 본인 리포트만 삭제 가능하게 한다.

    반환: 삭제 성공 여부 (True/False)
    """
    db = get_client()
    res = (
        db.table("reports")
        .delete()
        .eq("id", report_id)
        .eq("user_id", user_id)   # 본인 리포트만 삭제 가능
        .execute()
    )
    return bool(res.data)
