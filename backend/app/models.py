from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    events = relationship("Event", back_populates="user")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String, nullable=False)
    stage = Column(String, nullable=False)
    properties = Column(Text)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="events")


class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    churn_probability = Column(Float, nullable=False)
    predicted_at = Column(DateTime, default=datetime.utcnow)
