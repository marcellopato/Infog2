from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, Order as OrderSchema
from app.services.whatsapp import WhatsAppService

router = APIRouter()

@router.post("/", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Criar pedido
    db_order = Order(user_id=current_user.id)
    db.add(db_order)
    
    total = 0
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Produto {item.product_id} não encontrado")
        
        if not product.is_active:
            raise HTTPException(status_code=400, detail=f"Produto {product.name} indisponível")
        
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente para {product.name}")
        
        order_item = OrderItem(
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )
        db_order.items.append(order_item)
        total += product.price * item.quantity
        
        product.stock -= item.quantity
        db.add(product)
    
    db_order.total = total
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Enviar confirmação por WhatsApp
    try:
        whatsapp = WhatsAppService()
        message = {
            "type": "text",
            "message": f"""
            Olá! Seu pedido #{db_order.id} foi recebido.
            Total: R$ {db_order.total:.2f}
            
            Em breve você receberá mais informações.
            """
        }
        await whatsapp.send_message(current_user.phone, message)
    except Exception as e:
        logger.error(f"Erro ao enviar WhatsApp: {str(e)}")
    
    return db_order

@router.get("/", response_model=List[OrderSchema])
async def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Order).filter(Order.user_id == current_user.id).all()

@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return order

@router.patch("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if order.status != OrderStatus.pending:
        raise HTTPException(status_code=400, detail="Pedido não pode ser cancelado")
    
    # Restaurar estoque
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:  # Validação adicional
            product.stock += item.quantity
            db.add(product)
    
    order.status = OrderStatus.cancelled
    db.add(order)
    db.commit()
    return {"message": "Pedido cancelado com sucesso"}
