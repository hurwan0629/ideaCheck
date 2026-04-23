from datetime import date
from sqlalchemy.orm import Session
import json
from app.clients import gpt
from app.db import get_session
from app.models.collection.competitor_analyses import CompetitorAnalysis
from app.models.collection.competitors import Competitor
from app.models.collection.competitor_features import CompetitorFeature
from app.models.collection.competitor_policies import CompetitorPolicy

EMBEDDING_DIM = 1536



def generate_analyses_for_all(db: Session) -> None:
    """전 경쟁사 종합 분석. 분기 quarterly_job에서 호출."""
    competitor_ids = db.query(Competitor.competitor_id).all()
    for (competitor_id,) in competitor_ids:
        generate_analysis_for_one(db, competitor_id)


def generate_analysis_for_one(db: Session, competitor_id: int) -> None:
    """
    경쟁사 1개 분석 생성.
    재분석 큐(consume_reanalysis_queue)에서도 단건으로 호출됨.
    """
    context = _gather_competitor_context(db, competitor_id)
    analysis = _generate_with_ai(context)
    if not analysis:
        return

    _save_analysis(db, competitor_id, analysis)

    embedding_text = _build_embedding_text(context, analysis)
    embedding_vector = _create_embedding(embedding_text)
    _save_embedding(db, competitor_id, embedding_vector)


def _gather_competitor_context(db: Session, competitor_id: int) -> dict:
    # COMPETITORS 정보
    competitor = db.query(Competitor).filter(Competitor.competitor_id == competitor_id).first()
    if not competitor:
        return {}
    # COMPETITOR_FEATURES
    competitor_features = db.query(CompetitorFeature).filter(CompetitorFeature.competitor_id == competitor_id).all()
    # COMPETITOR_POLICIES — 가장 최근 1건
    latest_policy = db.query(CompetitorPolicy).filter(CompetitorPolicy.competitor_id == competitor_id).order_by(CompetitorPolicy.policy_date.desc()).first()
    return {
        "name": competitor.name,
        "description": competitor.description,
        "target_customer": competitor.target_customer,
        "features": [f.feature_name for f in competitor_features],
        "recent_policies": list(latest_policy.policy_data.keys()) if latest_policy and latest_policy.policy_data else [],
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
    response = gpt.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    try:
        data = response.choices[0].message.content
        if data is None:
            return
        return json.loads(data)
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


def _save_analysis(db: Session, competitor_id: int, analysis: dict) -> None:
    db.add(CompetitorAnalysis(
        competitor_id=competitor_id,
        analysis_date=date.today(),
        strength=analysis.get("strength"),
        weakness=analysis.get("weakness"),
        characteristic=analysis.get("characteristic"),
    ))
    db.commit()


def _save_embedding(db: Session, competitor_id: int, vector: list[float]) -> None:
    # TODO: DB upsert (pgvector 컬럼에 저장)
    pass
