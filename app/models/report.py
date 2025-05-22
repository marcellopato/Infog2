from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.models.base import Base

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # sales, products, stock
    period = Column(String)  # daily, weekly, monthly
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
