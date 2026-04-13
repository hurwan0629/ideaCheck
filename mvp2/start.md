  실행 방법

  백엔드:
  cd backend
  pip install -r requirements.txt
  cp .env.example .env   # ANTHROPIC_API_KEY 입력
  uvicorn app.main:app --reload

  프론트엔드:
  cd frontend
  npm install
  npm run dev