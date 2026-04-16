import hashlib
import httpx
from bs4 import BeautifulSoup

# DB에서 읽어올 감시 키워드 (임시 하드코딩)
COMPETITOR_KEYWORDS = [
    "토스 정책",
    "카카오페이 요금",
    "뱅크샐러드 업데이트",
]

# 중복 수집 방지용 URL 해시 세트 (서버 재시작 시 초기화됨. 추후 DB 조회로 대체)
_collected_url_hashes: set[str] = set()


def crawl_news() -> list[dict]:
    """
    경쟁사 관련 뉴스 수집. 저장은 하지 않음 — market_processor에서 담당.

    반환 형태:
    [{ "title", "url", "content", "source_type", "published_at" }]
    """
    results = []
    with httpx.Client(timeout=10.0) as client:
        for keyword in COMPETITOR_KEYWORDS:
            results.extend(_search_news(client, keyword))
    return results


def _search_news(client: httpx.Client, keyword: str) -> list[dict]:
    articles = []

    # TODO: 네이버 뉴스 검색 API 실제 호출
    # response = client.get(
    #     "https://openapi.naver.com/v1/search/news.json",
    #     params={"query": keyword, "display": 10, "sort": "date"},
    #     headers={"X-Naver-Client-Id": "...", "X-Naver-Client-Secret": "..."},
    # )
    # items = response.json()["items"]
    items = [
        {"title": f"{keyword} 관련 기사", "link": f"https://example.com/{keyword}", "pubDate": "2024-03-01"},
    ]

    for item in items:
        url = item["link"]
        url_hash = hashlib.md5(url.encode()).hexdigest()
        if url_hash in _collected_url_hashes:
            continue
        content = _fetch_article_content(client, url)
        _collected_url_hashes.add(url_hash)
        articles.append({
            "title": item["title"],
            "url": url,
            "content": content,
            "source_type": "NEWS",
            "published_at": item["pubDate"],
        })

    return articles


def _fetch_article_content(client: httpx.Client, url: str) -> str:
    try:
        response = client.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.find("article") or soup.find("div", class_="article-body")
        return body.get_text(strip=True) if body else ""
    except Exception:
        return ""
