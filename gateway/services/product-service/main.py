from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Product Service",
    description="상품 관리 마이크로서비스",
    version="1.0.0"
)

# 샘플 상품 데이터
products = [
    {"id": 101, "name": "노트북", "price": 25000, "category": "전자제품", "stock": 10, "description": "고성능 노트북"},
    {"id": 102, "name": "스마트폰", "price": 30000, "category": "전자제품", "stock": 15, "description": "최신 스마트폰"},
    {"id": 103, "name": "책상", "price": 25000, "category": "가구", "stock": 5, "description": "편안한 책상"},
    {"id": 104, "name": "의자", "price": 15000, "category": "가구", "stock": 8, "description": "인체공학 의자"}
]

class Product(BaseModel):
    id: int
    name: str
    price: float
    category: str
    stock: int
    description: str

class CreateProduct(BaseModel):
    name: str
    price: float
    category: str
    stock: int
    description: str

@app.get("/health")
async def health_check():
    """서비스 헬스 체크"""
    return {
        "status": "healthy",
        "service": "product-service",
        "port": os.getenv("SERVICE_PORT", "8003")
    }

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Product Service is running"}

@app.get("/api/products", response_model=List[Product])
async def get_products():
    """모든 상품 조회"""
    return products

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """특정 상품 조회"""
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/api/products/category/{category}", response_model=List[Product])
async def get_products_by_category(category: str):
    """카테고리별 상품 조회"""
    category_products = [product for product in products if product["category"] == category]
    return category_products

@app.post("/api/products", response_model=Product)
async def create_product(product: CreateProduct):
    """새 상품 생성"""
    new_id = max([p["id"] for p in products]) + 1 if products else 101
    new_product = {"id": new_id, **product.dict()}
    products.append(new_product)
    return new_product

@app.put("/api/products/{product_id}", response_model=Product)
async def update_product(product_id: int, product: CreateProduct):
    """상품 정보 수정"""
    for i, existing_product in enumerate(products):
        if existing_product["id"] == product_id:
            products[i] = {"id": product_id, **product.dict()}
            return products[i]
    raise HTTPException(status_code=404, detail="Product not found")

@app.put("/api/products/{product_id}/stock")
async def update_stock(product_id: int, stock: int):
    """재고 수량 업데이트"""
    if stock < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative")
    
    for i, product in enumerate(products):
        if product["id"] == product_id:
            products[i]["stock"] = stock
            return {"message": f"Product {product_id} stock updated to {stock}"}
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    """상품 삭제"""
    for i, product in enumerate(products):
        if product["id"] == product_id:
            deleted_product = products.pop(i)
            return {"message": f"Product {deleted_product['name']} deleted successfully"}
    raise HTTPException(status_code=404, detail="Product not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port) 