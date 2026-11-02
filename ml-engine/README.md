# EnerSense ML Engine

The ML engine is a separate FastAPI service. The main backend calls it at
`http://127.0.0.1:8000` for the `/api/ml/*` endpoints.

## First-time setup

Use Python 3.11 or newer. From this directory, create an environment, install
the dependencies, and prepare the model and analysis files:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python prepare_runtime.py
```

On macOS or Linux, create and activate the virtual environment with
`python3 -m venv .venv` and `source .venv/bin/activate`.

`prepare_runtime.py` trains the energy, production, quality, and XGBoost energy
models from `data/raw/factory_production_data.csv`. It then generates scenario
predictions, feasible plans, and the analysis reports used by the API. Model
binaries are local runtime artifacts and are not committed. Some generated CSV
reports are checked-in demo samples, so review `git status` after preparing the
runtime; the pipeline may update those files.

## Run the service

Keep the working directory at `ml-engine` so the API can find its generated
files:

```powershell
python -m uvicorn src.api.main:app --reload --port 8000
```

The OpenAPI page is at `http://localhost:8000/docs`. Start the main backend on
port 4000 as well. It calls this service at the `ML_ENGINE_URL` set in
`backend/.env` (default `http://127.0.0.1:8000`).

## Regenerate artifacts

Run `python prepare_runtime.py` again after changing the training data or model
code. This replaces generated model and analysis files. Unit tests can be run
from this directory with `python -m pytest`.
