from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class ReportCreate(BaseModel):
    type: str = Field(..., regex='^(sales|products|stock)$')
    period: str = Field(..., regex='^(daily|weekly|monthly)$')
    start_date: datetime
    end_date: Optional[datetime] = None

class Report(BaseModel):
    id: int
    type: str
    period: str
    data: Dict[str, Any]
    created_at: datetime

    class Config:
        orm_mode = True
