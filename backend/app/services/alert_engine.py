"""
Simulated alert engine for EnerSense.

Generates machine-condition alerts from the latest machine telemetry
and keeps them in an in-memory alert history.
"""

from datetime import datetime, timezone
import hashlib
from typing import Dict, List, Any

from app.data.machines import MACHINES_DATA
from app.models.alerts import AlertItem
from app.services.scoring import get_health_factors


# Simulated persistent alert history.
# In production, this would be stored in a database.
SIMULATED_ALERT_HISTORY: List[Dict[str, Any]] = []


def generate_machine_alert(machine: Dict[str, Any]) -> AlertItem | None:
    """
    Generate the highest-priority alert for a machine.

    Returns one alert for the most severe detected condition,
    or None when the machine has no critical/warning condition.
    """

    health_factors = get_health_factors(
        power_kw=machine["power_kw"],
        baseline_kw=machine["baseline_power_kw"],
        vibration_mms=machine["vibration_mms"],
        temperature_c=machine["temperature_c"],
        machine_type=machine["type"],
    )

    # Highest priority: critical vibration
    vibration = health_factors["vibration"]

    if vibration["status"] == "Critical":
        return AlertItem(
            id=generate_alert_id(machine["id"], "vibration"),
            title=f'{machine["name"]} · High vibration',
            detail=(
                f'Vibration is at {vibration["value"]} mm/s, '
                f'which exceeds the critical threshold.'
            ),
            time="Just now",
            severity="Critical",
            machine=machine["name"],
            machine_id=machine["id"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            recommended_action=(
                "Inspect rotating components, check bearing condition, "
                "and verify mechanical balance."
            ),
        )

    # Second priority: critical power consumption
    power = health_factors["power"]

    if power["status"] == "Critical":
        return AlertItem(
            id=generate_alert_id(machine["id"], "power"),
            title=f'{machine["name"]} · Excessive power draw',
            detail=(
                f'Power consumption is {power["deviation_pct"]}% '
                f'above the baseline of {power["baseline"]} kW.'
            ),
            time="Just now",
            severity="Critical",
            machine=machine["name"],
            machine_id=machine["id"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            recommended_action=(
                "Inspect the machine for abnormal loading, mechanical "
                "resistance, or inefficient operating conditions."
            ),
        )

    # Third priority: critical temperature
    temperature = health_factors["temperature"]

    if temperature["status"] == "Critical":
        return AlertItem(
            id=generate_alert_id(machine["id"], "temperature"),
            title=f'{machine["name"]} · Temperature anomaly',
            detail=(
                f'Temperature is {temperature["value"]}°C, '
                f'{temperature["deviation"]}°C away from the expected '
                f'{temperature["expected"]}°C.'
            ),
            time="Just now",
            severity="Critical",
            machine=machine["name"],
            machine_id=machine["id"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            recommended_action=(
                "Inspect cooling, thermal loading, and temperature-control "
                "systems immediately."
            ),
        )

    # Warning-level conditions

    if power["status"] == "High":
        return AlertItem(
            id=generate_alert_id(machine["id"], "power-warning"),
            title=f'{machine["name"]} · Elevated power draw',
            detail=(
                f'Power consumption is {power["deviation_pct"]}% '
                f'above the baseline of {power["baseline"]} kW.'
            ),
            time="Just now",
            severity="Warning",
            machine=machine["name"],
            machine_id=machine["id"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            recommended_action=(
                "Monitor power consumption and inspect the machine "
                "if the elevated draw persists."
            ),
        )

    if vibration["status"] == "Warning":
        return AlertItem(
            id=generate_alert_id(machine["id"], "vibration-warning"),
            title=f'{machine["name"]} · Elevated vibration',
            detail=(
                f'Vibration is at {vibration["value"]} mm/s '
                f'and is above the normal operating range.'
            ),
            time="Just now",
            severity="Warning",
            machine=machine["name"],
            machine_id=machine["id"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            recommended_action=(
                "Monitor vibration and inspect rotating components "
                "during the next maintenance window."
            ),
        )

    if temperature["status"] == "Warning":
        return AlertItem(
            id=generate_alert_id(machine["id"], "temperature-warning"),
            title=f'{machine["name"]} · Temperature deviation',
            detail=(
                f'Temperature is {temperature["value"]}°C, '
                f'{temperature["deviation"]}°C away from the expected '
                f'{temperature["expected"]}°C.'
            ),
            time="Just now",
            severity="Warning",
            machine=machine["name"],
            machine_id=machine["id"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            recommended_action=(
                "Monitor temperature and inspect thermal conditions "
                "if the deviation continues."
            ),
        )

    return None


def generate_alert_id(machine_id: str, condition: str) -> int:
    """Generate a stable ID for a simulated machine alert."""

    key = f"{machine_id}:{condition}"

    digest = hashlib.sha256(
        key.encode("utf-8")
    ).hexdigest()

    return int(digest[:8], 16)


def initialize_alert_history() -> None:
    """
    Generate initial simulated alerts from the current machine state.

    This runs once and prevents duplicate alerts from being added.
    """

    if SIMULATED_ALERT_HISTORY:
        return

    for machine in MACHINES_DATA:
        alert = generate_machine_alert(machine)

        if alert:
            SIMULATED_ALERT_HISTORY.append(
                alert.model_dump()
            )


def get_alert_history() -> List[Dict[str, Any]]:
    """Return the current simulated alert history."""

    initialize_alert_history()

    return SIMULATED_ALERT_HISTORY