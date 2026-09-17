def explain_recommendation(
    current_state,
    recommended_state,
    risk_score=None,
    uncertainty_percent=None
):
    """
    Explain why EnerSense recommends a new operating point.
    """

    current_energy = current_state["energy_kwh"]
    recommended_energy = recommended_state["energy_kwh"]

    current_production = current_state["production_units"]
    recommended_production = recommended_state["production_units"]

    current_defect = current_state["defect_rate"]
    recommended_defect = recommended_state["defect_rate"]

    current_energy_per_unit = current_state["energy_per_unit"]
    recommended_energy_per_unit = recommended_state["energy_per_unit"]

    # --------------------------------------------------
    # Energy impact
    # --------------------------------------------------

    energy_saved = current_energy - recommended_energy

    if current_energy > 0:
        energy_saving_percent = (
            energy_saved / current_energy
        ) * 100
    else:
        energy_saving_percent = 0

    # --------------------------------------------------
    # Production impact
    # --------------------------------------------------

    if current_production > 0:
        production_change_percent = (
            (recommended_production - current_production)
            / current_production
        ) * 100
    else:
        production_change_percent = 0

    # --------------------------------------------------
    # Quality impact
    # --------------------------------------------------

    defect_change = (
        recommended_defect - current_defect
    )

    # --------------------------------------------------
    # Energy intensity improvement
    # --------------------------------------------------

    if current_energy_per_unit > 0:
        energy_intensity_change_percent = (
            (recommended_energy_per_unit
             - current_energy_per_unit)
            / current_energy_per_unit
        ) * 100
    else:
        energy_intensity_change_percent = 0

    # --------------------------------------------------
    # Determine quality status
    # --------------------------------------------------

    if recommended_defect <= 0.02:
        quality_status = "WITHIN_LIMIT"
    else:
        quality_status = "ABOVE_LIMIT"

    # --------------------------------------------------
    # Determine risk status
    # --------------------------------------------------

    if risk_score is None:
        risk_status = "UNKNOWN"
    elif risk_score <= 20:
        risk_status = "LOW"
    elif risk_score <= 50:
        risk_status = "MEDIUM"
    else:
        risk_status = "HIGH"

    # --------------------------------------------------
    # Build explanation
    # --------------------------------------------------

    reasons = []

    if energy_saved > 0:
        reasons.append(
            "The recommended operating point reduces energy consumption."
        )

    if energy_intensity_change_percent < 0:
        reasons.append(
            "Energy required per production unit is lower."
        )

    if production_change_percent >= 0:
        reasons.append(
            "Production output is maintained or improved."
        )
    else:
        reasons.append(
            "Production decreases slightly but remains within the allowed tolerance."
        )

    if recommended_defect <= 0.02:
        reasons.append(
            "Predicted defect rate remains within the quality constraint."
        )

    explanation = " ".join(reasons)

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------

    return {
        "summary": explanation,

        "energy": {
            "current_kwh": round(current_energy, 3),
            "recommended_kwh": round(recommended_energy, 3),
            "saving_kwh": round(energy_saved, 3),
            "saving_percent": round(
                energy_saving_percent,
                2
            )
        },

        "production": {
            "current_units": round(
                current_production,
                2
            ),
            "recommended_units": round(
                recommended_production,
                2
            ),
            "change_percent": round(
                production_change_percent,
                2
            )
        },

        "quality": {
            "current_defect_rate": round(
                current_defect,
                4
            ),
            "recommended_defect_rate": round(
                recommended_defect,
                4
            ),
            "defect_change": round(
                defect_change,
                4
            ),
            "status": quality_status
        },

        "energy_intensity": {
            "current_kwh_per_unit": round(
                current_energy_per_unit,
                4
            ),
            "recommended_kwh_per_unit": round(
                recommended_energy_per_unit,
                4
            ),
            "change_percent": round(
                energy_intensity_change_percent,
                2
            )
        },

        "risk": {
            "risk_score": (
                round(risk_score, 2)
                if risk_score is not None
                else None
            ),
            "uncertainty_percent": (
                round(uncertainty_percent, 2)
                if uncertainty_percent is not None
                else None
            ),
            "status": risk_status
        }
    }

if __name__ == "__main__":

    current = {
        "energy_kwh": 78.5278,
        "production_units": 435.5476,
        "defect_rate": 0.0150,
        "energy_per_unit": 0.1803
    }

    recommended = {
        "energy_kwh": 55.3419,
        "production_units": 451.4392,
        "defect_rate": 0.0104,
        "energy_per_unit": 0.1226
    }

    result = explain_recommendation(
        current_state=current,
        recommended_state=recommended,
        risk_score=3.70,
        uncertainty_percent=0.1061
    )

    print("\n============================================")
    print("        ENERSENSE RECOMMENDATION")
    print("             EXPLANATION")
    print("============================================")

    print("\nSUMMARY:")
    print(result["summary"])

    print("\nENERGY:")
    print(result["energy"])

    print("\nPRODUCTION:")
    print(result["production"])

    print("\nQUALITY:")
    print(result["quality"])

    print("\nENERGY INTENSITY:")
    print(result["energy_intensity"])

    print("\nRISK:")
    print(result["risk"])