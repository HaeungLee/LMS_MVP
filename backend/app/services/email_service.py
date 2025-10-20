"""
이메일 전송 서비스
- 환영 이메일
- 무료 체험 리마인더
- 재참여 이메일
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """이메일 전송 서비스"""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_user)
        self.from_name = os.getenv('FROM_NAME', 'EduAI')
        
        # Jinja2 템플릿 환경 설정
        template_dir = Path(__file__).parent.parent / 'templates' / 'emails'
        template_dir.mkdir(parents=True, exist_ok=True)
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
        
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        이메일 전송 (내부 메서드)
        
        Args:
            to_email: 수신자 이메일
            subject: 제목
            html_content: HTML 본문
            text_content: 텍스트 본문 (선택)
            
        Returns:
            성공 여부
        """
        try:
            # 이메일 설정이 없으면 로그만 출력 (개발 환경)
            if not self.smtp_user or not self.smtp_password:
                logger.warning(f"📧 [DEV MODE] 이메일 전송 시뮬레이션")
                logger.info(f"To: {to_email}")
                logger.info(f"Subject: {subject}")
                logger.info(f"Content (first 100 chars): {html_content[:100]}...")
                return True
            
            # 이메일 메시지 생성
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email
            
            # 텍스트 본문 추가
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                message.attach(text_part)
            
            # HTML 본문 추가
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)
            
            # SMTP 서버 연결 및 전송
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"✅ 이메일 전송 성공: {to_email} - {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 이메일 전송 실패: {to_email} - {str(e)}")
            return False
    
    def send_welcome_email(
        self,
        to_email: str,
        user_name: str,
        user_id: int
    ) -> bool:
        """
        환영 이메일 전송
        
        Args:
            to_email: 수신자 이메일
            user_name: 사용자 이름
            user_id: 사용자 ID
            
        Returns:
            성공 여부
        """
        try:
            # 템플릿 렌더링
            template = self.jinja_env.get_template('welcome.html')
            html_content = template.render(
                user_name=user_name,
                dashboard_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/dashboard",
                onboarding_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/onboarding",
                current_year=datetime.now().year
            )
            
            # 텍스트 버전
            text_content = f"""
안녕하세요 {user_name}님,

EduAI에 가입해 주셔서 감사합니다! 🎉

AI가 당신만의 맞춤형 학습 경로를 만들어드립니다.
지금 바로 시작해보세요!

대시보드: {os.getenv('FRONTEND_URL', 'http://localhost:5174')}/dashboard

EduAI 팀 드림
            """
            
            return self._send_email(
                to_email=to_email,
                subject=f"{user_name}님, EduAI에 오신 것을 환영합니다! 🎉",
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"환영 이메일 전송 실패: {str(e)}")
            return False
    
    def send_trial_reminder_email(
        self,
        to_email: str,
        user_name: str,
        days_left: int,
        stats: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        무료 체험 리마인더 이메일
        
        Args:
            to_email: 수신자 이메일
            user_name: 사용자 이름
            days_left: 남은 일수
            stats: 학습 통계 (선택)
            
        Returns:
            성공 여부
        """
        try:
            template = self.jinja_env.get_template('trial_reminder.html')
            html_content = template.render(
                user_name=user_name,
                days_left=days_left,
                stats=stats or {},
                pricing_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/dashboard/pricing",
                dashboard_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/dashboard",
                current_year=datetime.now().year
            )
            
            text_content = f"""
{user_name}님, 무료 체험 종료가 {days_left}일 남았습니다! ⏰

지금까지 학습한 내용:
- 문제 풀이: {stats.get('problems_solved', 0)}개
- 학습 시간: {stats.get('study_hours', 0)}시간
- 정답률: {stats.get('accuracy', 0)}%

프리미엄으로 업그레이드하고 계속 학습하세요!

업그레이드: {os.getenv('FRONTEND_URL', 'http://localhost:5174')}/dashboard/pricing

EduAI 팀 드림
            """
            
            return self._send_email(
                to_email=to_email,
                subject=f"⏰ {user_name}님, 무료 체험 종료 {days_left}일 전입니다",
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"체험 리마인더 이메일 전송 실패: {str(e)}")
            return False
    
    def send_re_engagement_email(
        self,
        to_email: str,
        user_name: str,
        last_login_days: int,
        progress: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        재참여 유도 이메일
        
        Args:
            to_email: 수신자 이메일
            user_name: 사용자 이름
            last_login_days: 마지막 로그인 후 경과 일수
            progress: 학습 진행 상황 (선택)
            
        Returns:
            성공 여부
        """
        try:
            template = self.jinja_env.get_template('re_engagement.html')
            html_content = template.render(
                user_name=user_name,
                last_login_days=last_login_days,
                progress=progress or {},
                dashboard_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/dashboard",
                learn_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/dashboard/learn",
                current_year=datetime.now().year
            )
            
            text_content = f"""
{user_name}님, 당신의 학습을 기다리고 있어요! 😊

{last_login_days}일 동안 보지 못했습니다.
학습 진행률: {progress.get('completion_rate', 0)}%

지금 다시 시작하세요:
{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/dashboard

EduAI 팀 드림
            """
            
            return self._send_email(
                to_email=to_email,
                subject=f"😊 {user_name}님, 함께 학습을 계속해요!",
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"재참여 이메일 전송 실패: {str(e)}")
            return False
    
    def send_payment_success_email(
        self,
        to_email: str,
        user_name: str,
        plan_name: str,
        amount: int,
        next_billing_date: datetime
    ) -> bool:
        """
        결제 성공 확인 이메일
        
        Args:
            to_email: 수신자 이메일
            user_name: 사용자 이름
            plan_name: 플랜 이름
            amount: 결제 금액
            next_billing_date: 다음 결제일
            
        Returns:
            성공 여부
        """
        try:
            template = self.jinja_env.get_template('payment_success.html')
            html_content = template.render(
                user_name=user_name,
                plan_name=plan_name,
                amount=f"{amount:,}",
                next_billing_date=next_billing_date.strftime('%Y년 %m월 %d일'),
                dashboard_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/dashboard",
                subscription_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/dashboard/settings/subscription",
                current_year=datetime.now().year
            )
            
            text_content = f"""
{user_name}님, 결제가 완료되었습니다! 🎉

플랜: {plan_name}
금액: ₩{amount:,}
다음 결제일: {next_billing_date.strftime('%Y년 %m월 %d일')}

프리미엄 기능을 마음껏 사용하세요!

대시보드: {os.getenv('FRONTEND_URL', 'http://localhost:5174')}/dashboard

EduAI 팀 드림
            """
            
            return self._send_email(
                to_email=to_email,
                subject=f"✅ {user_name}님, {plan_name} 결제가 완료되었습니다",
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"결제 성공 이메일 전송 실패: {str(e)}")
            return False


# 싱글톤 인스턴스
_email_service_instance = None

def get_email_service() -> EmailService:
    """이메일 서비스 인스턴스 가져오기"""
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailService()
    return _email_service_instance
