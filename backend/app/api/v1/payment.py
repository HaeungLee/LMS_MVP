"""
결제 시스템 API - 토스페이먼츠 연동

- 결제 시작 (checkout)
- 결제 성공 처리 (success)
- 결제 실패 처리 (fail)
- 구독 상태 조회
- 구독 취소
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import requests
import os

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import User

router = APIRouter()

# 토스페이먼츠 API 설정
TOSS_SECRET_KEY = os.getenv("TOSS_SECRET_KEY", "test_sk_...")
TOSS_CLIENT_KEY = os.getenv("TOSS_CLIENT_KEY", "test_ck_...")
TOSS_API_URL = "https://api.tosspayments.com/v1"


# ============= Request/Response Models =============

class CheckoutRequest(BaseModel):
    """결제 시작 요청"""
    plan: str = "monthly"  # monthly or annual
    
class CheckoutResponse(BaseModel):
    """결제 시작 응답"""
    checkout_url: str
    order_id: str
    amount: int
    customer_key: str

class PaymentSuccessRequest(BaseModel):
    """결제 성공 콜백"""
    payment_key: str
    order_id: str
    amount: int

class SubscriptionInfo(BaseModel):
    """구독 정보"""
    status: str  # trial, active, cancelled, expired
    plan: str  # monthly, annual
    trial_end_date: Optional[datetime]
    next_billing_date: Optional[datetime]
    amount: int
    is_trial: bool
    days_remaining: int


# ============= API Endpoints =============

@router.post("/checkout", response_model=CheckoutResponse)
async def start_checkout(
    request: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    결제 프로세스 시작
    
    - 7일 무료 체험 자동 시작
    - 토스페이먼츠 결제창 URL 반환
    """
    
    # 가격 계산
    amount = 9900 if request.plan == "monthly" else 95000
    
    # 주문 ID 생성 (유니크해야 함)
    order_id = f"ORDER_{user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Customer Key (토스페이먼츠 고객 식별자)
    customer_key = f"CUSTOMER_{user.id}"
    
    # TODO: DB에 주문 정보 저장
    # - order_id, user_id, amount, plan, status='pending'
    
    # 결제창 URL 생성 (프론트엔드에서 토스 위젯 사용)
    checkout_url = f"https://your-frontend.com/payment/checkout?orderId={order_id}&amount={amount}&customerKey={customer_key}"
    
    return CheckoutResponse(
        checkout_url=checkout_url,
        order_id=order_id,
        amount=amount,
        customer_key=customer_key
    )


@router.post("/success")
async def payment_success(
    request: PaymentSuccessRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    결제 성공 처리
    
    - 토스페이먼츠 결제 승인 API 호출
    - 7일 무료 체험 시작
    - 구독 상태 업데이트
    """
    
    # 토스페이먼츠 결제 승인 API 호출
    try:
        response = requests.post(
            f"{TOSS_API_URL}/payments/confirm",
            json={
                "paymentKey": request.payment_key,
                "orderId": request.order_id,
                "amount": request.amount
            },
            headers={
                "Authorization": f"Basic {TOSS_SECRET_KEY}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="결제 승인 실패")
        
        payment_data = response.json()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"결제 처리 오류: {str(e)}")
    
    # 7일 무료 체험 시작
    trial_end_date = datetime.now() + timedelta(days=7)
    next_billing_date = trial_end_date
    
    # TODO: DB에 구독 정보 저장
    # Subscription 테이블:
    # - user_id, status='trial', plan, trial_end_date, next_billing_date
    # - payment_key, order_id, amount
    
    return {
        "success": True,
        "message": "7일 무료 체험이 시작되었습니다!",
        "trial_end_date": trial_end_date,
        "next_billing_date": next_billing_date
    }


@router.post("/fail")
async def payment_fail(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """결제 실패 처리"""
    
    body = await request.json()
    error_code = body.get("code")
    error_message = body.get("message")
    
    # TODO: 실패 로그 저장
    
    return {
        "success": False,
        "error_code": error_code,
        "error_message": error_message
    }


@router.get("/subscription", response_model=SubscriptionInfo)
async def get_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    현재 구독 상태 조회
    """
    
    # TODO: DB에서 구독 정보 조회
    # 임시 데이터 (7일 무료 체험 중)
    trial_end = datetime.now() + timedelta(days=7)
    days_remaining = (trial_end - datetime.now()).days
    
    return SubscriptionInfo(
        status="trial",
        plan="monthly",
        trial_end_date=trial_end,
        next_billing_date=trial_end,
        amount=9900,
        is_trial=True,
        days_remaining=days_remaining
    )


@router.post("/cancel")
async def cancel_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    구독 취소
    
    - 즉시 취소하지 않고 다음 결제일까지 유지
    - 자동 갱신만 중지
    """
    
    # TODO: DB에서 구독 상태 업데이트
    # - status='cancelled'
    # - auto_renew=False
    
    return {
        "success": True,
        "message": "구독이 취소되었습니다. 결제한 기간까지는 계속 이용 가능합니다."
    }


@router.get("/client-key")
async def get_client_key():
    """
    프론트엔드에서 토스 위젯 초기화용 클라이언트 키
    """
    return {
        "client_key": TOSS_CLIENT_KEY
    }
