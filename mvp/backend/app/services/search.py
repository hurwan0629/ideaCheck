# ============================================================
# services/search.py — 웹 검색 서비스
#
# Tavily API를 사용해서 실시간 웹 검색을 수행한다.
# Tavily는 AI용으로 설계된 검색 API로, 검색 결과를 깔끔하게 정리해준다.
#
# 사용 위치: routers/analyze.py
# 환경변수: TAVILY_API_KEY
# ============================================================

from tavily import TavilyClient
import os

# 싱글턴 패턴: 클라이언트를 한 번만 만들어서 재사용
_client: TavilyClient | None = None


def get_client() -> TavilyClient:
    """Tavily 클라이언트를 반환한다. 없으면 새로 만든다."""
    global _client
    if _client is None:
        _client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", ""))
    return _client


async def search_competitors(topic: str) -> list[dict]:
    """
    주제와 관련된 경쟁사 및 시장 정보를 검색한다.

    예) topic = "AI 시장조사 SaaS"
    → "AI 시장조사 SaaS startup competitor market analysis 2024" 검색
    → 최대 5개 결과 반환

    반환 형태: [{"title": "...", "url": "...", "content": "..."}, ...]
    """
    client = get_client()
    query = f"{topic} startup competitor market analysis 2024"
    result = client.search(query=query, max_results=5, include_answer=True)
    return result.get("results", [])


async def search_market_trends(topic: str) -> list[dict]:
    """
    주제의 시장 규모 및 트렌드를 검색한다.

    예) topic = "AI 시장조사 SaaS"
    → "AI 시장조사 SaaS market size TAM growth trend" 검색
    → 최대 3개 결과 반환 (비용 절감)
    """
    client = get_client()
    query = f"{topic} market size TAM growth trend"
    result = client.search(query=query, max_results=3)
    return result.get("results", [])
