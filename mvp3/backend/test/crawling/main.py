import json
from pathlib import Path

from companylist_url import crawl_wiki_list_of_unicorn_startup_companies
from default_crawler import crawl_wiki, distract_text_from_company_html
from headers import WIKIPEDIA_HEADERS
from analyzier import analyze_company

LIST_URL = "https://en.wikipedia.org/wiki/Lists_of_companies"
# WIKIPEDIA
BASE_URL = "https://en.wikipedia.org"
ONLINE_MARKETPLACES_LIST_URL = "https://en.wikipedia.org/wiki/List_of_online_marketplaces"
STREAMING_MEDIA_SERVICES_LIST_URL = "https://en.wikipedia.org/wiki/List_of_streaming_media_services"
SEARCH_ENGINE_LIST_URL = "https://en.wikipedia.org/wiki/List_of_search_engines"
MOST_VISITED_WEBSITES_LIST_URL = "https://en.wikipedia.org/wiki/List_of_most-visited_websites"
SOCIAL_NETWORKING_SERVICES_LIST_URL = "https://en.wikipedia.org/wiki/List_of_social_networking_services"
UNICORN_STARTUP_COMPANIES_LIST_URL = "https://en.wikipedia.org/wiki/List_of_unicorn_startup_companies"

# GIT
AWESOME_SAAS_LIST = "https://github.com/awesome-saas/awesome-saas"
AWESOME_STARTUPS_LIST = "https://github.com/softvar/awesome-startups"

# ETC
ALTERNNATIVETO_NET = "https://alternativeto.net/"


# html = fetch_html(URL)

# from bs4 import BeautifulSoup

# soup = BeautifulSoup(html, "html.parser")

# company_list = soup.select_one(".mw-content-ltr.mw-parser-output")

if __name__ == "__main__":
  result = None

  # 위키피디아에서 unicorn_startup_cmpanies 중에 it 기업 정보 가져오기 -> /data/unicorn_startup.json으로 제작
  # crawl_wiki_list_of_unicorn_startup_companies()

  # output_path = Path(__file__).parent / "unicorn_startup.json"
  # with output_path.open("w", encoding="utf-8") as f:
  #   json.dump(result, f, ensure_ascii=False, indent=2)

  # 
  company_list_path = Path(__file__).resolve().parent / "data" / "unicorn_startup.json"

  company_list = None

  # 만들어진 
  with company_list_path.open("r", encoding="utf-8") as f:
    company_list = json.load(f)
  # print(company_list)

  flag: bool = False
  for company in company_list:
    print()
    company_name = company.get("name", "unknown")
    print(company_name + " 작업 시작")
    if company_name == "Faire":
      flag=True
    if not flag:
      print(company_name + " 패스 (이미 존재)")
      continue
    # print(company.keys())
    html = crawl_wiki(company.get("url"))
    if html is None:
      print(company_name + " url 존재하지 않음")
      print()
      continue
    info = distract_text_from_company_html(html)
    with (Path(__file__).resolve().parent / "companies" / "html" / "openai.html").open("w", encoding="utf-8") as f:
      f.write(html)

    ai_company_analyze = analyze_company(company.get("name", "unknown"), info)
    with (Path(__file__).resolve().parent / "companies" / "analyze" / f"{company_name}.json").open("w", encoding="utf-8") as f:
      f.write(ai_company_analyze)
    # print(ai_company_analyze)
    print(company.get("name") + " 작업 끝")
    print()
    

  # company_analyses_list = Path(__file__).resolve().parent / "data" / "company_analyses_list.json"
  # print(company_list)


  # with company_analyses_list.open("w", encoding="utf-8") as f:
  #   for company in company_list[:1]:
  #     text = crawl_url(company.get("url"), WIKIPEDIA_HEADERS)
  #     f.write(text)

