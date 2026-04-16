import httpx
from openai import OpenAI
from app.config import settings

# import anthropic
# claude = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

gpt = OpenAI(api_key=settings.OPENAI_API_KEY)

# 브라우저처럼 보이는 HTTP 클라이언트
# User-Agent, Accept 계열 헤더를 실제 Chrome과 동일하게 설정해서
# User-Agent 체크 수준의 봇 차단은 통과할 수 있음
browser_client = httpx.Client(
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
    follow_redirects=True,
    timeout=15.0,
)
