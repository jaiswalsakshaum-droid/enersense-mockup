"""
Scoring Service for EnerSense Plant & Machine Health.
Computes composite energy health scores (0-100) based on power draw deviation,
vibration limits, thermal anomalies, and operating stability.
"""

from typing import Dict, Any

EXPECTED_TEMPERATURES = {
    "Melting furnace": 650.0,
    "Rotary screw compressor": 80.0,
    "CNC turning centre": 45.0,
    "Baghouse filter": 50.0,
    "Induced draft": 38.0,
}

def calculate_machine_health_score(
    power_kw: float,
    baseline_kw: float,
    vibration_mms: float,
    temperature_c: float,
    machine_type: str,
) -> int:
    """
    Computes 0-100 machine health score.
    100 = optimal operating conditions.
    """
    expected_temp_c = EXPECTED_TEMPERATURES.get(machine_type, 50.0)
    score = 100.0

    # Power draw penalty (if >10% over baseline)
    power_diff_pct = ((power_kw - baseline_kw) / max(baseline_kw, 1.0)) * 100.0
    if power_diff_pct > 10.0:
        score -= min(25.0, (power_diff_pct - 10.0) * 1.5)

    # Vibration penalty (normal < 2.5 mm/s, warning 2.5-4.5, critical > 4.5)
    if vibration_mms > 4.5:
        score -= min(35.0, (vibration_mms - 4.5) * 15.0 + 15.0)
    elif vibration_mms > 2.5:
        score -= (vibration_mms - 2.5) * 5.0

    # Temperature anomaly penalty
    temp_diff = abs(temperature_c - expected_temp_c)
    if temp_diff > 40.0:
        score -= min(20.0, (temp_diff - 40.0) * 0.4)

    return max(10, min(100, int(round(score))))
def get_health_factors(
    power_kw: float,
    baseline_kw: float,
    vibration_mms: float,
    temperature_c: float,
    machine_type: str,
) -> Dict[str, Any]:
    """
    Explain the telemetry factors contributing to machine health.
    """

    expected_temp_c = EXPECTED_TEMPERATURES.get(machine_type, 50.0)

    # Power analysis
    power_deviation_pct = (
        ((power_kw - baseline_kw) / max(baseline_kw, 1.0)) * 100.0
    )

    if power_deviation_pct <= 10:
        power_status = "Normal"
    elif power_deviation_pct <= 25:
        power_status = "High"
    else:
        power_status = "Critical"

    # Vibration analysis
    if vibration_mms <= 2.5:
        vibration_status = "Normal"
    elif vibration_mms <= 4.5:
        vibration_status = "Warning"
    else:
        vibration_status = "Critical"

    # Temperature analysis
    temperature_deviation = abs(temperature_c - expected_temp_c)

    if temperature_deviation <= 10:
        temperature_status = "Normal"
    elif temperature_deviation <= 40:
        temperature_status = "Warning"
    else:
        temperature_status = "Critical"

    return {
        "power": {
            "value": power_kw,
            "baseline": baseline_kw,
            "deviation_pct": round(power_deviation_pct, 1),
            "status": power_status,
        },
        "vibration": {
            "value": vibration_mms,
            "status": vibration_status,
        },
        "temperature": {
            "value": temperature_c,
            "expected": expected_temp_c,
            "deviation": round(temperature_deviation, 1),
            "status": temperature_status,
        },
    }
def get_machine_status(score: int) -> str:
    """Convert a health score into an operational status."""

    if score >= 90:
        return "Normal"
    elif score >= 70:
        return "Warning"
    else:
        return "Critical"