# 수집된 뉴스 원본을 DB에 저장하고, AI로 유의미한 내용만 추출해서 MARKET_EXTRACTS 생성.
#
# Anthropic Claude API란?
#   Claude에게 텍스트를 보내고 답변을 받는 API.
#   "이 뉴스가 어떤 카테고리인지 분류해줘" 같은 작업을 코드로 자동화할 수 있음.
#   공식문서: https://docs.anthropic.com/en/api/getting-started
import anthropic  # pip install anthropic
import json

# anthropic 클라이언트 초기화 (API 키는 환경변수 ANTHROPIC_API_KEY에서 자동으로 읽음)
claude = anthropic.AsyncAnthropic()


async def process_market_news(raw_news: list[dict]) -> None:
    """
    news_crawler에서 받은 뉴스 목록을 처리:
    1. MARKET_RAW_SOURCES 테이블에 원본 저장
    2. Claude API로 내용 분류 + 유의미 여부 판단
    3. 유의미하면 MARKET_EXTRACTS 저장

    raw_news 형태:
    [{ "title": "...", "url": "...", "content": "...", "source_type": "NEWS", "published_at": "..." }]
    """
    for article in raw_news:
        # 1단계: 원본을 MARKET_RAW_SOURCES에 저장 (나중에 재처리 가능하도록 원본 보존)
        raw_source_id = await _save_raw_source(article)

        # 2단계: Claude로 분류 및 추출
        extraction = await _extract_with_ai(article["title"], article["content"])

        # 3단계: AI가 유의미하다고 판단한 경우만 MARKET_EXTRACTS에 저장
        if extraction and extraction.get("is_meaningful"):
            await _save_extract(raw_source_id, extraction)


async def _save_raw_source(article: dict) -> int:
    """
    뉴스 원본을 MARKET_RAW_SOURCES 테이블에 저장.
    중복 URL은 저장하지 않음 (URL 해시로 체크).
    반환값: 저장된 RAW_SOURCE_ID (다음 단계에서 FK로 사용)
    """
    # TODO: DB 세션 열어서 INSERT, raw_source_id 반환
    return 0  # 구조 파악용 더미


async def _extract_with_ai(title: str, content: str) -> dict | None:
    """
    Claude API로 뉴스 내용을 분석해서 구조화된 정보 추출.

    Claude API 사용 방법:
      - messages.create() 로 대화 형식으로 요청
      - model: 사용할 Claude 모델명
      - max_tokens: 응답 최대 토큰 수 (길이 제한)
      - messages: [{"role": "user", "content": "질문"}] 형태

    JSON으로 응답받으려면 프롬프트에 "JSON으로 답해줘" 명시 + 예시 형태 제공이 핵심.
    """
    prompt = f"""
다음 뉴스 기사를 분석해서 창업자에게 유용한 정보인지 판단하고, JSON으로만 답해줘.

제목: {title}
본문: {content[:2000]}  # 토큰 절약을 위해 앞 2000자만 전달

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

    # Claude API 호출
    # 공식문서: https://docs.anthropic.com/en/api/messages
    response = await claude.messages.create(
        model="claude-sonnet-4-6",  # 모델 선택 — 빠르고 저렴한 모델로 분류 작업 처리
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    # response.content[0].text: Claude의 응답 텍스트
    try:
        return json.loads(response.content[0].text)
    except json.JSONDecodeError:
        return None  # JSON 파싱 실패 시 skip


async def _save_extract(raw_source_id: int, extraction: dict) -> None:
    """
    AI 추출 결과를 MARKET_EXTRACTS 테이블에 저장.
    실제 구현 시 SQLAlchemy AsyncSession 사용.
    """
    # TODO: DB 세션 열어서 INSERT
    pass
