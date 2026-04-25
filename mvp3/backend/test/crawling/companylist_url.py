import json

import httpx
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from default_crawler import crawl_wiki


# def fetch_html(url: str) -> str:
#   response = httpx.get(
#     url,
#     headers=WIKIPEDIA_HEADERS,
#     timeout=10.0,
#     follow_redirects=True,
#   )
#   response.raise_for_status()
#   return response.text


def _extract_text(cell) -> str:
  return cell.get_text(" ", strip=True)

# 위키에서 유니콘 기업의 목록 (메타정보 + url 목록 뽑기)
def crawl_wiki_list_of_unicorn_startup_companies(
    url: str = "https://en.wikipedia.org/wiki/List_of_unicorn_startup_companies"
      ) -> list[dict[str, str]] | None:
  
  # 아래에 있는 산업 종류가 하나라도 있어야 크롤링해줌
  ALLOWED_INDUSTRY = [
    "Internet",
    "Software",
    "Artificial intelligence",
    "Ai ",
    "Technology",
    "Tech",
    "Collaborative Software",
    "Financial services",
    "Educational Technology",
    "Financial Technology",
    "Financial technology",
    "Defense Technology",
    "Health Technology",
    "E-commerce",
    "Graphic Design",
    "Humanoid robotics",
    "Graphic design",
    "Semiconductors",
    "Robotics",
    "Cryptocurrency"
  ]

  # 위키피디아 html 긁어오기
  html = crawl_wiki(url)
  if html is None:
    print(f"empty url: {url}")
    return None
  # soup 형태로 바꾸기
  soup = BeautifulSoup(html, "html.parser")

  # 리스트 테이블 뽑아오기 (div)
  tables = soup.select("table.wikitable.sortable.sticky-header")
  # 첫번째 테이블은 국가별 테이블이기 때문에 2번째꺼 (index=1) 가져와야함
  if len(tables) < 2:
    return []

  # 기업 목록 뽑기
  target_table = tables[1]  
  # tbody에서 rows(list[soup]) 뽑기
  rows = target_table.select("tbody > tr")

  # 데이터 공간 준비
  result: list[dict[str, str]] = []

  # 첫번째는 컬럼명이기 때문에 패스
  for tr in rows[1:]:
    cells = tr.select("td")
    # cells 순서가 [기업명 | 시총 | 시총 날짜 | 산업 | 나라 | 창설자] 이기 때문에 혹시몰라 검증
    if len(cells) < 6:
      continue
    
    # 시총은 2개 이상일 경우 ", " 로 나누어져 있기 때문에 한번 리스트로 나눠주기
    industry_list = [
      item.strip()
      for item in cells[3].get_text(strip=True).split(", ")
    ]

    # 산업 목록에 ALLOWED_INDUSTRY에 포함된다가 모두 False일 경우 -> not False -> continue
    if not any(industry in ALLOWED_INDUSTRY for industry in industry_list):
      continue
    
    # 이름에 걸려있는 a태그(href가 있는) 뽑기
    link_tag = cells[0].select_one("a[href]")

    href=""
    # href 걸려 있을 때 뽑기 
    if link_tag is not None:
      href = link_tag.get("href")
      if href is not None:
        # 절대경로로 만들기
        href = urljoin("https://en.wikipedia.org", str(href))

    # 80-90 또는 3+ 같은 것들 정규화
    valuation: str = _extract_text(cells[1]).replace("+","")
    # print(valuation.split("–"))
    num_valuation = [float(each) for each in valuation.split("–")]
    # 10억 달러 기준이기 때문에 곱하기
    num = int(sum(num_valuation)/len(num_valuation) * 1_000_000_000)

    item = {
      "name": _extract_text(cells[0]),
      "url": href,
      "valuation (dollar)": num,
      "valuation_date": _extract_text(cells[2]),
      "industry":industry_list,
      "country": _extract_text(cells[4]),
      "founders": _extract_text(cells[5]),
    }
    result.append(item)

  # print(len(result))
  return result


if __name__ == "__main__":
  data = crawl_wiki_list_of_unicorn_startup_companies()
  if data is not None:
    print(json.dumps(data[:3], ensure_ascii=False, indent=2))
