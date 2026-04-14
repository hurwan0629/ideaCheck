# httpx: Python의 requests와 비슷하지만 async(비동기)를 지원하는 HTTP 라이브러리
# async가 중요한 이유: 뉴스 100개 URL을 순서대로 요청하면 느림.
#                      async면 동시에 여러 요청을 보내고 응답 오는 순서대로 처리 → 빠름
# 공식문서: https://www.python-httpx.org/
import httpx

# BeautifulSoup4: HTML 문자열에서 원하는 태그를 쉽게 꺼내는 라이브러리
# 예) <h1 class="title">기사 제목</h1> → soup.find("h1", class_="title").text
# 공식문서: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup

import hashlib  # URL을 해시로 변환해서 중복 체크에 사용
from datetime import datetime


# 검색할 경쟁사명 + 키워드 예시 (실제로는 DB에서 COMPETITORS 목록을 읽어옴)
COMPETITOR_KEYWORDS = [
    "토스 정책",
    "카카오페이 요금",
    "뱅크샐러드 업데이트",
]

# 이미 수집한 URL 해시 목록 (중복 방지용. 실제로는 DB에서 조회)
_collected_url_hashes: set[str] = set()


async def crawl_news() -> list[dict]:
    """
    경쟁사 관련 뉴스를 검색해서 원본 텍스트 리스트로 반환.
    저장은 하지 않음 — market_processor.py에서 담당.

    반환 형태:
    [
        {
            "title": "토스, 송금 수수료 무료화 선언",
            "url": "https://...",
            "content": "본문 전체...",
            "source_type": "NEWS",
            "published_at": "2024-03-01",
        },
        ...
    ]
    """
    results = []

    # httpx.AsyncClient: async HTTP 클라이언트. "async with"로 연결 열고 끝나면 자동으로 닫음
    async with httpx.AsyncClient(timeout=10.0) as client:
        for keyword in COMPETITOR_KEYWORDS:
            articles = await _search_news(client, keyword)
            results.extend(articles)

    return results


async def _search_news(client: httpx.AsyncClient, keyword: str) -> list[dict]:
    """
    키워드로 뉴스 검색 → 각 기사 URL 방문 → 본문 파싱.

    실제 구현 시 네이버 뉴스 검색 API 또는 Google News RSS를 사용.
    네이버 검색 API: https://developers.naver.com/docs/serviceapi/search/news/news.md
    """
    articles = []

    # 예시: 네이버 뉴스 검색 API 호출
    # 실제로는 CLIENT_ID, CLIENT_SECRET을 환경변수에서 읽어야 함
    # response = await client.get(
    #     "https://openapi.naver.com/v1/search/news.json",
    #     params={"query": keyword, "display": 10, "sort": "date"},
    #     headers={
    #         "X-Naver-Client-Id": "YOUR_CLIENT_ID",
    #         "X-Naver-Client-Secret": "YOUR_SECRET",
    #     },
    # )
    # items = response.json()["items"]  # 뉴스 목록

    # 아래는 구조 파악용 더미 데이터
    items = [
        {"title": f"{keyword} 관련 기사", "link": f"https://example.com/{keyword}", "pubDate": "2024-03-01"},
    ]

    for item in items:
        url = item["link"]
        url_hash = hashlib.md5(url.encode()).hexdigest()  # URL → 고정 길이 해시 문자열

        # 이미 수집한 URL이면 건너뜀 (중복 방지)
        if url_hash in _collected_url_hashes:
            continue

        # 기사 본문 페이지 직접 방문해서 HTML 파싱
        content = await _fetch_article_content(client, url)

        _collected_url_hashes.add(url_hash)
        articles.append({
            "title": item["title"],
            "url": url,
            "content": content,
            "source_type": "NEWS",
            "published_at": item["pubDate"],
        })

    return articles


async def _fetch_article_content(client: httpx.AsyncClient, url: str) -> str:
    """
    기사 URL 방문 → BeautifulSoup으로 본문 텍스트 추출.

    주의: 사이트마다 본문 태그가 다름. 실제 구현 시 각 언론사별로 selector 조정 필요.
    Playwright가 필요한 경우: JS로 늦게 렌더링되는 사이트 (SPA 등)
    → 이 크롤러는 JS 없이 바로 HTML이 오는 사이트만 담당
    """
    try:
        response = await client.get(url)
        response.raise_for_status()  # 4xx/5xx 에러면 예외 발생

        # BeautifulSoup으로 HTML 파싱
        # "html.parser": Python 내장 파서. lxml 설치하면 더 빠름
        soup = BeautifulSoup(response.text, "html.parser")

        # 기사 본문 추출 (실제 사이트에 맞게 selector 수정 필요)
        article_body = soup.find("article") or soup.find("div", class_="article-body")
        return article_body.get_text(strip=True) if article_body else ""

    except Exception:
        return ""  # 크롤링 실패 시 빈 문자열 반환 (전체 파이프라인 멈추지 않게)
