def calculate_production_duration(quantity, capacity_per_hour):
    return quantity / capacity_per_hour


def calculate_energy(quantity, energy_per_unit):
    return quantity * energy_per_unit


def calculate_energy_cost(energy_kwh, tariff):
    return energy_kwh * tariff


def calculate_carbon(energy_kwh, carbon_factor):
    return energy_kwh * carbon_factor


def calculate_quality(defect_rate):
    return 100 - (defect_rate * 100)


def calculate_expected_defects(quantity, defect_rate):
    return round(quantity * defect_rate)


def calculate_effective_quality(quantity, expected_defects):
    return ((quantity - expected_defects) / quantity) * 100


def check_constraints(
    completion_time,
    deadline,
    quality,
    minimum_quality,
    carbon,
    carbon_budget,
):
    deadline_met = completion_time <= deadline

    quality_met = quality >= float(minimum_quality)

    carbon_budget_met = (
        carbon_budget is None
        or carbon <= float(carbon_budget)
    )

    feasible = (
        deadline_met
        and quality_met
        and carbon_budget_met
    )

    return {
        "deadline_met": deadline_met,
        "quality_met": quality_met,
        "carbon_budget_met": carbon_budget_met,
        "feasible": feasible,
    }