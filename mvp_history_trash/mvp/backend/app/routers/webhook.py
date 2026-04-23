# ============================================================
# routers/webhook.py — Stripe 결제 이벤트 수신
#
# URL: POST /webhook/stripe
#
# Webhook이란?
#   Stripe가 결제 이벤트(구독 시작, 취소 등)를 우리 서버로
#   자동으로 HTTP 요청을 보내는 방식이다.
#   우리 서버가 먼저 요청하는 게 아니라 Stripe가 먼저 보낸다.
#
# 처리하는 이벤트:
#   customer.subscription.updated → 구독 정보 변경 시 DB 업데이트
#   customer.subscription.deleted → 구독 취소 시 상태를 'canceled'로 변경
#
# 보안:
#   Stripe는 요청에 서명(signature)을 포함한다.
#   STRIPE_WEBHOOK_SECRET으로 서명을 검증해서 가짜 요청을 막는다.
# ============================================================

from fastapi import APIRouter, Request, HTTPException
import stripe
import os

from app.db.supabase import get_client

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(request: Request):
    """
    Stripe에서 보내는 구독 이벤트를 수신하고 DB를 업데이트한다.

    처리 순서:
    1. 요청 본문(payload)과 서명을 읽는다
    2. 서명을 검증해서 Stripe가 보낸 게 맞는지 확인한다
    3. 이벤트 종류에 따라 subscriptions 테이블을 업데이트한다
    """
    payload = await request.body()  # 요청 본문 (바이트)
    sig = request.headers.get("stripe-signature", "")  # Stripe 서명 헤더

    # 서명 검증 — 실패하면 400 에러 반환 (가짜 요청 차단)
    try:
        event = stripe.Webhook.construct_event(
            payload, sig, os.getenv("STRIPE_WEBHOOK_SECRET", "")
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    db = get_client()

    # ── 구독 정보 변경 이벤트 ──────────────────────────────
    # 구독 생성, 플랜 변경, 결제 실패 등 다양한 상황에서 발생한다.
    if event["type"] == "customer.subscription.updated":
        sub = event["data"]["object"]
        # upsert: 있으면 update, 없으면 insert
        db.table("subscriptions").upsert({
            "stripe_sub_id": sub["id"],
            "stripe_customer_id": sub["customer"],
            "plan": sub["metadata"].get("plan", "lite"),  # Stripe 메타데이터에서 플랜 읽기
            "status": sub["status"],                       # 'active', 'past_due' 등
            "current_period_end": sub["current_period_end"],  # 다음 결제일
        }).execute()

    # ── 구독 취소 이벤트 ──────────────────────────────────
    elif event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        db.table("subscriptions").update({"status": "canceled"}).eq(
            "stripe_sub_id", sub["id"]
        ).execute()

    return {"received": True}
