# ============================================================
# db/supabase.py — Supabase 데이터베이스 클라이언트
#
# 역할:
#   Supabase에 접속하는 클라이언트 객체를 만들고 반환한다.
#
# 싱글턴 패턴 사용:
#   DB 연결은 비용이 크기 때문에 요청마다 새로 만들지 않는다.
#   처음 한 번만 만들고, 이후에는 같은 객체를 재사용한다.
#   _client 변수가 None이면 처음이라는 뜻 → 새로 생성
#   _client 변수가 있으면 기존 것을 그대로 반환
# ============================================================

from supabase import create_client, Client
import os

# 처음에는 None, 첫 호출 시에만 실제 클라이언트로 교체됨
_client: Client | None = None


def get_client() -> Client:
    """
    Supabase 클라이언트를 반환한다.
    서비스 전체에서 이 함수를 통해 DB에 접근한다.

    환경변수 필요:
      SUPABASE_URL        → Supabase 프로젝트 URL
      SUPABASE_SERVICE_KEY → 서버용 키 (권한이 강력하므로 절대 프론트에 노출 금지)
    """
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_KEY", "")
        _client = create_client(url, key)
    return _client
