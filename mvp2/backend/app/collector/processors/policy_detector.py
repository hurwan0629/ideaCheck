import anthropic
from anthropic.types import TextBlock
import json

from datetime import date, datetime, timedelta, timezone
from app.collector.queue.reanalysis_queue import add_to_queue
from sqlalchemy.orm import Session
from app.models.collection.competitors import Competitor
from app.models.collection.competitor_policies import CompetitorPolicy
from app.models.collection.policy_types import PolicyType

claude = anthropic.Anthropic()

# 동일한 기업이 한달 내로 아래 숫자 이상의 정책변경을 한다면 분기가 되지 않아도 기업 정보를 수정
REANALYSIS_THRESHOLD = 3


def detect_policy_changes(db: Session, raw_news: list[dict]) -> None:
    """
    수집된 뉴스에서 경쟁사 정책 변경 감지.
    매일 daily_job에서 process_market_news 다음에 호출.
    """
    # TODO: DB에서 COMPETITORS, POLICY_TYPES(is_active=true) 조회
    # policy_types에 policy_props 포함 — Claude가 POLICY_DATA 필드를 이 목록에 맞게 채움
    competitors = db.query(Competitor).all()
    """
    [{"competitor_id": 1, "name": "토스"}]
    """
    policy_types = db.query(PolicyType).filter(PolicyType.is_active == True).all()
    """
    [
        {
            "policy_type_id": 1,
            "name": "가격 정책",
            "policy_props": ["tier", "base_price", "enterprise_contact"],
        },
        {
            "policy_type_id": 2,
            "name": "현지화",
            "policy_props": ["region", "launch_date", "localized_features"],
        },
    ]
    """

    for article in raw_news:
        # 해당 뉴스가 특정 기업의 정책을 변경하는 내용이다
        # -> 경쟁사id, 정책id 뽑아서 
        detected = _detect_policy_in_article(article, competitors, policy_types)
        if not detected:
            continue

        # competitor_id의 정책이 policy_type_idㄹ 변경되었다.
        competitor_id = detected["competitor_id"]
        policy_type_id = detected["policy_type_id"]
        policy_data = detected["policy_data"]

        if _is_changed(db, competitor_id, policy_type_id, policy_data):
            _save_policy(db, competitor_id, policy_type_id, policy_data, article["published_at"])
            _check_reanalysis_threshold(db, competitor_id)


def _detect_policy_in_article(
    article: dict,
    competitors: list[Competitor],
    policy_types: list[PolicyType],
) -> dict | None:
    competitor_names = [c.name for c in competitors]

    # policy_props를 프롬프트에 포함 — Claude가 각 유형의 POLICY_DATA 필드를 정확히 채우도록 지정
    policy_type_descriptions = "\n".join(
        f'- "{pt.name}": policy_data 필드는 {pt.policy_props}'
        for pt in policy_types
    )

    prompt = f"""
다음 뉴스 기사가 아래 경쟁사 중 하나의 정책 변경에 해당하는지 판단해서 JSON으로만 답해줘.

감시 대상 경쟁사: {competitor_names}

감시할 정책 유형과 각 유형의 policy_data 필드:
{policy_type_descriptions}

뉴스 제목: {article["title"]}
뉴스 본문: {article["content"][:1500]}

해당하는 경우 — policy_data는 해당 policy_type의 지정된 필드만 사용:
{{
  "competitor_name": "해당 경쟁사명",
  "policy_type_name": "해당 정책 유형명",
  "policy_data": {{
    "지정된 필드명": "뉴스에서 추출한 값 (확인 불가면 null)"
  }},
  "published_date": "YYYY-MM-DD"
}}

해당하지 않으면: null
"""

    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    block = response.content[0]
    if not isinstance(block, TextBlock):
        return None
    text = block.text.strip()
    if text == "null":
        return None

    try:
        result = json.loads(text)

        # 경쟁사명 → competitor_id 변환
        competitor_map = {c.name: c.competitor_id for c in competitors}
        result["competitor_id"] = competitor_map.get(result.get("competitor_name"))

        # policy_type_name → policy_type_id 변환
        policy_type_map = {pt.name: pt.policy_type_id for pt in policy_types}
        result["policy_type_id"] = policy_type_map.get(result.get("policy_type_name"))

        if not result["competitor_id"] or not result["policy_type_id"]:
            return None

        return result
    except json.JSONDecodeError:
        return None


def _is_changed(db: Session, competitor_id: int, policy_type_id: int, new_policy_data: dict) -> bool:
    # 7일 이내에 동일 경쟁사 + 동일 정책 타입 레코드가 있으면 중복으로 간주
    # TODO: 추후 AI 기반 의미론적 비교로 교체
    since = date.today() - timedelta(days=7)
    exists = db.query(CompetitorPolicy).filter(
        CompetitorPolicy.competitor_id == competitor_id,
        CompetitorPolicy.policy_type_id == policy_type_id,
        CompetitorPolicy.policy_date >= since,
    ).first()
    return exists is None


def _save_policy(
    db: Session,
    competitor_id: int,
    policy_type_id: int,
    policy_data: dict,
    published_date: str,
) -> None:
    db.add(CompetitorPolicy(
        competitor_id=competitor_id,
        policy_type_id=policy_type_id,
        policy_date=date.fromisoformat(published_date),
        policy_data=policy_data
    ))

def _check_reanalysis_threshold(db: Session, competitor_id: int) -> None:
    since = datetime.now(timezone.utc) - timedelta(days=30)
    count = db.query(CompetitorPolicy).filter(
        CompetitorPolicy.competitor_id==competitor_id,
        CompetitorPolicy.policy_date>=since).count()
    if count >= REANALYSIS_THRESHOLD:
        add_to_queue(competitor_id)
