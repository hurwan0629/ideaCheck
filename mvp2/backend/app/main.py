from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine
from .config import settings
from .models import user

app = FastAPI()

# Cors 허가 origin 목록
allowed_origins = [
  "http://localhost:3000",
  "http://127.0.0.1:3000",
  "http://localhost:5173",
  "http://127.0.0.1:5173",
  "https://hoppscotch.io"
]

# cors 설정
app.add_middleware(
  CORSMiddleware,
  allow_origins=allowed_origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)

@app.on_event("startup")
def on_startup():
  Base.metadata.create_all(engine)

@app.get("/")
def root():
  return {"message": "This is 'Find Your Market Service'"}

@app.get("/test")
def test():
  return {"message": f"${settings.DATABASE_URL}"}