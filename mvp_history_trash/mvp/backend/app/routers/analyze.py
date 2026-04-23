# ============================================================
# routers/analyze.py — 아이디어 분석 요청 처리
#
# URL: POST /analyze
#
# 핵심 흐름:
#   1. 프론트에서 아이디어 정보를 받는다
#   2. Tavily로 관련 경쟁사/시장 정보를 웹 검색한다
#   3. 검색 결과 + 유저 입력을 OpenAI에 전달해 분석한다
#   4. AI 응답을 SSE로 실시간으로 프론트에 스트리밍한다
#   5. 완료되면 DB에 저장하고 report_id를 전달한다
#
# SSE(Server-Sent Events):
#   응답을 한 번에 보내지 않고 조각조각 보내는 방식.
#   AI가 글을 생성하면서 실시간으로 타이핑 효과를 내기 위해 사용.
# ============================================================

from fastapi import APIRouter, Header
from fastapi.responses import StreamingResponse
import json

from app.models.report import AnalyzeInput
from app.services import search as search_svc
from app.services import ai as ai_svc
from app.services import report as report_svc

router = APIRouter()


@router.post("/analyze")
async def analyze(
    body: AnalyzeInput,                              # 요청 본문 (자동으로 유효성 검사)
    authorization: str | None = Header(default=None), # Authorization 헤더 (로그인 유저 식별용)
):
    """
    아이디어 분석을 시작하고 SSE 스트림으로 결과를 반환한다.

    SSE 이벤트 종류:
      event: status  → 현재 진행 상태 메시지 (예: "검색 중...")
      event: chunk   → AI 응답 조각 (글자 단위로 올 수 있음)
      event: done    → 분석 완료, {"report_id": "uuid"} 포함
      event: error   → 오류 발생
    """
    user_id = _extract_user_id(authorization)  # JWT에서 유저 ID 추출 (TODO)

    async def event_stream():
        # ① 경쟁사 & 시장 검색
        yield _sse("status", "경쟁사 및 시장 데이터 검색 중...")
        search_results = await search_svc.search_competitors(body.topic)
        market_results = await search_svc.search_market_trends(body.topic)
        all_results = search_results + market_results  # 두 검색 결과 합치기

        # ② AI 스트리밍 분석
        yield _sse("status", "AI 분석 중...")
        buffer = ""  # AI 응답 조각을 모아두는 버퍼
        async for chunk in ai_svc.stream_analysis(
            body.topic,
            body.target or "",
            body.revenue_model or "",
            all_results,
        ):
            buffer += chunk           # 버퍼에 조각 누적
            yield _sse("chunk", chunk) # 동시에 프론트로 전달

        # ③ DB 저장 & 완료 알림
        try:
            result = json.loads(buffer)  # 누적된 버퍼를 JSON으로 파싱
            plan = "free"                # TODO: 유저 플랜 조회로 교체
            report_id = await report_svc.save_report(body, result, plan, user_id)
            yield _sse("done", json.dumps({"report_id": report_id}))
        except json.JSONDecodeError:
            # AI가 유효하지 않은 JSON을 반환했을 때
            yield _sse("error", "분석 결과 파싱 실패")

    # StreamingResponse: 응답을 한 번에 보내지 않고 event_stream()이 yield할 때마다 전송
    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _sse(event: str, data: str) -> str:
    """
    SSE 형식의 문자열을 만든다.
    SSE 규격: "event: 이벤트명\ndata: 데이터\n\n"
    빈 줄(\n\n) 이 이벤트 하나의 끝을 나타낸다.
    """
    return f"event: {event}\ndata: {data}\n\n"


def _extract_user_id(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ")
    try:
        from app.db.supabase import get_client
        res = get_client().auth.get_user(token)
        return res.user.id if res.user else None
    except Exception:
        return None
