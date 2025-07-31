# MSA Gateway

FastAPI 기반의 마이크로서비스 아키텍처 게이트웨이입니다. 프록시 패턴을 사용하여 서비스 디스커버리 기능을 제공합니다.

## 주요 기능

- **프록시 패턴**: 모든 요청을 적절한 마이크로서비스로 전달
- **서비스 디스커버리**: 동적 서비스 등록 및 헬스 체크
- **로드 밸런싱**: 헬시한 서비스로만 요청 전달
- **API 게이트웨이**: 통합된 API 엔드포인트 제공

## 설치 및 실행

### 1. Docker Compose를 사용한 실행 (권장)

```bash
# 게이트웨이 디렉토리로 이동
cd gateway

# 실행 권한 부여
chmod +x docker-compose.sh

# 모든 서비스 시작
./docker-compose.sh start

# 서비스 상태 확인
./docker-compose.sh status

# 헬스 체크
./docker-compose.sh health

# API 테스트
./docker-compose.sh test

# 로그 확인
./docker-compose.sh logs

# 서비스 중지
./docker-compose.sh stop
```

### 2. 수동 실행

#### 의존성 설치
```bash
cd gateway/app
pip install -r requirements.txt
```

#### 게이트웨이 실행
```bash
cd gateway/app
python -m uvicorn www.main:app --host 0.0.0.0 --port 8000 --reload
```

## API 엔드포인트

### 게이트웨이 헬스 체크
```
GET /health
```

### 서비스 디스커버리 API

#### 모든 서비스 조회
```
GET /discovery/services
```

#### 특정 서비스 정보 조회
```
GET /discovery/services/{service_name}
```

#### 서비스 등록
```
POST /discovery/services
Content-Type: application/json

{
    "service_name": "new-service",
    "service_info": {
        "url": "http://localhost:8004",
        "health_check": "/health",
        "status": "healthy"
    }
}
```

#### 서비스 등록 해제
```
DELETE /discovery/services/{service_name}
```

#### 서비스 헬스 체크
```
GET /discovery/services/{service_name}/health
```

#### 모든 서비스 헬스 체크
```
GET /discovery/health/all
```

### 프록시 라우팅

게이트웨이는 다음 경로 패턴에 따라 요청을 전달합니다:

- `/api/users/*` → `user-service` (포트 8001)
- `/api/orders/*` → `order-service` (포트 8002)
- `/api/products/*` → `product-service` (포트 8003)

## 서비스 구성

### 기본 등록된 서비스

1. **user-service**: `http://localhost:8001` (컨테이너: user-service)
2. **order-service**: `http://localhost:8002` (컨테이너: order-service)
3. **product-service**: `http://localhost:8003` (컨테이너: product-service)

### 새로운 서비스 추가

새로운 마이크로서비스를 추가하려면:

1. 서비스가 `/health` 엔드포인트를 제공하는지 확인
2. 서비스 디스커버리 API를 통해 등록
3. 라우팅 규칙에 추가 (필요시)

## 예제 사용법

### 1. Docker Compose로 전체 시스템 시작
```bash
cd gateway
./docker-compose.sh start
```

### 2. 서비스 상태 확인
```bash
# Docker Compose 상태
./docker-compose.sh status

# 게이트웨이를 통한 서비스 상태
curl http://localhost:8000/discovery/services
```

### 3. 헬스 체크
```bash
# 전체 시스템 헬스 체크
./docker-compose.sh health

# 특정 서비스 헬스 체크
curl http://localhost:8000/discovery/services/user-service/health
```

### 4. API 테스트
```bash
# 전체 API 테스트
./docker-compose.sh test

# 개별 API 테스트
curl http://localhost:8000/api/users/1
curl http://localhost:8000/api/orders/123
curl http://localhost:8000/api/products/456
```

### 5. 로그 확인
```bash
# 모든 서비스 로그
./docker-compose.sh logs

# 특정 서비스 로그
./docker-compose.sh logs gateway
./docker-compose.sh logs user-service
```

## Docker Compose 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client        │    │   Nginx         │    │   Gateway       │
│                 │    │   (Port 80)     │    │   (Port 8000)   │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │   App     │──┼───▶│   Load      │──┼───▶│   Proxy     │  │
│  └───────────┘  │    │   Balancer  │  │    │  └───────────┘  │
└─────────────────┘    └───────────────┘    └─────────────────┘
                                                      │
                                                      ▼
                       ┌─────────────────────────────────────────────┐
                       │              Microservices                  │
                       │                                             │
                       │  ┌───────────┐  ┌───────────┐  ┌───────────┐  │
                       │  │User       │  │Order      │  │Product    │  │
                       │  │Service    │  │Service    │  │Service    │  │
                       │  │(Port 8001)│  │(Port 8002)│  │(Port 8003)│  │
                       │  └───────────┘  └───────────┘  └───────────┘  │
                       └─────────────────────────────────────────────┘
                                                      │
                                                      ▼
                       ┌─────────────────────────────────────────────┐
                       │              Infrastructure                 │
                       │                                             │
                       │  ┌───────────┐                             │
                       │  │Redis      │                             │
                       │  │(Port 6379)│                             │
                       │  └───────────┘                             │
                       └─────────────────────────────────────────────┘
```

## 서비스 구성

### Docker Compose 서비스

1. **gateway** (포트 8000): MSA 게이트웨이
2. **user-service** (포트 8001): 사용자 관리 서비스
3. **order-service** (포트 8002): 주문 관리 서비스
4. **product-service** (포트 8003): 상품 관리 서비스
5. **redis** (포트 6379): 캐싱 및 세션 저장소
6. **nginx** (포트 80): 로드 밸런서 및 리버스 프록시

## 환경 변수

- `GATEWAY_HOST`: 게이트웨이 호스트 (기본값: 0.0.0.0)
- `GATEWAY_PORT`: 게이트웨이 포트 (기본값: 8000)

## 로깅

게이트웨이는 다음 정보를 로깅합니다:

- 서비스 등록/해제
- 헬스 체크 결과
- 프록시 요청/응답
- 오류 및 예외

## 개발

### 프로젝트 구조
```
gateway/
├── app/
│   ├── domain/
│   │   └── discovery/
│   │       ├── controller/
│   │       │   └── discovery_controller.py
│   │       └── model/
│   │           └── service_registry.py
│   └── www/
│       └── main.py
├── requirements.txt
└── README.md
```

### 테스트

```bash
# 게이트웨이 테스트
curl http://localhost:8000/health

# 서비스 디스커버리 테스트
curl http://localhost:8000/discovery/services

# 프록시 테스트
curl http://localhost:8000/api/users/1
``` 
``` 