import anthropic
import json

claude = anthropic.Anthropic()

EMBEDDING_DIM = 1536


def generate_analyses_for_all() -> None:
    """전 경쟁사 종합 분석. 분기 quarterly_job에서 호출."""
    # TODO: DB에서 SELECT * FROM COMPETITORS
    competitor_ids = [1, 2, 3]
    for competitor_id in competitor_ids:
        generate_analysis_for_one(competitor_id)


def generate_analysis_for_one(competitor_id: int) -> None:
    """
    경쟁사 1개 분석 생성.
    재분석 큐(consume_reanalysis_queue)에서도 단건으로 호출됨.
    """
    context = _gather_competitor_context(competitor_id)
    analysis = _generate_with_ai(context)
    if not analysis:
        return

    _save_analysis(competitor_id, analysis)

    embedding_text = _build_embedding_text(context, analysis)
    embedding_vector = _create_embedding(embedding_text)
    _save_embedding(competitor_id, embedding_vector)


def _gather_competitor_context(competitor_id: int) -> dict:
    # TODO: DB에서 COMPETITORS + COMPETITOR_FEATURES + 최근 COMPETITOR_POLICIES 조회
    return {
        "name": "토스",
        "description": "금융 슈퍼앱",
        "target_customer": "MZ세대 개인",
        "features": ["간편 송금", "투자", "보험"],
        "recent_policies": ["프리미엄 구독 도입", "동남아 진출"],
    }


def _generate_with_ai(context: dict) -> dict | None:
    prompt = f"""
다음 경쟁사 정보를 분석해서 JSON으로만 답해줘.

경쟁사 정보:
{json.dumps(context, ensure_ascii=False, indent=2)}

답변 형식:
{{
  "strength": ["강점1", "강점2"],
  "weakness": ["약점1", "약점2"],
  "characteristic": {{
    "market_share": {{
      "estimated_pct": "10-20%",
      "confidence": "low",
      "basis": "추정 근거"
    }},
    "growth": {{
      "yoy_pct": null,
      "trend": "up",
      "confidence": "medium",
      "basis": "성장 판단 근거"
    }},
    "keywords": ["키워드1", "키워드2"]
  }}
}}

실수치 데이터가 없으면 yoy_pct는 null, confidence는 low.
"""
    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        return json.loads(response.content[0].text)
    except json.JSONDecodeError:
        return None


def _build_embedding_text(context: dict, analysis: dict) -> str:
    parts = [
        context.get("description", ""),
        f"타겟 고객: {context.get('target_customer', '')}",
        f"강점: {', '.join(analysis.get('strength', []))}",
        f"약점: {', '.join(analysis.get('weakness', []))}",
        f"키워드: {', '.join(analysis.get('characteristic', {}).get('keywords', []))}",
    ]
    return " | ".join(filter(None, parts))


def _create_embedding(text: str) -> list[float]:
    # TODO: OpenAI text-embedding-3-small 실제 호출
    # import openai
    # client = openai.OpenAI()
    # response = client.embeddings.create(model="text-embedding-3-small", input=text)
    # return response.data[0].embedding
    return [0.0] * EMBEDDING_DIM


def _save_analysis(competitor_id: int, analysis: dict) -> None:
    # TODO: DB INSERT (UPDATE 없이 새 행 — 이력 보존)
    pass


def _save_embedding(competitor_id: int, vector: list[float]) -> None:
    # TODO: DB upsert (pgvector 컬럼에 저장)
    pass
