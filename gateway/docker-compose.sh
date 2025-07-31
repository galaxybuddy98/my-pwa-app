#!/bin/bash

# MSA Gateway Docker Compose 실행 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
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

# Docker 설치 확인
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되지 않았습니다."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose가 설치되지 않았습니다."
        exit 1
    fi
    
    log_success "Docker 및 Docker Compose가 설치되어 있습니다."
}

# 컨테이너 상태 확인
check_containers() {
    log_info "컨테이너 상태 확인 중..."
    docker-compose ps
}

# 서비스 시작
start_services() {
    log_info "MSA 서비스들을 시작합니다..."
    docker-compose up -d
    
    log_info "서비스 시작 대기 중..."
    sleep 10
    
    check_containers
}

# 서비스 중지
stop_services() {
    log_info "MSA 서비스들을 중지합니다..."
    docker-compose down
    log_success "모든 서비스가 중지되었습니다."
}

# 서비스 재시작
restart_services() {
    log_info "MSA 서비스들을 재시작합니다..."
    docker-compose restart
    log_success "모든 서비스가 재시작되었습니다."
}

# 로그 확인
show_logs() {
    if [ -z "$1" ]; then
        log_info "모든 서비스의 로그를 확인합니다..."
        docker-compose logs -f
    else
        log_info "$1 서비스의 로그를 확인합니다..."
        docker-compose logs -f "$1"
    fi
}

# 헬스 체크
health_check() {
    log_info "서비스 헬스 체크를 수행합니다..."
    
    # 게이트웨이 헬스 체크
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "게이트웨이가 정상 작동 중입니다."
    else
        log_error "게이트웨이에 연결할 수 없습니다."
    fi
    
    # 사용자 서비스 헬스 체크
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        log_success "사용자 서비스가 정상 작동 중입니다."
    else
        log_error "사용자 서비스에 연결할 수 없습니다."
    fi
    
    # 주문 서비스 헬스 체크
    if curl -f http://localhost:8002/health > /dev/null 2>&1; then
        log_success "주문 서비스가 정상 작동 중입니다."
    else
        log_error "주문 서비스에 연결할 수 없습니다."
    fi
    
    # 상품 서비스 헬스 체크
    if curl -f http://localhost:8003/health > /dev/null 2>&1; then
        log_success "상품 서비스가 정상 작동 중입니다."
    else
        log_error "상품 서비스에 연결할 수 없습니다."
    fi
}

# 테스트 실행
run_tests() {
    log_info "API 테스트를 실행합니다..."
    
    # 게이트웨이 테스트
    echo "=== 게이트웨이 테스트 ==="
    curl -s http://localhost:8000/health | jq .
    
    # 사용자 서비스 테스트
    echo -e "\n=== 사용자 서비스 테스트 ==="
    curl -s http://localhost:8000/api/users | jq .
    
    # 주문 서비스 테스트
    echo -e "\n=== 주문 서비스 테스트 ==="
    curl -s http://localhost:8000/api/orders | jq .
    
    # 상품 서비스 테스트
    echo -e "\n=== 상품 서비스 테스트 ==="
    curl -s http://localhost:8000/api/products | jq .
    
    log_success "테스트가 완료되었습니다."
}

# 도움말
show_help() {
    echo "MSA Gateway Docker Compose 관리 스크립트"
    echo ""
    echo "사용법: $0 [명령어]"
    echo ""
    echo "명령어:"
    echo "  start     - 모든 서비스 시작"
    echo "  stop      - 모든 서비스 중지"
    echo "  restart   - 모든 서비스 재시작"
    echo "  status    - 서비스 상태 확인"
    echo "  logs      - 모든 서비스 로그 확인"
    echo "  logs [서비스명] - 특정 서비스 로그 확인"
    echo "  health    - 서비스 헬스 체크"
    echo "  test      - API 테스트 실행"
    echo "  help      - 이 도움말 표시"
    echo ""
    echo "예시:"
    echo "  $0 start"
    echo "  $0 logs gateway"
    echo "  $0 health"
}

# 메인 로직
main() {
    case "${1:-help}" in
        start)
            check_docker
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            check_containers
            ;;
        logs)
            show_logs "$2"
            ;;
        health)
            health_check
            ;;
        test)
            run_tests
            ;;
        help|*)
            show_help
            ;;
    esac
}

# 스크립트 실행
main "$@" 