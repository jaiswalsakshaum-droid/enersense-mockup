from app.database.connection import get_connection

from app.services.scoring import (
    calculate_machine_health_score,
    get_health_factors,
    get_machine_status,
)


def get_machine_health(machine_id: str):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # Get machine information + latest telemetry
            cur.execute("""
                SELECT
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
                WHERE m.machine_id = %s
                ORDER BY t.timestamp DESC
                LIMIT 1;
            """, (machine_id,))

            row = cur.fetchone()

            if row is None:
                return None

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

            # PostgreSQL NUMERIC values are returned as Decimal.
            # Convert them to float before passing them to the scoring service.
            baseline_power_kw = float(baseline_power_kw)
            power_kw = float(power_kw)
            temperature_c = float(temperature_c)
            vibration_mms = float(vibration_mms)

            # Calculate health score using the existing scoring service
            score = calculate_machine_health_score(
                power_kw=power_kw,
                baseline_kw=baseline_power_kw,
                vibration_mms=vibration_mms,
                temperature_c=temperature_c,
                machine_type=machine_type,
            )

            # Calculate explainable health factors
            health_factors = get_health_factors(
                power_kw=power_kw,
                baseline_kw=baseline_power_kw,
                vibration_mms=vibration_mms,
                temperature_c=temperature_c,
                machine_type=machine_type,
            )

            # Convert score into Normal / Warning / Critical
            status = get_machine_status(score)

            return {
                "machine_id": machine_id,
                "name": name,
                "health_score": score,
                "health_status": status,
                "telemetry": {
                    "timestamp": timestamp,
                    "power_kw": power_kw,
                    "temperature_c": temperature_c,
                    "vibration_mms": vibration_mms,
                },
                "health_factors": health_factors,
            }

    finally:
        conn.close()