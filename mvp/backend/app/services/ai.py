# ============================================================
# services/ai.py — AI 분석 서비스
#
# OpenAI gpt-4o-mini를 사용해서 아이디어를 분석한다.
# 스트리밍 방식으로 응답을 조금씩 반환하여 타이핑 효과를 낸다.
#
# 사용 위치: routers/analyze.py
# 환경변수: OPENAI_API_KEY
#
# 추후 계획: Claude API (claude-sonnet)로 전환 예정
# ============================================================

from openai import AsyncOpenAI
from typing import AsyncGenerator
import os

# 싱글턴 패턴
_client: AsyncOpenAI | None = None

# ── 시스템 프롬프트 ─────────────────────────────────────────
# AI에게 "너는 이런 역할이야, 이런 형식으로 답해"라고 알려주는 지시문.
# response_format=json_object와 함께 사용하므로 반드시 JSON 반환을 요구해야 한다.
ANALYZE_SYSTEM_PROMPT = """당신은 스타트업 아이디어 검증 전문가입니다.
주어진 아이디어와 시장 조사 데이터를 바탕으로 다음을 JSON 형식으로 분석하세요:
- summary: 아이디어 요약 및 가능성 평가 (2~3문장)
- competitors: 경쟁사 목록 [{name, description, url, strength, weakness}]
- market_size: {tam, sam, som, growth_rate, source}
- action_plan: 즉시 실행 가능한 다음 단계 목록 (5개)
- sources: 참고한 URL 목록

반드시 유효한 JSON만 반환하세요."""


def get_client() -> AsyncOpenAI:
    """OpenAI 클라이언트를 반환한다. 없으면 새로 만든다."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
    return _client


async def stream_analysis(
    topic: str,
    target: str,
    revenue_model: str,
    search_results: list[dict],
) -> AsyncGenerator[str, None]:
    """
    아이디어 분석 결과를 스트리밍으로 생성한다.

    AsyncGenerator: 일반 함수처럼 한 번에 결과를 반환하지 않고,
    yield로 조각조각 반환한다. 타이핑 효과를 내기 위해 필요하다.

    처리 순서:
    1. 검색 결과를 텍스트로 정리 (컨텍스트 구성)
    2. 시스템 프롬프트 + 유저 입력 + 검색 결과를 OpenAI에 전달
    3. AI 응답 조각(chunk)을 받을 때마다 yield로 내보냄
    """
    client = get_client()

    # 검색 결과 목록을 텍스트 형태로 정리
    # 각 결과의 title과 content 앞 300자만 사용 (토큰 절감)
    context = "\n".join([
        f"- {r.get('title', '')}: {r.get('content', '')[:300]}"
        for r in search_results
    ])

    # AI에게 전달할 유저 메시지 구성
    user_prompt = f"""
아이디어: {topic}
타겟: {target or '미정'}
수익 모델: {revenue_model or '미정'}

시장 조사 데이터:
{context}
"""

    # OpenAI 스트리밍 호출
    # stream=True → 응답을 한 번에 받지 않고 조각으로 받음
    # response_format=json_object → 반드시 JSON만 반환하도록 강제
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": ANALYZE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        stream=True,
        response_format={"type": "json_object"},
    )

    # 응답 조각이 도착할 때마다 yield로 내보냄
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
