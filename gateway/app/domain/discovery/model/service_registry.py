from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class ServiceInfo(BaseModel):
    """서비스 정보 모델"""
    url: str
    health_check: str
    status: str = "healthy"
    last_check: Optional[float] = None
    metadata: Optional[Dict] = None

class ServiceRegistry(BaseModel):
    """서비스 레지스트리 모델"""
    services: Dict[str, ServiceInfo]
    
    def get_service(self, service_name: str) -> Optional[ServiceInfo]:
        """서비스 정보 조회"""
        return self.services.get(service_name)
    
    def register_service(self, service_name: str, service_info: ServiceInfo):
        """서비스 등록"""
        self.services[service_name] = service_info
    
    def unregister_service(self, service_name: str):
        """서비스 등록 해제"""
        if service_name in self.services:
            del self.services[service_name]
    
    def update_service_status(self, service_name: str, status: str):
        """서비스 상태 업데이트"""
        if service_name in self.services:
            self.services[service_name].status = status
            self.services[service_name].last_check = datetime.now().timestamp() 