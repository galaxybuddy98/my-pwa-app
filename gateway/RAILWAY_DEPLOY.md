# Railway 배포 가이드

## 🚀 Railway에서 MSA Gateway 배포하기

### 1. Railway 계정 설정

1. [Railway](https://railway.app)에 가입
2. GitHub 계정 연결
3. 새 프로젝트 생성

### 2. 프로젝트 구조

```
gateway/
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── www/main.py
├── services/
│   ├── user-service/
│   ├── order-service/
│   └── product-service/
├── railway.json
├── railway-docker-compose.yml
└── README.md
```

### 3. Railway CLI 설치 (선택사항)

```bash
npm install -g @railway/cli
railway login
```

### 4. 배포 방법

#### 방법 1: Railway 웹 대시보드 사용

1. Railway 대시보드에서 "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. GitHub 저장소 연결
4. 프로젝트 설정:
   - **Root Directory**: `gateway`
   - **Build Command**: `docker-compose -f railway-docker-compose.yml build`
   - **Start Command**: `docker-compose -f railway-docker-compose.yml up`

#### 방법 2: Railway CLI 사용

```bash
# 프로젝트 초기화
railway init

# 환경변수 설정
railway variables set GATEWAY_HOST=0.0.0.0
railway variables set GATEWAY_PORT=$PORT

# 배포
railway up
```

### 5. 환경변수 설정

Railway 대시보드에서 다음 환경변수들을 설정:

```
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=$PORT
RAILWAY_ENVIRONMENT=production
```

### 6. 서비스별 배포

각 마이크로서비스를 별도 서비스로 배포하려면:

#### 사용자 서비스
```bash
railway service create user-service
cd services/user-service
railway up
```

#### 주문 서비스
```bash
railway service create order-service
cd services/order-service
railway up
```

#### 상품 서비스
```bash
railway service create product-service
cd services/product-service
railway up
```

### 7. 배포 후 확인

배포가 완료되면 Railway에서 제공하는 URL로 접근:

```
# 게이트웨이 Swagger UI
https://your-app-name.railway.app/docs

# 헬스 체크
https://your-app-name.railway.app/health

# API 테스트
https://your-app-name.railway.app/api/users
https://your-app-name.railway.app/api/orders
https://your-app-name.railway.app/api/products
```

### 8. 로그 확인

```bash
# Railway CLI로 로그 확인
railway logs

# 특정 서비스 로그
railway logs --service gateway
```

### 9. 문제 해결

#### 포트 문제
Railway는 동적으로 포트를 할당하므로 `$PORT` 환경변수를 사용해야 합니다.

#### 빌드 실패
```bash
# 로컬에서 빌드 테스트
docker-compose -f railway-docker-compose.yml build

# 로그 확인
railway logs --service gateway
```

#### 서비스 연결 문제
각 서비스가 올바른 URL로 연결되는지 확인:

```python
# 게이트웨이에서 서비스 URL 업데이트
SERVICE_REGISTRY = {
    "user-service": {
        "url": "https://user-service.railway.app",
        "health_check": "/health",
        "status": "healthy"
    },
    "order-service": {
        "url": "https://order-service.railway.app",
        "health_check": "/health", 
        "status": "healthy"
    },
    "product-service": {
        "url": "https://product-service.railway.app",
        "health_check": "/health",
        "status": "healthy"
    }
}
```

### 10. 모니터링

Railway 대시보드에서:
- 서비스 상태 확인
- 로그 실시간 모니터링
- 리소스 사용량 확인
- 자동 스케일링 설정

### 11. 커스텀 도메인

Railway에서 커스텀 도메인을 설정할 수 있습니다:
1. Railway 대시보드 → Settings → Domains
2. 커스텀 도메인 추가
3. DNS 설정 업데이트

이제 Railway에서 MSA Gateway를 성공적으로 배포할 수 있습니다! 🎉 