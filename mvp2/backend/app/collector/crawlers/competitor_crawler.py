import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def crawl_competitors() -> None:
    """
    DB에 등록된 전 경쟁사 공식 사이트 크롤링 → COMPETITORS, COMPETITOR_FEATURES 갱신.
    분기 1회 quarterly_job에서 호출.

    needs_js 기준으로 크롤링 방식 분기:
      False → httpx + BeautifulSoup (정적 HTML, 빠름)
      True  → Playwright sync API (JS 렌더링 필요한 동적 사이트)
    """
    # TODO: DB에서 SELECT * FROM COMPETITORS
    competitors = [
        {"competitor_id": 1, "name": "토스", "website": "https://toss.im", "needs_js": False},
        {"competitor_id": 2, "name": "카카오페이", "website": "https://kakaopay.com", "needs_js": True},
    ]

    for competitor in competitors:
        if competitor["needs_js"]:
            data = _crawl_with_playwright(competitor["website"])
        else:
            data = _crawl_with_httpx(competitor["website"])
        _update_competitor(competitor["competitor_id"], data)


def _crawl_with_httpx(url: str) -> dict:
    with httpx.Client(timeout=15.0) as client:
        response = client.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return {
            "description": _extract_text(soup, "meta[name='description']", attr="content"),
            "features": _extract_features(soup),
        }


def _crawl_with_playwright(url: str) -> dict:
    # sync_playwright: Playwright의 동기 API. async 없이 그대로 사용 가능.
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        html = page.content()
        browser.close()
    soup = BeautifulSoup(html, "html.parser")
    return {
        "description": _extract_text(soup, "meta[name='description']", attr="content"),
        "features": _extract_features(soup),
    }


def _extract_text(soup: BeautifulSoup, selector: str, attr: str | None = None) -> str:
    tag = soup.select_one(selector)
    if not tag:
        return ""
    return tag.get(attr, "") if attr else tag.get_text(strip=True)


def _extract_features(soup: BeautifulSoup) -> list[dict]:
    # TODO: 경쟁사별 실제 selector 적용
    features = []
    for item in soup.select(".feature-item"):
        features.append({
            "name": _extract_text(item, ".feature-title"),
            "description": _extract_text(item, ".feature-desc"),
        })
    return features


def _update_competitor(competitor_id: int, data: dict) -> None:
    # TODO: DB 세션 열어서 변경 감지 후 저장
    pass
