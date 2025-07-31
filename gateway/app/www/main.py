from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import asyncio
import logging
from typing import Dict, List, Optional
import json
import time
from contextlib import asynccontextmanager
from domain.discovery.controller.discovery_controller import DiscoveryController

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 서비스 디스커버리 설정
SERVICE_REGISTRY = {
    "user-service": {
        "url": "http://localhost:8001",
        "health_check": "/health",
        "status": "healthy",
        "last_check": time.time()
    },
    "order-service": {
        "url": "http://localhost:8002", 
        "health_check": "/health",
        "status": "healthy",
        "last_check": time.time()
    },
    "product-service": {
        "url": "http://localhost:8003",
        "health_check": "/health", 
        "status": "healthy",
        "last_check": time.time()
    }
}

# 라우팅 규칙
ROUTE_MAPPING = {
    "/api/users": "user-service",
    "/api/orders": "order-service", 
    "/api/products": "product-service"
}

class ServiceDiscovery:
    """서비스 디스커버리 클래스"""
    
    def __init__(self):
        self.service_registry = SERVICE_REGISTRY.copy()
    
    async def health_check_service(self, service_name: str) -> bool:
        """서비스 헬스 체크"""
        if service_name not in self.service_registry:
            return False
            
        service_info = self.service_registry[service_name]
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_info['url']}{service_info['health_check']}")
                if response.status_code == 200:
                    self.service_registry[service_name]["status"] = "healthy"
                    self.service_registry[service_name]["last_check"] = time.time()
                    return True
                else:
                    self.service_registry[service_name]["status"] = "unhealthy"
                    return False
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            self.service_registry[service_name]["status"] = "unhealthy"
            return False
    
    async def get_healthy_service(self, service_name: str) -> Optional[Dict]:
        """헬시한 서비스 정보 반환"""
        if service_name not in self.service_registry:
            return None
            
        # 헬스 체크 수행
        is_healthy = await self.health_check_service(service_name)
        if is_healthy:
            return self.service_registry[service_name]
        return None
    
    def get_service_by_path(self, path: str) -> Optional[str]:
        """경로에 따른 서비스 매핑"""
        for route_path, service_name in ROUTE_MAPPING.items():
            if path.startswith(route_path):
                return service_name
        return None

class ProxyService:
    """프록시 서비스 클래스"""
    
    def __init__(self):
        self.service_discovery = ServiceDiscovery()
        self.discovery_controller = None  # 나중에 설정
    
    def set_discovery_controller(self, discovery_controller):
        """서비스 디스커버리 컨트롤러 설정"""
        self.discovery_controller = discovery_controller
    
    async def forward_request(self, request: Request, path: str) -> JSONResponse:
        """요청을 적절한 서비스로 전달"""
        # 서비스 매핑 확인
        service_name = self.service_discovery.get_service_by_path(path)
        if not service_name:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # 서비스 디스커버리에서 서비스 정보 가져오기
        service_info = None
        if self.discovery_controller:
            service = self.discovery_controller.service_registry.get_service(service_name)
            if service:
                service_info = {
                    "url": service.url,
                    "health_check": service.health_check,
                    "status": service.status
                }
        
        # 기존 방식으로 폴백
        if not service_info:
            service_info = await self.service_discovery.get_healthy_service(service_name)
        
        if not service_info:
            raise HTTPException(status_code=503, detail=f"Service {service_name} is unavailable")
        
        # 요청 전달
        try:
            target_url = f"{service_info['url']}{path}"
            method = request.method
            headers = dict(request.headers)
            
            # 호스트 헤더 제거 (타겟 서비스에서 처리)
            headers.pop("host", None)
            
            # 요청 본문 읽기
            body = await request.body()
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    params=request.query_params
                )
                
                # 응답 반환
                return JSONResponse(
                    content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
        except httpx.RequestError as e:
            logger.error(f"Request failed to {service_name}: {e}")
            raise HTTPException(status_code=502, detail="Bad Gateway")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

# 전역 변수로 프록시 서비스 인스턴스 생성
proxy_service = ProxyService()

# 서비스 디스커버리 컨트롤러 생성
discovery_controller = DiscoveryController()

# 프록시 서비스에 디스커버리 컨트롤러 설정
proxy_service.set_discovery_controller(discovery_controller)

# 기본 서비스 등록
def register_default_services():
    """기본 서비스들을 등록"""
    from domain.discovery.model.service_registry import ServiceInfo
    
    default_services = {
        "user-service": ServiceInfo(
            url="http://localhost:8001",
            health_check="/health",
            status="healthy"
        ),
        "order-service": ServiceInfo(
            url="http://localhost:8002",
            health_check="/health",
            status="healthy"
        ),
        "product-service": ServiceInfo(
            url="http://localhost:8003",
            health_check="/health",
            status="healthy"
        )
    }
    
    for service_name, service_info in default_services.items():
        discovery_controller.service_registry.register_service(service_name, service_info)
        logger.info(f"Registered default service: {service_name}")

# 기본 서비스 등록
register_default_services()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("Gateway starting up...")
    yield
    logger.info("Gateway shutting down...")

# FastAPI 앱 생성
app = FastAPI(
    title="MSA Gateway",
    description="Microservice Architecture Gateway with Service Discovery",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 디스커버리 라우터 추가
app.include_router(discovery_controller.get_router())

@app.get("/health")
async def health_check():
    """게이트웨이 헬스 체크"""
    return {"status": "healthy", "service": "gateway"}

@app.get("/services/status")
async def get_services_status():
    """등록된 서비스들의 상태 확인"""
    services_status = {}
    for service_name, service_info in proxy_service.service_discovery.service_registry.items():
        is_healthy = await proxy_service.service_discovery.health_check_service(service_name)
        services_status[service_name] = {
            "url": service_info["url"],
            "status": "healthy" if is_healthy else "unhealthy",
            "last_check": service_info["last_check"]
        }
    return services_status

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_route(request: Request, path: str):
    """모든 요청을 프록시로 처리"""
    return await proxy_service.forward_request(request, f"/{path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
