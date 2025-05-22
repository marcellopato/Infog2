from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus

class ProductSearchParams(BaseModel):
    query: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    order_by: Optional[str] = "name"
    order: Optional[str] = "asc"
    page: int = Field(1, gt=0)
    per_page: int = Field(10, gt=0, le=100)

class OrderSearchParams(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[OrderStatus] = None
    order_by: Optional[str] = "created_at"
    order: Optional[str] = "desc"
    page: int = Field(1, gt=0)
    per_page: int = Field(10, gt=0, le=100)
