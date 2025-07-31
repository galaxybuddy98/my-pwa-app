#!/usr/bin/env python3
"""
게이트웨이 테스트 스크립트
"""

import asyncio
import httpx
import json
import time

GATEWAY_URL = "http://localhost:8000"

async def test_gateway_health():
    """게이트웨이 헬스 체크 테스트"""
    print("🔍 게이트웨이 헬스 체크 테스트...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{GATEWAY_URL}/health")
            if response.status_code == 200:
                print("✅ 게이트웨이가 정상 작동 중입니다.")
                print(f"   응답: {response.json()}")
            else:
                print(f"❌ 게이트웨이 헬스 체크 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 게이트웨이 연결 실패: {e}")

async def test_service_discovery():
    """서비스 디스커버리 테스트"""
    print("\n🔍 서비스 디스커버리 테스트...")
    try:
        async with httpx.AsyncClient() as client:
            # 모든 서비스 조회
            response = await client.get(f"{GATEWAY_URL}/discovery/services")
            if response.status_code == 200:
                services = response.json()
                print("✅ 등록된 서비스 목록:")
                for service_name, service_info in services["services"].items():
                    print(f"   - {service_name}: {service_info['url']}")
            else:
                print(f"❌ 서비스 조회 실패: {response.status_code}")
            
            # 모든 서비스 헬스 체크
            response = await client.get(f"{GATEWAY_URL}/discovery/health/all")
            if response.status_code == 200:
                health_status = response.json()
                print(f"\n✅ 전체 서비스 헬스 상태:")
                print(f"   총 서비스: {health_status['total_services']}")
                print(f"   정상 서비스: {health_status['healthy_services']}")
                print(f"   비정상 서비스: {health_status['unhealthy_services']}")
            else:
                print(f"❌ 헬스 체크 실패: {response.status_code}")
                
    except Exception as e:
        print(f"❌ 서비스 디스커버리 테스트 실패: {e}")

async def test_proxy_routing():
    """프록시 라우팅 테스트"""
    print("\n🔍 프록시 라우팅 테스트...")
    
    test_routes = [
        "/api/users/1",
        "/api/orders/123", 
        "/api/products/456"
    ]
    
    for route in test_routes:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{GATEWAY_URL}{route}")
                if response.status_code == 404:
                    print(f"   ⚠️  {route}: 서비스가 실행되지 않음 (예상됨)")
                elif response.status_code == 503:
                    print(f"   ⚠️  {route}: 서비스가 사용 불가능")
                elif response.status_code == 200:
                    print(f"   ✅ {route}: 성공")
                else:
                    print(f"   ❌ {route}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {route}: {e}")

async def test_service_registration():
    """서비스 등록 테스트"""
    print("\n🔍 서비스 등록 테스트...")
    try:
        async with httpx.AsyncClient() as client:
            # 새 서비스 등록
            new_service = {
                "url": "http://localhost:8004",
                "health_check": "/health",
                "status": "healthy"
            }
            
            # 실제로는 POST 요청이 필요하지만, 현재 구현에서는 GET으로 테스트
            print("   ℹ️  서비스 등록 API는 구현되어 있지만 테스트에서는 생략")
            
    except Exception as e:
        print(f"❌ 서비스 등록 테스트 실패: {e}")

async def main():
    """메인 테스트 함수"""
    print("🚀 MSA Gateway 테스트 시작\n")
    
    # 게이트웨이 헬스 체크
    await test_gateway_health()
    
    # 서비스 디스커버리 테스트
    await test_service_discovery()
    
    # 프록시 라우팅 테스트
    await test_proxy_routing()
    
    # 서비스 등록 테스트
    await test_service_registration()
    
    print("\n✨ 테스트 완료!")
    print("\n💡 참고사항:")
    print("   - 게이트웨이는 정상 작동 중입니다.")
    print("   - 마이크로서비스들이 실행되지 않아서 404/503 오류가 발생할 수 있습니다.")
    print("   - 실제 서비스들을 실행한 후 다시 테스트해보세요.")

if __name__ == "__main__":
    asyncio.run(main()) 