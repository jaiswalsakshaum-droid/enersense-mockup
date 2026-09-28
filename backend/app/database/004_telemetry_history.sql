-- ============================================================
-- 24-HOUR MACHINE TELEMETRY HISTORY
-- ============================================================

-- Remove existing demo telemetry so this script can be
-- safely re-run.
DELETE FROM machine_telemetry;


-- ============================================================
-- Generate hourly telemetry for 2026-09-28
-- ============================================================

INSERT INTO machine_telemetry
    (
        machine_id,
        power_kw,
        temperature_c,
        vibration_mms,
        timestamp
    )

SELECT
    m.machine_id,

    -- Power varies throughout the day.
    ROUND(
        (
            m.base_power
            * (
                0.88
                + 0.12 * SIN(
                    EXTRACT(HOUR FROM t.ts) * PI() / 12
                )
            )
            + m.power_variation
                * SIN(
                    EXTRACT(HOUR FROM t.ts) * PI() / 6
                )
        )::numeric,
        2
    ) AS power_kw,

    -- Temperature follows machine load.
    ROUND(
        (
            m.base_temperature
            + (
                m.base_temperature * 0.04
                * SIN(
                    EXTRACT(HOUR FROM t.ts) * PI() / 12
                )
            )
        )::numeric,
        2
    ) AS temperature_c,

    -- Small vibration variation.
    ROUND(
        (
            m.base_vibration
            + 0.15
            * SIN(
                EXTRACT(HOUR FROM t.ts) * PI() / 6
            )
        )::numeric,
        2
    ) AS vibration_mms,

    t.ts AS timestamp

FROM
(
    VALUES
        (
            'induction-furnace-01',
            182.0,
            18.0,
            684.0,
            2.4
        ),
        (
            'compressor-02',
            68.0,
            8.0,
            82.0,
            3.8
        ),
        (
            'cnc-lathe-04',
            41.0,
            5.0,
            46.0,
            1.6
        ),
        (
            'dust-collector-01',
            29.0,
            4.0,
            54.0,
            5.2
        ),
        (
            'cooling-tower-01',
            36.0,
            4.0,
            38.0,
            1.9
        )
) AS m(
    machine_id,
    base_power,
    power_variation,
    base_temperature,
    base_vibration
)

CROSS JOIN LATERAL
generate_series(
    TIMESTAMP '2026-09-28 00:00:00',
    TIMESTAMP '2026-09-28 23:00:00',
    INTERVAL '1 hour'
) AS t(ts);