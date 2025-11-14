# -*- coding: utf-8 -*-
"""
Safe Code Assistant - Constitutional AI 기반 코드 리뷰 시스템

3단계 검증:
1. Safety (보안 취약점 검사)
2. Ethics (윤리적 문제 검사)
3. Education (교육적 피드백 생성)
"""
import re
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from app.core.anthropic_client import anthropic_client

logger = logging.getLogger(__name__)


# ============================================================
# Pydantic 모델
# ============================================================

class SecurityVulnerability(BaseModel):
    """보안 취약점"""
    type: str  # "SQL_INJECTION", "XSS", "COMMAND_INJECTION" 등
    severity: str  # "critical", "high", "medium", "low"
    line_number: Optional[int] = None
    description: str
    safe_alternative: str


class EthicalIssue(BaseModel):
    """윤리적 문제"""
    type: str  # "MALWARE", "PRIVACY_VIOLATION", "COPYRIGHT_INFRINGEMENT" 등
    description: str
    reason: str


class CodeReview(BaseModel):
    """코드 리뷰 결과"""
    safe_to_run: bool
    vulnerabilities: List[SecurityVulnerability]
    ethical_issues: List[EthicalIssue]
    educational_feedback: Optional[str] = None
    reviewed_at: datetime = datetime.utcnow()


# ============================================================
# Safe Code Assistant 클래스
# ============================================================

class SafeCodeAssistant:
    """
    Constitutional AI 기반 코드 어시스턴트
    
    기능:
    - 보안 취약점 자동 탐지
    - 윤리적 문제 검사
    - 교육적 피드백 생성 (Claude)
    """
    
    def __init__(self):
        self.anthropic = anthropic_client
        
        # 보안 패턴 (정규표현식)
        self.security_patterns = {
            "SQL_INJECTION": [
                (r'\.execute\(["\'].*%s.*["\']\s*%', "String formatting in SQL query"),
                (r'\.execute\(["\'].*\+.*["\']\)', "String concatenation in SQL query"),
                (r'\.execute\(f["\'].*\{.*\}.*["\']\)', "f-string in SQL query"),
                (r'cursor\.execute\(["\'][^"\']*["\']\.format\(', "str.format() in SQL query"),
            ],
            "COMMAND_INJECTION": [
                (r'os\.system\(["\'][^"\']*\{.*\}', "User input in os.system()"),
                (r'subprocess\.(call|run|Popen)\(.*shell\s*=\s*True', "shell=True with user input"),
                (r'eval\(', "eval() with potential user input"),
                (r'exec\(', "exec() with potential user input"),
            ],
            "UNSAFE_DESERIALIZATION": [
                (r'pickle\.loads\(', "pickle.loads() - Remote Code Execution risk"),
                (r'yaml\.load\([^,]*\)', "yaml.load() without SafeLoader"),
            ],
            "HARDCODED_SECRETS": [
                (r'(password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']', "Hardcoded password"),
                (r'(api_key|apikey|api_secret)\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded API key"),
                (r'(token|secret|private_key)\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded secret"),
            ],
            "WEAK_CRYPTO": [
                (r'hashlib\.(md5|sha1)\(', "Weak hashing algorithm (MD5/SHA1)"),
                (r'random\.(randint|choice|random)\(', "Non-cryptographic random (use secrets module)"),
            ],
            "PATH_TRAVERSAL": [
                (r'open\(.*\+.*user', "User input in file path"),
                (r'open\(f["\'].*\{.*\}', "f-string with user input in file path"),
            ]
        }
        
        # 윤리적 패턴 (키워드 기반)
        self.ethical_keywords = {
            "MALWARE": [
                "malware", "virus", "trojan", "ransomware", "keylogger",
                "backdoor", "rootkit", "스파이웨어", "악성코드"
            ],
            "HACKING_TOOLS": [
                "brute.?force", "crack.*password", "sql.*injection.*tool",
                "exploit.*kit", "port.*scanner", "vulnerability.*scanner",
                "비밀번호.*크래킹", "해킹.*도구"
            ],
            "DDOS": [
                "ddos", "denial.*of.*service", "flood.*attack", "서비스.*거부"
            ],
            "PRIVACY_VIOLATION": [
                "keylogger", "screen.*capture.*stealth", "hidden.*camera",
                "spy.*software", "개인정보.*무단.*수집"
            ],
            "SPAM": [
                "mass.*email.*sender", "spam.*bot", "auto.*follow.*bot",
                "스팸.*발송", "자동.*메시지.*봇"
            ]
        }
    
    async def review_code(
        self,
        code: str,
        language: str,
        user_level: str = "beginner"
    ) -> CodeReview:
        """
        코드 리뷰 (3단계 검증)
        
        Args:
            code: 검토할 코드
            language: 프로그래밍 언어
            user_level: 학습자 레벨
        
        Returns:
            CodeReview: 전체 리뷰 결과
        """
        logger.info(f"Reviewing {language} code (user_level: {user_level})")
        
        # Step 1: 보안 취약점 검사
        vulnerabilities = await self._check_safety(code, language)
        
        # Step 2: 윤리적 문제 검사
        ethical_issues = await self._check_ethics(code)
        
        # Step 3: 교육적 피드백 생성 (Claude)
        educational_feedback = None
        if vulnerabilities or ethical_issues:
            # 문제가 있는 경우에만 피드백 생성
            educational_feedback = await self._generate_educational_feedback(
                code=code,
                language=language,
                vulnerabilities=vulnerabilities,
                ethical_issues=ethical_issues,
                user_level=user_level
            )
        
        # 실행 안전성 판단
        safe_to_run = (
            len(vulnerabilities) == 0 and 
            len(ethical_issues) == 0
        )
        
        return CodeReview(
            safe_to_run=safe_to_run,
            vulnerabilities=vulnerabilities,
            ethical_issues=ethical_issues,
            educational_feedback=educational_feedback
        )
    
    async def _check_safety(
        self,
        code: str,
        language: str
    ) -> List[SecurityVulnerability]:
        """
        보안 취약점 검사
        
        정규표현식 기반 패턴 매칭으로 빠르게 탐지
        """
        vulnerabilities = []
        code_lower = code.lower()
        
        # Python 코드만 검사 (다른 언어는 추후 확장)
        if language.lower() != "python":
            return vulnerabilities
        
        for vuln_type, patterns in self.security_patterns.items():
            for pattern, description in patterns:
                matches = re.finditer(pattern, code, re.IGNORECASE)
                
                for match in matches:
                    # 라인 번호 계산
                    line_number = code[:match.start()].count('\n') + 1
                    
                    # 심각도 판단
                    severity = self._determine_severity(vuln_type)
                    
                    # 안전한 대안 제시
                    safe_alternative = self._get_safe_alternative(vuln_type)
                    
                    vulnerabilities.append(SecurityVulnerability(
                        type=vuln_type,
                        severity=severity,
                        line_number=line_number,
                        description=description,
                        safe_alternative=safe_alternative
                    ))
        
        return vulnerabilities
    
    async def _check_ethics(self, code: str) -> List[EthicalIssue]:
        """
        윤리적 문제 검사
        
        키워드 기반 탐지 + 컨텍스트 분석
        """
        ethical_issues = []
        code_lower = code.lower()
        
        for issue_type, keywords in self.ethical_keywords.items():
            for keyword in keywords:
                # 정규표현식으로 키워드 검색
                if re.search(keyword, code_lower):
                    # 발견된 경우
                    description = self._get_ethical_issue_description(issue_type)
                    reason = self._get_ethical_reason(issue_type)
                    
                    ethical_issues.append(EthicalIssue(
                        type=issue_type,
                        description=description,
                        reason=reason
                    ))
                    break  # 중복 방지
        
        return ethical_issues
    
    async def _generate_educational_feedback(
        self,
        code: str,
        language: str,
        vulnerabilities: List[SecurityVulnerability],
        ethical_issues: List[EthicalIssue],
        user_level: str
    ) -> str:
        """
        교육적 피드백 생성 (Claude 사용)
        
        Constitutional AI 원칙을 적용한 친절하고 교육적인 피드백
        """
        try:
            feedback = await self.anthropic.generate_with_constitutional_ai(
                user_code=code,
                language=language,
                user_level=user_level,
                vulnerabilities=[v.dict() for v in vulnerabilities],
                ethical_issues=[e.dict() for e in ethical_issues]
            )
            return feedback
        except Exception as e:
            logger.error(f"Failed to generate educational feedback: {e}")
            # Fallback: 기본 피드백
            return self._generate_fallback_feedback(vulnerabilities, ethical_issues)
    
    def _determine_severity(self, vuln_type: str) -> str:
        """취약점 심각도 판단"""
        critical = ["SQL_INJECTION", "COMMAND_INJECTION", "UNSAFE_DESERIALIZATION"]
        high = ["HARDCODED_SECRETS", "PATH_TRAVERSAL"]
        medium = ["WEAK_CRYPTO"]
        
        if vuln_type in critical:
            return "critical"
        elif vuln_type in high:
            return "high"
        elif vuln_type in medium:
            return "medium"
        else:
            return "low"
    
    def _get_safe_alternative(self, vuln_type: str) -> str:
        """안전한 대안 코드 예시"""
        alternatives = {
            "SQL_INJECTION": "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))",
            "COMMAND_INJECTION": "subprocess.run(['ping', host], shell=False, check=True)",
            "UNSAFE_DESERIALIZATION": "json.loads(data) 또는 ast.literal_eval() 사용",
            "HARDCODED_SECRETS": "os.getenv('API_KEY') 또는 환경변수 사용",
            "WEAK_CRYPTO": "hashlib.sha256() 또는 bcrypt 사용",
            "PATH_TRAVERSAL": "Path('/uploads').resolve() / filename (pathlib 사용)"
        }
        return alternatives.get(vuln_type, "안전한 대안을 찾아보세요.")
    
    def _get_ethical_issue_description(self, issue_type: str) -> str:
        """윤리적 문제 설명"""
        descriptions = {
            "MALWARE": "악성코드 또는 바이러스 관련 코드",
            "HACKING_TOOLS": "해킹 도구 또는 무단 접근 시도",
            "DDOS": "서비스 거부 공격 (DDoS)",
            "PRIVACY_VIOLATION": "개인정보 보호 위반",
            "SPAM": "스팸 발송 도구"
        }
        return descriptions.get(issue_type, "윤리적 문제 발견")
    
    def _get_ethical_reason(self, issue_type: str) -> str:
        """윤리적 문제 이유"""
        reasons = {
            "MALWARE": "악성코드 제작 및 배포는 불법이며 타인에게 피해를 줍니다.",
            "HACKING_TOOLS": "무단 접근 도구는 불법이며 개인정보를 침해합니다.",
            "DDOS": "서비스 거부 공격은 불법이며 다른 사용자에게 피해를 줍니다.",
            "PRIVACY_VIOLATION": "동의 없는 개인정보 수집은 불법입니다.",
            "SPAM": "스팸 발송은 불법이며 타인에게 피해를 줍니다."
        }
        return reasons.get(issue_type, "비윤리적 코드입니다.")
    
    def _generate_fallback_feedback(
        self,
        vulnerabilities: List[SecurityVulnerability],
        ethical_issues: List[EthicalIssue]
    ) -> str:
        """Claude API 실패 시 기본 피드백"""
        feedback_parts = []
        
        if vulnerabilities:
            feedback_parts.append("🔴 **보안 취약점 발견:**\n")
            for v in vulnerabilities:
                feedback_parts.append(
                    f"- [{v.severity.upper()}] {v.type}: {v.description}\n"
                    f"  💡 안전한 대안: {v.safe_alternative}\n"
                )
        
        if ethical_issues:
            feedback_parts.append("\n🚫 **윤리적 문제 발견:**\n")
            for e in ethical_issues:
                feedback_parts.append(
                    f"- {e.type}: {e.description}\n"
                    f"  이유: {e.reason}\n"
                )
        
        return "\n".join(feedback_parts)


# 싱글톤 인스턴스
safe_code_assistant = SafeCodeAssistant()

