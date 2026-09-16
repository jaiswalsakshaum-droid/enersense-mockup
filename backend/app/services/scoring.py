"""
Scoring Service for EnerSense Plant & Machine Health.
Computes composite energy health scores (0-100) based on power draw deviation,
vibration limits, thermal anomalies, and operating stability.
"""

from typing import Dict, Any


def calculate_machine_health_score(
    power_kw: float,
    baseline_kw: float,
    vibration_mms: float,
    temperature_c: float,
    expected_temp_c: float = 650.0,
) -> int:
    """
    Computes 0-100 machine health score.
    100 = optimal operating conditions.
    """
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
