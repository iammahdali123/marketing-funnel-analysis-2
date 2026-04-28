# Marketing Funnel Analyzer

An **Automated Marketing Funnel Analyzer** that turns raw event data into growth strategy.

## Features

| Layer | Technology |
|-------|------------|
| Backend API | FastAPI + Uvicorn |
| Database | PostgreSQL + SQLAlchemy |
| ML / Churn | scikit-learn (Random Forest heuristic) |
| Frontend | React 18 + Vite |
| Charts | Recharts |
| Containerisation | Docker + Docker Compose |

## Architecture

```
Browser → React (port 3000)
              ↓ /api/*  (nginx proxy)
         FastAPI (port 8000)
              ↓
         PostgreSQL (port 5432)
```

## Quick Start

```bash
# Clone the repo
git clone https://github.com/iammahdali123/marketing-funnel-analysis-2.git
cd marketing-funnel-analysis-2

# Build & run all services
docker compose up --build
```

Then open **http://localhost:3000** in your browser.

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/events/` | Ingest a single event |
| POST | `/events/bulk` | Ingest multiple events |
| GET | `/events/` | List events |
| GET | `/funnel/analysis` | Funnel stage counts + conversion rates |
| GET | `/churn/predictions` | Per-user churn probabilities |

### Example: Ingest an event

```bash
curl -X POST http://localhost:8000/events/ \
  -H "Content-Type: application/json" \
  -d '{"user_external_id":"u1","event_type":"page_view","stage":"awareness"}'
```

### Example: Bulk ingest

```bash
curl -X POST http://localhost:8000/events/bulk \
  -H "Content-Type: application/json" \
  -d '{"events":[
    {"user_external_id":"u1","event_type":"page_view","stage":"awareness"},
    {"user_external_id":"u1","event_type":"ad_click","stage":"interest"}
  ]}'
```

## Funnel Stages

1. **Awareness** – First touch (ad view, organic search)
2. **Interest** – Engaged visitors (click, scroll)
3. **Consideration** – Product research (product view, comparison)
4. **Intent** – High intent (add to cart, pricing view)
5. **Purchase** – Conversion

## Churn Model

The churn engine scores each user on four signals:

- **Stage depth** – how far they progressed through the funnel
- **Event volume** – total interactions recorded
- **Stage diversity** – number of distinct stages visited
- **Engagement velocity** – events per day

Risk levels: 🔴 **high** (≥ 70%) · 🟡 **medium** (40–69%) · 🟢 **low** (< 40%)

## Development

```bash
# Backend only (requires local Postgres)
cd backend
pip install -r requirements.txt
DATABASE_URL=postgresql://funnel:funnel@localhost:5432/funnel_db \
  uvicorn app.main:app --reload

# Frontend only
cd frontend
npm install
VITE_API_URL=http://localhost:8000 npm run dev
```
