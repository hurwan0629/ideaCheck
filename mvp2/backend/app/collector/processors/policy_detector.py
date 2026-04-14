# 뉴스에서 경쟁사의 정책 변경을 감지해서 COMPETITOR_POLICIES에 저장.
# 변경이 많은 경쟁사는 재분석 큐에 자동 적재.
import json
import hashlib
import anthropic

from app.collector.queue.reanalysis_queue import reanalysis_queue

claude = anthropic.AsyncAnthropic()

# 30일 안에 정책 변경이 이 횟수 이상이면 즉시 재분석 큐에 올림
REANALYSIS_THRESHOLD = 3


async def detect_policy_changes(raw_news: list[dict]) -> None:
    """
    수집된 뉴스 목록에서 경쟁사 정책 변경 감지.
    매일 daily_job에서 market_processor 다음에 호출.
    """
    # 실제로는 DB에서 읽어옴:
    # - COMPETITORS 목록 (어떤 경쟁사를 감시할지)
    # - POLICY_TYPES(is_active=true) 목록 (어떤 유형의 정책을 감지할지)
    competitors = [{"competitor_id": 1, "name": "토스"}]
    policy_types = [
        {"policy_type_id": 1, "name": "가격 정책"},
        {"policy_type_id": 2, "name": "현지화"},
    ]

    for article in raw_news:
        # Claude로 "이 뉴스가 어떤 경쟁사의 어떤 정책 변경인지" 판단
        detected = await _detect_policy_in_article(article, competitors, policy_types)

        if not detected:
            continue  # 정책 변경 없는 뉴스면 skip

        competitor_id = detected["competitor_id"]
        policy_type_id = detected["policy_type_id"]
        policy_data = detected["policy_data"]

        # 이전 정책과 실제로 다른지 해시 비교 (변경 없으면 저장 안 함)
        if await _is_changed(competitor_id, policy_type_id, policy_data):
            await _save_policy(competitor_id, policy_type_id, policy_data, article["published_at"])
            await _check_reanalysis_threshold(competitor_id)


async def _detect_policy_in_article(
    article: dict,
    competitors: list[dict],
    policy_types: list[dict],
) -> dict | None:
    """
    Claude에게 뉴스를 보내서 경쟁사 정책 변경 여부를 판단.
    해당 없으면 null 반환.
    """
    competitor_names = [c["name"] for c in competitors]
    policy_type_names = [p["name"] for p in policy_types]

    prompt = f"""
다음 뉴스 기사가 아래 경쟁사 중 하나의 정책 변경에 해당하는지 판단해서 JSON으로만 답해줘.

감시 대상 경쟁사: {competitor_names}
감시할 정책 유형: {policy_type_names}

뉴스 제목: {article["title"]}
뉴스 본문: {article["content"][:1500]}

해당하는 경우:
{{
  "competitor_name": "해당 경쟁사명",
  "policy_type_name": "해당 정책 유형명",
  "policy_data": {{
    "변경 내용을 유형에 맞게 key-value로 정리"
  }},
  "published_date": "YYYY-MM-DD"
}}

해당하지 않으면: null
"""

    response = await claude.messages.create(
        model="claude-haiku-4-5-20251001",  # 분류 작업은 빠르고 저렴한 Haiku 사용
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    if text == "null":
        return None

    try:
        result = json.loads(text)
        # 경쟁사명/유형명 → ID로 변환 (DB에서 매핑)
        # 여기서는 구조 파악용으로 생략
        return result
    except json.JSONDecodeError:
        return None


async def _is_changed(competitor_id: int, policy_type_id: int, new_policy_data: dict) -> bool:
    """
    직전에 저장된 같은 유형의 POLICY_DATA와 해시 비교.
    다르면 True (저장 필요), 같으면 False (변경 없음).
    """
    # 실제 구현:
    # prev_row = DB에서 WHERE competitor_id=X AND policy_type_id=Y ORDER BY created_at DESC LIMIT 1
    # prev_hash = hashlib.md5(json.dumps(prev_row.policy_data, sort_keys=True).encode()).hexdigest()
    new_hash = hashlib.md5(json.dumps(new_policy_data, sort_keys=True).encode()).hexdigest()

    # TODO: 직전 해시와 비교
    return True  # 구조 파악용 더미 (항상 변경된 것으로 간주)


async def _save_policy(
    competitor_id: int,
    policy_type_id: int,
    policy_data: dict,
    published_date: str,
) -> None:
    """
    COMPETITOR_POLICIES에 새 행 추가.
    UPDATE 없이 새 행 — 이력 보존 원칙.
    """
    # TODO: DB 세션 열어서 INSERT
    pass


async def _check_reanalysis_threshold(competitor_id: int) -> None:
    """
    최근 30일 내 이 경쟁사의 정책 변경 횟수 확인.
    REANALYSIS_THRESHOLD 이상이면 즉시 재분석 큐에 적재.
    """
    # 실제 구현:
    # count = DB에서 30일 내 해당 competitor_id 정책 변경 행 수 집계
    count = 1  # 구조 파악용 더미

    if count >= REANALYSIS_THRESHOLD:
        reanalysis_queue.add(competitor_id)
