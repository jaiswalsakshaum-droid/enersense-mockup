from app.services.machine_health import get_machine_health
from app.database.connection import get_connection
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.machines import Machine, MachineDetail
from app.data.machines import MACHINES_DATA
from app.services.scoring import (
    calculate_machine_health_score,
    get_machine_status,
    get_health_factors,
)
router = APIRouter(prefix="/machines", tags=["Machines"])

@router.get("", response_model=List[Machine])
async def get_machines():
    """
    Retrieve all machines using the latest database-backed telemetry.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT DISTINCT ON (m.machine_id)
                    m.machine_id,
                    m.name,
                    m.machine_type,
                    m.production_line,
                    m.baseline_power_kw,
                    m.peak_power_kw,
                    m.status,
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

            machines = []

            for row in rows:

                (
                    machine_id,
                    name,
                    machine_type,
                    production_line,
                    baseline_power_kw,
                    peak_power_kw,
                    db_status,
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

                machines.append(
                    Machine(
                        id=machine_id,
                        name=name,
                        type=machine_type,
                        line=production_line,
                        score=score,
                        status=status,
                        maintenance=(
                            "Available"
                            if str(db_status).upper() == "AVAILABLE"
                            else str(db_status)
                        ),
                        reading=f"{power_kw:.1f} kW",
                        power_kw=power_kw,
                        temperature_c=temperature_c,
                        vibration_mms=vibration_mms,
                    )
                )

            return machines

    finally:
        conn.close()

@router.get("/{machine_id}/health")
async def get_machine_health_endpoint(machine_id: str):
    """
    Retrieve the latest database-backed telemetry and calculated
    health information for a machine.
    """
    health = get_machine_health(machine_id)

    if health is None:
        raise HTTPException(
            status_code=404,
            detail=f"Machine '{machine_id}' not found"
        )

    return health

@router.get("/{machine_id}", response_model=MachineDetail)
async def get_machine_detail(machine_id: str):
    """
    Retrieve database-backed machine details, latest telemetry,
    24-hour telemetry history, health factors and machine metadata.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # =====================================================
            # 1. Get machine metadata + latest telemetry
            # =====================================================
            cur.execute("""
                SELECT
                    m.machine_id,
                    m.name,
                    m.machine_type,
                    m.production_line,
                    m.baseline_power_kw,
                    m.peak_power_kw,
                    m.status,
                    latest.power_kw,
                    latest.temperature_c,
                    latest.vibration_mms,
                    latest.timestamp
                FROM machines m
                JOIN LATERAL (
                    SELECT
                        t.power_kw,
                        t.temperature_c,
                        t.vibration_mms,
                        t.timestamp
                    FROM machine_telemetry t
                    WHERE t.machine_id = m.machine_id
                    ORDER BY t.timestamp DESC
                    LIMIT 1
                ) latest ON TRUE
                WHERE m.machine_id = %s;
            """, (machine_id,))

            row = cur.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Machine '{machine_id}' not found"
                )

            (
                db_machine_id,
                name,
                machine_type,
                production_line,
                baseline_power_kw,
                peak_power_kw,
                db_status,
                power_kw,
                temperature_c,
                vibration_mms,
                latest_timestamp,
            ) = row

            baseline_power_kw = float(baseline_power_kw)
            peak_power_kw = float(peak_power_kw)
            power_kw = float(power_kw)
            temperature_c = float(temperature_c)
            vibration_mms = float(vibration_mms)

            # =====================================================
            # 2. Calculate health
            # =====================================================
            calculated_score = calculate_machine_health_score(
                power_kw=power_kw,
                baseline_kw=baseline_power_kw,
                vibration_mms=vibration_mms,
                temperature_c=temperature_c,
                machine_type=machine_type,
            )

            calculated_status = get_machine_status(
                calculated_score
            )

            health_factors = get_health_factors(
                power_kw=power_kw,
                baseline_kw=baseline_power_kw,
                vibration_mms=vibration_mms,
                temperature_c=temperature_c,
                machine_type=machine_type,
            )

            # =====================================================
            # 3. Get last 24 hours of telemetry
            # =====================================================
            cur.execute("""
                SELECT
                    timestamp,
                    power_kw,
                    temperature_c,
                    vibration_mms
                FROM machine_telemetry
                WHERE machine_id = %s
                ORDER BY timestamp ASC;
            """, (machine_id,))

            telemetry_rows = cur.fetchall()

            recent_readings = []

            for telemetry in telemetry_rows:

                (
                    timestamp,
                    telemetry_power,
                    telemetry_temperature,
                    telemetry_vibration,
                ) = telemetry

                recent_readings.append({
                    "timestamp": timestamp.isoformat(),
                    "power_kw": float(telemetry_power),
                    "temperature_c": float(
                        telemetry_temperature
                    ),
                    "vibration_mms": float(
                        telemetry_vibration
                    ),
                })

            # =====================================================
            # 4. Calculate 24-hour average and peak
            # =====================================================
            power_values = [
                float(row[1])
                for row in telemetry_rows
            ]

            if power_values:

                avg_24h_power_kw = round(
                    sum(power_values) / len(power_values),
                    2
                )

                telemetry_peak_kw = max(
                    power_values
                )

            else:

                avg_24h_power_kw = power_kw
                telemetry_peak_kw = power_kw

            # Use the higher of configured machine peak and
            # observed telemetry peak.
            effective_peak_kw = max(
                peak_power_kw,
                telemetry_peak_kw
            )

            # =====================================================
            # 5. Return machine detail
            # =====================================================
            return MachineDetail(
                id=db_machine_id,
                name=name,
                type=machine_type,
                line=production_line,
                score=calculated_score,
                status=calculated_status,

                maintenance=(
                    "Available"
                    if str(db_status).upper() == "AVAILABLE"
                    else str(db_status)
                ),

                reading=f"{power_kw:.1f} kW",

                power_kw=power_kw,
                temperature_c=temperature_c,
                vibration_mms=vibration_mms,

                baseline_power_kw=baseline_power_kw,

                peak_power_kw=round(
                    effective_peak_kw,
                    2
                ),

                avg_24h_power_kw=avg_24h_power_kw,

                health_factors=health_factors,

                recent_readings=recent_readings,

                history_readings_24h=[
                    round(value, 2)
                    for value in power_values
                ],

                # Maintenance history is empty for now because
                # there is currently no maintenance-history table
                # in PostgreSQL.
                maintenance_history=[],
            )

    finally:
        conn.close()
    """
    Retrieve single machine telemetry details, 24h trend values,
    recent readings, and service logs.
    """
    machine = next((m for m in MACHINES_DATA if m["id"] == machine_id), None)

    if not machine:
        raise HTTPException(
            status_code=404,
            detail=f"Machine '{machine_id}' not found"
        )

    calculated_score = calculate_machine_health_score(
        power_kw=machine["power_kw"],
        baseline_kw=machine["baseline_power_kw"],
        vibration_mms=machine["vibration_mms"],
        temperature_c=machine["temperature_c"],
        machine_type=machine["type"],
    )

    calculated_status = get_machine_status(calculated_score)

    health_factors = get_health_factors(
    power_kw=machine["power_kw"],
    baseline_kw=machine["baseline_power_kw"],
    vibration_mms=machine["vibration_mms"],
    temperature_c=machine["temperature_c"],
    machine_type=machine["type"],
)

    machine_detail = machine.copy()
    machine_detail["score"] = calculated_score
    machine_detail["status"] = calculated_status
    machine_detail["health_factors"] = health_factors

    return MachineDetail(**machine_detail)
