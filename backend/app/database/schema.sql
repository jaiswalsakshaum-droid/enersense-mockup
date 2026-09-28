CREATE TABLE IF NOT EXISTS factories (
    factory_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location VARCHAR(100),
    industry_type VARCHAR(100),
    max_power_kw NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS machines (
    machine_id VARCHAR(30) PRIMARY KEY,
    factory_id VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    machine_type VARCHAR(100),
    production_line VARCHAR(100),
    capacity_units_per_hour NUMERIC(10,2),
    energy_kwh_per_hour NUMERIC(10,2),
    baseline_power_kw NUMERIC(10,2),
    peak_power_kw NUMERIC(10,2),
    defect_rate NUMERIC(6,4),
    quality_score NUMERIC(6,2),
    status VARCHAR(30) DEFAULT 'AVAILABLE',
    FOREIGN KEY (factory_id) REFERENCES factories(factory_id)
);
CREATE TABLE IF NOT EXISTS machine_telemetry (
    telemetry_id SERIAL PRIMARY KEY,
    machine_id VARCHAR(30) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    power_kw NUMERIC(10,2) NOT NULL,
    temperature_c NUMERIC(10,2) NOT NULL,
    vibration_mms NUMERIC(10,2) NOT NULL,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(30) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    unit_weight_kg NUMERIC(10,3),
    minimum_quality NUMERIC(6,2)
);

CREATE TABLE IF NOT EXISTS machine_product_capabilities (
    machine_id VARCHAR(30),
    product_id VARCHAR(30),
    processing_time_min NUMERIC(10,3),
    energy_kwh_per_unit NUMERIC(10,4),
    defect_rate NUMERIC(6,4),
    max_batch_size INTEGER,
    PRIMARY KEY (machine_id, product_id),
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS machine_availability (
    availability_id SERIAL PRIMARY KEY,
    machine_id VARCHAR(30) NOT NULL,
    available_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    reason VARCHAR(200),
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

CREATE TABLE IF NOT EXISTS energy_tariffs (
    tariff_id SERIAL PRIMARY KEY,
    factory_id VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    price_per_kwh NUMERIC(10,4) NOT NULL,
    carbon_factor_kg_per_kwh NUMERIC(10,4),
    FOREIGN KEY (factory_id) REFERENCES factories(factory_id)
);

CREATE TABLE IF NOT EXISTS production_orders (
    order_id VARCHAR(30) PRIMARY KEY,
    factory_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(30) NOT NULL,
    quantity INTEGER NOT NULL,
    deadline TIMESTAMP NOT NULL,
    minimum_quality NUMERIC(6,2),
    carbon_budget_kg NUMERIC(12,2),
    priority VARCHAR(20) DEFAULT 'NORMAL',
    status VARCHAR(30) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (factory_id) REFERENCES factories(factory_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS production_plans (
    plan_id VARCHAR(30) PRIMARY KEY,
    order_id VARCHAR(30) NOT NULL,
    status VARCHAR(30) DEFAULT 'SIMULATED',
    total_cost_inr NUMERIC(14,2),
    total_energy_kwh NUMERIC(14,2),
    total_carbon_kg NUMERIC(14,2),
    completion_time TIMESTAMP,
    quality_percent NUMERIC(6,2),
    peak_demand_kw NUMERIC(10,2),
    objective_score NUMERIC(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES production_orders(order_id)
);

CREATE TABLE IF NOT EXISTS plan_operations (
    operation_id SERIAL PRIMARY KEY,
    plan_id VARCHAR(30) NOT NULL,
    machine_id VARCHAR(30) NOT NULL,
    product_id VARCHAR(30) NOT NULL,
    quantity INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    energy_kwh NUMERIC(14,2),
    cost_inr NUMERIC(14,2),
    carbon_kg NUMERIC(14,2),
    expected_defects INTEGER,
    FOREIGN KEY (plan_id) REFERENCES production_plans(plan_id),
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);