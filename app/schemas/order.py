from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.order import OrderStatus

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderItemResponse(OrderItemCreate):
    id: int
    price: float
    
    class Config:
        orm_mode = True

class Order(BaseModel):
    id: int
    user_id: int
    total: float
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True
