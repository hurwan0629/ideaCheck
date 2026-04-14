# 경쟁사 공식 사이트 크롤링.
# 두 가지 방식을 모두 사용:
#   1. httpx + BeautifulSoup: 서버에서 HTML을 바로 반환하는 정적 사이트 (빠름)
#   2. Playwright: JavaScript로 렌더링하는 동적 사이트 (느리지만 현대 웹사이트 대응 가능)
#
# Playwright란?
#   실제 Chrome/Firefox 브라우저를 코드로 조종하는 라이브러리.
#   "버튼 클릭", "스크롤", "로그인" 등 사람이 하는 동작을 자동화할 수 있음.
#   JS가 필요한 사이트는 httpx로 가져오면 빈 페이지가 오기 때문에 Playwright 사용.
#   공식문서: https://playwright.dev/python/docs/intro
import httpx
from bs4 import BeautifulSoup

# Playwright async API
# 설치: pip install playwright && playwright install chromium
from playwright.async_api import async_playwright


async def crawl_competitors() -> None:
    """
    DB에 등록된 전 경쟁사 공식 사이트를 크롤링해서
    COMPETITORS, COMPETITOR_FEATURES 테이블을 갱신.
    분기 1회 quarterly_job에서 호출.
    """
    # 실제로는 DB에서 SELECT * FROM COMPETITORS 로 목록 읽어옴
    competitors = [
        {"competitor_id": 1, "name": "토스", "website": "https://toss.im", "needs_js": False},
        {"competitor_id": 2, "name": "카카오페이", "website": "https://kakaopay.com", "needs_js": True},
    ]

    for competitor in competitors:
        if competitor["needs_js"]:
            # JS 렌더링이 필요한 사이트 → Playwright 사용
            data = await _crawl_with_playwright(competitor["website"])
        else:
            # 정적 HTML 사이트 → httpx + BeautifulSoup (더 빠름)
            data = await _crawl_with_httpx(competitor["website"])

        # 파싱된 데이터로 DB 갱신
        await _update_competitor(competitor["competitor_id"], data)


async def _crawl_with_httpx(url: str) -> dict:
    """
    httpx로 HTML 가져와서 BeautifulSoup으로 파싱.
    JS 없이 서버에서 바로 HTML이 오는 사이트에 사용.
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        return {
            # 실제 사이트에 맞게 selector 수정 필요
            "description": _extract_text(soup, "meta[name='description']", attr="content"),
            "features": _extract_features(soup),
        }


async def _crawl_with_playwright(url: str) -> dict:
    """
    Playwright로 실제 브라우저를 띄워서 JS 렌더링 후 HTML 파싱.

    흐름:
      1. async_playwright() 로 Playwright 엔진 시작
      2. chromium.launch() 로 Chrome 브라우저 실행 (headless=True = 창 없이 백그라운드 실행)
      3. page.goto(url) 로 해당 URL 방문
      4. page.wait_for_load_state("networkidle") 로 JS 렌더링 완료까지 대기
      5. page.content() 로 최종 HTML 가져옴
      6. BeautifulSoup으로 파싱
    """
    async with async_playwright() as p:
        # headless=True: 화면 없이 백그라운드에서 실행 (서버 환경)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url)
        # networkidle: 네트워크 요청이 0개가 될 때까지 대기 (JS 로딩 완료 신호)
        await page.wait_for_load_state("networkidle")

        html = await page.content()  # JS 실행 후 최종 HTML 반환
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    return {
        "description": _extract_text(soup, "meta[name='description']", attr="content"),
        "features": _extract_features(soup),
    }


def _extract_text(soup: BeautifulSoup, selector: str, attr: str | None = None) -> str:
    """CSS selector로 태그 찾아서 텍스트 또는 속성값 반환."""
    tag = soup.select_one(selector)
    if not tag:
        return ""
    return tag.get(attr, "") if attr else tag.get_text(strip=True)


def _extract_features(soup: BeautifulSoup) -> list[dict]:
    """
    기능 소개 섹션에서 기능 목록 추출.
    실제 사이트마다 HTML 구조가 다르므로 각 경쟁사별로 selector 조정 필요.
    """
    features = []
    # 예시 selector — 실제 사이트에 맞게 변경해야 함
    for item in soup.select(".feature-item"):
        features.append({
            "name": _extract_text(item, ".feature-title"),
            "description": _extract_text(item, ".feature-desc"),
        })
    return features


async def _update_competitor(competitor_id: int, data: dict) -> None:
    """
    크롤링 결과를 DB에 반영.
    - COMPETITORS: 변경된 필드만 UPDATE
    - COMPETITOR_FEATURES: 이전 행과 다를 경우 새 행 추가
    실제 구현 시 SQLAlchemy AsyncSession 사용.
    """
    # TODO: DB 세션 열어서 변경 감지 후 저장
    pass
