"""
Simulation Service for EnerSense What-If Calculator.

Uses plant telemetry and configured energy tariffs from PostgreSQL to
calculate deterministic what-if scenarios:

1. Load Shifting
2. Equipment Upgrade
3. Process & Leak Rectification

The calculations are engineering estimates, not measured savings.
"""

from typing import Dict, Any, Tuple

from app.models.simulate import SimulateResponse, InterventionType
from app.database.connection import get_connection


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _get_plant_baseline_kwh() -> float:
    """
    Estimate monthly plant energy consumption from the latest 24 telemetry
    readings for each machine.

    Formula:
        average plant power (kW) × 24 hours × 30 days
    """

    query = """
        WITH ranked AS (
            SELECT
                mt.machine_id,
                mt.power_kw,
                mt.timestamp,
                ROW_NUMBER() OVER (
                    PARTITION BY mt.machine_id
                    ORDER BY mt.timestamp DESC
                ) AS rn
            FROM machine_telemetry mt
        ),
        machine_average AS (
            SELECT
                machine_id,
                AVG(power_kw) AS avg_power_kw
            FROM ranked
            WHERE rn <= 24
            GROUP BY machine_id
        )
        SELECT COALESCE(SUM(avg_power_kw) * 24 * 30, 0)
        FROM machine_average;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()

    baseline_kwh = float(result[0] or 0)

    if baseline_kwh <= 0:
        raise ValueError("No valid telemetry data is available for simulation.")

    return baseline_kwh


def _get_weighted_tariff() -> float:
    """
    Calculate the time-weighted average tariff for FAC-001.

    The weighting is based on the duration of each configured tariff period.
    """

    query = """
        SELECT
            start_time,
            end_time,
            price_per_kwh
        FROM energy_tariffs
        WHERE factory_id = 'FAC-001'
        ORDER BY start_time;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    if not rows:
        raise ValueError("No energy tariff data is configured for FAC-001.")

    total_hours = 0.0
    weighted_cost = 0.0

    for start_time, end_time, price_per_kwh in rows:
        start_seconds = (
            start_time.hour * 3600
            + start_time.minute * 60
            + start_time.second
        )

        end_seconds = (
            end_time.hour * 3600
            + end_time.minute * 60
            + end_time.second
        )

        # Handle a tariff that crosses midnight.
        if end_seconds <= start_seconds:
            end_seconds += 24 * 3600

        duration_hours = (end_seconds - start_seconds) / 3600.0

        total_hours += duration_hours
        weighted_cost += duration_hours * float(price_per_kwh)

    if total_hours <= 0:
        raise ValueError("Invalid energy tariff durations.")

    return weighted_cost / total_hours


def _get_peak_and_off_peak_tariffs() -> Tuple[float, float]:
    """
    Return the highest and lowest configured tariff for FAC-001.
    """

    query = """
        SELECT
            MAX(price_per_kwh),
            MIN(price_per_kwh)
        FROM energy_tariffs
        WHERE factory_id = 'FAC-001';
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            peak, off_peak = cur.fetchone()

    if peak is None or off_peak is None:
        raise ValueError("No energy tariff data is configured for FAC-001.")

    return float(peak), float(off_peak)


# ---------------------------------------------------------------------------
# Main dispatcher
# ---------------------------------------------------------------------------

def calculate_simulation(
    intervention_type: InterventionType,
    params: Dict[str, Any],
) -> SimulateResponse:
    """
    Execute a deterministic what-if calculation.
    """

    if intervention_type == "load_shift":
        return _calculate_load_shift(params)

    if intervention_type == "equipment_upgrade":
        return _calculate_equipment_upgrade(params)

    if intervention_type == "process_change":
        return _calculate_process_change(params)

    raise ValueError(
        f"Unsupported intervention type: {intervention_type}"
    )


# ---------------------------------------------------------------------------
# 1. Load shifting
# ---------------------------------------------------------------------------

def _calculate_load_shift(params: Dict[str, Any]) -> SimulateResponse:
    """
    Calculate savings from moving production energy consumption from a
    high-tariff period to a lower-tariff period.

    Important:
        Load shifting does NOT reduce physical energy consumption.
        It reduces the electricity bill by changing when the energy is used.
    """

    shift_kwh_per_day = float(
        params.get("shift_kwh_per_day", 450.0)
    )

    operating_days_per_month = float(
        params.get("operating_days_per_month", 26.0)
    )

    automation_capex_inr = float(
        params.get("automation_capex_inr", 15000.0)
    )

    # Use actual database tariffs when available.
    configured_peak, configured_off_peak = _get_peak_and_off_peak_tariffs()

    peak_tariff_inr = float(
        params.get("peak_tariff_inr", configured_peak)
    )

    off_peak_tariff_inr = float(
        params.get("off_peak_tariff_inr", configured_off_peak)
    )

    # Plant baseline comes from telemetry.
    total_baseline_kwh = _get_plant_baseline_kwh()

    # Weighted average tariff represents the plant's configured tariff mix.
    weighted_tariff = _get_weighted_tariff()

    monthly_kwh_shifted = (
        shift_kwh_per_day * operating_days_per_month
    )

    # Don't allow the scenario to shift more energy than the plant consumes.
    monthly_kwh_shifted = min(
        monthly_kwh_shifted,
        total_baseline_kwh,
    )

    tariff_difference = max(
        peak_tariff_inr - off_peak_tariff_inr,
        0.0,
    )

    monthly_savings_inr = (
        monthly_kwh_shifted * tariff_difference
    )

    baseline_cost = (
        total_baseline_kwh * weighted_tariff
    )

    projected_cost = (
        baseline_cost - monthly_savings_inr
    )

    payback_months = (
        round(
            automation_capex_inr / monthly_savings_inr,
            1,
        )
        if monthly_savings_inr > 0 and automation_capex_inr > 0
        else 0.0
    )

    # Pure tariff shifting does not reduce kWh.
    # Therefore direct CO2 reduction is zero unless time-specific
    # carbon factors are introduced later.
    co2_saved_tons_year = 0.0

    return SimulateResponse(
        intervention_type="load_shift",
        intervention_title=(
            "ToD Tariff Load Shifting "
            "(Off-Peak Batch Scheduling)"
        ),
        baseline_kwh=round(total_baseline_kwh, 1),
        projected_kwh=round(total_baseline_kwh, 1),
        kwh_saved_monthly=0.0,
        percent_reduction=0.0,
        baseline_cost_rupees_per_month=round(
            baseline_cost,
            0,
        ),
        projected_cost_rupees_per_month=round(
            projected_cost,
            0,
        ),
        projected_savings_rupees_per_month=round(
            monthly_savings_inr,
            0,
        ),
        estimated_capex_rupees=round(
            automation_capex_inr,
            0,
        ),
        payback_months=payback_months,
        co2_reduction_tons_per_year=co2_saved_tons_year,
        summary=(
            f"Shifting {int(shift_kwh_per_day):,} kWh/day "
            f"to the off-peak tariff of "
            f"₹{off_peak_tariff_inr:.2f}/kWh reduces the monthly "
            f"electricity bill by approximately "
            f"₹{int(monthly_savings_inr):,}, "
            f"with an estimated {payback_months}-month payback."
        ),
        breakdown={
            "monthly_kwh_shifted": round(
                monthly_kwh_shifted,
                1,
            ),
            "tariff_differential_inr": round(
                tariff_difference,
                2,
            ),
            "peak_tariff": round(
                peak_tariff_inr,
                2,
            ),
            "off_peak_tariff": round(
                off_peak_tariff_inr,
                2,
            ),
            "weighted_plant_tariff": round(
                weighted_tariff,
                4,
            ),
            "energy_impact": "No kWh reduction; tariff shift only",
        },
    )


# ---------------------------------------------------------------------------
# 2. Equipment upgrade
# ---------------------------------------------------------------------------

def _calculate_equipment_upgrade(
    params: Dict[str, Any],
) -> SimulateResponse:
    """
    Calculate energy and cost savings from an efficiency improvement such
    as a VFD or IE4 motor.

    The user controls the assumed motor load, efficiency improvement and
    capex. Electricity tariff comes from the database unless explicitly
    overridden for scenario testing.
    """

    connected_load_kw = float(
        params.get("connected_load_kw", 75.0)
    )

    operating_hours_per_day = float(
        params.get("operating_hours_per_day", 16.0)
    )

    days_per_month = float(
        params.get("days_per_month", 26.0)
    )

    efficiency_gain_pct = float(
        params.get("efficiency_gain_pct", 18.0)
    )

    capex_inr = float(
        params.get("capex_inr", 115000.0)
    )

    # Use database tariff as the default.
    database_tariff = _get_weighted_tariff()

    avg_tariff_inr = float(
        params.get("avg_tariff_inr", database_tariff)
    )

    total_baseline_kwh = _get_plant_baseline_kwh()

    monthly_operating_hours = (
        operating_hours_per_day * days_per_month
    )

    baseline_equipment_monthly_kwh = (
        connected_load_kw * monthly_operating_hours
    )

    kwh_saved_monthly = (
        baseline_equipment_monthly_kwh
        * (efficiency_gain_pct / 100.0)
    )

    # Never allow the scenario to save more energy than the plant consumes.
    kwh_saved_monthly = min(
        kwh_saved_monthly,
        total_baseline_kwh,
    )

    total_projected_kwh = (
        total_baseline_kwh - kwh_saved_monthly
    )

    percent_reduction = round(
        (kwh_saved_monthly / total_baseline_kwh) * 100.0,
        2,
    )

    monthly_savings_inr = (
        kwh_saved_monthly * avg_tariff_inr
    )

    baseline_cost = (
        total_baseline_kwh * avg_tariff_inr
    )

    projected_cost = (
        total_projected_kwh * avg_tariff_inr
    )

    payback_months = (
        round(
            capex_inr / monthly_savings_inr,
            1,
        )
        if monthly_savings_inr > 0 and capex_inr > 0
        else 0.0
    )

    # Current tariff table has a carbon factor of 0.70 kg/kWh.
    carbon_factor = 0.70

    co2_saved_tons_year = round(
        (kwh_saved_monthly * 12 * carbon_factor) / 1000.0,
        2,
    )

    return SimulateResponse(
        intervention_type="equipment_upgrade",
        intervention_title=(
            "Variable Frequency Drive (VFD) "
            "& IE4 Motor Retrofit"
        ),
        baseline_kwh=round(
            total_baseline_kwh,
            1,
        ),
        projected_kwh=round(
            total_projected_kwh,
            1,
        ),
        kwh_saved_monthly=round(
            kwh_saved_monthly,
            1,
        ),
        percent_reduction=percent_reduction,
        baseline_cost_rupees_per_month=round(
            baseline_cost,
            0,
        ),
        projected_cost_rupees_per_month=round(
            projected_cost,
            0,
        ),
        projected_savings_rupees_per_month=round(
            monthly_savings_inr,
            0,
        ),
        estimated_capex_rupees=round(
            capex_inr,
            0,
        ),
        payback_months=payback_months,
        co2_reduction_tons_per_year=co2_saved_tons_year,
        summary=(
            f"Applying a {efficiency_gain_pct:.0f}% efficiency "
            f"improvement to a {connected_load_kw:.0f} kW motor load "
            f"could reduce consumption by approximately "
            f"{int(kwh_saved_monthly):,} kWh/month and save "
            f"₹{int(monthly_savings_inr):,}/month."
        ),
        breakdown={
            "connected_load_kw": connected_load_kw,
            "monthly_operating_hours": round(
                monthly_operating_hours,
                1,
            ),
            "efficiency_gain_pct": efficiency_gain_pct,
            "average_tariff_inr": round(
                avg_tariff_inr,
                4,
            ),
            "annual_kwh_saved": round(
                kwh_saved_monthly * 12,
                0,
            ),
            "carbon_factor_kg_per_kwh": carbon_factor,
        },
    )


# ---------------------------------------------------------------------------
# 3. Process / leak rectification
# ---------------------------------------------------------------------------

def _calculate_process_change(
    params: Dict[str, Any],
) -> SimulateResponse:
    """
    Calculate energy savings from compressed-air leak rectification and
    associated process/thermal-loss improvements.
    """

    leak_count = float(
        params.get("leak_count", 6.0)
    )

    leak_loss_kw_per_point = float(
        params.get("leak_loss_kw_per_point", 1.8)
    )

    operating_hours_per_month = float(
        params.get("operating_hours_per_month", 420.0)
    )

    repair_capex_inr = float(
        params.get("repair_capex_inr", 9500.0)
    )

    database_tariff = _get_weighted_tariff()

    avg_tariff_inr = float(
        params.get("avg_tariff_inr", database_tariff)
    )

    total_baseline_kwh = _get_plant_baseline_kwh()

    total_wasted_kw = (
        leak_count * leak_loss_kw_per_point
    )

    kwh_saved_monthly = (
        total_wasted_kw
        * operating_hours_per_month
    )

    # Don't allow the calculated saving to exceed total plant consumption.
    kwh_saved_monthly = min(
        kwh_saved_monthly,
        total_baseline_kwh,
    )

    total_projected_kwh = (
        total_baseline_kwh - kwh_saved_monthly
    )

    percent_reduction = round(
        (kwh_saved_monthly / total_baseline_kwh) * 100.0,
        2,
    )

    monthly_savings_inr = (
        kwh_saved_monthly * avg_tariff_inr
    )

    baseline_cost = (
        total_baseline_kwh * avg_tariff_inr
    )

    projected_cost = (
        total_projected_kwh * avg_tariff_inr
    )

    payback_months = (
        round(
            repair_capex_inr / monthly_savings_inr,
            1,
        )
        if monthly_savings_inr > 0 and repair_capex_inr > 0
        else 0.0
    )

    carbon_factor = 0.70

    co2_saved_tons_year = round(
        (kwh_saved_monthly * 12 * carbon_factor) / 1000.0,
        2,
    )

    return SimulateResponse(
        intervention_type="process_change",
        intervention_title=(
            "Pneumatic Leak Rectification "
            "& Thermal Barrier Optimization"
        ),
        baseline_kwh=round(
            total_baseline_kwh,
            1,
        ),
        projected_kwh=round(
            total_projected_kwh,
            1,
        ),
        kwh_saved_monthly=round(
            kwh_saved_monthly,
            1,
        ),
        percent_reduction=percent_reduction,
        baseline_cost_rupees_per_month=round(
            baseline_cost,
            0,
        ),
        projected_cost_rupees_per_month=round(
            projected_cost,
            0,
        ),
        projected_savings_rupees_per_month=round(
            monthly_savings_inr,
            0,
        ),
        estimated_capex_rupees=round(
            repair_capex_inr,
            0,
        ),
        payback_months=payback_months,
        co2_reduction_tons_per_year=co2_saved_tons_year,
        summary=(
            f"Rectifying {int(leak_count)} pneumatic leak points "
            f"could recover approximately "
            f"{int(kwh_saved_monthly):,} kWh/month, "
            f"worth about ₹{int(monthly_savings_inr):,}/month."
        ),
        breakdown={
            "leak_count": leak_count,
            "loss_per_leak_kw": leak_loss_kw_per_point,
            "total_power_recovered_kw": round(
                total_wasted_kw,
                2,
            ),
            "monthly_operating_hours": round(
                operating_hours_per_month,
                1,
            ),
            "average_tariff_inr": round(
                avg_tariff_inr,
                4,
            ),
            "carbon_factor_kg_per_kwh": carbon_factor,
        },
    )