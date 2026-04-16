from openai import OpenAI
from app.config import settings

# import anthropic
# claude = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

gpt = OpenAI(api_key=settings.OPENAI_API_KEY)
