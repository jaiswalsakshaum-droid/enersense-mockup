import asyncio
import json
import datetime

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.database.connection import get_connection


router = APIRouter(
    prefix="/stream",
    tags=["Streaming"]
)


@router.get("/live")
async def stream_live_readings(
    machine_id: str = Query(
        "induction-furnace-01",
        description="ID of the machine to stream"
    )
):
    """
    Stream the latest database-backed telemetry through SSE.

    The database currently contains hourly telemetry rather than
    continuously arriving sensor readings, so this endpoint
    repeatedly publishes the latest database reading instead of
    generating fake/random sensor values.
    """

    async def event_generator():

        while True:

            conn = None

            try:
                conn = get_connection()

                with conn.cursor() as cur:

                    cur.execute("""
                        SELECT
                            m.machine_id,
                            m.baseline_power_kw,
                            t.power_kw,
                            t.temperature_c,
                            t.vibration_mms,
                            t.timestamp
                        FROM machines m
                        JOIN LATERAL (
                            SELECT
                                power_kw,
                                temperature_c,
                                vibration_mms,
                                timestamp
                            FROM machine_telemetry
                            WHERE machine_id = m.machine_id
                            ORDER BY timestamp DESC
                            LIMIT 1
                        ) t ON TRUE
                        WHERE m.machine_id = %s;
                    """, (machine_id,))

                    row = cur.fetchone()

                if not row:
                    payload = {
                        "machine_id": machine_id,
                        "error": "Machine telemetry not found"
                    }

                else:

                    (
                        db_machine_id,
                        baseline_power_kw,
                        power_kw,
                        temperature_c,
                        vibration_mms,
                        telemetry_timestamp,
                    ) = row

                    baseline_power_kw = float(
                        baseline_power_kw
                    )

                    power_kw = float(power_kw)
                    temperature_c = float(
                        temperature_c
                    )
                    vibration_mms = float(
                        vibration_mms
                    )

                    # Simple status derived from current
                    # telemetry relative to machine baseline.
                    if vibration_mms >= 4.8:
                        status = "Critical"

                    elif (
                        vibration_mms >= 3.2
                        or power_kw > baseline_power_kw * 1.15
                    ):
                        status = "Warning"

                    else:
                        status = "Normal"

                    payload = {
                        "machine_id": db_machine_id,

                        # Timestamp of the actual telemetry
                        # record, not a fabricated sensor value.
                        "timestamp": (
                            telemetry_timestamp.isoformat()
                        ),

                        # Time when the SSE message was sent.
                        "streamed_at": (
                            datetime.datetime.now().isoformat()
                        ),

                        "power_kw": round(
                            power_kw,
                            2
                        ),

                        "temperature_c": round(
                            temperature_c,
                            2
                        ),

                        "vibration_mms": round(
                            vibration_mms,
                            2
                        ),

                        "status": status,
                    }

                yield (
                    f"data: {json.dumps(payload)}\n\n"
                )

            except Exception as e:

                yield (
                    "data: "
                    + json.dumps({
                        "machine_id": machine_id,
                        "error": str(e)
                    })
                    + "\n\n"
                )

            finally:

                if conn:
                    conn.close()

            await asyncio.sleep(3)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )