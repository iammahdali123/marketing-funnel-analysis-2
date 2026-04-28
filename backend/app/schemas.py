from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class EventCreate(BaseModel):
    user_external_id: str
    email: Optional[str] = None
    event_type: str
    stage: str
    properties: Optional[str] = None
    occurred_at: Optional[datetime] = None


class EventOut(BaseModel):
    id: int
    user_id: int
    event_type: str
    stage: str
    properties: Optional[str]
    occurred_at: datetime

    class Config:
        from_attributes = True


class FunnelStage(BaseModel):
    stage: str
    count: int
    conversion_rate: Optional[float] = None


class FunnelAnalysis(BaseModel):
    stages: List[FunnelStage]
    total_users: int


class ChurnPredictionOut(BaseModel):
    user_external_id: str
    churn_probability: float
    risk_level: str


class BulkEventCreate(BaseModel):
    events: List[EventCreate]
