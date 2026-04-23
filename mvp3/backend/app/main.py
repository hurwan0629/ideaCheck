from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router import v1

app = FastAPI()

allowed_origins = [
  "http://localhost:3000", # Next
  "http://127.0.0.1:3000",
  "http://localhost:5173", # React (Vite)
  "http://127.0.0.1:5173", 
  "https://hoppscotch.io"  # 외부 사이트
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=allowed_origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)

app.include_router(v1)

@context