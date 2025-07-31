from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Order Service",
    description="주문 관리 마이크로서비스",
    version="1.0.0"
)

# 샘플 주문 데이터
orders = [
    {"id": 1, "user_id": 1, "product_id": 101, "quantity": 2, "total_price": 50000, "status": "pending", "created_at": "2024-01-15T10:30:00"},
    {"id": 2, "user_id": 2, "product_id": 102, "quantity": 1, "total_price": 30000, "status": "completed", "created_at": "2024-01-14T15:20:00"},
    {"id": 3, "user_id": 3, "product_id": 103, "quantity": 3, "total_price": 75000, "status": "shipped", "created_at": "2024-01-13T09:45:00"}
]

class Order(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    status: str
    created_at: str

class CreateOrder(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    total_price: float

@app.get("/health")
async def health_check():
    """서비스 헬스 체크"""
    return {
        "status": "healthy",
        "service": "order-service",
        "port": os.getenv("SERVICE_PORT", "8002")
    }

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Order Service is running"}

@app.get("/api/orders", response_model=List[Order])
async def get_orders():
    """모든 주문 조회"""
    return orders

@app.get("/api/orders/{order_id}", response_model=Order)
async def get_order(order_id: int):
    """특정 주문 조회"""
    for order in orders:
        if order["id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")

@app.get("/api/orders/user/{user_id}", response_model=List[Order])
async def get_orders_by_user(user_id: int):
    """사용자별 주문 조회"""
    user_orders = [order for order in orders if order["user_id"] == user_id]
    return user_orders

@app.post("/api/orders", response_model=Order)
async def create_order(order: CreateOrder):
    """새 주문 생성"""
    new_id = max([o["id"] for o in orders]) + 1 if orders else 1
    new_order = {
        "id": new_id,
        **order.dict(),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    orders.append(new_order)
    return new_order

@app.put("/api/orders/{order_id}/status")
async def update_order_status(order_id: int, status: str):
    """주문 상태 업데이트"""
    valid_statuses = ["pending", "processing", "shipped", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    for i, order in enumerate(orders):
        if order["id"] == order_id:
            orders[i]["status"] = status
            return {"message": f"Order {order_id} status updated to {status}"}
    raise HTTPException(status_code=404, detail="Order not found")

@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: int):
    """주문 삭제"""
    for i, order in enumerate(orders):
        if order["id"] == order_id:
            deleted_order = orders.pop(i)
            return {"message": f"Order {deleted_order['id']} deleted successfully"}
    raise HTTPException(status_code=404, detail="Order not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port) 