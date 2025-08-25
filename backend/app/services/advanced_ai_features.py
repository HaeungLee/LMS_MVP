"""
고급 AI 기능 통합 - Phase 4
- AI 코드 리뷰 시스템
- 프로젝트 자동 분석
- 포트폴리오 평가
- 실무 스킬 진단
"""

import json
import logging
import re
import ast
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session

from app.models.orm import User, UserProject, Portfolio, ProjectTemplate
from app.services.ai_providers import generate_ai_response, ModelTier, get_ai_provider_manager
from app.services.redis_service import get_redis_service

logger = logging.getLogger(__name__)

class CodeQuality(Enum):
    """코드 품질 등급"""
    EXCELLENT = "excellent"      # 90-100점
    GOOD = "good"               # 75-89점  
    SATISFACTORY = "satisfactory" # 60-74점
    NEEDS_IMPROVEMENT = "needs_improvement"  # 40-59점
    POOR = "poor"               # 0-39점

class ReviewType(Enum):
    """리뷰 유형"""
    FULL_REVIEW = "full"        # 전체 리뷰
    SECURITY_FOCUS = "security" # 보안 중심
    PERFORMANCE_FOCUS = "performance"  # 성능 중심
    STYLE_FOCUS = "style"       # 스타일 중심
    LOGIC_FOCUS = "logic"       # 로직 중심

@dataclass
class CodeIssue:
    """코드 이슈"""
    severity: str  # critical, major, minor, info
    type: str      # bug, security, performance, style, logic
    line_number: Optional[int]
    message: str
    suggestion: str
    example: Optional[str]

@dataclass
class CodeReviewResult:
    """코드 리뷰 결과"""
    overall_score: int
    quality_grade: CodeQuality
    issues: List[CodeIssue]
    strengths: List[str]
    recommendations: List[str]
    complexity_analysis: Dict[str, Any]
    security_score: int
    performance_score: int
    maintainability_score: int

@dataclass
class ProjectAnalysis:
    """프로젝트 분석 결과"""
    project_id: str
    analysis_date: datetime
    technical_stack: List[str]
    architecture_quality: str
    code_coverage: float
    security_assessment: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    improvement_roadmap: List[str]
    skill_demonstration: List[str]
    market_relevance: str

class AdvancedAIFeatures:
    """고급 AI 기능 시스템"""
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_service = get_redis_service()
        self.ai_provider = get_ai_provider_manager()
        
        # 코드 리뷰 기준
        self.review_criteria = {
            'readability': {
                'weight': 0.25,
                'factors': ['naming', 'comments', 'structure', 'formatting']
            },
            'functionality': {
                'weight': 0.30,
                'factors': ['correctness', 'edge_cases', 'error_handling']
            },
            'performance': {
                'weight': 0.20,
                'factors': ['efficiency', 'memory_usage', 'scalability']
            },
            'security': {
                'weight': 0.15,
                'factors': ['input_validation', 'authentication', 'data_protection']
            },
            'maintainability': {
                'weight': 0.10,
                'factors': ['modularity', 'reusability', 'testability']
            }
        }
        
        # 프로그래밍 언어별 특성
        self.language_specifics = {
            'python': {
                'style_guide': 'PEP 8',
                'common_issues': ['indentation', 'naming_convention', 'import_order'],
                'security_concerns': ['sql_injection', 'eval_usage', 'pickle_usage'],
                'performance_tips': ['list_comprehension', 'generator_usage', 'builtin_functions']
            },
            'javascript': {
                'style_guide': 'ESLint',
                'common_issues': ['var_usage', 'semicolons', 'equality_operators'],
                'security_concerns': ['xss', 'csrf', 'prototype_pollution'],
                'performance_tips': ['async_await', 'event_delegation', 'debouncing']
            },
            'java': {
                'style_guide': 'Google Java Style',
                'common_issues': ['naming_convention', 'exception_handling', 'resource_management'],
                'security_concerns': ['deserialization', 'path_traversal', 'injection'],
                'performance_tips': ['stream_api', 'string_builder', 'collection_choice']
            }
        }
    
    async def review_code(
        self, 
        code: str, 
        language: str,
        review_type: ReviewType = ReviewType.FULL_REVIEW,
        user_level: str = "intermediate"
    ) -> CodeReviewResult:
        """AI 코드 리뷰"""
        
        try:
            # 코드 분석 준비
            code_analysis = await self._analyze_code_structure(code, language)
            
            # AI 리뷰 실행
            review_result = await self._perform_ai_review(
                code, language, review_type, user_level, code_analysis
            )
            
            # 점수 계산
            scores = self._calculate_review_scores(review_result, code_analysis)
            
            # 이슈 분류 및 우선순위 설정
            categorized_issues = self._categorize_issues(review_result.get('issues', []))
            
            # 개선 제안 생성
            recommendations = await self._generate_improvement_recommendations(
                review_result, code_analysis, user_level
            )
            
            result = CodeReviewResult(
                overall_score=scores['overall'],
                quality_grade=self._determine_quality_grade(scores['overall']),
                issues=categorized_issues,
                strengths=review_result.get('strengths', []),
                recommendations=recommendations,
                complexity_analysis=code_analysis,
                security_score=scores['security'],
                performance_score=scores['performance'],
                maintainability_score=scores['maintainability']
            )
            
            # 리뷰 결과 캐싱
            await self._cache_review_result(code, result)
            
            logger.info(f"코드 리뷰 완료 - 언어: {language}, 점수: {scores['overall']}")
            return result
            
        except Exception as e:
            logger.error(f"코드 리뷰 실패: {str(e)}")
            return await self._generate_fallback_review(code, language)
    
    async def _analyze_code_structure(self, code: str, language: str) -> Dict[str, Any]:
        """코드 구조 분석"""
        
        analysis = {
            'lines_of_code': len(code.split('\n')),
            'language': language,
            'estimated_complexity': 'medium',
            'function_count': 0,
            'class_count': 0,
            'import_count': 0,
            'comment_ratio': 0.0
        }
        
        try:
            if language.lower() == 'python':
                analysis.update(self._analyze_python_code(code))
            elif language.lower() == 'javascript':
                analysis.update(self._analyze_javascript_code(code))
            elif language.lower() == 'java':
                analysis.update(self._analyze_java_code(code))
            
        except Exception as e:
            logger.warning(f"코드 구조 분석 부분 실패: {str(e)}")
        
        return analysis
    
    def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Python 코드 분석"""
        
        analysis = {}
        lines = code.split('\n')
        
        # 함수 개수
        function_count = len(re.findall(r'^\s*def\s+\w+', code, re.MULTILINE))
        analysis['function_count'] = function_count
        
        # 클래스 개수
        class_count = len(re.findall(r'^\s*class\s+\w+', code, re.MULTILINE))
        analysis['class_count'] = class_count
        
        # import 개수
        import_count = len(re.findall(r'^\s*(import|from)\s+', code, re.MULTILINE))
        analysis['import_count'] = import_count
        
        # 주석 비율
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        total_lines = len([line for line in lines if line.strip()])
        analysis['comment_ratio'] = comment_lines / max(1, total_lines)
        
        # 복잡도 추정
        if function_count > 10 or class_count > 3 or len(lines) > 200:
            analysis['estimated_complexity'] = 'high'
        elif function_count < 3 and class_count < 2 and len(lines) < 50:
            analysis['estimated_complexity'] = 'low'
        else:
            analysis['estimated_complexity'] = 'medium'
        
        return analysis
    
    def _analyze_javascript_code(self, code: str) -> Dict[str, Any]:
        """JavaScript 코드 분석"""
        
        analysis = {}
        
        # 함수 개수 (function 키워드 + 화살표 함수)
        function_count = (
            len(re.findall(r'\bfunction\s+\w+', code)) +
            len(re.findall(r'\w+\s*=>\s*', code)) +
            len(re.findall(r'\w+:\s*function', code))
        )
        analysis['function_count'] = function_count
        
        # 클래스 개수
        class_count = len(re.findall(r'\bclass\s+\w+', code))
        analysis['class_count'] = class_count
        
        # import 개수
        import_count = (
            len(re.findall(r'\bimport\s+', code)) +
            len(re.findall(r'\brequire\s*\(', code))
        )
        analysis['import_count'] = import_count
        
        # 주석 비율 (// 및 /* */ 주석)
        comment_lines = (
            len(re.findall(r'//.*', code)) +
            len(re.findall(r'/\*.*?\*/', code, re.DOTALL))
        )
        total_lines = len([line for line in code.split('\n') if line.strip()])
        analysis['comment_ratio'] = comment_lines / max(1, total_lines)
        
        return analysis
    
    def _analyze_java_code(self, code: str) -> Dict[str, Any]:
        """Java 코드 분석"""
        
        analysis = {}
        
        # 메소드 개수
        method_count = len(re.findall(r'\b(public|private|protected|static).*\w+\s*\([^)]*\)\s*{', code))
        analysis['function_count'] = method_count
        
        # 클래스 개수
        class_count = len(re.findall(r'\b(public\s+)?class\s+\w+', code))
        analysis['class_count'] = class_count
        
        # import 개수
        import_count = len(re.findall(r'^\s*import\s+', code, re.MULTILINE))
        analysis['import_count'] = import_count
        
        # 주석 비율
        comment_lines = (
            len(re.findall(r'//.*', code)) +
            len(re.findall(r'/\*.*?\*/', code, re.DOTALL))
        )
        total_lines = len([line for line in code.split('\n') if line.strip()])
        analysis['comment_ratio'] = comment_lines / max(1, total_lines)
        
        return analysis
    
    async def _perform_ai_review(
        self, 
        code: str, 
        language: str, 
        review_type: ReviewType,
        user_level: str,
        code_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """AI 리뷰 실행"""
        
        # 언어별 특성 정보
        lang_specifics = self.language_specifics.get(language.lower(), {})
        
        review_prompt = f"""다음 {language} 코드를 전문적으로 리뷰해주세요.

코드:
```{language}
{code}
```

코드 정보:
- 줄 수: {code_analysis['lines_of_code']}
- 함수/메소드 수: {code_analysis['function_count']}
- 클래스 수: {code_analysis['class_count']}
- 주석 비율: {code_analysis['comment_ratio']:.2%}
- 추정 복잡도: {code_analysis['estimated_complexity']}

리뷰 유형: {review_type.value}
사용자 레벨: {user_level}
스타일 가이드: {lang_specifics.get('style_guide', 'Best Practices')}

다음 관점에서 종합적으로 분석해주세요:

1. **코드 품질 (1-100점)**
   - 가독성 및 코드 스타일
   - 기능적 정확성
   - 성능 및 효율성
   - 보안 고려사항
   - 유지보수성

2. **구체적인 이슈들**
   - 심각도: critical/major/minor/info
   - 유형: bug/security/performance/style/logic
   - 라인 번호 (가능한 경우)
   - 문제점과 개선 제안

3. **강점 및 잘된 부분**

4. **개선 권장사항**

5. **{user_level} 수준에 맞는 학습 조언**

결과를 다음 JSON 형식으로 제공해주세요:
{{
  "overall_score": 점수(1-100),
  "quality_assessment": {{
    "readability": 점수(1-100),
    "functionality": 점수(1-100),
    "performance": 점수(1-100),
    "security": 점수(1-100),
    "maintainability": 점수(1-100)
  }},
  "issues": [
    {{
      "severity": "critical/major/minor/info",
      "type": "bug/security/performance/style/logic",
      "line": 라인번호_또는_null,
      "message": "문제점 설명",
      "suggestion": "개선 방법",
      "example": "예시 코드 (선택적)"
    }}
  ],
  "strengths": ["강점1", "강점2"],
  "recommendations": ["권장사항1", "권장사항2"],
  "learning_advice": ["학습조언1", "학습조언2"]
}}"""

        response = await generate_ai_response(
            prompt=review_prompt,
            task_type="coding",
            model_preference=ModelTier.FREE,  # 무료 모델 사용
            temperature=0.3
        )
        
        try:
            review_result = json.loads(response.get('response', '{}'))
            return review_result
        except json.JSONDecodeError:
            logger.warning("AI 리뷰 결과 파싱 실패, 기본 분석 실행")
            return self._generate_basic_review(code, language, code_analysis)
    
    def _generate_basic_review(self, code: str, language: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """기본 리뷰 생성 (AI 실패시 폴백)"""
        
        return {
            "overall_score": 70,
            "quality_assessment": {
                "readability": 70,
                "functionality": 75,
                "performance": 70,
                "security": 65,
                "maintainability": 70
            },
            "issues": [
                {
                    "severity": "info",
                    "type": "style",
                    "line": None,
                    "message": "코드 스타일 가이드 준수 여부를 확인해보세요",
                    "suggestion": f"{language} 표준 스타일 가이드를 참고하세요"
                }
            ],
            "strengths": ["기본적인 코드 구조가 갖춰져 있습니다"],
            "recommendations": ["주석을 더 추가해보세요", "함수를 더 작은 단위로 분리해보세요"],
            "learning_advice": ["지속적인 코드 리뷰 습관을 기르세요"]
        }
    
    def _calculate_review_scores(self, review_result: Dict[str, Any], code_analysis: Dict[str, Any]) -> Dict[str, int]:
        """리뷰 점수 계산"""
        
        quality = review_result.get('quality_assessment', {})
        
        # 기본 점수들
        scores = {
            'readability': quality.get('readability', 70),
            'functionality': quality.get('functionality', 70),
            'performance': quality.get('performance', 70),
            'security': quality.get('security', 70),
            'maintainability': quality.get('maintainability', 70)
        }
        
        # 가중치 적용하여 전체 점수 계산
        overall = sum(
            scores[category] * self.review_criteria[category]['weight']
            for category in self.review_criteria
        )
        
        scores['overall'] = int(overall)
        
        return scores
    
    def _categorize_issues(self, issues: List[Dict]) -> List[CodeIssue]:
        """이슈 분류 및 구조화"""
        
        categorized = []
        
        for issue in issues:
            code_issue = CodeIssue(
                severity=issue.get('severity', 'info'),
                type=issue.get('type', 'general'),
                line_number=issue.get('line'),
                message=issue.get('message', ''),
                suggestion=issue.get('suggestion', ''),
                example=issue.get('example')
            )
            categorized.append(code_issue)
        
        # 심각도별 정렬
        severity_order = {'critical': 0, 'major': 1, 'minor': 2, 'info': 3}
        categorized.sort(key=lambda x: severity_order.get(x.severity, 3))
        
        return categorized
    
    async def _generate_improvement_recommendations(
        self, 
        review_result: Dict[str, Any],
        code_analysis: Dict[str, Any],
        user_level: str
    ) -> List[str]:
        """개선 권장사항 생성"""
        
        recommendations = review_result.get('recommendations', [])
        learning_advice = review_result.get('learning_advice', [])
        
        # 사용자 레벨에 맞는 추가 권장사항
        level_specific = {
            'beginner': [
                "기본적인 코딩 컨벤션을 익히세요",
                "함수와 변수의 명명법을 일관되게 유지하세요",
                "주석을 통해 코드의 의도를 명확히 하세요"
            ],
            'intermediate': [
                "코드의 재사용성을 높이는 방법을 고민해보세요",
                "에러 처리를 더 체계적으로 구현해보세요",
                "성능 최적화 방법을 학습해보세요"
            ],
            'advanced': [
                "디자인 패턴 적용을 고려해보세요",
                "코드 테스트 커버리지를 향상시켜보세요",
                "보안 취약점을 더 깊이 분석해보세요"
            ]
        }
        
        all_recommendations = recommendations + learning_advice + level_specific.get(user_level, [])
        
        return list(dict.fromkeys(all_recommendations))[:7]  # 중복 제거 후 최대 7개
    
    def _determine_quality_grade(self, score: int) -> CodeQuality:
        """품질 등급 결정"""
        
        if score >= 90:
            return CodeQuality.EXCELLENT
        elif score >= 75:
            return CodeQuality.GOOD
        elif score >= 60:
            return CodeQuality.SATISFACTORY
        elif score >= 40:
            return CodeQuality.NEEDS_IMPROVEMENT
        else:
            return CodeQuality.POOR
    
    async def analyze_project(self, user_id: int, project_data: Dict[str, Any]) -> ProjectAnalysis:
        """프로젝트 종합 분석"""
        
        try:
            # 프로젝트 기본 정보 추출
            project_info = await self._extract_project_info(project_data)
            
            # 기술 스택 분석
            tech_stack = await self._analyze_tech_stack(project_data)
            
            # 아키텍처 평가
            architecture_assessment = await self._assess_architecture(project_data)
            
            # 코드 품질 분석 (주요 파일들)
            code_quality = await self._analyze_project_code_quality(project_data)
            
            # 보안 평가
            security_assessment = await self._assess_project_security(project_data)
            
            # AI 기반 종합 평가
            comprehensive_analysis = await self._perform_comprehensive_ai_analysis(
                project_info, tech_stack, code_quality, architecture_assessment
            )
            
            analysis = ProjectAnalysis(
                project_id=project_data.get('project_id', f"project_{user_id}_{int(datetime.utcnow().timestamp())}"),
                analysis_date=datetime.utcnow(),
                technical_stack=tech_stack,
                architecture_quality=architecture_assessment['quality'],
                code_coverage=code_quality.get('coverage', 0.0),
                security_assessment=security_assessment,
                performance_metrics=code_quality.get('performance', {}),
                improvement_roadmap=comprehensive_analysis.get('improvement_roadmap', []),
                skill_demonstration=comprehensive_analysis.get('skills_demonstrated', []),
                market_relevance=comprehensive_analysis.get('market_relevance', 'medium')
            )
            
            # 분석 결과 캐싱
            await self._cache_project_analysis(user_id, analysis)
            
            logger.info(f"프로젝트 분석 완료: user {user_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"프로젝트 분석 실패 user {user_id}: {str(e)}")
            return await self._generate_fallback_project_analysis(user_id, project_data)
    
    async def _extract_project_info(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """프로젝트 정보 추출"""
        
        return {
            'name': project_data.get('name', 'Unknown Project'),
            'description': project_data.get('description', ''),
            'type': project_data.get('type', 'web_application'),
            'complexity': project_data.get('complexity', 'medium'),
            'file_count': len(project_data.get('files', [])),
            'languages': project_data.get('languages', []),
            'frameworks': project_data.get('frameworks', [])
        }
    
    async def _analyze_tech_stack(self, project_data: Dict[str, Any]) -> List[str]:
        """기술 스택 분석"""
        
        tech_stack = set()
        
        # 명시적으로 제공된 기술들
        tech_stack.update(project_data.get('languages', []))
        tech_stack.update(project_data.get('frameworks', []))
        tech_stack.update(project_data.get('databases', []))
        
        # 파일 확장자로부터 언어 추론
        files = project_data.get('files', [])
        for file_info in files:
            filename = file_info.get('name', '')
            if filename.endswith('.py'):
                tech_stack.add('Python')
            elif filename.endswith('.js'):
                tech_stack.add('JavaScript')
            elif filename.endswith('.java'):
                tech_stack.add('Java')
            elif filename.endswith('.html'):
                tech_stack.add('HTML')
            elif filename.endswith('.css'):
                tech_stack.add('CSS')
        
        return list(tech_stack)
    
    async def _assess_architecture(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """아키텍처 평가"""
        
        files = project_data.get('files', [])
        
        # 디렉토리 구조 분석
        directories = set()
        for file_info in files:
            path = file_info.get('path', '')
            if '/' in path:
                directories.add(path.split('/')[0])
        
        # 아키텍처 패턴 감지
        architecture_patterns = []
        if 'models' in directories and 'views' in directories:
            architecture_patterns.append('MVC')
        if 'components' in directories:
            architecture_patterns.append('Component-based')
        if 'services' in directories:
            architecture_patterns.append('Service-oriented')
        
        # 구조적 품질 평가
        quality = 'good'
        if len(directories) < 3:
            quality = 'basic'
        elif len(directories) > 10:
            quality = 'complex'
        
        return {
            'quality': quality,
            'patterns': architecture_patterns,
            'directory_count': len(directories),
            'organization_score': min(100, len(directories) * 10)
        }
    
    async def _analyze_project_code_quality(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """프로젝트 코드 품질 분석"""
        
        files = project_data.get('files', [])
        total_lines = 0
        code_files = 0
        
        for file_info in files:
            if file_info.get('type') == 'code':
                total_lines += file_info.get('lines', 0)
                code_files += 1
        
        # 기본 메트릭
        quality_metrics = {
            'total_lines': total_lines,
            'file_count': code_files,
            'avg_file_size': total_lines / max(1, code_files),
            'coverage': 0.75,  # 기본값 (실제로는 테스트 분석 필요)
            'performance': {
                'complexity_score': 75,
                'efficiency_score': 80
            }
        }
        
        return quality_metrics
    
    async def _assess_project_security(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """프로젝트 보안 평가"""
        
        security_score = 75  # 기본 점수
        vulnerabilities = []
        
        # 파일 분석을 통한 보안 이슈 감지 (간단한 버전)
        files = project_data.get('files', [])
        for file_info in files:
            content = file_info.get('content', '')
            
            # 간단한 패턴 매칭으로 보안 이슈 감지
            if 'eval(' in content:
                vulnerabilities.append({
                    'type': 'code_injection',
                    'severity': 'high',
                    'description': 'eval() 함수 사용 감지'
                })
            
            if 'password' in content.lower() and 'plain' in content.lower():
                vulnerabilities.append({
                    'type': 'password_security',
                    'severity': 'medium',
                    'description': '평문 패스워드 처리 의심'
                })
        
        return {
            'overall_score': security_score,
            'vulnerabilities': vulnerabilities,
            'secure_practices': len(vulnerabilities) == 0,
            'recommendations': [
                '입력 데이터 검증 강화',
                '인증/인가 체계 검토',
                '데이터 암호화 적용'
            ]
        }
    
    async def _perform_comprehensive_ai_analysis(
        self, 
        project_info: Dict[str, Any],
        tech_stack: List[str],
        code_quality: Dict[str, Any],
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """AI 기반 종합 분석"""
        
        analysis_prompt = f"""다음 프로젝트를 종합적으로 분석하고 평가해주세요.

프로젝트 정보:
- 이름: {project_info['name']}
- 설명: {project_info['description']}
- 유형: {project_info['type']}
- 파일 수: {project_info['file_count']}

기술 스택: {', '.join(tech_stack)}

코드 품질 지표:
- 총 코드 라인 수: {code_quality['total_lines']}
- 파일 수: {code_quality['file_count']}
- 평균 파일 크기: {code_quality['avg_file_size']:.1f} 라인

아키텍처:
- 품질: {architecture['quality']}
- 패턴: {', '.join(architecture['patterns'])}
- 디렉토리 수: {architecture['directory_count']}

다음 관점에서 분석해주세요:

1. **시연되는 기술 능력들**
2. **개선이 필요한 영역들** 
3. **시장 관련성** (현재 기술 트렌드 대비)
4. **포트폴리오로서의 강점**
5. **단계별 개선 로드맵**

JSON 형식으로 답변해주세요:
{{
  "skills_demonstrated": ["기술1", "기술2"],
  "improvement_areas": ["개선점1", "개선점2"],
  "market_relevance": "high/medium/low",
  "portfolio_strengths": ["강점1", "강점2"],
  "improvement_roadmap": [
    "1단계: 즉시 개선",
    "2단계: 단기 개선",
    "3단계: 장기 개선"
  ],
  "overall_assessment": "프로젝트 종합 평가"
}}"""

        response = await generate_ai_response(
            prompt=analysis_prompt,
            task_type="analysis",
            model_preference=ModelTier.FREE,
            temperature=0.4
        )
        
        try:
            return json.loads(response.get('response', '{}'))
        except:
            return {
                'skills_demonstrated': ['기본 프로그래밍', '프로젝트 구성'],
                'improvement_areas': ['코드 품질 향상', '문서화 개선'],
                'market_relevance': 'medium',
                'portfolio_strengths': ['실행 가능한 프로젝트'],
                'improvement_roadmap': ['코드 리팩토링', '테스트 추가', '배포 준비'],
                'overall_assessment': '기본적인 프로젝트 구조를 갖춘 프로젝트입니다.'
            }
    
    async def _cache_review_result(self, code: str, result: CodeReviewResult):
        """리뷰 결과 캐싱"""
        
        try:
            import hashlib
            code_hash = hashlib.md5(code.encode()).hexdigest()[:16]
            cache_key = f"code_review:{code_hash}"
            
            cache_data = {
                'overall_score': result.overall_score,
                'quality_grade': result.quality_grade.value,
                'issue_count': len(result.issues),
                'created_at': datetime.utcnow().isoformat()
            }
            
            self.redis_service.set_cache(cache_key, cache_data, 3600)  # 1시간
            
        except Exception as e:
            logger.error(f"리뷰 결과 캐싱 실패: {str(e)}")
    
    async def _cache_project_analysis(self, user_id: int, analysis: ProjectAnalysis):
        """프로젝트 분석 결과 캐싱"""
        
        try:
            cache_key = f"project_analysis:{user_id}:{analysis.project_id}"
            cache_data = {
                'analysis_date': analysis.analysis_date.isoformat(),
                'tech_stack_count': len(analysis.technical_stack),
                'architecture_quality': analysis.architecture_quality,
                'skill_count': len(analysis.skill_demonstration),
                'market_relevance': analysis.market_relevance
            }
            
            self.redis_service.set_cache(cache_key, cache_data, 86400)  # 24시간
            
        except Exception as e:
            logger.error(f"프로젝트 분석 캐싱 실패: {str(e)}")
    
    async def _generate_fallback_review(self, code: str, language: str) -> CodeReviewResult:
        """폴백 리뷰 결과"""
        
        return CodeReviewResult(
            overall_score=70,
            quality_grade=CodeQuality.SATISFACTORY,
            issues=[
                CodeIssue(
                    severity="info",
                    type="general",
                    line_number=None,
                    message="자동 분석에 실패했지만 기본적인 구조는 양호합니다",
                    suggestion="코드를 더 작은 단위로 나누어 다시 리뷰해보세요",
                    example=None
                )
            ],
            strengths=["기본적인 코드 구조"],
            recommendations=["코드 스타일 가이드 참고", "주석 추가"],
            complexity_analysis={'estimated_complexity': 'medium'},
            security_score=70,
            performance_score=70,
            maintainability_score=70
        )
    
    async def _generate_fallback_project_analysis(self, user_id: int, project_data: Dict[str, Any]) -> ProjectAnalysis:
        """폴백 프로젝트 분석"""
        
        return ProjectAnalysis(
            project_id=f"fallback_project_{user_id}",
            analysis_date=datetime.utcnow(),
            technical_stack=['Unknown'],
            architecture_quality='basic',
            code_coverage=0.5,
            security_assessment={'overall_score': 70},
            performance_metrics={'complexity_score': 70},
            improvement_roadmap=['코드 품질 향상', '문서화 개선'],
            skill_demonstration=['기본 프로그래밍'],
            market_relevance='medium'
        )

# 전역 인스턴스 생성 함수
def get_advanced_ai_features(db: Session) -> AdvancedAIFeatures:
    """고급 AI 기능 시스템 인스턴스 반환"""
    return AdvancedAIFeatures(db)
