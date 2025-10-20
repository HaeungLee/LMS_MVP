"""
구독 서비스 레이어 (Application Layer)

Clean Architecture 원칙:
- Domain 레이어(orm.py)와 Interface 레이어(api) 사이의 비즈니스 로직
- 트랜잭션 관리
- 데이터 변환 및 검증
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.orm import Subscription, Payment, User


class SubscriptionService:
    """구독 관리 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_trial_subscription(self, user_id: int, trial_days: int = 7) -> Subscription:
        """
        체험 구독 생성
        
        Args:
            user_id: 사용자 ID
            trial_days: 체험 기간 (기본 7일)
            
        Returns:
            생성된 Subscription 객체
            
        Raises:
            ValueError: 이미 구독이 존재하는 경우
        """
        # 기존 구독 확인
        existing = self.db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
        
        if existing:
            raise ValueError(f"User {user_id} already has a subscription")
        
        # 체험 구독 생성
        now = datetime.utcnow()
        trial_end = now + timedelta(days=trial_days)
        
        subscription = Subscription(
            user_id=user_id,
            status="trial",
            plan="monthly",
            trial_start_date=now,
            trial_end_date=trial_end,
            created_at=now,
            updated_at=now
        )
        
        try:
            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)
            return subscription
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Failed to create subscription for user {user_id}")
    
    def activate_subscription(
        self,
        subscription_id: int,
        plan: str,
        period_days: int
    ) -> Subscription:
        """
        구독 활성화 (결제 완료 후)
        
        Args:
            subscription_id: 구독 ID
            plan: 플랜 (monthly, annual)
            period_days: 구독 기간 (30 or 365)
            
        Returns:
            업데이트된 Subscription 객체
            
        Raises:
            ValueError: 구독을 찾을 수 없거나 이미 활성화된 경우
        """
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        if subscription.status == "active":
            raise ValueError(f"Subscription {subscription_id} is already active")
        
        # 구독 활성화
        now = datetime.utcnow()
        period_end = now + timedelta(days=period_days)
        
        subscription.status = "active"
        subscription.plan = plan
        subscription.current_period_start = now
        subscription.current_period_end = period_end
        subscription.updated_at = now
        
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
    
    def cancel_subscription(
        self,
        subscription_id: int,
        cancel_at_period_end: bool = True
    ) -> Subscription:
        """
        구독 취소
        
        Args:
            subscription_id: 구독 ID
            cancel_at_period_end: True면 기간 종료 시 취소, False면 즉시 취소
            
        Returns:
            업데이트된 Subscription 객체
            
        Raises:
            ValueError: 구독을 찾을 수 없거나 이미 취소된 경우
        """
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        if subscription.status in ["cancelled", "expired"]:
            raise ValueError(f"Subscription {subscription_id} is already cancelled/expired")
        
        # 취소 처리
        now = datetime.utcnow()
        subscription.cancel_at_period_end = cancel_at_period_end
        subscription.cancelled_at = now
        
        if not cancel_at_period_end:
            # 즉시 취소
            subscription.status = "cancelled"
        
        subscription.updated_at = now
        
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
    
    def get_subscription_by_user(self, user_id: int) -> Optional[Subscription]:
        """
        사용자의 구독 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Subscription 객체 또는 None
        """
        return self.db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
    
    def get_subscription_status(self, user_id: int) -> Dict[str, Any]:
        """
        사용자의 구독 상태 조회 (프론트엔드용)
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            구독 상태 정보 딕셔너리
        """
        subscription = self.get_subscription_by_user(user_id)
        
        if not subscription:
            return {
                "status": "free",
                "plan": None,
                "trial_days_left": None,
                "days_left": None,
                "cancel_at_period_end": False,
                "period_end": None
            }
        
        now = datetime.utcnow()
        
        # 체험 기간 남은 일수
        trial_days_left = None
        if subscription.status == "trial" and subscription.trial_end_date:
            delta = subscription.trial_end_date - now
            trial_days_left = max(0, delta.days)
        
        # 유료 구독 남은 일수
        days_left = None
        if subscription.status == "active" and subscription.current_period_end:
            delta = subscription.current_period_end - now
            days_left = max(0, delta.days)
        
        return {
            "status": subscription.status,
            "plan": subscription.plan,
            "trial_days_left": trial_days_left,
            "days_left": days_left,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None
        }
    
    def check_and_expire_subscriptions(self) -> int:
        """
        만료된 구독 처리 (배치 작업용)
        
        Returns:
            만료 처리된 구독 수
        """
        now = datetime.utcnow()
        
        # 체험 만료
        expired_trials = self.db.query(Subscription).filter(
            Subscription.status == "trial",
            Subscription.trial_end_date <= now
        ).all()
        
        for sub in expired_trials:
            sub.status = "expired"
            sub.updated_at = now
        
        # 유료 구독 만료 (cancel_at_period_end=True인 경우)
        expired_active = self.db.query(Subscription).filter(
            Subscription.status == "active",
            Subscription.cancel_at_period_end == True,
            Subscription.current_period_end <= now
        ).all()
        
        for sub in expired_active:
            sub.status = "expired"
            sub.updated_at = now
        
        self.db.commit()
        
        return len(expired_trials) + len(expired_active)


class PaymentService:
    """결제 관리 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_payment(
        self,
        subscription_id: int,
        order_id: str,
        amount: int,
        payment_key: Optional[str] = None
    ) -> Payment:
        """
        결제 생성
        
        Args:
            subscription_id: 구독 ID
            order_id: 주문 ID (멱등성 보장)
            amount: 결제 금액
            payment_key: 토스페이먼츠 결제 키
            
        Returns:
            생성된 Payment 객체
            
        Raises:
            ValueError: 중복된 order_id인 경우
        """
        # 중복 확인 (멱등성)
        existing = self.db.query(Payment).filter(
            Payment.order_id == order_id
        ).first()
        
        if existing:
            return existing  # 이미 존재하면 기존 결제 반환
        
        payment = Payment(
            subscription_id=subscription_id,
            order_id=order_id,
            amount=amount,
            payment_key=payment_key,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        try:
            self.db.add(payment)
            self.db.commit()
            self.db.refresh(payment)
            return payment
        except IntegrityError:
            self.db.rollback()
            # 동시성 이슈로 중복 생성 시도된 경우
            existing = self.db.query(Payment).filter(
                Payment.order_id == order_id
            ).first()
            if existing:
                return existing
            raise ValueError(f"Failed to create payment for order {order_id}")
    
    def complete_payment(
        self,
        order_id: str,
        payment_key: str,
        payment_method: str
    ) -> Payment:
        """
        결제 완료 처리
        
        Args:
            order_id: 주문 ID
            payment_key: 토스페이먼츠 결제 키
            payment_method: 결제 수단
            
        Returns:
            업데이트된 Payment 객체
            
        Raises:
            ValueError: 결제를 찾을 수 없는 경우
        """
        payment = self.db.query(Payment).filter(
            Payment.order_id == order_id
        ).first()
        
        if not payment:
            raise ValueError(f"Payment with order_id {order_id} not found")
        
        payment.payment_key = payment_key
        payment.payment_method = payment_method
        payment.status = "success"
        payment.paid_at = datetime.utcnow()
        payment.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def fail_payment(
        self,
        order_id: str,
        reason: str
    ) -> Payment:
        """
        결제 실패 처리
        
        Args:
            order_id: 주문 ID
            reason: 실패 사유
            
        Returns:
            업데이트된 Payment 객체
        """
        payment = self.db.query(Payment).filter(
            Payment.order_id == order_id
        ).first()
        
        if not payment:
            raise ValueError(f"Payment with order_id {order_id} not found")
        
        payment.status = "failed"
        payment.failed_reason = reason
        payment.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def refund_payment(
        self,
        payment_id: int,
        refund_amount: int,
        refund_reason: str
    ) -> Payment:
        """
        결제 환불 처리
        
        Args:
            payment_id: 결제 ID
            refund_amount: 환불 금액
            refund_reason: 환불 사유
            
        Returns:
            업데이트된 Payment 객체
        """
        payment = self.db.query(Payment).filter(
            Payment.id == payment_id
        ).first()
        
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if payment.status != "success":
            raise ValueError(f"Payment {payment_id} is not in success status")
        
        payment.status = "refunded"
        payment.refund_amount = refund_amount
        payment.refund_reason = refund_reason
        payment.refunded_at = datetime.utcnow()
        payment.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def get_payment_by_order_id(self, order_id: str) -> Optional[Payment]:
        """
        주문 ID로 결제 조회
        
        Args:
            order_id: 주문 ID
            
        Returns:
            Payment 객체 또는 None
        """
        return self.db.query(Payment).filter(
            Payment.order_id == order_id
        ).first()
