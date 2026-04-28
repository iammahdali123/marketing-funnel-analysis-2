from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.ml.churn_model import build_user_features, classify_risk, predict_churn_probability

router = APIRouter(prefix="/churn", tags=["churn"])


@router.get("/predictions", response_model=List[schemas.ChurnPredictionOut])
def get_churn_predictions(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    results = []
    for user in users:
        events = [
            {
                "event_type": e.event_type,
                "stage": e.stage,
                "occurred_at": e.occurred_at,
            }
            for e in user.events
        ]
        features = build_user_features(events)
        prob = predict_churn_probability(features)
        risk = classify_risk(prob)
        results.append(
            schemas.ChurnPredictionOut(
                user_external_id=user.external_id,
                churn_probability=prob,
                risk_level=risk,
            )
        )
        # Persist latest prediction
        prediction = models.ChurnPrediction(
            user_id=user.id, churn_probability=prob
        )
        db.add(prediction)
    db.commit()
    return results
