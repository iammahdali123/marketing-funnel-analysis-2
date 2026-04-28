from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/funnel", tags=["funnel"])

ORDERED_STAGES = ["awareness", "interest", "consideration", "intent", "purchase"]


@router.get("/analysis", response_model=schemas.FunnelAnalysis)
def get_funnel_analysis(db: Session = Depends(get_db)):
    # Count distinct users per stage
    rows = (
        db.query(models.Event.stage, func.count(models.Event.user_id.distinct()))
        .group_by(models.Event.stage)
        .all()
    )

    stage_counts = {row[0]: row[1] for row in rows}

    stages: List[schemas.FunnelStage] = []
    prev_count = None
    for stage_name in ORDERED_STAGES:
        count = stage_counts.get(stage_name, 0)
        conversion_rate = None
        if prev_count is not None and prev_count > 0:
            conversion_rate = round(count / prev_count * 100, 2)
        stages.append(
            schemas.FunnelStage(
                stage=stage_name, count=count, conversion_rate=conversion_rate
            )
        )
        prev_count = count

    total_users = db.query(models.User).count()
    return schemas.FunnelAnalysis(stages=stages, total_users=total_users)
