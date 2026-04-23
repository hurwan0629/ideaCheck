from fastapi import APIRouter

v1 = APIRouter(
  prefix="/v1",
  tags=["test", "v1", "mvp3"]
)

@v1.get("/health")
def get_health():
  return {"message": "server alive!"}