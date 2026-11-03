# EnerSense — Industrial Energy Intelligence Platform

EnerSense is an industrial energy intelligence platform designed for manufacturing plants, foundries, and industrial SME units. It monitors plant energy consumption, computes equipment health scores, delivers predictive alerts, models what-if efficiency retrofits, simulates production orders on a process digital twin, uses ML models to recommend energy-optimal operating plans, and matches government energy conservation schemes (BEE / PAT / GEDA).

---

## Architecture

```
Browser ──► Frontend :5173 ──► Backend :4000 ──► PostgreSQL
                                    │
                                    └──► ML Engine :8000 (models + optimizer)
```

Start order: PostgreSQL → ML engine → backend → frontend.

---

## Repository Structure

```
enersense/
├── backend/            # Python FastAPI service (port 4000)
│   ├── main.py         # FastAPI application & router entry point
│   ├── requirements.txt
│   ├── tests/          # pytest suite
│   └── app/
│       ├── auth/       # JWT login, password hashing, admin bootstrap
│       ├── data/       # Seed datasets (machines, alerts, recommendations, schemes)
│       ├── database/   # PostgreSQL schema, migrations, connection helper
│       ├── models/     # Pydantic schemas for request & response shapes
│       ├── routers/    # API endpoints
│       └── services/   # Business logic (simulation, scoring, alerts, optimization, ML client)
├── frontend/           # TanStack Start + React 19 + Tailwind v4 + shadcn/ui (port 5173)
│   ├── src/
│   │   ├── components/ # Industrial UI components & AppShell
│   │   ├── lib/        # Typed API client (api.ts), auth helpers, i18n context
│   │   └── routes/     # Pages (login, dashboard, machines, alerts, audit, simulate, process twin)
│   ├── package.json
│   └── vite.config.ts
├── ml-engine/          # Separate FastAPI ML service (port 8000)
│   ├── src/            # Models, optimizer, simulation, analysis, API
│   ├── tests/
│   └── prepare_runtime.py   # Trains models and generates runtime reports
└── README.md
```

---

## Getting Started

### 1. Backend Service (FastAPI)

Runs on **port 4000** with interactive OpenAPI docs at `http://localhost:4000/docs`.
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

### 2. ML Engine

The ML engine runs separately on **port 8000** and is required by the backend's
`/api/ml/*` endpoints. Follow [ml-engine/README.md](ml-engine/README.md) to
install its dependencies, train its models, generate runtime reports, and start
the service. Its OpenAPI docs are at `http://localhost:8000/docs`.

### 3. Frontend Web App (TanStack Start + React 19)

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
The root route redirects to the login page.

---

## Configuration

| Variable | Where | Purpose |
|---|---|---|
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | `backend/.env` | PostgreSQL connection |
| `JWT_SECRET` | `backend/.env` | Token signing key. Required; the backend will not start without it |
| `ML_ENGINE_URL` | `backend/.env` | ML service URL (default `http://127.0.0.1:8000`) |
| `VITE_API_BASE_URL` | `frontend/.env` | Backend API URL (default `http://localhost:4000/api`) |
| `CORS_ORIGINS` | `backend/.env` | Comma-separated browser origins allowed to call the API (default: the local Vite dev server) |

---

## Authentication

All `/api/*` routes except `/api/auth/login` and `/api/health` require an
`Authorization: Bearer <token>` header. Tokens are issued by `/api/auth/login`
and expire after 30 minutes. Accounts have a role of `admin` or `plant_user`.

---

## API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Email and password in, JWT access token out |
| `GET` | `/api/auth/me` | Current authenticated user |
| `GET` | `/api/health` | Database connectivity check |
| `GET` | `/api/dashboard/summary` | Overall plant health score, today's kWh, cost, CO₂e, peer benchmarks, 24h load trend |
| `GET` | `/api/machines` | Equipment registry with health scores, power draw, and status |
| `GET` | `/api/machines/{machine_id}` | Detailed telemetry, 24h trend, and maintenance logs for a single machine |
| `GET` | `/api/machines/{machine_id}/health` | Health score breakdown for a machine |
| `GET` | `/api/stream/live?machine_id=...` | **Server-Sent Events (SSE)** telemetry stream from stored readings |
| `GET` | `/api/alerts` | Operational events ordered by severity (Critical, Warning, Resolved, Info) |
| `GET` | `/api/recommendations` | Ranked energy audit retrofit recommendations with kWh, ₹ savings & payback |
| `POST` | `/api/simulate` | Deterministic **What-If ROI Calculator** for load shifting, VFDs, and leak fixes |
| `GET` | `/api/schemes` | BEE, SIDBI, and state government energy efficiency subsidies matcher |
| `GET` / `POST` | `/api/orders/` | List and create production orders |
| `POST` | `/api/process-twin/simulate/{order_id}` | Simulate a production order on the process digital twin |
| `POST` | `/api/optimization/run/{order_id}` | Optimize an order |
| `POST` | `/api/plans/generate/{order_id}` | Generate an operating plan for an order |
| `GET` | `/api/plans/{plan_id}` | Fetch a generated plan |
| `POST` | `/api/ml/analyze` | Proxy to the ML engine: analyze a machine's current state |
| `POST` | `/api/ml/simulate` | Proxy to the ML engine: what-if on load and speed |
| `POST` | `/api/ml/counterfactual` | Proxy to the ML engine: counterfactual exploration |

---

## Key Features

1. **JWT Authentication**: Login page and token-protected API routes.
2. **Live Telemetry Streaming**: Machine detail pages stream the latest stored telemetry over SSE.
3. **What-If Simulator (`/simulate`)**: Interactive slider-based tool calculating before/after kWh, monthly ₹ savings, and payback period.
4. **Process Digital Twin (`/process-twin`)**: Create a production order and simulate it end to end.
5. **ML Intelligence**: Energy, production, and defect-rate prediction, optimization of operating plans, and counterfactual exploration (ML engine).
6. **WhatsApp Alert Preview**: UI preview of how critical anomalies would be dispatched to supervisors. Dispatch itself is not connected yet.
7. **Peer Benchmarking**: Anonymized comparator widget ranking plant performance against regional SME foundry cluster percentiles.
8. **PAT / BEE Scheme Matcher**: Discover applicable Indian government subsidies and tradable ESCerts programs.
9. **English / Hindi Language Toggle**: Instant header toggle between English and Hindi.

---

## Testing

```bash
# Backend (no database required)
cd backend
python -m pytest -v

# ML engine (run `python prepare_runtime.py` first to train the models)
cd ml-engine
python -m pytest
```

---

## Status and Limitations

- ML models are trained on synthetic data (`ml-engine/data/raw`).
- Telemetry is seeded hourly data, not a live sensor feed.
- Alerts are computed on request, not stored.
- Roles exist but are not yet enforced per route.
- The frontend does not yet call the `/api/ml/*` endpoints.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `JWT_SECRET is missing from environment variables` | Copy `backend/.env.example` to `backend/.env` and set a value |
| `ML Engine is unavailable` | Start the ML engine on port 8000 and check `ML_ENGINE_URL` |
| Every request returns 401 | Your token expired (30 minutes). Log in again |
| `/api/health` returns 503 | PostgreSQL is not running, or the `DB_*` values are wrong |