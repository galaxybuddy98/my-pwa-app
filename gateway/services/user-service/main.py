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
    title="User Service",
    description="사용자 관리 마이크로서비스",
    version="1.0.0"
)

# 샘플 사용자 데이터
users = [
    {"id": 1, "name": "김철수", "email": "kim@example.com", "age": 25},
    {"id": 2, "name": "이영희", "email": "lee@example.com", "age": 30},
    {"id": 3, "name": "박민수", "email": "park@example.com", "age": 28}
]

class User(BaseModel):
    id: int
    name: str
    email: str
    age: int

class CreateUser(BaseModel):
    name: str
    email: str
    age: int

@app.get("/health")
async def health_check():
    """서비스 헬스 체크"""
    return {
        "status": "healthy",
        "service": "user-service",
        "port": os.getenv("SERVICE_PORT", "8001")
    }

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "User Service is running"}

@app.get("/api/users", response_model=List[User])
async def get_users():
    """모든 사용자 조회"""
    return users

@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """특정 사용자 조회"""
    for user in users:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/api/users", response_model=User)
async def create_user(user: CreateUser):
    """새 사용자 생성"""
    new_id = max([u["id"] for u in users]) + 1 if users else 1
    new_user = {"id": new_id, **user.dict()}
    users.append(new_user)
    return new_user

@app.put("/api/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: CreateUser):
    """사용자 정보 수정"""
    for i, existing_user in enumerate(users):
        if existing_user["id"] == user_id:
            users[i] = {"id": user_id, **user.dict()}
            return users[i]
    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int):
    """사용자 삭제"""
    for i, user in enumerate(users):
        if user["id"] == user_id:
            deleted_user = users.pop(i)
            return {"message": f"User {deleted_user['name']} deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port) 