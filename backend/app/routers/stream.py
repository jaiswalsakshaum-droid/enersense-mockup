import asyncio
import json
import random
import datetime
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from app.data.machines import MACHINES_DATA

router = APIRouter(prefix="/stream", tags=["Streaming"])


@router.get("/live")
async def stream_live_readings(machine_id: str = Query("induction-furnace-01", description="ID of the machine to stream")):
    """
    Server-Sent Events (SSE) endpoint streaming simulated real-time telemetry readings
    every 3 seconds with a smooth random walk around baseline operating levels.
    """
    machine = next((m for m in MACHINES_DATA if m["id"] == machine_id), MACHINES_DATA[0])

    async def event_generator():
        # Keep track of rolling state
        current_power = float(machine["power_kw"])
        current_temp = float(machine["temperature_c"])
        current_vibe = float(machine["vibration_mms"])

        while True:
            # Random walk with mean reversion
            power_drift = random.uniform(-1.5, 1.5)
            # Revert gently towards base
            base_power = float(machine["baseline_power_kw"])
            if current_power > base_power + 15:
                power_drift -= 1.0
            elif current_power < base_power - 10:
                power_drift += 1.0
            current_power = max(5.0, round(current_power + power_drift, 1))

            temp_drift = random.uniform(-0.8, 0.8)
            current_temp = max(20.0, round(current_temp + temp_drift, 1))

            vibe_drift = random.uniform(-0.15, 0.15)
            current_vibe = max(0.2, round(current_vibe + vibe_drift, 2))

            # Dynamic health score
            health_score = int(machine["score"])
            if current_vibe > 4.5 or current_power > base_power * 1.2:
                health_score = max(50, health_score - 2)

            now_str = datetime.datetime.now().strftime("%H:%M:%S")

            payload = {
                "machine_id": machine["id"],
                "timestamp": now_str,
                "power_kw": current_power,
                "temperature_c": current_temp,
                "vibration_mms": current_vibe,
                "score": health_score,
                "status": "Critical" if current_vibe > 4.8 else ("Warning" if current_vibe > 3.2 or current_power > base_power * 1.15 else "Normal"),
            }

            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(3.0)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
