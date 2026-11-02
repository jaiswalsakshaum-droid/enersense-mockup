"""Train models and generate the data files required by the ML API."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
SOURCE_DATA = ROOT / "data" / "raw" / "factory_production_data.csv"

PIPELINE = (
    "src/models/energy_model.py",
    "src/models/production_model.py",
    "src/models/quality_model.py",
    "src/models/compare_energy_models.py",
    "src/simulation/scenario_generator.py",
    "src/optimization/optimizer.py",
    "src/analysis/energy_debt.py",
    "src/analysis/process_dna.py",
    "src/analysis/dna_drift.py",
    "src/analysis/cascade_detector.py",
    "src/optimization/risk_aware_optimizer.py",
)


def main() -> None:
    if not SOURCE_DATA.is_file():
        raise SystemExit(
            f"Required training data is missing: {SOURCE_DATA.relative_to(ROOT)}"
        )

    for script in PIPELINE:
        print(f"\n==> Running {script}", flush=True)
        subprocess.run(
            [sys.executable, str(ROOT / script)],
            cwd=ROOT,
            check=True,
        )

    print("\nML runtime artifacts are ready. Start the API with:")
    print("python -m uvicorn src.api.main:app --reload --port 8000")


if __name__ == "__main__":
    main()
