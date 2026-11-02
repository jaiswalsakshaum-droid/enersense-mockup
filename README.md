# EnerSense — Industrial Energy Intelligence Platform

EnerSense is an industrial energy intelligence platform designed for manufacturing plants, foundries, and industrial SME units. It monitors plant energy consumption, computes equipment health scores, delivers predictive alerts, models what-if efficiency retrofits, and matches government energy conservation schemes (BEE / PAT / GEDA).

---

## Repository Structure

```
enersense-mockup-main/
├── backend/            # Python FastAPI service (telemetry, SSE streaming, what-if calculation)
│   ├── main.py         # FastAPI application & router entry point
│   ├── requirements.txt
│   └── app/
│       ├── data/       # Seed datasets (machines, alerts, recommendations, schemes)
│       ├── models/     # Pydantic schemas for request & response shapes
│       ├── routers/    # API endpoints (machines, dashboard, alerts, recommendations, simulate, schemes, stream)
│       └── services/   # Business logic (simulation engine & energy health scoring)
├── frontend/           # TanStack Start + React 19 + Tailwind v4 + shadcn/ui
│   ├── src/
│   │   ├── components/ # Industrial UI components & AppShell
│   │   ├── lib/        # Typed API client (api.ts), i18n context (i18n.tsx)
│   │   └── routes/     # App pages (dashboard, machines, alerts, audit, simulate)
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## Getting Started

### 1. Backend Service (FastAPI)

Runs on **port 4000** with interactive OpenAPI docs available at `http://localhost:4000/docs`.
PostgreSQL is required for telemetry, orders, and login.

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
# macOS / Linux:
python -m venv venv
source venv/bin/activate

# Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure PostgreSQL and JWT signing (copy the template, then edit values)
# PowerShell:
Copy-Item .env.example .env
# macOS / Linux:
cp .env.example .env

# Create the database, then run these from the backend directory
createdb enersense
psql -d enersense -f app/database/schema.sql
python -m app.data.seed
psql -d enersense -f app/database/002_database_improvements.sql
psql -d enersense -f app/database/003_machine_availability.sql
psql -d enersense -f app/database/004_telemetry_history.sql

# Create the first login account
python -m app.auth.create_admin

# Start FastAPI dev server with hot reload
uvicorn main:app --reload --port 4000
```

Apply the numbered SQL migrations once, in order. The admin creation command
prompts for the email, name, and password; passwords must be at least 12
characters. Set `JWT_SECRET` in `.env` to a unique random value.
Set `ML_ENGINE_URL` in the backend `.env` if the ML service is hosted elsewhere.

### 2. Frontend Web App (TanStack Start + React 19)

Runs on **port 5173** (or the next available port) and communicates with the backend at `http://localhost:4000/api`.

```bash
# Navigate to frontend directory
cd frontend

# Optional: copy the frontend API URL template (PowerShell)
Copy-Item .env.example .env
# macOS / Linux:
cp .env.example .env

# Install dependencies (using bun or npm)
bun install
# or: npm install

# Start Vite dev server
bun run dev
# or: npm run dev
```

Open [http://localhost:5173/auth](http://localhost:5173/auth) in your browser.
The root route redirects to the login page. Set `VITE_API_BASE_URL` if the
backend API is not at the default `http://localhost:4000/api`.

### 3. ML Engine

The ML Engine runs separately on **port 8000** and is required by the backend's
`/api/ml/*` endpoints. Follow [ml-engine/README.md](ml-engine/README.md) to
install its dependencies, train its models, generate runtime reports, and start
the service.

---

## API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/summary` | Overall plant health score, today's kWh, cost, CO₂e, peer benchmarks, 24h load trend |
| `GET` | `/api/machines` | Equipment registry with health scores, power draw, and status |
| `GET` | `/api/machines/{machine_id}` | Detailed telemetry, 24h trend, and maintenance logs for a single machine |
| `GET` | `/api/stream/live?machine_id=...` | **Server-Sent Events (SSE)** real-time telemetry stream (updates every 3s) |
| `GET` | `/api/alerts` | Operational events ordered by severity (Critical, Warning, Resolved, Info) |
| `GET` | `/api/recommendations` | Ranked energy audit retrofit recommendations with kWh, ₹ savings & payback |
| `POST` | `/api/simulate` | Deterministic **What-If ROI Calculator** for load shifting, VFDs, and leak fixes |
| `GET` | `/api/schemes` | BEE, SIDBI, and state government energy efficiency subsidies matcher |

---

## Key Features

1. **Live SSE Telemetry Streaming**: Real-time telemetry charts on machine detail pages that update live without page refreshing.
2. **What-If Simulator (`/simulate`)**: Interactive slider-based tool calculating before/after kWh, monthly ₹ savings, and payback period.
3. **WhatsApp Critical Alerts Dispatch**: Real-time mock preview for instant supervisory dispatch of emergency anomalies.
4. **Peer Benchmarking**: Anonymized comparator widget ranking plant performance against regional SME foundry cluster percentiles.
5. **PAT / BEE Scheme Matcher**: Discover applicable Indian government subsidies and tradable ESCerts programs.
6. **English / Hindi Language Toggle**: Instant header toggle between English and Hindi.
