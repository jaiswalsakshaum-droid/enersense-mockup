from app.database.connection import get_connection


def seed_database():
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # -------------------------
            # 1. FACTORY
            # -------------------------
            cur.execute("""
                INSERT INTO factories
                (factory_id, name, location, industry_type, max_power_kw)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (factory_id) DO NOTHING;
            """, (
                "FAC-001",
                "Rajkot Foundry Unit",
                "Rajkot, Gujarat",
                "Automobile Components",
                500
            ))

            # -------------------------
            # 2. MACHINES
            # -------------------------
            machines = [
                (
                    "induction-furnace-01",
                    "Induction Furnace 01",
                    "Induction Furnace",
                    "Foundry Line A",
                    120,
                    182,
                    175,
                    214,
                    0.025,
                    92
                ),
                (
                    "compressor-02",
                    "Air Compressor 02",
                    "Air Compressor",
                    "Utilities",
                    200,
                    68,
                    58,
                    74,
                    0.035,
                    76
                ),
                (
                    "cnc-lathe-04",
                    "CNC Lathe 04",
                    "CNC Lathe",
                    "Machining Line B",
                    60,
                    41,
                    38,
                    48,
                    0.015,
                    88
                ),
                (
                    "dust-collector-01",
                    "Dust Collector 01",
                    "Dust Collector",
                    "Foundry Line A",
                    150,
                    29,
                    22,
                    34,
                    0.020,
                    61
                ),
                (
                    "cooling-tower-01",
                    "Cooling Tower 01",
                    "Cooling Tower",
                    "Utilities",
                    180,
                    36,
                    34,
                    42,
                    0.010,
                    84
                )
            ]

            for machine in machines:
                cur.execute("""
                    INSERT INTO machines
                    (
                        machine_id,
                        factory_id,
                        name,
                        machine_type,
                        production_line,
                        capacity_units_per_hour,
                        energy_kwh_per_hour,
                        baseline_power_kw,
                        peak_power_kw,
                        defect_rate,
                        quality_score
                    )
                    VALUES
                    (%s, 'FAC-001', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (machine_id) DO NOTHING;
                """, machine)

            # -------------------------
            # 3. PRODUCT
            # -------------------------
            cur.execute("""
                INSERT INTO products
                (
                    product_id,
                    name,
                    description,
                    unit_weight_kg,
                    minimum_quality
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO NOTHING;
            """, (
                "PROD-001",
                "Automobile Component A",
                "Synthetic automobile component for ProcessTwin simulation",
                2.5,
                95
            ))

            # -------------------------
            # 4. MACHINE CAPABILITIES
            # -------------------------
            capabilities = [
                (
                    "induction-furnace-01",
                    30,
                    1.8,
                    0.025,
                    120
                ),
                (
                    "cnc-lathe-04",
                    8,
                    0.7,
                    0.015,
                    60
                )
            ]

            for machine_id, processing_time, energy, defect, batch_size in capabilities:
                cur.execute("""
                    INSERT INTO machine_product_capabilities
                    (
                        machine_id,
                        product_id,
                        processing_time_min,
                        energy_kwh_per_unit,
                        defect_rate,
                        max_batch_size
                    )
                    VALUES (%s, 'PROD-001', %s, %s, %s, %s)
                    ON CONFLICT (machine_id, product_id) DO NOTHING;
                """, (
                    machine_id,
                    processing_time,
                    energy,
                    defect,
                    batch_size
                ))

            # -------------------------
            # 5. ENERGY TARIFFS
            # -------------------------
            tariffs = [
                ("00:00", "06:00", 4.40, 0.70),
                ("06:00", "18:00", 7.20, 0.70),
                ("18:00", "22:00", 9.80, 0.70),
                ("22:00", "23:59", 5.50, 0.70)
            ]

            for start, end, price, carbon_factor in tariffs:
                cur.execute("""
                    INSERT INTO energy_tariffs
                    (
                        factory_id,
                        start_time,
                        end_time,
                        price_per_kwh,
                        carbon_factor_kg_per_kwh
                    )
                    VALUES ('FAC-001', %s, %s, %s, %s);
                """, (
                    start,
                    end,
                    price,
                    carbon_factor
                ))

        conn.commit()

        print("Database seeded successfully!")

    except Exception as e:
        conn.rollback()
        print("Seeding failed:")
        print(e)

    finally:
        conn.close()


if __name__ == "__main__":
    seed_database()