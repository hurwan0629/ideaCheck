# ============================================================
# models/user.py — 유저 관련 데이터 타입 정의
# ============================================================

from pydantic import BaseModel


class UserProfile(BaseModel):
    """
    GET /user/profile 응답 데이터 형태.
    Supabase profiles 테이블의 데이터를 담는다.
    """
    id: str            # 유저 고유 ID (Supabase Auth의 UUID)
    display_name: str | None  # 닉네임 (없을 수도 있음)
    plan: str          # 현재 구독 플랜: 'free' | 'lite' | 'pro'
    created_at: str    # 가입 일시


class UsageStats(BaseModel):
    """
    GET /user/usage 응답 데이터 형태.
    이번 달 사용량을 담아 무료 플랜의 한도 초과 여부를 확인할 때 쓴다.
    """
    month: str           # 조회 기준 월 (예: "2026-04")
    analyze_count: int   # 이번 달 분석 요청 횟수
    pdf_download_count: int  # 이번 달 PDF 다운로드 횟수
    limit: int           # 플랜별 월 한도 (free=2, lite=10, pro=999)
