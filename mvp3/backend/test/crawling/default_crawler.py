from typing import Any
import httpx

def crawl_url(url: str, agent: dict[str, Any] | list[Any]):
  if url is None:
    print("url is None")
    return
  response = httpx.get(
    url,
    headers=agent,
    timeout=10.0,
    follow_redirects=True
  )
  print(f"status: {response.raise_for_status()}")
  return response.text