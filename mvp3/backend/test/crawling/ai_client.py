from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

CHATGPT_API_KEY = os.getenv("OPENAI_API_KEY", "")

client = OpenAI()