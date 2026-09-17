import sys
from pathlib import Path

# Allow imports from ml-engine
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.simulation.simulate import predict_state
from src.simulation.counterfactual_explorer import explore_counterfactuals
from src.analysis.recommendation_explainer import explain_recommendation


def test_end_to_end_factory_pipeline():

    # --------------------------------------------------
    # 1. Current factory state
    # --------------------------------------------------

    current = predict_state(
        machine_id="HEAT_01",
        product_id="P001",
        load_percent=90,
        speed_percent=80,
        ambient_temperature_c=30,
        machine_temperature_c=70,
        maintenance_age_days=60,
        cycle_time_sec=60,
        shift="A"
    )

    # Basic prediction validation
    assert current["energy_kwh"] > 0
    assert current["production_units"] > 0
    assert 0 <= current["defect_rate"] <= 1
    assert current["energy_per_unit"] > 0

    # --------------------------------------------------
    # 2. Counterfactual exploration
    # --------------------------------------------------

    result = explore_counterfactuals(
        machine_id="HEAT_01",
        product_id="P001",
        current_load_percent=90,
        current_speed_percent=80,
        ambient_temperature_c=30,
        machine_temperature_c=70,
        maintenance_age_days=60,
        cycle_time_sec=60,
        shift="A"
    )

    assert result["total_scenarios_tested"] > 0
    assert result["feasible_scenarios"] > 0
    assert len(result["recommendations"]) > 0

    # --------------------------------------------------
    # 3. Select recommended scenario
    # --------------------------------------------------

    recommended = result["recommendations"][0]

    recommended_state = {
        "energy_kwh": recommended["energy_kwh"],
        "production_units": recommended["production_units"],
        "defect_rate": recommended["defect_rate"],
        "energy_per_unit": recommended["energy_per_unit"]
    }

    # --------------------------------------------------
    # 4. Explain recommendation
    # --------------------------------------------------

    explanation = explain_recommendation(
        current_state=current,
        recommended_state=recommended_state
    )

    assert "summary" in explanation
    assert "energy" in explanation
    assert "production" in explanation
    assert "quality" in explanation
    assert "energy_intensity" in explanation

    # --------------------------------------------------
    # 5. Validate recommendation
    # --------------------------------------------------

    assert explanation["energy"]["recommended_kwh"] > 0
    assert explanation["production"]["recommended_units"] > 0
    assert explanation["quality"]["recommended_defect_rate"] >= 0