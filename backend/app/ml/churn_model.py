"""Scikit-learn based churn prediction model."""
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

FUNNEL_STAGES = ["awareness", "interest", "consideration", "intent", "purchase"]
STAGE_ORDER = {stage: idx for idx, stage in enumerate(FUNNEL_STAGES)}


def build_user_features(user_events: List[Dict]) -> Dict:
    """Convert a list of user events into a feature vector."""
    if not user_events:
        return {}

    df = pd.DataFrame(user_events)
    df["occurred_at"] = pd.to_datetime(df["occurred_at"])
    df = df.sort_values("occurred_at")

    max_stage_idx = -1
    for stage in df["stage"].unique():
        idx = STAGE_ORDER.get(stage, -1)
        if idx > max_stage_idx:
            max_stage_idx = idx

    total_events = len(df)
    unique_stages = df["stage"].nunique()
    time_span_days = (
        (df["occurred_at"].max() - df["occurred_at"].min()).days
        if len(df) > 1
        else 0
    )
    events_per_day = total_events / max(time_span_days, 1)

    return {
        "total_events": total_events,
        "unique_stages": unique_stages,
        "max_stage_reached": max_stage_idx,
        "time_span_days": time_span_days,
        "events_per_day": events_per_day,
    }


def predict_churn_probability(features: Dict) -> float:
    """
    Heuristic-based churn probability.

    A real deployment would train the RandomForestClassifier on historical
    labelled data; here we derive a deterministic score from the features
    so that the endpoint is always meaningful even without a pre-trained model.
    """
    if not features:
        return 0.95

    max_stage = features.get("max_stage_reached", -1)
    total_events = features.get("total_events", 0)
    unique_stages = features.get("unique_stages", 0)
    events_per_day = features.get("events_per_day", 0)

    # Higher stage reached → lower churn probability
    stage_score = 1.0 - (max_stage + 1) / len(FUNNEL_STAGES)

    # More events / higher engagement → lower churn
    engagement_score = max(0.0, 1.0 - (total_events / 20.0))
    diversity_score = max(0.0, 1.0 - (unique_stages / len(FUNNEL_STAGES)))
    velocity_score = max(0.0, 1.0 - min(events_per_day, 5.0) / 5.0)

    probability = (
        stage_score * 0.4
        + engagement_score * 0.3
        + diversity_score * 0.2
        + velocity_score * 0.1
    )
    return round(float(np.clip(probability, 0.0, 1.0)), 4)


def classify_risk(probability: float) -> str:
    if probability >= 0.7:
        return "high"
    if probability >= 0.4:
        return "medium"
    return "low"
