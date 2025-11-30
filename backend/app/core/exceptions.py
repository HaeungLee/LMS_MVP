"""
표준화된 에러 응답 및 전역 예외 핸들러

사용법:
    from app.core.exceptions import (
        AppException,
        NotFoundException,
        ValidationException,
        AuthenticationException,
        AuthorizationException,
    )
    
    # 에러 발생 시
    raise NotFoundException("User", user_id)
    raise ValidationException("Invalid email format")
"""
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback
import logging

logger = logging.getLogger(__name__)


# ============================================
# 표준 에러 응답 스키마
# ============================================

class ErrorResponse(BaseModel):
    """표준 에러 응답 형식"""
    success: bool = False
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "NOT_FOUND",
                "message": "User with id 123 not found",
                "details": None,
                "request_id": "abc123"
            }
        }


# ============================================
# 커스텀 예외 클래스
# ============================================

class AppException(Exception):
    """애플리케이션 기본 예외"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "APP_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundException(AppException):
    """리소스를 찾을 수 없음 (404)"""
    
    def __init__(self, resource: str, identifier: Any = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": str(identifier) if identifier else None}
        )


class ValidationException(AppException):
    """유효성 검사 실패 (400)"""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"field": field, **(details or {})}
        )


class AuthenticationException(AppException):
    """인증 실패 (401)"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationException(AppException):
    """권한 부족 (403)"""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ConflictException(AppException):
    """리소스 충돌 (409) - 예: 중복 이메일"""
    
    def __init__(self, message: str, resource: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details={"resource": resource} if resource else None
        )


class RateLimitException(AppException):
    """요청 제한 초과 (429)"""
    
    def __init__(self, message: str = "Too many requests", retry_after: Optional[int] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after} if retry_after else None
        )


class ExternalServiceException(AppException):
    """외부 서비스 에러 (502) - 예: AI API 실패"""
    
    def __init__(self, service: str, message: str = "External service unavailable"):
        super().__init__(
            message=f"{service}: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={"service": service}
        )


# ============================================
# 전역 예외 핸들러
# ============================================

def get_request_id(request: Request) -> Optional[str]:
    """Request ID 추출"""
    return getattr(request.state, "request_id", None) or request.headers.get("x-request-id")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """AppException 처리"""
    request_id = get_request_id(request)
    
    # 에러 로깅
    logger.warning(
        f"[{request_id}] {exc.error_code}: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.error_code,
            message=exc.message,
            details=exc.details,
            request_id=request_id,
        ).model_dump()
    )


async def http_exception_handler(request: Request, exc) -> JSONResponse:
    """FastAPI HTTPException 처리"""
    from fastapi import HTTPException
    
    request_id = get_request_id(request)
    
    # 상태 코드별 에러 코드 매핑
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_ERROR",
    }
    
    error_code = error_code_map.get(exc.status_code, "ERROR")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=error_code,
            message=str(exc.detail),
            request_id=request_id,
        ).model_dump()
    )


async def validation_exception_handler(request: Request, exc) -> JSONResponse:
    """Pydantic ValidationError 처리"""
    from pydantic import ValidationError
    
    request_id = get_request_id(request)
    
    # 첫 번째 에러 메시지를 메인 메시지로
    errors = exc.errors() if hasattr(exc, 'errors') else []
    first_error = errors[0] if errors else {}
    
    message = first_error.get("msg", "Validation failed")
    field = ".".join(str(loc) for loc in first_error.get("loc", []))
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="VALIDATION_ERROR",
            message=f"{field}: {message}" if field else message,
            details={"errors": errors},
            request_id=request_id,
        ).model_dump()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """처리되지 않은 예외 처리"""
    request_id = get_request_id(request)
    
    # 스택 트레이스 로깅
    logger.error(
        f"[{request_id}] Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc(),
        }
    )
    
    # 프로덕션에서는 상세 에러 숨김
    import os
    is_production = os.getenv("ENVIRONMENT", "development") == "production"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="INTERNAL_ERROR",
            message="An unexpected error occurred" if is_production else str(exc),
            request_id=request_id,
        ).model_dump()
    )


def register_exception_handlers(app):
    """FastAPI 앱에 예외 핸들러 등록"""
    from fastapi import HTTPException
    from fastapi.exceptions import RequestValidationError
    
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
