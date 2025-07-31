from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import logging
import os
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
import asyncio

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="MSA Gateway",
    description="Microservice Architecture Gateway with Service Discovery",
    version="1.0.0"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 정보 모델
class ServiceInfo(BaseModel):
    url: str
    health_check: str
    status: str = "unknown"
    last_check: Optional[datetime] = None
    metadata: Dict = {}

# 서비스 레지스트리
class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
    
    def register(self, name: str, url: str, health_check: str = "/health", metadata: Dict = {}):
        self.services[name] = ServiceInfo(
            url=url,
            health_check=health_check,
            metadata=metadata
        )
        logger.info(f"서비스 등록: {name} -> {url}")
    
    def unregister(self, name: str):
        if name in self.services:
            del self.services[name]
            logger.info(f"서비스 등록 해제: {name}")
    
    def get_service(self, name: str) -> Optional[ServiceInfo]:
        return self.services.get(name)
    
    def get_all_services(self) -> Dict[str, ServiceInfo]:
        return self.services
    
    def update_status(self, name: str, status: str):
        if name in self.services:
            self.services[name].status = status
            self.services[name].last_check = datetime.now()

# 서비스 디스커버리
class ServiceDiscovery:
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
    
    async def health_check(self, service_name: str) -> bool:
        service = self.registry.get_service(service_name)
        if not service:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service.url}{service.health_check}")
                is_healthy = response.status_code == 200
                self.registry.update_status(service_name, "healthy" if is_healthy else "unhealthy")
                return is_healthy
        except Exception as e:
            logger.error(f"헬스체크 실패 {service_name}: {e}")
            self.registry.update_status(service_name, "unhealthy")
            return False
    
    async def health_check_all(self) -> Dict[str, bool]:
        results = {}
        for service_name in self.registry.get_all_services().keys():
            results[service_name] = await self.health_check(service_name)
        return results
    
    def get_service_by_path(self, path: str) -> Optional[ServiceInfo]:
        # 경로 기반 서비스 매핑
        path_mapping = {
            "/users": "user-service",
            "/orders": "order-service", 
            "/products": "product-service",
            "/api/users": "user-service",
            "/api/orders": "order-service",
            "/api/products": "product-service"
        }
        
        for route, service_name in path_mapping.items():
            if path.startswith(route):
                return self.registry.get_service(service_name)
        return None

# 프록시 서비스
class ProxyService:
    def __init__(self, discovery: ServiceDiscovery):
        self.discovery = discovery
    
    async def forward_request(self, request: Request, path: str) -> JSONResponse:
        # 서비스 찾기
        service = self.discovery.get_service_by_path(path)
        if not service:
            raise HTTPException(status_code=404, detail="서비스를 찾을 수 없습니다")
        
        # 헬스체크
        if not await self.discovery.health_check(service.url.split('/')[-1]):
            raise HTTPException(status_code=503, detail="서비스가 사용 불가능합니다")
        
        # 요청 전달
        try:
            # 요청 바디 읽기
            body = await request.body()
            
            # 헤더 준비
            headers = dict(request.headers)
            headers.pop("host", None)  # 호스트 헤더 제거
            
            # 프록시 요청
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=request.method,
                    url=f"{service.url}{path}",
                    headers=headers,
                    content=body,
                    params=request.query_params
                )
                
                return JSONResponse(
                    content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
        except Exception as e:
            logger.error(f"프록시 요청 실패: {e}")
            raise HTTPException(status_code=500, detail="내부 서버 오류")

# 전역 인스턴스 생성
service_registry = ServiceRegistry()
service_discovery = ServiceDiscovery(service_registry)
proxy_service = ProxyService(service_discovery)

# 기본 서비스 등록
def register_default_services():
    services = {
        "user-service": {
            "url": os.getenv("USER_SERVICE_URL", "http://user-service:8001"),
            "health_check": "/health"
        },
        "order-service": {
            "url": os.getenv("ORDER_SERVICE_URL", "http://order-service:8002"),
            "health_check": "/health"
        },
        "product-service": {
            "url": os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8003"),
            "health_check": "/health"
        }
    }
    
    for name, config in services.items():
        service_registry.register(name, config["url"], config["health_check"])

# 앱 시작/종료 이벤트
@app.on_event("startup")
async def startup_event():
    logger.info("MSA Gateway 시작 중...")
    register_default_services()
    logger.info("기본 서비스 등록 완료")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("MSA Gateway 종료 중...")

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "msa-gateway"
    }

# 서비스 상태 확인
@app.get("/services/status")
async def get_services_status():
    services = service_registry.get_all_services()
    status = {}
    
    for name, service in services.items():
        is_healthy = await service_discovery.health_check(name)
        status[name] = {
            "url": service.url,
            "status": service.status,
            "healthy": is_healthy,
            "last_check": service.last_check.isoformat() if service.last_check else None
        }
    
    return status

# 서비스 등록 API
@app.post("/services")
async def register_service(name: str, url: str, health_check: str = "/health"):
    service_registry.register(name, url, health_check)
    return {"message": f"서비스 {name} 등록 완료"}

# 서비스 등록 해제 API
@app.delete("/services/{service_name}")
async def unregister_service(service_name: str):
    service_registry.unregister(service_name)
    return {"message": f"서비스 {service_name} 등록 해제 완료"}

# 모든 서비스 헬스체크
@app.get("/health/all")
async def health_check_all():
    results = await service_discovery.health_check_all()
    return {
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

# 프록시 라우트 - 모든 경로를 처리
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_route(request: Request, path: str):
    return await proxy_service.forward_request(request, f"/{path}")

# 루트 경로
@app.get("/")
async def root():
    return {
        "message": "MSA Gateway",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "services_status": "/services/status",
            "health_all": "/health/all",
            "register_service": "POST /services",
            "unregister_service": "DELETE /services/{service_name}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
