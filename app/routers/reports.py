from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, desc, or_, and_, true
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
from app.core.database import get_db
from app.core.security import get_current_admin_user
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User
from app.models.report import Report
from app.schemas.report import ReportCreate, Report as ReportSchema

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=ReportSchema)
async def generate_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    try:
        data: Dict[str, Any] = {
            "period": {
                "start": report.start_date.isoformat(),
                "end": (report.end_date or datetime.now()).isoformat()
            }
        }

        if report.type == "products":
            results = db.query(
                Product.name,
                func.coalesce(func.sum(OrderItem.quantity), 0).label("total_sold"),
                func.coalesce(func.sum(OrderItem.price), 0).label("total_revenue")
            ).outerjoin(
                OrderItem
            ).outerjoin(
                Order, 
                and_(
                    Order.id == OrderItem.order_id,
                    Order.status == OrderStatus.paid,
                    Order.created_at >= report.start_date,
                    or_(
                        Order.created_at <= report.end_date if report.end_date 
                        else true()
                    )
                )
            ).group_by(
                Product.name
            ).order_by(
                desc("total_sold")
            ).limit(10).all()

            data["products"] = [
                {
                    "name": name,
                    "total_sold": int(total_sold),
                    "revenue": float(total_revenue)
                }
                for name, total_sold, total_revenue in results
            ]

        db_report = Report(
            type=report.type,
            period=report.period,
            data=data
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report

    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )

@router.get("/{report_id}", response_model=ReportSchema)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    return report
