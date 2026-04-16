import json

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session

from app.clients import browser_client, gpt
from app.models.collection.competitor_features import CompetitorFeature
from app.models.collection.competitors import Competitor

# 경쟁사 서비스 유형 카테고리 (type 컬럼 값 후보)
# AI가 자유 텍스트로 쓰면 매번 달라지므로 고정 목록을 프롬프트에 명시
COMPETITOR_TYPES = ["핀테크", "이커머스", "SaaS", "헬스케어", "에듀테크", "물류", "기타"]

_AI_SYSTEM_PROMPT = f"""
웹사이트 텍스트를 분석해서 아래 JSON 형식으로만 응답해. 다른 텍스트는 절대 포함하지 마.
{{
    "description": "서비스 한 줄 설명 (50자 이내)",
    "target_customer": "주요 타겟 고객층 (예: 20-30대 직장인, 중소기업 대표)",
    "type": "서비스 유형. 반드시 다음 중 하나로만 답해: {', '.join(COMPETITOR_TYPES)}",
    "features": [
        {{"name": "기능명", "description": "기능 설명 (30자 이내)"}}
    ]
}}
"""


def crawl_competitors(db: Session) -> None:
    """
    DB에 등록된 전 경쟁사 공식 사이트 크롤링 → COMPETITORS, COMPETITOR_FEATURES 갱신.
    분기 1회 quarterly_job에서 호출.

    흐름:
      1. httpx(정적)로 먼저 시도
      2. JS 렌더링이 필요한 사이트로 판단되면 Playwright로 재시도
      3. BeautifulSoup으로 파싱한 결과를 AI에게 넘겨 구조화된 데이터 추출
    """
    competitors = db.query(Competitor).all()

    for competitor in competitors:
        soup = _fetch_with_httpx(competitor.website)

        if _needs_js(soup):
            soup = _fetch_with_playwright(competitor.website)

        data = _extract_with_ai(soup)
        _update_competitor(db, competitor.competitor_id, data)


def _fetch_with_httpx(url: str) -> BeautifulSoup:
    response = browser_client.get(url)
    return BeautifulSoup(response.text, "html.parser")


def _fetch_with_playwright(url: str) -> BeautifulSoup:
    with sync_playwright() as p:
        # AutomationControlled 비활성화: headless 브라우저임을 감지하는 navigator.webdriver 플래그 숨김
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        # Playwright도 브라우저와 동일한 User-Agent 사용
        page.set_extra_http_headers({
            "User-Agent": browser_client.headers["User-Agent"],
            "Accept-Language": browser_client.headers["Accept-Language"],
        })
        page.goto(url)
        page.wait_for_load_state("networkidle")
        html = page.content()
        browser.close()
    return BeautifulSoup(html, "html.parser")


def _needs_js(soup: BeautifulSoup) -> bool:
    # SPA 루트 엘리먼트 (React/Vue/Angular 공통 패턴)
    if soup.select_one("#root, #app, #__next, [data-reactroot]"):
        return True

    # noscript에 경고 문구가 있으면 JS 없이는 동작 안 함
    noscript = soup.find("noscript")
    if noscript and len(noscript.get_text(strip=True)) > 20:
        return True

    # body 텍스트가 거의 없으면 JS가 콘텐츠를 채우는 구조
    body_text = soup.body.get_text(strip=True) if soup.body else ""
    if len(body_text) < 200:
        return True

    return False


def _extract_with_ai(soup: BeautifulSoup) -> dict:
    # HTML 태그 제거하고 텍스트만 추출 → 토큰 절약
    body_text = soup.body.get_text(separator="\n", strip=True) if soup.body else ""

    response = gpt.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _AI_SYSTEM_PROMPT},
            {"role": "user", "content": body_text[:8000]},
        ],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return {
        "description": result.get("description", ""),
        "target_customer": result.get("target_customer", ""),
        "type": result.get("type", "기타"),
        "features": result.get("features", []),
    }


def _update_competitor(db: Session, competitor_id: int, data: dict) -> None:
    # Competitor 기본 정보 갱신
    competitor = db.query(Competitor).filter(Competitor.competitor_id == competitor_id).one()
    competitor.description = data["description"]
    competitor.target_customer = data["target_customer"]
    competitor.type = data["type"]

    # 기존 features 전부 삭제 후 새로 insert
    # 분기 1회 전체 갱신이라 upsert 없이 delete → insert가 단순함
    db.query(CompetitorFeature).filter(CompetitorFeature.competitor_id == competitor_id).delete()
    for feature in data["features"]:
        db.add(CompetitorFeature(
            competitor_id=competitor_id,
            feature_name=feature["name"],
            feature_desc={"description": feature["description"]},
        ))

    db.commit()
