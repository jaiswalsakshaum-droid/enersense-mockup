import sys
from pathlib import Path

# Add ml-engine root to Python path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.simulation.simulate import predict_state


def get_test_result():
    return predict_state(
        machine_id="HEAT_01",
        product_id="P001",
        load_percent=80,
        speed_percent=90,
        ambient_temperature_c=30,
        machine_temperature_c=70,
        maintenance_age_days=60,
        cycle_time_sec=60,
        shift="A"
    )


def test_energy_prediction_positive():
    result = get_test_result()

    assert result["energy_kwh"] > 0


def test_production_prediction_positive():
    result = get_test_result()

    assert result["production_units"] > 0


def test_defect_rate_valid():
    result = get_test_result()

    assert 0 <= result["defect_rate"] <= 1