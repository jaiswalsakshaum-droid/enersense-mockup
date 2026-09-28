-- ============================================================
-- DATABASE IMPROVEMENTS
-- EnerSense / ProcessTwin
-- ============================================================


-- ============================================================
-- 1. FACTORIES
-- ============================================================

ALTER TABLE factories
ADD CONSTRAINT factories_max_power_positive
CHECK (max_power_kw IS NULL OR max_power_kw > 0);


-- ============================================================
-- 2. MACHINES
-- ============================================================

ALTER TABLE machines
ADD CONSTRAINT machines_capacity_positive
CHECK (
    capacity_units_per_hour IS NULL
    OR capacity_units_per_hour > 0
);

ALTER TABLE machines
ADD CONSTRAINT machines_energy_positive
CHECK (
    energy_kwh_per_hour IS NULL
    OR energy_kwh_per_hour >= 0
);

ALTER TABLE machines
ADD CONSTRAINT machines_power_valid
CHECK (
    baseline_power_kw IS NULL
    OR peak_power_kw IS NULL
    OR peak_power_kw >= baseline_power_kw
);

ALTER TABLE machines
ADD CONSTRAINT machines_defect_rate_valid
CHECK (
    defect_rate IS NULL
    OR (defect_rate >= 0 AND defect_rate <= 1)
);

ALTER TABLE machines
ADD CONSTRAINT machines_quality_score_valid
CHECK (
    quality_score IS NULL
    OR (quality_score >= 0 AND quality_score <= 100)
);


-- ============================================================
-- 3. MACHINE TELEMETRY
-- ============================================================

ALTER TABLE machine_telemetry
ADD CONSTRAINT telemetry_power_nonnegative
CHECK (power_kw >= 0);

ALTER TABLE machine_telemetry
ADD CONSTRAINT telemetry_temperature_valid
CHECK (temperature_c >= -50);

ALTER TABLE machine_telemetry
ADD CONSTRAINT telemetry_vibration_nonnegative
CHECK (vibration_mms >= 0);


-- ============================================================
-- 4. PRODUCTS
-- ============================================================

ALTER TABLE products
ADD CONSTRAINT products_weight_nonnegative
CHECK (
    unit_weight_kg IS NULL
    OR unit_weight_kg >= 0
);

ALTER TABLE products
ADD CONSTRAINT products_quality_valid
CHECK (
    minimum_quality IS NULL
    OR (minimum_quality >= 0 AND minimum_quality <= 100)
);


-- ============================================================
-- 5. MACHINE PRODUCT CAPABILITIES
-- ============================================================

ALTER TABLE machine_product_capabilities
ADD CONSTRAINT capability_processing_time_positive
CHECK (processing_time_min > 0);

ALTER TABLE machine_product_capabilities
ADD CONSTRAINT capability_energy_nonnegative
CHECK (energy_kwh_per_unit >= 0);

ALTER TABLE machine_product_capabilities
ADD CONSTRAINT capability_defect_rate_valid
CHECK (
    defect_rate >= 0
    AND defect_rate <= 1
);

ALTER TABLE machine_product_capabilities
ADD CONSTRAINT capability_batch_positive
CHECK (max_batch_size > 0);


-- ============================================================
-- 6. MACHINE AVAILABILITY
-- ============================================================

ALTER TABLE machine_availability
ADD CONSTRAINT availability_time_valid
CHECK (start_time < end_time);


-- ============================================================
-- 7. ENERGY TARIFFS
-- ============================================================

ALTER TABLE energy_tariffs
ADD CONSTRAINT tariff_time_valid
CHECK (start_time < end_time);

ALTER TABLE energy_tariffs
ADD CONSTRAINT tariff_price_nonnegative
CHECK (price_per_kwh >= 0);

ALTER TABLE energy_tariffs
ADD CONSTRAINT tariff_carbon_nonnegative
CHECK (
    carbon_factor_kg_per_kwh IS NULL
    OR carbon_factor_kg_per_kwh >= 0
);


-- ============================================================
-- 8. PRODUCTION ORDERS
-- ============================================================

ALTER TABLE production_orders
ADD CONSTRAINT orders_quantity_positive
CHECK (quantity > 0);

ALTER TABLE production_orders
ADD CONSTRAINT orders_quality_valid
CHECK (
    minimum_quality IS NULL
    OR (minimum_quality >= 0 AND minimum_quality <= 100)
);

ALTER TABLE production_orders
ADD CONSTRAINT orders_carbon_budget_valid
CHECK (
    carbon_budget_kg IS NULL
    OR carbon_budget_kg >= 0
);


-- ============================================================
-- 9. PRODUCTION PLANS
-- ============================================================

ALTER TABLE production_plans
ADD CONSTRAINT plans_cost_nonnegative
CHECK (
    total_cost_inr IS NULL
    OR total_cost_inr >= 0
);

ALTER TABLE production_plans
ADD CONSTRAINT plans_energy_nonnegative
CHECK (
    total_energy_kwh IS NULL
    OR total_energy_kwh >= 0
);

ALTER TABLE production_plans
ADD CONSTRAINT plans_carbon_nonnegative
CHECK (
    total_carbon_kg IS NULL
    OR total_carbon_kg >= 0
);

ALTER TABLE production_plans
ADD CONSTRAINT plans_quality_valid
CHECK (
    quality_percent IS NULL
    OR (quality_percent >= 0 AND quality_percent <= 100)
);

ALTER TABLE production_plans
ADD CONSTRAINT plans_peak_power_nonnegative
CHECK (
    peak_demand_kw IS NULL
    OR peak_demand_kw >= 0
);


-- ============================================================
-- 10. PLAN OPERATIONS
-- ============================================================

ALTER TABLE plan_operations
ADD CONSTRAINT operations_quantity_positive
CHECK (quantity > 0);

ALTER TABLE plan_operations
ADD CONSTRAINT operations_time_valid
CHECK (start_time < end_time);

ALTER TABLE plan_operations
ADD CONSTRAINT operations_energy_nonnegative
CHECK (
    energy_kwh IS NULL
    OR energy_kwh >= 0
);

ALTER TABLE plan_operations
ADD CONSTRAINT operations_cost_nonnegative
CHECK (
    cost_inr IS NULL
    OR cost_inr >= 0
);

ALTER TABLE plan_operations
ADD CONSTRAINT operations_carbon_nonnegative
CHECK (
    carbon_kg IS NULL
    OR carbon_kg >= 0
);

ALTER TABLE plan_operations
ADD CONSTRAINT operations_defects_nonnegative
CHECK (
    expected_defects IS NULL
    OR expected_defects >= 0
);


-- ============================================================
-- 11. INDEXES
-- ============================================================

-- Machine lookups
CREATE INDEX IF NOT EXISTS idx_machines_factory
ON machines(factory_id);

CREATE INDEX IF NOT EXISTS idx_machines_status
ON machines(status);

CREATE INDEX IF NOT EXISTS idx_machines_factory_status
ON machines(factory_id, status);


-- Telemetry lookups
CREATE INDEX IF NOT EXISTS idx_telemetry_machine
ON machine_telemetry(machine_id);

CREATE INDEX IF NOT EXISTS idx_telemetry_machine_time
ON machine_telemetry(machine_id, timestamp DESC);


-- Product capability lookups
CREATE INDEX IF NOT EXISTS idx_capabilities_product
ON machine_product_capabilities(product_id);

CREATE INDEX IF NOT EXISTS idx_capabilities_machine
ON machine_product_capabilities(machine_id);


-- Machine availability
CREATE INDEX IF NOT EXISTS idx_availability_machine_date
ON machine_availability(machine_id, available_date);


-- Energy tariff lookup
CREATE INDEX IF NOT EXISTS idx_tariffs_factory_time
ON energy_tariffs(factory_id, start_time, end_time);


-- Production orders
CREATE INDEX IF NOT EXISTS idx_orders_factory
ON production_orders(factory_id);

CREATE INDEX IF NOT EXISTS idx_orders_product
ON production_orders(product_id);

CREATE INDEX IF NOT EXISTS idx_orders_status
ON production_orders(status);

CREATE INDEX IF NOT EXISTS idx_orders_deadline
ON production_orders(deadline);


-- Production plans
CREATE INDEX IF NOT EXISTS idx_plans_order
ON production_plans(order_id);

CREATE INDEX IF NOT EXISTS idx_plans_status
ON production_plans(status);

CREATE INDEX IF NOT EXISTS idx_plans_created
ON production_plans(created_at DESC);


-- Plan operations
CREATE INDEX IF NOT EXISTS idx_operations_plan
ON plan_operations(plan_id);

CREATE INDEX IF NOT EXISTS idx_operations_machine
ON plan_operations(machine_id);

CREATE INDEX IF NOT EXISTS idx_operations_start_time
ON plan_operations(start_time);