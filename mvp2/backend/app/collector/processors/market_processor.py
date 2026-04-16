import anthropic
import json

from sqlalchemy.orm import Session

from app.db import get_session
from app.models.collection.market_raw_sources import MarketRawSource, SourceType
from app.models.collection.market_extracts import MarketExtract, ExtractType

claude = anthropic.Anthropic()


def process_market_news(raw_news: list[dict]) -> None:
    """
    news_crawler에서 받은 뉴스 목록 처리:
    1. MARKET_RAW_SOURCES에 원본 저장
    2. Claude로 분류 + 유의미 여부 판단
    3. 유의미하면 MARKET_EXTRACTS 저장
    """
    with get_session() as db:
        for article in raw_news:
            raw_source_id = _save_raw_source(db, article)
            extraction = _extract_with_ai(article["title"], article["content"])
            if extraction and extraction.get("is_meaningful"):
                _save_extract(db, raw_source_id, extraction)


def _save_raw_source(db: Session, article: dict) -> int:
    record = MarketRawSource(
        title=article["title"],
        source_type=SourceType(article["source_type"]),
        source_url=article.get("url"),
        raw_content=article.get("content"),
        published_at=article.get("published_at"),
    )
    db.add(record)
    db.flush()  # INSERT 실행 → raw_source_id 채워짐 (commit은 아님)
    return record.raw_source_id


def _extract_with_ai(title: str, content: str) -> dict | None:
    prompt = f"""
다음 뉴스 기사를 분석해서 창업자에게 유용한 정보인지 판단하고, JSON으로만 답해줘.

제목: {title}
본문: {content[:2000]}

분류 기준:
- PAIN_POINT: 사람들이 겪는 불편함, 사회 문제, 미해결 니즈를 다루는 내용
- MARKET_SIZE: 특정 시장의 규모나 성장률 수치가 담긴 내용
- STARTUP_CASE: 특정 문제를 해결하려는 스타트업 사례

답변 형식 (이 JSON만 반환, 다른 텍스트 없이):
{{
  "is_meaningful": true or false,
  "extract_type": "PAIN_POINT" or "MARKET_SIZE" or "STARTUP_CASE",
  "topic": "핵심 주제 한 줄",
  "pain_area": "세무/물류/고용 등 (PAIN_POINT일 때만, 나머지는 null)",
  "summary": {{
    "insight": "핵심 인사이트 한 문장",
    "keywords": ["키워드1", "키워드2"],
    "sentiment": "positive or negative or neutral"
  }}
}}

창업자에게 전혀 유용하지 않은 단순 이벤트/사고 기사면 is_meaningful: false로만 반환.
"""
    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        return json.loads(response.content[0].text)
    except json.JSONDecodeError:
        return None


def _save_extract(db: Session, raw_source_id: int, extraction: dict) -> None:
    record = MarketExtract(
        raw_source_id=raw_source_id,
        extract_type=ExtractType(extraction["extract_type"]),
        topic=extraction["topic"],
        pain_area=extraction.get("pain_area"),
        extracted_data=extraction.get("summary"),
    )
    db.add(record)
