from typing import Any
import httpx
from bs4 import BeautifulSoup, Tag
from headers import WIKIPEDIA_HEADERS

SKIP_SECTION_TITLES = {
  "contents",
  "see also",
  "references",
  "external links",
  "further reading",
  "notes",
}

SKIP_PARENT_CLASSES = {
  "infobox",
  "toc",
  "reference",
  "reflist",
  "navbox",
  "metadata",
  "mw-editsection",
  "hatnote",
}


def _normalize_text(text: str) -> str:
  return " ".join(text.split())


def _is_heading(tag: Tag, names: set[str]) -> bool:
  return tag.name in names


def _should_skip_node(tag: Tag) -> bool:
  for parent in [tag, *tag.parents]:
    if not isinstance(parent, Tag):
      continue

    if parent.name in {"table", "figure", "footer", "nav"}:
      return True

    parent_classes = set(parent.get("class") or [])
    if parent_classes & SKIP_PARENT_CLASSES:
      return True

  return False

def crawl_wiki(url: str, agent: dict[str, Any]  | list[Any] = WIKIPEDIA_HEADERS) -> str | None:
  if url is None or len(url) < 20:
    print("url is None")
    return
  response = httpx.get(
    url,
    headers=agent,
    timeout=10.0,
    follow_redirects=True
  )
  # print(f"status: {response.raise_for_status()}")
  if response.status_code == 404:
    return None
  return response.text

def distract_text_from_company_html(text: str) -> dict[str, Any]:
  soup = BeautifulSoup(text, "html.parser")

  for tag in soup(["script", "style", "noscript", "svg"]):
    tag.decompose()

  main = soup.find("main") or soup.body or soup

  title = ""
  if soup.title is not None:
    title = _normalize_text(soup.title.get_text(" ", strip=True))

  page_heading = ""
  h1 = main.find("h1")
  if h1 is not None:
    page_heading = _normalize_text(h1.get_text(" ", strip=True))

  lead_paragraphs: list[str] = []
  sections: list[dict[str, str]] = []
  current_section: dict[str, Any] | None = None

  for node in main.find_all(["h2", "h3", "p", "ul", "ol"]):
    if _should_skip_node(node):
      continue

    if _is_heading(node, {"h2", "h3"}):
      raw_heading = node.get_text(" ", strip=True)
      section_title = _normalize_text(raw_heading.replace("[edit]", ""))

      if section_title.lower() in SKIP_SECTION_TITLES:
        current_section = None
        continue

      current_section = {
        "heading": section_title,
        "content_parts": [],
      }
      sections.append(current_section)
      continue

    text_content = _normalize_text(node.get_text(" ", strip=True))
    if not text_content:
      continue

    if current_section is None:
      if node.name == "p":
        lead_paragraphs.append(text_content)
      continue

    current_section["content_parts"].append(text_content)

  normalized_sections: list[dict[str, str]] = []
  for section in sections:
    content = "\n".join(section["content_parts"]).strip()
    if not content:
      continue

    normalized_sections.append({
      "heading": section["heading"],
      "content": content,
    })

  return {
    "title": title,
    "page_heading": page_heading,
    "lead_paragraphs": lead_paragraphs[:3],
    "sections": normalized_sections,
  }
