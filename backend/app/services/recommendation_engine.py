from typing import Any, Dict, List

from app.database.connection import get_connection


FACTORY_ID = "FAC-001"

# These are engineering estimates, not measured savings.
# They are intentionally conservative so the audit does not present
# simulated savings as historical fact.
COMPRESSOR_SAVING_RATE = 0.08
COOLING_TOWER_SAVING_RATE = 0.12
FURNACE_SAVING_RATE = 0.08
OFF_PEAK_SHIFT_RATE = 0.20

COMPRESSOR_CAPEX = 8500.0
COOLING_TOWER_CAPEX = 102000.0
FURNACE_CAPEX = 102600.0


def _money(value: float) -> str:
    return f"₹{value:,.0f} / mo"


def _kwh(value: float) -> str:
    return f"{value:,.0f} kWh / mo"


def _payback(capex: float, monthly_saving: float) -> float:
    if capex <= 0:
        return 0.0

    if monthly_saving <= 0:
        return 999.0

    return round(capex / monthly_saving, 1)


def _payback_text(months: float, capex: float) -> str:
    if capex == 0:
        return "Immediate"

    if months >= 999:
        return "N/A"

    return f"{months:.1f} months"


def _get_machine_energy() -> Dict[str, Dict[str, float]]:
    """
    Get the latest 24 telemetry readings for each machine and calculate
    average power.

    Returns:
        {
            "Air Compressor": {
                "avg_power_kw": ...,
                "latest_power_kw": ...,
                "latest_vibration": ...,
                "latest_temperature": ...
            },
            ...
        }
    """

    query = """
        WITH ranked AS (
            SELECT
                m.machine_id,
                m.machine_type,
                t.power_kw,
                t.temperature_c,
                t.vibration_mms,
                t.timestamp,
                ROW_NUMBER() OVER (
                    PARTITION BY t.machine_id
                    ORDER BY t.timestamp DESC
                ) AS rn
            FROM machine_telemetry t
            JOIN machines m
                ON m.machine_id = t.machine_id
        )
        SELECT
            machine_id,
            machine_type,
            AVG(power_kw) AS avg_power_kw,
            MAX(power_kw) FILTER (WHERE rn = 1) AS latest_power_kw,
            MAX(temperature_c) FILTER (WHERE rn = 1) AS latest_temperature_c,
            MAX(vibration_mms) FILTER (WHERE rn = 1) AS latest_vibration_mms
        FROM ranked
        WHERE rn <= 24
        GROUP BY machine_id, machine_type
    """

    result: Dict[str, Dict[str, float]] = {}

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)

            for row in cur.fetchall():
                (
                    machine_id,
                    machine_type,
                    avg_power,
                    latest_power,
                    latest_temperature,
                    latest_vibration,
                ) = row

                result[str(machine_type)] = {
                    "machine_id": str(machine_id),
                    "avg_power_kw": float(avg_power or 0),
                    "latest_power_kw": float(latest_power or 0),
                    "latest_temperature_c": float(latest_temperature or 0),
                    "latest_vibration_mms": float(latest_vibration or 0),
                }

    return result


def _get_tariffs() -> List[Dict[str, Any]]:
    """
    Read the plant's tariff schedule from PostgreSQL.
    """

    query = """
        SELECT
            start_time,
            end_time,
            price_per_kwh
        FROM energy_tariffs
        WHERE factory_id = %s
        ORDER BY start_time
    """

    tariffs: List[Dict[str, Any]] = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (FACTORY_ID,))

            for start_time, end_time, price_per_kwh in cur.fetchall():
                tariffs.append(
                    {
                        "start_time": start_time,
                        "end_time": end_time,
                        "price_per_kwh": float(price_per_kwh),
                    }
                )

    return tariffs


def _weighted_tariff(tariffs: List[Dict[str, Any]]) -> float:
    """
    Calculate a time-weighted average tariff across the configured day.
    """

    if not tariffs:
        return 0.0

    total_hours = 0.0
    weighted_cost = 0.0

    for tariff in tariffs:
        start = tariff["start_time"]
        end = tariff["end_time"]

        start_minutes = start.hour * 60 + start.minute + start.second / 60
        end_minutes = end.hour * 60 + end.minute + end.second / 60

        # Handle a tariff that crosses midnight.
        if end_minutes <= start_minutes:
            end_minutes += 24 * 60

        hours = (end_minutes - start_minutes) / 60.0

        total_hours += hours
        weighted_cost += hours * tariff["price_per_kwh"]

    if total_hours == 0:
        return 0.0

    return weighted_cost / total_hours


def _off_peak_tariff(tariffs: List[Dict[str, Any]]) -> float:
    """
    Return the lowest configured tariff.
    """

    if not tariffs:
        return 0.0

    return min(t["price_per_kwh"] for t in tariffs)


def get_recommendations() -> List[Dict[str, Any]]:
    """
    Generate energy-audit opportunities from PostgreSQL telemetry
    and the configured energy tariff schedule.

    Savings are estimates derived from the available 24-hour telemetry.
    """

    machines = _get_machine_energy()
    tariffs = _get_tariffs()

    average_tariff = _weighted_tariff(tariffs)
    off_peak_tariff = _off_peak_tariff(tariffs)

    recommendations: List[Dict[str, Any]] = []

    # ---------------------------------------------------------
    # 1. COMPRESSED AIR
    # ---------------------------------------------------------

    compressor = machines.get("Air Compressor")

    if compressor:
        monthly_energy = (
            compressor["avg_power_kw"] * 24 * 30
        )

        monthly_saving_kwh = monthly_energy * COMPRESSOR_SAVING_RATE

        monthly_saving_inr = (
            monthly_saving_kwh * average_tariff
        )

        # Higher vibration makes this opportunity more relevant.
        vibration = compressor["latest_vibration_mms"]

        tag = "Quick win" if vibration >= 3.5 else "Maintenance"

        capex = COMPRESSOR_CAPEX
        payback_months = _payback(
            capex,
            monthly_saving_inr,
        )

        recommendations.append(
            {
                "rank": "01",
                "title": "Inspect compressed-air system for leaks and unload losses",
                "description": (
                    f"Compressor telemetry averages "
                    f"{compressor['avg_power_kw']:.1f} kW with "
                    f"{vibration:.2f} mm/s vibration. "
                    "Inspect the pneumatic network and compressor unloading "
                    "cycles for avoidable energy use."
                ),
                "saving": _kwh(monthly_saving_kwh),
                "rupees": _money(monthly_saving_inr),
                "payback": _payback_text(payback_months, capex),
                "tag": tag,
                "annual_saving_kwh": round(monthly_saving_kwh * 12, 2),
                "monthly_saving_inr": round(monthly_saving_inr, 2),
                "payback_months": payback_months,
                "capex_inr": capex,
            }
        )

    # ---------------------------------------------------------
    # 2. COOLING TOWER
    # ---------------------------------------------------------

    cooling_tower = machines.get("Cooling Tower")

    if cooling_tower:
        monthly_energy = (
            cooling_tower["avg_power_kw"] * 24 * 30
        )

        monthly_saving_kwh = (
            monthly_energy * COOLING_TOWER_SAVING_RATE
        )

        monthly_saving_inr = (
            monthly_saving_kwh * average_tariff
        )

        capex = COOLING_TOWER_CAPEX

        payback_months = _payback(
            capex,
            monthly_saving_inr,
        )

        recommendations.append(
            {
                "rank": "02",
                "title": "Install VFD on cooling tower fan",
                "description": (
                    f"Cooling tower telemetry averages "
                    f"{cooling_tower['avg_power_kw']:.1f} kW. "
                    "A variable-frequency drive can reduce fan speed "
                    "during partial-load operation."
                ),
                "saving": _kwh(monthly_saving_kwh),
                "rupees": _money(monthly_saving_inr),
                "payback": _payback_text(payback_months, capex),
                "tag": "High impact",
                "annual_saving_kwh": round(monthly_saving_kwh * 12, 2),
                "monthly_saving_inr": round(monthly_saving_inr, 2),
                "payback_months": payback_months,
                "capex_inr": capex,
            }
        )

    # ---------------------------------------------------------
    # 3. INDUCTION FURNACE
    # ---------------------------------------------------------

    furnace = machines.get("Induction Furnace")

    if furnace:
        monthly_energy = (
            furnace["avg_power_kw"] * 24 * 30
        )

        monthly_saving_kwh = (
            monthly_energy * FURNACE_SAVING_RATE
        )

        monthly_saving_inr = (
            monthly_saving_kwh * average_tariff
        )

        capex = FURNACE_CAPEX

        payback_months = _payback(
            capex,
            monthly_saving_inr,
        )

        temperature = furnace["latest_temperature_c"]

        recommendations.append(
            {
                "rank": "03",
                "title": "Improve furnace door seals and insulation",
                "description": (
                    f"Furnace telemetry averages "
                    f"{furnace['avg_power_kw']:.1f} kW and the latest "
                    f"temperature is {temperature:.1f} °C. "
                    "Inspect door seals and insulation to reduce avoidable "
                    "thermal losses during heating."
                ),
                "saving": _kwh(monthly_saving_kwh),
                "rupees": _money(monthly_saving_inr),
                "payback": _payback_text(payback_months, capex),
                "tag": "Maintenance",
                "annual_saving_kwh": round(monthly_saving_kwh * 12, 2),
                "monthly_saving_inr": round(monthly_saving_inr, 2),
                "payback_months": payback_months,
                "capex_inr": capex,
            }
        )

    # ---------------------------------------------------------
    # 4. OFF-PEAK OPERATION
    # ---------------------------------------------------------

    if furnace and average_tariff > 0 and off_peak_tariff > 0:

        monthly_furnace_energy = (
            furnace["avg_power_kw"] * 24 * 30
        )

        shiftable_energy = (
            monthly_furnace_energy * OFF_PEAK_SHIFT_RATE
        )

        tariff_difference = max(
            average_tariff - off_peak_tariff,
            0.0,
        )

        monthly_saving_inr = (
            shiftable_energy * tariff_difference
        )

        recommendations.append(
            {
                "rank": "04",
                "title": "Shift batch pre-heating to off-peak hours",
                "description": (
                    f"The configured tariff schedule ranges down to "
                    f"₹{off_peak_tariff:.2f}/kWh during the lowest-cost period. "
                    "Where production constraints allow, shift pre-heating "
                    "to those lower-tariff hours."
                ),
                "saving": "—",
                "rupees": _money(monthly_saving_inr),
                "payback": "Immediate",
                "tag": "No capex",
                "annual_saving_kwh": 0.0,
                "monthly_saving_inr": round(monthly_saving_inr, 2),
                "payback_months": 0.0,
                "capex_inr": 0.0,
            }
        )

    # Keep the audit ordered by estimated financial impact.
    recommendations.sort(
        key=lambda item: item["monthly_saving_inr"],
        reverse=True,
    )

    # Re-number after ranking.
    for index, item in enumerate(recommendations, start=1):
        item["rank"] = f"{index:02d}"

    return recommendations