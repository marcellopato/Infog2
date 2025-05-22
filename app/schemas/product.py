from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, example="Camisa Polo", description="Nome do produto")
    description: Optional[str] = Field(None, example="Camisa polo em algodão", description="Descrição detalhada do produto")
    price: float = Field(..., gt=0, example=89.90, description="Preço em reais")
    stock: int = Field(..., ge=0, example=10, description="Quantidade em estoque")
    is_active: bool = True

class ProductCreate(ProductBase):
    category_id: Optional[int] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Camisa Polo", description="Nome do produto")
    description: Optional[str] = Field(None, example="Camisa polo em algodão", description="Descrição detalhada do produto")
    price: Optional[float] = Field(None, gt=0, example=89.90, description="Preço em reais")
    stock: Optional[int] = Field(None, ge=0, example=10, description="Quantidade em estoque")
    is_active: Optional[bool] = None

class Product(ProductBase):
    id: int
    category_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
