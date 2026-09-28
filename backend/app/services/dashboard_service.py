from app.database.connection import get_connection
from app.services.scoring import (
    calculate_machine_health_score,
    get_machine_status,
)


def get_dashboard_summary():
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # =========================================================
            # 1. Get the latest telemetry for every machine
            # =========================================================
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
                ORDER BY m.machine_id, t.timestamp DESC;
            """)

            machines = cur.fetchall()

            if not machines:
                raise RuntimeError(
                    "No machine telemetry available"
                )

            # =========================================================
            # 2. Calculate current plant health
            # =========================================================
            machine_scores = []
            warning_count = 0
            critical_count = 0

            machine_states = []

            for row in machines:

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

                baseline_power_kw = float(baseline_power_kw)
                power_kw = float(power_kw)
                temperature_c = float(temperature_c)
                vibration_mms = float(vibration_mms)

                score = calculate_machine_health_score(
                    power_kw=power_kw,
                    baseline_kw=baseline_power_kw,
                    vibration_mms=vibration_mms,
                    temperature_c=temperature_c,
                    machine_type=machine_type,
                )

                status = get_machine_status(score)

                machine_scores.append(score)

                if status == "Warning":
                    warning_count += 1

                elif status == "Critical":
                    critical_count += 1

                machine_states.append({
                    "machine_id": machine_id,
                    "name": name,
                    "score": score,
                    "status": status,
                    "power_kw": power_kw,
                    "timestamp": timestamp,
                })

            # Average health of all monitored machines
            health_score = round(
                sum(machine_scores) / len(machine_scores)
            )

            active_alerts_count = (
                warning_count + critical_count
            )

            # =========================================================
            # 3. Find the telemetry date available in the database
            # =========================================================
            cur.execute("""
                SELECT MAX(timestamp)::date
                FROM machine_telemetry;
            """)

            telemetry_date = cur.fetchone()[0]

            if telemetry_date is None:
                raise RuntimeError(
                    "No telemetry date available"
                )

            # =========================================================
            # 4. Get hourly plant energy data
            #
            # Each telemetry reading represents the machine's
            # power during that one-hour interval.
            #
            # Therefore:
            #     kW × 1 hour = kWh
            # =========================================================
            cur.execute("""
                SELECT
                    EXTRACT(HOUR FROM t.timestamp)::int AS hour,
                    SUM(t.power_kw) AS plant_power_kw,
                    SUM(m.baseline_power_kw) AS baseline_power_kw,

                    SUM(
                        t.power_kw
                    ) AS energy_kwh,

                    SUM(
                        t.power_kw * COALESCE(
                            (
                                SELECT et.price_per_kwh
                                FROM energy_tariffs et
                                WHERE et.factory_id = m.factory_id
                                  AND et.start_time <= t.timestamp::time
                                  AND et.end_time >= t.timestamp::time
                                ORDER BY et.start_time DESC
                                LIMIT 1
                            ),
                            7.20
                        )
                    ) AS energy_cost_inr,

                    SUM(
                        t.power_kw * COALESCE(
                            (
                                SELECT et.carbon_factor_kg_per_kwh
                                FROM energy_tariffs et
                                WHERE et.factory_id = m.factory_id
                                  AND et.start_time <= t.timestamp::time
                                  AND et.end_time >= t.timestamp::time
                                ORDER BY et.start_time DESC
                                LIMIT 1
                            ),
                            0.70
                        )
                    ) AS carbon_kg

                FROM machine_telemetry t
                JOIN machines m
                    ON m.machine_id = t.machine_id

                WHERE t.timestamp::date = %s

                GROUP BY EXTRACT(HOUR FROM t.timestamp)::int

                ORDER BY hour;
            """, (telemetry_date,))

            hourly_rows = cur.fetchall()

            # =========================================================
            # 5. Build 24-hour arrays
            # =========================================================
            hourly_data = {}

            for row in hourly_rows:

                (
                    hour,
                    plant_power_kw,
                    baseline_power_kw,
                    energy_kwh,
                    energy_cost_inr,
                    carbon_kg,
                ) = row

                hourly_data[int(hour)] = {
                    "power_kw": float(plant_power_kw or 0),
                    "baseline_kw": float(
                        baseline_power_kw or 0
                    ),
                    "energy_kwh": float(
                        energy_kwh or 0
                    ),
                    "cost_inr": float(
                        energy_cost_inr or 0
                    ),
                    "carbon_kg": float(
                        carbon_kg or 0
                    ),
                }

            energy_trend_24h = []
            baseline_trend_24h = []

            total_energy_kwh = 0.0
            total_cost_inr = 0.0
            total_carbon_kg = 0.0

            for hour in range(24):

                data = hourly_data.get(
                    hour,
                    {
                        "power_kw": 0.0,
                        "baseline_kw": 0.0,
                        "energy_kwh": 0.0,
                        "cost_inr": 0.0,
                        "carbon_kg": 0.0,
                    },
                )

                energy_trend_24h.append(
                    round(data["power_kw"], 2)
                )

                baseline_trend_24h.append(
                    round(data["baseline_kw"], 2)
                )

                total_energy_kwh += data["energy_kwh"]
                total_cost_inr += data["cost_inr"]
                total_carbon_kg += data["carbon_kg"]

            # =========================================================
            # 6. Build dynamic alerts
            # =========================================================
            latest_alerts = []

            for machine in machine_states:

                if machine["status"] == "Critical":

                    latest_alerts.append({
                        "id": hash(
                            f'{machine["machine_id"]}:critical'
                        ) & 0x7FFFFFFF,

                        "machine_name": machine["name"],

                        "detail": (
                            "Machine health is in the "
                            "critical range."
                        ),

                        "time": "Just now",
                        "severity": "Critical",
                    })

                elif machine["status"] == "Warning":

                    latest_alerts.append({
                        "id": hash(
                            f'{machine["machine_id"]}:warning'
                        ) & 0x7FFFFFFF,

                        "machine_name": machine["name"],

                        "detail": (
                            "Machine health requires "
                            "attention."
                        ),

                        "time": "Just now",
                        "severity": "Warning",
                    })

            # =========================================================
            # 7. Return dashboard response
            # =========================================================
            return {

                "plant_name": "Rajkot Foundry Unit",

                "health_score": health_score,
                "score_target": 80,
                "health_change_pct": 0.0,

                "energy_use_today_kwh": round(
                    total_energy_kwh,
                    2
                ),

                "energy_use_change_pct": 0.0,

                "energy_cost_today_inr": round(
                    total_cost_inr,
                    2
                ),

                "energy_cost_change_pct": 0.0,

                "co2e_today_tons": round(
                    total_carbon_kg / 1000,
                    3
                ),

                "co2e_change_pct": 0.0,

                "active_alerts_count": active_alerts_count,

                "active_alerts_change": (
                    f"{active_alerts_count} active"
                ),

                "energy_trend_24h": energy_trend_24h,

                "baseline_trend_24h": baseline_trend_24h,

                # Benchmark remains demo data because
                # we do not currently have a real external
                # benchmark dataset.
                "peer_benchmark": {

                    "plant_score": health_score,

                    "peer_average_score": 74,

                    "peer_top_quartile": 89,

                    "industry_label": (
                        "SME Induction Foundries (< 500 kW)"
                    ),

                    "percentile": 84,

                    "comparison_text": (
                        "Benchmark data is currently "
                        "demo data."
                    ),
                },

                "latest_alerts": latest_alerts,
            }

    finally:
        conn.close()