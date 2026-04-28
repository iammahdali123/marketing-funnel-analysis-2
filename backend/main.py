# backend/main.py
import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData, JSON
from sqlalchemy.orm import sessionmaker
from analytics import compute_funnel, top_dropoff, load_events_df
from ml_utils import prepare_training_data, train_decision_tree, explain_feature_importances

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./funnel.db')

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(bind=engine)
metadata = MetaData()

events = Table(
    'events', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('user_id', String, index=True, nullable=False),
    Column('event', String, index=True, nullable=False),
    Column('timestamp', DateTime, default=datetime.utcnow, index=True),
    Column('properties', JSON, nullable=True)
)
metadata.create_all(engine)

app = FastAPI(title='Funnel Analyzer')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

@app.post('/ingest/csv')
async def ingest_csv(file: UploadFile = File(...)):
    content = await file.read()
    try:
        s = content.decode('utf-8')
    except Exception:
        s = content.decode('latin-1')
    df = pd.read_csv(io.StringIO(s))
    expected = {'user_id','event','timestamp'}
    if not expected.issubset(set(df.columns)):
        raise HTTPException(status_code=400, detail=f'CSV must include columns: {expected}')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    inserted = 0
    with engine.begin() as conn:
        for _, row in df.iterrows():
            props = None
            if 'properties' in df.columns and not pd.isna(row.get('properties')):
                try:
                    props = json.loads(row['properties']) if isinstance(row['properties'], str) else row['properties']
                except Exception:
                    props = None
            conn.execute(events.insert().values(
                user_id=str(row['user_id']),
                event=str(row['event']),
                timestamp=row['timestamp'].to_pydatetime(),
                properties=props
            ))
            inserted += 1
    return {'inserted': inserted}

@app.post('/ingest/event')
async def ingest_event(payload: dict):
    if 'user_id' not in payload or 'event' not in payload:
        raise HTTPException(status_code=400, detail='user_id and event required')
    ts = payload.get('timestamp')
    if ts:
        ts = datetime.fromisoformat(ts)
    else:
        ts = datetime.utcnow()
    props = payload.get('properties')
    with engine.begin() as conn:
        conn.execute(events.insert().values(
            user_id=str(payload['user_id']),
            event=str(payload['event']),
            timestamp=ts,
            properties=props
        ))
    return {'status':'ok'}

@app.get('/funnel')
def get_funnel(steps: str):
    funnel_steps = [s.strip() for s in steps.split(',')]
    df = load_events_df(engine)
    if df.empty:
        return {'error':'no events', 'steps': funnel_steps}
    res = compute_funnel(df, funnel_steps)
    res['top_dropoff'] = top_dropoff(res['dropoffs'])
    return res

@app.get('/suggestions')
def get_suggestions(steps: str):
    funnel_steps = [s.strip() for s in steps.split(',')]
    df = load_events_df(engine)
    if df.empty:
        return {'error':'no events'}
    rows = prepare_training_data(df, funnel_steps)
    clf, vec, score = train_decision_tree(rows)
    if clf is None:
        return {'message':'not enough data or not enough label variance for ML suggestions', 'ml_score': score if score else None}
    imps = explain_feature_importances(clf, vec, top_n=8)
    return {'ml_score': score, 'feature_importances': imps}

@app.get('/health')
def health():
    return {'status':'ok'}

@app.post('/dev/clear')
def dev_clear(confirm: bool = Form(...)):
    if not confirm:
        raise HTTPException(status_code=400, detail='must confirm')
    with engine.begin() as conn:
        conn.execute(events.delete())
    return {'cleared': True}
