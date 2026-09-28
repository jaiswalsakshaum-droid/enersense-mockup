-- ============================================================
-- MACHINE AVAILABILITY SEED DATA
-- ============================================================

-- Remove existing demo availability records
-- so this script can be safely re-run.
DELETE FROM machine_availability;


-- ============================================================
-- INDUCTION FURNACE 01
-- ============================================================

INSERT INTO machine_availability
    (machine_id, available_date, start_time, end_time, available, reason)
VALUES
    ('induction-furnace-01', '2026-09-28', '06:00', '22:00', TRUE, 'Normal production availability'),
    ('induction-furnace-01', '2026-09-29', '06:00', '22:00', TRUE, 'Normal production availability'),
    ('induction-furnace-01', '2026-09-30', '06:00', '22:00', TRUE, 'Normal production availability');


-- ============================================================
-- CNC LATHE 04
-- ============================================================

INSERT INTO machine_availability
    (machine_id, available_date, start_time, end_time, available, reason)
VALUES
    ('cnc-lathe-04', '2026-09-28', '08:00', '20:00', TRUE, 'Normal production availability'),
    ('cnc-lathe-04', '2026-09-29', '08:00', '20:00', TRUE, 'Normal production availability'),
    ('cnc-lathe-04', '2026-09-30', '08:00', '20:00', TRUE, 'Normal production availability');


-- ============================================================
-- AIR COMPRESSOR 02
-- ============================================================

INSERT INTO machine_availability
    (machine_id, available_date, start_time, end_time, available, reason)
VALUES
    ('compressor-02', '2026-09-28', '00:00', '23:59', TRUE, 'Utilities equipment'),
    ('compressor-02', '2026-09-29', '00:00', '23:59', TRUE, 'Utilities equipment'),
    ('compressor-02', '2026-09-30', '00:00', '23:59', TRUE, 'Utilities equipment');


-- ============================================================
-- DUST COLLECTOR 01
-- ============================================================

INSERT INTO machine_availability
    (machine_id, available_date, start_time, end_time, available, reason)
VALUES
    ('dust-collector-01', '2026-09-28', '00:00', '23:59', FALSE, 'Maintenance required'),
    ('dust-collector-01', '2026-09-29', '00:00', '23:59', FALSE, 'Maintenance required'),
    ('dust-collector-01', '2026-09-30', '00:00', '23:59', FALSE, 'Maintenance required');


-- ============================================================
-- COOLING TOWER 01
-- ============================================================

INSERT INTO machine_availability
    (machine_id, available_date, start_time, end_time, available, reason)
VALUES
    ('cooling-tower-01', '2026-09-28', '00:00', '23:59', TRUE, 'Utilities equipment'),
    ('cooling-tower-01', '2026-09-29', '00:00', '23:59', TRUE, 'Utilities equipment'),
    ('cooling-tower-01', '2026-09-30', '00:00', '23:59', TRUE, 'Utilities equipment');