from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/events", tags=["events"])


def _get_or_create_user(db: Session, external_id: str, email: str | None):
    user = db.query(models.User).filter(models.User.external_id == external_id).first()
    if not user:
        user = models.User(external_id=external_id, email=email)
        db.add(user)
        db.flush()
    return user


@router.post("/", response_model=schemas.EventOut, status_code=201)
def create_event(event_in: schemas.EventCreate, db: Session = Depends(get_db)):
    user = _get_or_create_user(db, event_in.user_external_id, event_in.email)
    event = models.Event(
        user_id=user.id,
        event_type=event_in.event_type,
        stage=event_in.stage,
        properties=event_in.properties,
        occurred_at=event_in.occurred_at or datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.post("/bulk", status_code=201)
def create_events_bulk(payload: schemas.BulkEventCreate, db: Session = Depends(get_db)):
    created = 0
    for event_in in payload.events:
        user = _get_or_create_user(db, event_in.user_external_id, event_in.email)
        event = models.Event(
            user_id=user.id,
            event_type=event_in.event_type,
            stage=event_in.stage,
            properties=event_in.properties,
            occurred_at=event_in.occurred_at or datetime.utcnow(),
        )
        db.add(event)
        created += 1
    db.commit()
    return {"created": created}


@router.get("/", response_model=List[schemas.EventOut])
def list_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Event).offset(skip).limit(limit).all()
