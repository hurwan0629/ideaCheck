# ============================================================
# models/report.py — 리포트 관련 데이터 타입 정의
#
# Pydantic BaseModel을 사용한다.
# 역할:
#   - 잘못된 데이터가 들어오면 FastAPI가 자동으로 422 에러 반환
#   - 어떤 데이터를 받고 보내는지 문서화 역할도 함
#   - /docs 페이지에서 자동으로 스키마로 보여짐
# ============================================================

from pydantic import BaseModel
from typing import Any


class AnalyzeInput(BaseModel):
    """
    POST /analyze 요청 시 프론트에서 보내는 데이터 형태.
    topic은 필수, 나머지는 선택(None 허용).
    """
    topic: str                   # 아이디어 주제 (예: "AI 시장조사 SaaS") — 필수
    target: str | None = None    # 타겟 유저 (예: "개발자 창업자") — 선택
    revenue_model: str | None = None  # 수익 모델 (예: "Freemium SaaS") — 선택
    description: str | None = None   # 추가 설명 — 선택


class ReportResult(BaseModel):
    """
    AI가 분석하고 반환하는 결과 데이터 형태.
    ai.py에서 OpenAI가 이 구조의 JSON을 생성하도록 프롬프트에 안내한다.
    """
    summary: str                       # 아이디어 요약 및 가능성 평가
    competitors: list[dict[str, Any]]  # 경쟁사 목록 (이름, 설명, 강점, 약점)
    market_size: dict[str, Any]        # 시장 규모 (TAM, SAM, SOM)
    action_plan: list[str]             # 즉시 실행 가능한 다음 단계 5개
    sources: list[str]                 # 참고한 URL 목록


class ReportRow(BaseModel):
    """
    Supabase reports 테이블의 한 행(row) 형태.
    DB에서 데이터를 읽어올 때 이 타입으로 변환한다.
    """
    id: str                    # 리포트 고유 ID (UUID)
    user_id: str | None        # 생성한 유저 ID (비로그인이면 None)
    input: dict[str, Any]      # 유저가 입력한 원문 (AnalyzeInput을 dict로 저장)
    result: dict[str, Any]     # AI 분석 결과 (ReportResult를 dict로 저장)
    plan: str                  # 생성 시점의 플랜 ('free', 'lite', 'pro')
    created_at: str            # 생성 일시 (ISO 8601 형식)
