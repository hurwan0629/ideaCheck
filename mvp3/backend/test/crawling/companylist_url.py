import json

import httpx
from urllib.parse import urljoin
from bs4 import BeautifulSoup


WIKIPEDIA_HEADERS = {
  "User-Agent": "IdeaCheckBot/0.1 (contact: your-email@example.com)",
  "Accept": "text/html, application/xhtml+xml",
  "Accept-Language": "en-US,en;q=0.9",
}


def fetch_html(url: str) -> str:
  response = httpx.get(
    url,
    headers=WIKIPEDIA_HEADERS,
    timeout=10.0,
    follow_redirects=True,
  )
  response.raise_for_status()
  return response.text


def _extract_text(cell) -> str:
  return cell.get_text(" ", strip=True)


def crawl_wiki_list_of_unicorn_startup_companies() -> list[dict[str, str]]:
  url = "https://en.wikipedia.org/wiki/List_of_unicorn_startup_companies"

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

  html = fetch_html(url)
  soup = BeautifulSoup(html, "html.parser")

  tables = soup.select("table.wikitable.sortable.sticky-header")
  if len(tables) < 2:
    return []

  target_table = tables[1]
  rows = target_table.select("tbody > tr")

  result: list[dict[str, str]] = []

  for tr in rows[1:]:
    cells = tr.select("td")
    if len(cells) < 6:
      continue
    
    industry_list = [
      item.strip()
      for item in cells[3].get_text(strip=True).split(", ")
      if item.strip
    ]

    if not any(industry in ALLOWED_INDUSTRY for industry in industry_list):
      continue

    link_tag = cells[0].select_one("a[href]")

    href=""
    if link_tag is not None:
      href = link_tag.get("href")
      if href is not None:
        href = urljoin("https://en.wikipedia.org", str(href))


    item = {
      "name": _extract_text(cells[0]),
      "url": href,
      "valuation": _extract_text(cells[1]),
      "valuation_date": _extract_text(cells[2]),
      "industry":industry_list,
      "country": _extract_text(cells[4]),
      "founders": _extract_text(cells[5]),
    }
    result.append(item)

  print(len(result))
  return result


if __name__ == "__main__":
  data = crawl_wiki_list_of_unicorn_startup_companies()
  print(json.dumps(data[:3], ensure_ascii=False, indent=2))
