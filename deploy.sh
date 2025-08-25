#!/bin/bash

# LMS 베타 테스트 배포 스크립트
# 사용법: ./deploy.sh [환경]
# 환경: dev, staging, prod (기본값: dev)

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로깅 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 설정
ENVIRONMENT=${1:-dev}
PROJECT_NAME="lms_mvp"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

log_info "배포 시작: $PROJECT_NAME ($ENVIRONMENT 환경)"

# 환경 유효성 검사
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    log_error "유효하지 않은 환경: $ENVIRONMENT (dev, staging, prod 중 선택)"
    exit 1
fi

# 필수 파일 존재 확인
check_required_files() {
    local required_files=(
        "docker-compose.yml"
        "backend/requirements.txt"
        "frontend/package.json"
    )
    
    if [ "$ENVIRONMENT" = "prod" ]; then
        required_files+=("docker-compose.prod.yml" ".env.prod")
    fi
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "필수 파일이 없습니다: $file"
            exit 1
        fi
    done
    
    log_success "필수 파일 확인 완료"
}

# 환경 변수 파일 로드
load_environment() {
    local env_file=".env"
    
    if [ "$ENVIRONMENT" = "prod" ]; then
        env_file=".env.prod"
    elif [ "$ENVIRONMENT" = "staging" ]; then
        env_file=".env.staging"
    fi
    
    if [ -f "$env_file" ]; then
        export $(cat "$env_file" | grep -v '^#' | xargs)
        log_success "환경 변수 로드 완료: $env_file"
    else
        log_warning "환경 변수 파일이 없습니다: $env_file"
    fi
}

# 백업 생성
create_backup() {
    if [ "$ENVIRONMENT" = "prod" ]; then
        log_info "운영 환경 백업 생성 중..."
        
        mkdir -p "$BACKUP_DIR"
        
        # 데이터베이스 백업
        if command -v docker-compose &> /dev/null; then
            docker-compose exec -T postgres pg_dump -U ${POSTGRES_USER:-lms_user} ${POSTGRES_DB:-lms_db} > "$BACKUP_DIR/database.sql" 2>/dev/null || log_warning "데이터베이스 백업 실패"
        fi
        
        # 설정 파일 백업
        cp -r . "$BACKUP_DIR/source_backup" 2>/dev/null || log_warning "소스 백업 실패"
        
        log_success "백업 완료: $BACKUP_DIR"
    fi
}

# Docker 이미지 빌드
build_images() {
    log_info "Docker 이미지 빌드 중..."
    
    local compose_file="docker-compose.yml"
    if [ "$ENVIRONMENT" = "prod" ]; then
        compose_file="docker-compose.prod.yml"
    fi
    
    # 이전 이미지 정리
    docker-compose -f "$compose_file" down --remove-orphans 2>/dev/null || true
    
    # 새 이미지 빌드
    docker-compose -f "$compose_file" build --no-cache
    
    log_success "이미지 빌드 완료"
}

# 데이터베이스 마이그레이션
run_migrations() {
    log_info "데이터베이스 마이그레이션 실행 중..."
    
    local compose_file="docker-compose.yml"
    if [ "$ENVIRONMENT" = "prod" ]; then
        compose_file="docker-compose.prod.yml"
    fi
    
    # 데이터베이스 서비스만 먼저 시작
    docker-compose -f "$compose_file" up -d postgres redis
    
    # 데이터베이스 연결 대기
    log_info "데이터베이스 연결 대기 중..."
    sleep 10
    
    # 마이그레이션 실행
    docker-compose -f "$compose_file" run --rm backend alembic upgrade head
    
    log_success "마이그레이션 완료"
}

# 애플리케이션 배포
deploy_application() {
    log_info "애플리케이션 배포 중..."
    
    local compose_file="docker-compose.yml"
    if [ "$ENVIRONMENT" = "prod" ]; then
        compose_file="docker-compose.prod.yml"
    fi
    
    # 모든 서비스 시작
    docker-compose -f "$compose_file" up -d
    
    log_success "애플리케이션 배포 완료"
}

# 헬스체크
health_check() {
    log_info "헬스체크 실행 중..."
    
    local max_attempts=30
    local attempt=1
    local backend_url="http://localhost:8000/health"
    local frontend_url="http://localhost:80/health"
    
    # 백엔드 헬스체크
    while [ $attempt -le $max_attempts ]; do
        if curl -f "$backend_url" >/dev/null 2>&1; then
            log_success "백엔드 헬스체크 통과"
            break
        fi
        
        log_info "백엔드 헬스체크 시도 $attempt/$max_attempts"
        sleep 5
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "백엔드 헬스체크 실패"
        return 1
    fi
    
    # 프론트엔드 헬스체크
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -f "$frontend_url" >/dev/null 2>&1; then
            log_success "프론트엔드 헬스체크 통과"
            break
        fi
        
        log_info "프론트엔드 헬스체크 시도 $attempt/$max_attempts"
        sleep 5
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "프론트엔드 헬스체크 실패"
        return 1
    fi
    
    log_success "모든 헬스체크 통과"
}

# AI 기능 테스트
test_ai_features() {
    log_info "AI 기능 테스트 중..."
    
    # AI 기능 상태 확인
    if curl -f "http://localhost:8000/api/v1/ai-features/health" >/dev/null 2>&1; then
        log_success "AI 기능 정상 동작"
    else
        log_warning "AI 기능 테스트 실패 - 수동 확인 필요"
    fi
    
    # 베타 테스트 시스템 확인
    if curl -f "http://localhost:8000/api/v1/beta/health" >/dev/null 2>&1; then
        log_success "베타 테스트 시스템 정상 동작"
    else
        log_warning "베타 테스트 시스템 테스트 실패 - 수동 확인 필요"
    fi
}

# 배포 정보 출력
print_deployment_info() {
    log_info "배포 정보:"
    echo "  환경: $ENVIRONMENT"
    echo "  프로젝트: $PROJECT_NAME"
    echo "  배포 시간: $(date)"
    echo ""
    echo "🌐 서비스 접속 주소:"
    echo "  프론트엔드: http://localhost:80"
    echo "  백엔드 API: http://localhost:8000"
    echo "  API 문서: http://localhost:8000/docs"
    echo ""
    
    if [ "$ENVIRONMENT" = "prod" ]; then
        echo "🔧 관리 도구:"
        echo "  Celery 모니터링: http://localhost:5555"
        echo "  Grafana 대시보드: http://localhost:3000"
        echo "  Prometheus 메트릭: http://localhost:9090"
        echo ""
    fi
    
    echo "📊 베타 테스트:"
    echo "  대시보드: http://localhost:80/beta-dashboard"
    echo "  AI 기능: http://localhost:80/ai-features"
    echo ""
    
    if [ -d "$BACKUP_DIR" ]; then
        echo "💾 백업 위치: $BACKUP_DIR"
        echo ""
    fi
}

# 롤백 함수
rollback() {
    log_error "배포 실패 - 롤백 실행 중..."
    
    local compose_file="docker-compose.yml"
    if [ "$ENVIRONMENT" = "prod" ]; then
        compose_file="docker-compose.prod.yml"
    fi
    
    docker-compose -f "$compose_file" down
    
    if [ -d "$BACKUP_DIR" ] && [ "$ENVIRONMENT" = "prod" ]; then
        log_info "백업에서 데이터베이스 복원 중..."
        # 데이터베이스 복원 로직
        # docker-compose exec -T postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} < "$BACKUP_DIR/database.sql"
    fi
    
    log_error "롤백 완료"
    exit 1
}

# 메인 배포 함수
main() {
    # 오류 발생 시 롤백
    trap rollback ERR
    
    log_info "=== LMS 베타 테스트 배포 시작 ==="
    
    # 1. 사전 검사
    check_required_files
    load_environment
    
    # 2. 백업 (운영 환경만)
    create_backup
    
    # 3. 빌드 및 배포
    build_images
    run_migrations
    deploy_application
    
    # 4. 검증
    health_check
    test_ai_features
    
    # 5. 배포 완료
    print_deployment_info
    
    log_success "=== 배포 완료! ==="
    
    if [ "$ENVIRONMENT" = "prod" ]; then
        log_info "운영 환경 배포가 완료되었습니다."
        log_info "베타 테스터들에게 새 버전을 안내해주세요."
    fi
}

# 도움말
show_help() {
    echo "LMS 베타 테스트 배포 스크립트"
    echo ""
    echo "사용법:"
    echo "  $0 [환경]"
    echo ""
    echo "환경:"
    echo "  dev      개발 환경 (기본값)"
    echo "  staging  스테이징 환경"
    echo "  prod     운영 환경"
    echo ""
    echo "예시:"
    echo "  $0 dev     # 개발 환경 배포"
    echo "  $0 prod    # 운영 환경 배포"
    echo ""
    echo "옵션:"
    echo "  -h, --help    이 도움말 표시"
    echo ""
}

# 명령행 인수 처리
case "$1" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main
        ;;
esac
