import json
from pathlib import Path

from companylist_url import crawl_wiki_list_of_unicorn_startup_companies

LIST_URL = "https://en.wikipedia.org/wiki/Lists_of_companies"
# WIKIPEDIA
BASE_URL = "https://en.wikipedia.org"
ONLINE_MARKETPLACES_LIST_URL="https://en.wikipedia.org/wiki/List_of_online_marketplaces"
STREAMING_MEDIA_SERVICES_LIST_URL="https://en.wikipedia.org/wiki/List_of_streaming_media_services"
SEARCH_ENGINE_LIST_URL="https://en.wikipedia.org/wiki/List_of_search_engines"
MOST_VISITED_WEBSITES_LIST_URL="https://en.wikipedia.org/wiki/List_of_most-visited_websites"
SOCIAL_NETWORKING_SERVICES_LIST_URL="https://en.wikipedia.org/wiki/List_of_social_networking_services"
UNICORN_STARTUP_COMPANIES_LIST_URL="https://en.wikipedia.org/wiki/List_of_unicorn_startup_companies"

# GIT
AWESOME_SAAS_LIST="https://github.com/awesome-saas/awesome-saas"
AWESOME_STARTUPS_LIST="https://github.com/softvar/awesome-startups"

# ETC
ALTERNNATIVETO_NET="https://alternativeto.net/"

result = crawl_wiki_list_of_unicorn_startup_companies()

# html = fetch_html(URL)

# bs4 추출

# from bs4 import BeautifulSoup

# soup = BeautifulSoup(html, "html.parser")

# company_list = soup.select_one(".mw-content-ltr.mw-parser-output")

# html 저장
from pathlib import Path

output_path = Path(__file__).parent / "unicorn_startup.json"
with output_path.open("w", encoding="utf-8") as f:
  json.dump(result, f, ensure_ascii=False, indent=2)
