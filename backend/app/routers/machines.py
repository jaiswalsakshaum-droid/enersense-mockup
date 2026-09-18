from fastapi import APIRouter, HTTPException
from typing import List
from app.models.machines import Machine, MachineDetail
from app.data.machines import MACHINES_DATA
from app.services.scoring import (
    calculate_machine_health_score,
    get_machine_status,
)
router = APIRouter(prefix="/machines", tags=["Machines"])

@router.get("", response_model=List[Machine])
async def get_machines():
    machines = []

    for m in MACHINES_DATA:
        calculated_score = calculate_machine_health_score(
            power_kw=m["power_kw"],
            baseline_kw=m["baseline_power_kw"],
            vibration_mms=m["vibration_mms"],
            temperature_c=m["temperature_c"],
            machine_type=m["type"],
        )
        calculated_status = get_machine_status(calculated_score)
        machines.append(
            Machine(
                id=m["id"],
                name=m["name"],
                type=m["type"],
                line=m["line"],
                score=calculated_score,
                status=calculated_status,
                maintenance=m["maintenance"],
                reading=m["reading"],
                power_kw=m["power_kw"],
                temperature_c=m["temperature_c"],
                vibration_mms=m["vibration_mms"],
            )
        )

    return machines


@router.get("/{machine_id}", response_model=MachineDetail)
async def get_machine_detail(machine_id: str):
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

    machine_detail = machine.copy()
    machine_detail["score"] = calculated_score
    machine_detail["status"] = calculated_status

    return MachineDetail(**machine_detail)
