from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db import Base, engine
from .config import settings

from app.models.user.user import User
from app.models.user.auth_accounts import AuthAccount
from app.models.user.user_ideas import UserIdea
from app.models.user.user_subscriptions import UserSubscription
from app.models.user.idea_analyses import IdeaAnalysis
from app.models.user.idea_notes import IdeaNote
from app.models.service.plans import Plan
from app.models.collection.competitors import Competitor
from app.models.collection.competitor_features import CompetitorFeature
from app.models.collection.competitor_policies import CompetitorPolicy
from app.models.collection.competitor_analyses import CompetitorAnalysis
from app.models.collection.market_raw_sources import MarketRawSource
from app.models.collection.market_extracts import MarketExtract
from app.models.collection.trends import Trend
from app.models.collection.idea_topic_stats import IdeaTopicStats
from app.models.collection.feature_categories import FeatureCategory
from app.models.collection.policy_types import PolicyType

@asynccontextmanager
async def lifespan(app: FastAPI):
  Base.metadata.create_all(engine)
  try:
    yield
  finally:
    pass

app = FastAPI(lifespan=lifespan)

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

@app.get("/")
def root():
  return {"message": "This is 'Find Your Market Service'"}

@app.get("/test")
def test():
  return {"message": f"${settings.DATABASE_URL}"}