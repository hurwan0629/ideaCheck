# ============================================================
# routers/trends.py — 시장 트렌드 조회
#
# URL: GET /trends
#
# 역할:
#   아이디어가 없는 유저를 위해 요즘 뜨는 시장 카테고리를
#   미리 검색해서 보여준다.
#   로그인 없이 접근 가능한 무료 기능이다.
# ============================================================

from fastapi import APIRouter
from app.services.search import search_market_trends

router = APIRouter()

# 미리 정해진 트렌드 카테고리 목록
# 실제 서비스에서는 DB나 설정 파일로 관리할 수 있다.
TREND_TOPICS = [
    "AI SaaS", "no-code tools", "creator economy",
    "health tech", "fintech", "edtech",
]


@router.get("/trends")
async def get_trends():
    """
    트렌드 카테고리별 시장 정보를 반환한다.

    비용 절감을 위해 6개 카테고리 중 3개만 조회한다.
    각 카테고리에서 최대 2개 결과만 포함한다.

    응답 형태:
    {
      "trends": [
        {"topic": "AI SaaS", "data": [{...}, {...}]},
        ...
      ]
    }
    """
    results = []
    for topic in TREND_TOPICS[:3]:  # 처음 3개만 (API 호출 비용 절감)
        items = await search_market_trends(topic)
        results.append({"topic": topic, "data": items[:2]})  # 결과는 2개만
    return {"trends": results}
