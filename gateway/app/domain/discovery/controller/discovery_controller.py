from fastapi import APIRouter, HTTPException
from typing import Dict, List
import httpx
import asyncio
import logging
from ..model.service_registry import ServiceRegistry, ServiceInfo

logger = logging.getLogger(__name__)

class DiscoveryController:
    """서비스 디스커버리 컨트롤러"""
    
    def __init__(self):
        self.router = APIRouter(prefix="/discovery", tags=["discovery"])
        self.service_registry = ServiceRegistry(services={})
        self._setup_routes()
    
    def _setup_routes(self):
        """라우트 설정"""
        
        @self.router.get("/services")
        async def get_all_services():
            """등록된 모든 서비스 조회"""
            return {
                "services": self.service_registry.services,
                "total": len(self.service_registry.services)
            }
        
        @self.router.get("/services/{service_name}")
        async def get_service(service_name: str):
            """특정 서비스 정보 조회"""
            service = self.service_registry.get_service(service_name)
            if not service:
                raise HTTPException(status_code=404, detail="Service not found")
            return service
        
        @self.router.post("/services")
        async def register_service(service_name: str, service_info: ServiceInfo):
            """서비스 등록"""
            try:
                self.service_registry.register_service(service_name, service_info)
                logger.info(f"Service {service_name} registered successfully")
                return {"message": f"Service {service_name} registered successfully"}
            except Exception as e:
                logger.error(f"Failed to register service {service_name}: {e}")
                raise HTTPException(status_code=500, detail="Failed to register service")
        
        @self.router.delete("/services/{service_name}")
        async def unregister_service(service_name: str):
            """서비스 등록 해제"""
            try:
                self.service_registry.unregister_service(service_name)
                logger.info(f"Service {service_name} unregistered successfully")
                return {"message": f"Service {service_name} unregistered successfully"}
            except Exception as e:
                logger.error(f"Failed to unregister service {service_name}: {e}")
                raise HTTPException(status_code=500, detail="Failed to unregister service")
        
        @self.router.get("/services/{service_name}/health")
        async def check_service_health(service_name: str):
            """서비스 헬스 체크"""
            service = self.service_registry.get_service(service_name)
            if not service:
                raise HTTPException(status_code=404, detail="Service not found")
            
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{service.url}{service.health_check}")
                    is_healthy = response.status_code == 200
                    
                    # 상태 업데이트
                    status = "healthy" if is_healthy else "unhealthy"
                    self.service_registry.update_service_status(service_name, status)
                    
                    return {
                        "service_name": service_name,
                        "status": status,
                        "response_time": response.elapsed.total_seconds(),
                        "status_code": response.status_code
                    }
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                self.service_registry.update_service_status(service_name, "unhealthy")
                raise HTTPException(status_code=503, detail="Service health check failed")
        
        @self.router.get("/health/all")
        async def check_all_services_health():
            """모든 서비스 헬스 체크"""
            results = {}
            for service_name in self.service_registry.services.keys():
                try:
                    service = self.service_registry.get_service(service_name)
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        response = await client.get(f"{service.url}{service.health_check}")
                        is_healthy = response.status_code == 200
                        
                        status = "healthy" if is_healthy else "unhealthy"
                        self.service_registry.update_service_status(service_name, status)
                        
                        results[service_name] = {
                            "status": status,
                            "response_time": response.elapsed.total_seconds(),
                            "status_code": response.status_code
                        }
                except Exception as e:
                    logger.error(f"Health check failed for {service_name}: {e}")
                    self.service_registry.update_service_status(service_name, "unhealthy")
                    results[service_name] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
            
            return {
                "total_services": len(results),
                "healthy_services": len([r for r in results.values() if r["status"] == "healthy"]),
                "unhealthy_services": len([r for r in results.values() if r["status"] == "unhealthy"]),
                "results": results
            }
    
    def get_router(self):
        """라우터 반환"""
        return self.router 