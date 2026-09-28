"""
Database-backed machine alert engine.

Alerts are generated from the latest machine telemetry in PostgreSQL.
The same health-factor logic used by the Machines page is used here,
so the application has one source of truth for machine conditions.
"""

from datetime import datetime, timezone
import hashlib
from typing import Dict, List, Any

from app.database.connection import get_connection
from app.models.alerts import AlertItem
from app.services.scoring import get_health_factors


def generate_alert_id(machine_id: str, condition: str) -> int:
    """Generate a stable alert ID for a machine condition."""

    key = f"{machine_id}:{condition}"

    digest = hashlib.sha256(
        key.encode("utf-8")
    ).hexdigest()

    return int(digest[:8], 16)


def generate_machine_alert(
    machine: Dict[str, Any]
) -> AlertItem | None:
    """
    Generate the highest-priority current alert for one machine.
    """

    health_factors = get_health_factors(
        power_kw=machine["power_kw"],
        baseline_kw=machine["baseline_power_kw"],
        vibration_mms=machine["vibration_mms"],
        temperature_c=machine["temperature_c"],
        machine_type=machine["machine_type"],
    )

    vibration = health_factors["vibration"]
    power = health_factors["power"]
    temperature = health_factors["temperature"]

    now = datetime.now(timezone.utc).isoformat()

    # =============================================================
    # CRITICAL CONDITIONS
    # =============================================================

    if vibration["status"] == "Critical":
        return AlertItem(
            id=generate_alert_id(
                machine["machine_id"],
                "vibration-critical",
            ),
            title=(
                f'{machine["name"]} · High vibration'
            ),
            detail=(
                f'Vibration is {vibration["value"]} mm/s '
                f'and exceeds the critical threshold.'
            ),
            time="Just now",
            severity="Critical",
            machine=machine["name"],
            machine_id=machine["machine_id"],
            timestamp=now,
            recommended_action=(
                "Inspect rotating components, bearing condition, "
                "and mechanical balance immediately."
            ),
        )

    if power["status"] == "Critical":
        return AlertItem(
            id=generate_alert_id(
                machine["machine_id"],
                "power-critical",
            ),
            title=(
                f'{machine["name"]} · Excessive power draw'
            ),
            detail=(
                f'Power consumption is '
                f'{power["deviation_pct"]}% above the '
                f'baseline of {power["baseline"]} kW.'
            ),
            time="Just now",
            severity="Critical",
            machine=machine["name"],
            machine_id=machine["machine_id"],
            timestamp=now,
            recommended_action=(
                "Inspect abnormal loading, mechanical resistance, "
                "or inefficient operating conditions."
            ),
        )

    if temperature["status"] == "Critical":
        return AlertItem(
            id=generate_alert_id(
                machine["machine_id"],
                "temperature-critical",
            ),
            title=(
                f'{machine["name"]} · Temperature anomaly'
            ),
            detail=(
                f'Temperature is {temperature["value"]}°C, '
                f'{temperature["deviation"]}°C away from the '
                f'expected {temperature["expected"]}°C.'
            ),
            time="Just now",
            severity="Critical",
            machine=machine["name"],
            machine_id=machine["machine_id"],
            timestamp=now,
            recommended_action=(
                "Inspect cooling, thermal loading, and "
                "temperature-control systems."
            ),
        )

    # =============================================================
    # WARNING CONDITIONS
    # =============================================================

    if power["status"] == "High":
        return AlertItem(
            id=generate_alert_id(
                machine["machine_id"],
                "power-warning",
            ),
            title=(
                f'{machine["name"]} · Elevated power draw'
            ),
            detail=(
                f'Power consumption is '
                f'{power["deviation_pct"]}% above the '
                f'baseline of {power["baseline"]} kW.'
            ),
            time="Just now",
            severity="Warning",
            machine=machine["name"],
            machine_id=machine["machine_id"],
            timestamp=now,
            recommended_action=(
                "Monitor power consumption and inspect "
                "the machine if the elevated draw persists."
            ),
        )

    if vibration["status"] == "Warning":
        return AlertItem(
            id=generate_alert_id(
                machine["machine_id"],
                "vibration-warning",
            ),
            title=(
                f'{machine["name"]} · Elevated vibration'
            ),
            detail=(
                f'Vibration is {vibration["value"]} mm/s '
                f'and is above the normal operating range.'
            ),
            time="Just now",
            severity="Warning",
            machine=machine["name"],
            machine_id=machine["machine_id"],
            timestamp=now,
            recommended_action=(
                "Monitor vibration and inspect rotating "
                "components during the next maintenance window."
            ),
        )

    if temperature["status"] == "Warning":
        return AlertItem(
            id=generate_alert_id(
                machine["machine_id"],
                "temperature-warning",
            ),
            title=(
                f'{machine["name"]} · Temperature deviation'
            ),
            detail=(
                f'Temperature is {temperature["value"]}°C, '
                f'{temperature["deviation"]}°C away from the '
                f'expected {temperature["expected"]}°C.'
            ),
            time="Just now",
            severity="Warning",
            machine=machine["name"],
            machine_id=machine["machine_id"],
            timestamp=now,
            recommended_action=(
                "Monitor temperature and inspect thermal "
                "conditions if the deviation continues."
            ),
        )

    return None


def get_alert_history() -> List[Dict[str, Any]]:
    """
    Return current alerts generated from the latest database telemetry.

    No historical mock alerts are included.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT DISTINCT ON (m.machine_id)
                    m.machine_id,
                    m.name,
                    m.machine_type,
                    m.baseline_power_kw,
                    t.power_kw,
                    t.temperature_c,
                    t.vibration_mms,
                    t.timestamp
                FROM machines m
                JOIN machine_telemetry t
                    ON m.machine_id = t.machine_id
                ORDER BY
                    m.machine_id,
                    t.timestamp DESC;
            """)

            rows = cur.fetchall()

            alerts = []

            for row in rows:

                (
                    machine_id,
                    name,
                    machine_type,
                    baseline_power_kw,
                    power_kw,
                    temperature_c,
                    vibration_mms,
                    timestamp,
                ) = row

                machine = {
                    "machine_id": machine_id,
                    "name": name,
                    "machine_type": machine_type,
                    "baseline_power_kw": float(
                        baseline_power_kw
                    ),
                    "power_kw": float(power_kw),
                    "temperature_c": float(
                        temperature_c
                    ),
                    "vibration_mms": float(
                        vibration_mms
                    ),
                    "telemetry_timestamp": timestamp,
                }

                alert = generate_machine_alert(machine)

                if alert:
                    alerts.append(
                        alert.model_dump()
                    )

            # Critical alerts first, then warnings.
            severity_order = {
                "Critical": 0,
                "Warning": 1,
                "Resolved": 2,
                "Info": 3,
            }

            alerts.sort(
                key=lambda alert: severity_order.get(
                    alert["severity"],
                    99
                )
            )

            return alerts

    finally:
        conn.close()