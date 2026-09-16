"""
Simulation Service for EnerSense What-If Calculator.

Provides deterministic calculations for industrial energy efficiency interventions:
1. Load Shifting (Time of Day / Peak to Off-Peak Tariff Optimization)
2. Equipment Upgrade (VFD, IE4 Super Premium Motors, Furnace Insulation)
3. Process & Leak Rectification (Compressed Air Leaks, Heat Loss Mitigation)

NOTE FOR PHASE 3:
This module is isolated so that deterministic heuristic calculations can be
seamlessly swapped with machine-learned surrogate models / thermodynamic physics models.
"""

from typing import Dict, Any
from app.models.simulate import SimulateResponse, InterventionType


def calculate_simulation(intervention_type: InterventionType, params: Dict[str, Any]) -> SimulateResponse:
    """
    Executes a deterministic what-if calculation based on intervention parameters.
    """
    if intervention_type == "load_shift":
        return _calculate_load_shift(params)
    elif intervention_type == "equipment_upgrade":
        return _calculate_equipment_upgrade(params)
    elif intervention_type == "process_change":
        return _calculate_process_change(params)
    else:
        raise ValueError(f"Unsupported intervention type: {intervention_type}")


def _calculate_load_shift(params: Dict[str, Any]) -> SimulateResponse:
    """
    Load Shift calculation:
    Calculates cost reduction by moving batch thermal pre-heating or high-energy
    processes from peak tariff periods (e.g. ₹9.80/kWh) to off-peak slots (e.g. ₹4.40/kWh).
    KWh consumption remains constant, but total rupee expenditure reduces.
    """
    shift_kwh_per_day = float(params.get("shift_kwh_per_day", 450.0))
    operating_days_per_month = float(params.get("operating_days_per_month", 26.0))
    peak_tariff_inr = float(params.get("peak_tariff_inr", 9.80))
    off_peak_tariff_inr = float(params.get("off_peak_tariff_inr", 4.40))
    automation_capex_inr = float(params.get("automation_capex_inr", 15000.0))  # Minor timer/PLC logic setup

    # Monthly shifted volume
    monthly_kwh_shifted = shift_kwh_per_day * operating_days_per_month
    total_baseline_kwh = float(params.get("baseline_kwh", 72000.0))  # Plant monthly kWh
    
    # Baseline cost for the shifted block vs Projected cost
    cost_before = monthly_kwh_shifted * peak_tariff_inr
    cost_after = monthly_kwh_shifted * off_peak_tariff_inr
    monthly_savings_inr = cost_before - cost_after

    total_baseline_cost = (total_baseline_kwh - monthly_kwh_shifted) * 8.20 + cost_before
    total_projected_cost = total_baseline_cost - monthly_savings_inr

    # Payback period in months
    payback_months = round(automation_capex_inr / max(monthly_savings_inr, 1.0), 1) if automation_capex_inr > 0 else 0.0

    # Grid CO2 emission reduction (minimal direct kWh reduction for pure load shifting, but off-peak grid is often cleaner)
    co2_saved_tons_year = round((monthly_kwh_shifted * 12 * 0.00015), 2)

    return SimulateResponse(
        intervention_type="load_shift",
        intervention_title="ToD Tariff Load Shifting (Off-Peak Batch Scheduling)",
        baseline_kwh=round(total_baseline_kwh, 1),
        projected_kwh=round(total_baseline_kwh, 1),  # Same energy, lower tariff
        kwh_saved_monthly=0.0,
        percent_reduction=0.0,
        baseline_cost_rupees_per_month=round(total_baseline_cost, 0),
        projected_cost_rupees_per_month=round(total_projected_cost, 0),
        projected_savings_rupees_per_month=round(monthly_savings_inr, 0),
        estimated_capex_rupees=automation_capex_inr,
        payback_months=payback_months,
        co2_reduction_tons_per_year=co2_saved_tons_year,
        summary=f"Shifting {int(shift_kwh_per_day)} kWh/day to off-peak tariff (₹{off_peak_tariff_inr}/unit) yields ₹{int(monthly_savings_inr):,} monthly bill reduction with a {payback_months}-month payback.",
        breakdown={
            "monthly_kwh_shifted": monthly_kwh_shifted,
            "tariff_differential_inr": peak_tariff_inr - off_peak_tariff_inr,
            "peak_tariff": peak_tariff_inr,
            "off_peak_tariff": off_peak_tariff_inr,
        }
    )


def _calculate_equipment_upgrade(params: Dict[str, Any]) -> SimulateResponse:
    """
    Equipment Upgrade calculation:
    Models replacing standard DOL motors with VFD or upgrading to IE4 motors / furnace coil insulation.
    """
    connected_load_kw = float(params.get("connected_load_kw", 75.0))
    operating_hours_per_day = float(params.get("operating_hours_per_day", 16.0))
    days_per_month = float(params.get("days_per_month", 26.0))
    efficiency_gain_pct = float(params.get("efficiency_gain_pct", 18.0))  # e.g., 18% with VFD on centrifugal loads
    avg_tariff_inr = float(params.get("avg_tariff_inr", 8.50))
    capex_inr = float(params.get("capex_inr", 115000.0))

    monthly_operating_hours = operating_hours_per_day * days_per_month
    baseline_equipment_monthly_kwh = connected_load_kw * monthly_operating_hours
    kwh_saved_monthly = baseline_equipment_monthly_kwh * (efficiency_gain_pct / 100.0)
    projected_equipment_monthly_kwh = baseline_equipment_monthly_kwh - kwh_saved_monthly

    total_baseline_kwh = float(params.get("baseline_kwh", 72000.0))
    total_projected_kwh = total_baseline_kwh - kwh_saved_monthly
    percent_reduction = round((kwh_saved_monthly / total_baseline_kwh) * 100.0, 2)

    monthly_savings_inr = kwh_saved_monthly * avg_tariff_inr
    baseline_cost = total_baseline_kwh * avg_tariff_inr
    projected_cost = total_projected_kwh * avg_tariff_inr

    payback_months = round(capex_inr / max(monthly_savings_inr, 1.0), 1)
    # 0.82 kg CO2 per kWh for Indian grid average
    co2_saved_tons_year = round((kwh_saved_monthly * 12 * 0.82) / 1000.0, 2)

    return SimulateResponse(
        intervention_type="equipment_upgrade",
        intervention_title="Variable Frequency Drive (VFD) & IE4 Motor Retrofit",
        baseline_kwh=round(total_baseline_kwh, 1),
        projected_kwh=round(total_projected_kwh, 1),
        kwh_saved_monthly=round(kwh_saved_monthly, 1),
        percent_reduction=percent_reduction,
        baseline_cost_rupees_per_month=round(baseline_cost, 0),
        projected_cost_rupees_per_month=round(projected_cost, 0),
        projected_savings_rupees_per_month=round(monthly_savings_inr, 0),
        estimated_capex_rupees=capex_inr,
        payback_months=payback_months,
        co2_reduction_tons_per_year=co2_saved_tons_year,
        summary=f"Installing VFD/IE4 upgrade cuts monthly consumption by {int(kwh_saved_monthly):,} kWh ({percent_reduction}% plant reduction), saving ₹{int(monthly_savings_inr):,}/mo with payback in {payback_months} months.",
        breakdown={
            "connected_load_kw": connected_load_kw,
            "monthly_operating_hours": monthly_operating_hours,
            "efficiency_gain_pct": efficiency_gain_pct,
            "annual_kwh_saved": round(kwh_saved_monthly * 12, 0),
        }
    )


def _calculate_process_change(params: Dict[str, Any]) -> SimulateResponse:
    """
    Process & Leak Rectification calculation:
    Models fixing compressed air pneumatic leaks and optimizing furnace heat barrier seals.
    """
    leak_count = float(params.get("leak_count", 6.0))
    leak_loss_kw_per_point = float(params.get("leak_loss_kw_per_point", 1.8))
    operating_hours_per_month = float(params.get("operating_hours_per_month", 420.0))
    avg_tariff_inr = float(params.get("avg_tariff_inr", 8.50))
    repair_capex_inr = float(params.get("repair_capex_inr", 9500.0))

    total_wasted_kw = leak_count * leak_loss_kw_per_point
    kwh_saved_monthly = total_wasted_kw * operating_hours_per_month
    total_baseline_kwh = float(params.get("baseline_kwh", 72000.0))
    total_projected_kwh = total_baseline_kwh - kwh_saved_monthly
    percent_reduction = round((kwh_saved_monthly / total_baseline_kwh) * 100.0, 2)

    monthly_savings_inr = kwh_saved_monthly * avg_tariff_inr
    baseline_cost = total_baseline_kwh * avg_tariff_inr
    projected_cost = total_projected_kwh * avg_tariff_inr

    payback_months = round(repair_capex_inr / max(monthly_savings_inr, 1.0), 1)
    co2_saved_tons_year = round((kwh_saved_monthly * 12 * 0.82) / 1000.0, 2)

    return SimulateResponse(
        intervention_type="process_change",
        intervention_title="Pneumatic Leak Rectification & Thermal Barrier Optimization",
        baseline_kwh=round(total_baseline_kwh, 1),
        projected_kwh=round(total_projected_kwh, 1),
        kwh_saved_monthly=round(kwh_saved_monthly, 1),
        percent_reduction=percent_reduction,
        baseline_cost_rupees_per_month=round(baseline_cost, 0),
        projected_cost_rupees_per_month=round(projected_cost, 0),
        projected_savings_rupees_per_month=round(monthly_savings_inr, 0),
        estimated_capex_rupees=repair_capex_inr,
        payback_months=payback_months,
        co2_reduction_tons_per_year=co2_saved_tons_year,
        summary=f"Rectifying {int(leak_count)} pneumatic leak points prevents {int(kwh_saved_monthly):,} kWh monthly waste, returning ₹{int(monthly_savings_inr):,}/mo in savings with near-instant {payback_months} month payback.",
        breakdown={
            "leak_count": leak_count,
            "total_power_recovered_kw": round(total_wasted_kw, 2),
            "monthly_operating_hours": operating_hours_per_month,
        }
    )
