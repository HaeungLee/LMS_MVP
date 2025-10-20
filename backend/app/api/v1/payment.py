"""
결제 시스템 API - 토스페이먼츠 연동

Clean Architecture:
- Interface Layer (API Controllers)
- Application Layer (Services)
- Domain Layer (Entities)

Features:
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
import logging
import base64

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import User
from app.services.subscription_service import SubscriptionService, PaymentService

router = APIRouter()
logger = logging.getLogger(__name__)

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
    
    - 구독이 없으면 7일 무료 체험 자동 생성
    - 결제 정보 DB에 저장 (멱등성 보장)
    - 토스페이먼츠 결제창 정보 반환
    """
    
    try:
        subscription_service = SubscriptionService(db)
        payment_service = PaymentService(db)
        
        # 1. 구독 조회 또는 생성
        subscription = subscription_service.get_subscription_by_user(user.id)
        if not subscription:
            logger.info(f"새 체험 구독 생성: user_id={user.id}")
            subscription = subscription_service.create_trial_subscription(user.id, trial_days=7)
        
        # 2. 가격 계산
        amount = 9900 if request.plan == "monthly" else 95000
        
        # 3. 주문 ID 생성 (유니크해야 함)
        order_id = f"ORDER_{user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        
        # 4. Customer Key (토스페이먼츠 고객 식별자)
        customer_key = f"CUSTOMER_{user.id}"
        
        # 5. 결제 레코드 생성 (멱등성 보장)
        payment = payment_service.create_payment(
            subscription_id=subscription.id,
            order_id=order_id,
            amount=amount
        )
        
        logger.info(f"결제 생성 완료: payment_id={payment.id}, order_id={order_id}")
        
        # 6. 결제창 URL (프론트엔드에서 토스 위젯 사용)
        checkout_url = f"/payment/checkout?orderId={order_id}&amount={amount}&customerKey={customer_key}"
        
        return CheckoutResponse(
            checkout_url=checkout_url,
            order_id=order_id,
            amount=amount,
            customer_key=customer_key
        )
    
    except ValueError as e:
        logger.error(f"결제 시작 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"결제 시작 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="결제 시작 처리 중 오류가 발생했습니다.")


@router.post("/success")
async def payment_success(
    request: PaymentSuccessRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    결제 성공 처리
    
    - 토스페이먼츠 결제 승인 API 호출
    - 결제 정보 DB 업데이트
    - 구독 활성화 (trial → active)
    """
    
    try:
        subscription_service = SubscriptionService(db)
        payment_service = PaymentService(db)
        
        # 1. 결제 조회
        payment = payment_service.get_payment_by_order_id(request.order_id)
        if not payment:
            raise HTTPException(status_code=404, detail="결제 정보를 찾을 수 없습니다.")
        
        # 2. 이미 완료된 결제인지 확인 (멱등성)
        if payment.status == "success":
            logger.info(f"이미 완료된 결제: order_id={request.order_id}")
            subscription = subscription_service.get_subscription_by_user(user.id)
            return {
                "success": True,
                "message": "이미 처리된 결제입니다.",
                "subscription_status": subscription.status if subscription else "unknown"
            }
        
        # 3. 토스페이먼츠 결제 승인 API 호출
        try:
            # Base64 인코딩 (토스 API 인증 방식)
            auth_string = f"{TOSS_SECRET_KEY}:"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            
            response = requests.post(
                f"{TOSS_API_URL}/payments/confirm",
                json={
                    "paymentKey": request.payment_key,
                    "orderId": request.order_id,
                    "amount": request.amount
                },
                headers={
                    "Authorization": f"Basic {encoded_auth}",
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            
            if response.status_code != 200:
                error_data = response.json()
                logger.error(f"토스 결제 승인 실패: {error_data}")
                
                # 결제 실패 처리
                payment_service.fail_payment(
                    request.order_id,
                    error_data.get('message', '결제 승인 실패')
                )
                
                raise HTTPException(status_code=400, detail=error_data.get('message', '결제 승인 실패'))
            
            payment_data = response.json()
            payment_method = payment_data.get('method', 'CARD')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"토스 API 호출 오류: {str(e)}")
            payment_service.fail_payment(request.order_id, f"API 오류: {str(e)}")
            raise HTTPException(status_code=500, detail="결제 승인 처리 중 오류가 발생했습니다.")
        
        # 4. 결제 완료 처리
        payment = payment_service.complete_payment(
            request.order_id,
            request.payment_key,
            payment_method
        )
        
        # 5. 구독 활성화
        subscription = subscription_service.get_subscription_by_user(user.id)
        if subscription:
            # 플랜에 따라 기간 설정
            period_days = 30 if subscription.plan == "monthly" else 365
            subscription = subscription_service.activate_subscription(
                subscription.id,
                subscription.plan,
                period_days
            )
        
        logger.info(f"결제 완료: user_id={user.id}, order_id={request.order_id}")
        
        return {
            "success": True,
            "message": "결제가 완료되었습니다!",
            "subscription_status": subscription.status if subscription else "unknown",
            "period_end": subscription.current_period_end.isoformat() if subscription and subscription.current_period_end else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"결제 성공 처리 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="결제 처리 중 오류가 발생했습니다.")


@router.post("/fail")
async def payment_fail(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """결제 실패 처리"""
    
    try:
        body = await request.json()
        error_code = body.get("code", "UNKNOWN")
        error_message = body.get("message", "알 수 없는 오류")
        order_id = body.get("orderId")
        
        if order_id:
            payment_service = PaymentService(db)
            payment_service.fail_payment(order_id, f"{error_code}: {error_message}")
            logger.warning(f"결제 실패 기록: order_id={order_id}, reason={error_message}")
        
        return {
            "success": False,
            "error_code": error_code,
            "error_message": error_message
        }
    
    except Exception as e:
        logger.error(f"결제 실패 처리 오류: {str(e)}")
        return {
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "error_message": "결제 실패 처리 중 오류가 발생했습니다."
        }


@router.get("/subscription", response_model=SubscriptionInfo)
async def get_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    현재 구독 상태 조회
    """
    
    try:
        subscription_service = SubscriptionService(db)
        status_info = subscription_service.get_subscription_status(user.id)
        
        # SubscriptionInfo 형식으로 변환
        subscription = subscription_service.get_subscription_by_user(user.id)
        
        if not subscription:
            # 구독 없음 - 무료 사용자
            return SubscriptionInfo(
                status="free",
                plan="free",
                trial_end_date=None,
                next_billing_date=None,
                amount=0,
                is_trial=False,
                days_remaining=0
            )
        
        # 날짜 계산
        trial_end_date = subscription.trial_end_date
        next_billing_date = subscription.current_period_end
        
        # 금액
        amount = 9900 if subscription.plan == "monthly" else 95000
        
        # 남은 일수
        if subscription.status == "trial":
            days_remaining = status_info.get("trial_days_left", 0)
        elif subscription.status == "active":
            days_remaining = status_info.get("days_left", 0)
        else:
            days_remaining = 0
        
        return SubscriptionInfo(
            status=subscription.status,
            plan=subscription.plan,
            trial_end_date=trial_end_date,
            next_billing_date=next_billing_date,
            amount=amount,
            is_trial=(subscription.status == "trial"),
            days_remaining=days_remaining
        )
    
    except Exception as e:
        logger.error(f"구독 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="구독 정보 조회 중 오류가 발생했습니다.")


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
    
    try:
        subscription_service = SubscriptionService(db)
        
        # 구독 조회
        subscription = subscription_service.get_subscription_by_user(user.id)
        if not subscription:
            raise HTTPException(status_code=404, detail="활성 구독을 찾을 수 없습니다.")
        
        # 구독 취소 (기간 종료 시 취소)
        subscription = subscription_service.cancel_subscription(
            subscription.id,
            cancel_at_period_end=True
        )
        
        logger.info(f"구독 취소: user_id={user.id}, subscription_id={subscription.id}")
        
        return {
            "success": True,
            "message": "구독이 취소되었습니다. 결제한 기간까지는 계속 이용 가능합니다.",
            "period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None
        }
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"구독 취소 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="구독 취소 처리 중 오류가 발생했습니다.")


@router.get("/client-key")
async def get_client_key():
    """
    프론트엔드에서 토스 위젯 초기화용 클라이언트 키
    """
    return {
        "client_key": TOSS_CLIENT_KEY
    }
