from fastapi import APIRouter, HTTPException
from typing import List
from app.models.machines import Machine, MachineDetail
from app.data.machines import MACHINES_DATA

router = APIRouter(prefix="/machines", tags=["Machines"])


@router.get("", response_model=List[Machine])
async def get_machines():
    """
    Retrieve all monitored plant machines with their health score, status, and current reading.
    """
    return [
        Machine(
            id=m["id"],
            name=m["name"],
            type=m["type"],
            line=m["line"],
            score=m["score"],
            status=m["status"],
            maintenance=m["maintenance"],
            reading=m["reading"],
            power_kw=m["power_kw"],
            temperature_c=m["temperature_c"],
            vibration_mms=m["vibration_mms"],
        )
        for m in MACHINES_DATA
    ]


@router.get("/{machine_id}", response_model=MachineDetail)
async def get_machine_detail(machine_id: str):
    """
    Retrieve single machine telemetry details, 24h trend values, recent readings, and service logs.
    """
    machine = next((m for m in MACHINES_DATA if m["id"] == machine_id), None)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{machine_id}' not found")
    return MachineDetail(**machine)
