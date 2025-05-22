from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List
from app.core.database import get_db
from app.models.product import Product
from app.models.order import Order
from app.schemas.search import ProductSearchParams, OrderSearchParams
from app.schemas.product import Product as ProductSchema
from app.schemas.order import Order as OrderSchema

router = APIRouter()

@router.get("/products", response_model=List[ProductSchema])
async def search_products(
    params: ProductSearchParams = Depends(),
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.is_active == True)
    
    if params.query:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{params.query}%"),
                Product.description.ilike(f"%{params.query}%")
            )
        )
    
    if params.category_id:
        query = query.filter(Product.category_id == params.category_id)
    
    if params.min_price is not None:
        query = query.filter(Product.price >= params.min_price)
    
    if params.max_price is not None:
        query = query.filter(Product.price <= params.max_price)
    
    # Ordenação
    order_column = getattr(Product, params.order_by, Product.name)
    if params.order.lower() == "desc":
        order_column = order_column.desc()
    
    query = query.order_by(order_column)
    
    # Paginação
    offset = (params.page - 1) * params.per_page
    query = query.offset(offset).limit(params.per_page)
    
    return query.all()
