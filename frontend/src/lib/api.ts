/**
 * EnerSense Backend API Client
 * Typed fetch wrappers for all FastAPI endpoints.
 */

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || "http://localhost:4000/api";

export type MachineStatus = "Normal" | "Warning" | "Critical";

export interface Machine {
  id: string;
  name: string;
  type: string;
  line: string;
  score: number;
  status: MachineStatus;
  maintenance: string;
  reading: string;
  power_kw: number;
  temperature_c: number;
  vibration_mms: number;
}

export interface MachineReading {
  timestamp: string;
  power_kw: number;
  temperature_c: number;
  vibration_mms: number;
}

export interface MaintenanceRecord {
  date: string;
  title: string;
  detail: string;
  active?: boolean;
}

export interface PowerHealthFactor {
  value: number;
  baseline: number;
  deviation_pct: number;
  status: string;
  penalty: number;
}

export interface VibrationHealthFactor {
  value: number;
  status: string;
  penalty: number;
}

export interface TemperatureHealthFactor {
  value: number;
  expected: number;
  deviation: number;
  status: string;
  penalty: number;
}

export interface HealthFactors {
  power: PowerHealthFactor;
  vibration: VibrationHealthFactor;
  temperature: TemperatureHealthFactor;
}


export interface MachineDetail extends Machine {
  baseline_power_kw: number;
  peak_power_kw: number;
  avg_24h_power_kw: number;
  recent_readings: MachineReading[];
  history_readings_24h: number[];
  maintenance_history: MaintenanceRecord[];
  health_factors: HealthFactors;
}

export interface PeerBenchmark {
  plant_score: number;
  peer_average_score: number;
  peer_top_quartile: number;
  industry_label: string;
  percentile: number;
  comparison_text: string;
}

export interface DashboardAlertPreview {
  id: number;
  machine_name: string;
  detail: string;
  time: string;
  severity: string;
}

export interface DashboardSummary {
  plant_name: string;
  health_score: number;
  score_target: number;
  health_change_pct: number;
  energy_use_today_kwh: number;
  energy_use_change_pct: number;
  energy_cost_today_inr: number;
  energy_cost_change_pct: number;
  co2e_today_tons: number;
  co2e_change_pct: number;
  active_alerts_count: number;
  active_alerts_change: string;
  energy_trend_24h: number[];
  baseline_trend_24h: number[];
  peer_benchmark: PeerBenchmark;
  latest_alerts: DashboardAlertPreview[];
}

export interface AlertItem {
  id: number;
  title: string;
  detail: string;
  time: string;
  severity: "Critical" | "Warning" | "Resolved" | "Info";
  machine: string;
  machine_id?: string;
  timestamp?: string;
  recommended_action?: string;
}

export interface RecommendationItem {
  rank: string;
  title: string;
  description: string;
  saving: string;
  rupees: string;
  payback: string;
  tag: string;
  annual_saving_kwh: number;
  monthly_saving_inr: number;
  payback_months: number;
  capex_inr: number;
}

export type InterventionType = "load_shift" | "equipment_upgrade" | "process_change";

export interface SimulateRequest {
  intervention_type: InterventionType;
  params?: Record<string, any>;
}

export interface SimulateResponse {
  intervention_type: InterventionType;
  intervention_title: string;
  baseline_kwh: number;
  projected_kwh: number;
  kwh_saved_monthly: number;
  percent_reduction: number;
  baseline_cost_rupees_per_month: number;
  projected_cost_rupees_per_month: number;
  projected_savings_rupees_per_month: number;
  estimated_capex_rupees: number;
  payback_months: number;
  co2_reduction_tons_per_year: number;
  summary: string;
  breakdown: Record<string, any>;
}
export interface OptimizationScenario {
  machine_allocations: {
    machine_id: string;
    machine_name: string;
    quantity: number;
  }[];
  duration_hours: number;
  energy_kwh: number;
  energy_cost_inr: number;
  carbon_kg: number;
  quality_percent: number;
  deadline_met: boolean;
  quality_met: boolean;
  carbon_budget_met: boolean;
  feasible: boolean;
}

export interface OptimizationResult {
  order_id: string;
  product_id: string;
  quantity: number;
  scenarios: OptimizationScenario[];
  best_plan: OptimizationScenario | null;
  message: string;
}
export interface SchemeItem {
  id: string;
  title: string;
  organization: string;
  category: string;
  eligible_industries: string[];
  incentive: string;
  max_benefit_inr: string;
  eligibility_summary: string;
  deadline: string;
  status: string;
  action_url: string;
}

export interface LiveStreamPayload {
  machine_id: string;
  timestamp: string;
  power_kw: number;
  temperature_c: number;
  vibration_mms: number;
  score: number;
  status: MachineStatus;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => "");
    throw new Error(`API error ${res.status}: ${errorText || res.statusText}`);
  }

  return res.json();
}

export async function fetchMachines(): Promise<Machine[]> {
  return request<Machine[]>("/machines");
}

export async function fetchMachineDetail(id: string): Promise<MachineDetail> {
  return request<MachineDetail>(`/machines/${id}`);
}

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>("/dashboard/summary");
}

export async function fetchAlerts(): Promise<AlertItem[]> {
  return request<AlertItem[]>("/alerts");
}

export async function fetchRecommendations(): Promise<RecommendationItem[]> {
  return request<RecommendationItem[]>("/recommendations");
}

export async function runSimulation(data: SimulateRequest): Promise<SimulateResponse> {
  return request<SimulateResponse>("/simulate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function fetchSchemes(industryType?: string, monthlyConsumption?: number): Promise<SchemeItem[]> {
  const params = new URLSearchParams();
  if (industryType) params.append("industry_type", industryType);
  if (monthlyConsumption) params.append("monthly_consumption_kwh", monthlyConsumption.toString());
  const query = params.toString() ? `?${params.toString()}` : "";
  return request<SchemeItem[]>(`/schemes${query}`);
}

export function getLiveStreamUrl(machineId: string): string {
  return `${API_BASE}/stream/live?machine_id=${encodeURIComponent(machineId)}`;
}
export interface MachineHealthInfo {
  score: number;
  status: MachineStatus;
}

export interface OptimizationScenario {
  allocation: Record<string, number>;
  machine_names: Record<string, string>;
  machine_health: Record<string, MachineHealthInfo>;
  energy_kwh: number;
  cost_inr: number;
  carbon_kg: number;
  duration_hours: number;
  completion_time: string;
  quality_percent: number;
  deadline_met: boolean;
  quality_met: boolean;
  carbon_budget_met: boolean;
  feasible: boolean;
}

export interface OptimizationResult {
  order_id: string;
  quantity: number;
  deadline: string;
  minimum_quality: number;
  energy_pricing: {
    price_per_kwh: number;
    carbon_factor_kg_per_kwh: number;
  };
  total_scenarios_tested: number;
  scenarios: OptimizationScenario[];
  critical_machines: Array<{
    machine_id: string;
    name: string;
    health_score: number;
    health_status: MachineStatus;
  }>;
  eligible_machines: Array<{
    machine_id: string;
    name: string;
    health_score: number;
    health_status: MachineStatus;
  }>;
  carbon_budget_kg: number | null;
  baseline: OptimizationScenario;
  best_plan: OptimizationScenario | null;
  message: string;
}

export interface ProcessTwinScenario {
  machine_health: MachineHealthInfo;
  energy_pricing: {
    price_per_kwh: number;
    carbon_factor_kg_per_kwh: number;
  };
  machine_id: string;
  machine_name: string;
  quantity: number;
  duration_hours: number;
  start_time: string;
  completion_time: string;
  energy_kwh: number;
  energy_cost_inr: number;
  carbon_kg: number;
  expected_defects: number;
  quality_percent: number;
  deadline_met: boolean;
  quality_met: boolean;
  carbon_budget_met: boolean;
  feasible: boolean;
}

export interface ProcessTwinResult {
  order_id: string;
  quantity: number;
  deadline: string;
  minimum_quality: number;
  energy_pricing: {
    price_per_kwh: number;
    carbon_factor_kg_per_kwh: number;
  };
  critical_machines: Array<{
    machine_id: string;
    name: string;
    health_score: number;
    health_status: MachineStatus;
  }>;
  eligible_machines: Array<{
    machine_id: string;
    name: string;
    health_score: number;
    health_status: MachineStatus;
  }>;
  carbon_budget_kg: number | null;
  scenarios: ProcessTwinScenario[];
  best_scenario: ProcessTwinScenario | null;
  recommendation: string;
}
export interface ProductionOrderCreate {
  order_id: string;
  factory_id: string;
  product_id: string;
  quantity: number;
  deadline: string;
  minimum_quality: number;
  carbon_budget_kg: number;
  priority: string;
}

export interface ProductionOrderResponse {
  order_id: string;
  status: string;
}

export async function createProductionOrder(
  order: ProductionOrderCreate
): Promise<ProductionOrderResponse> {
  return request<ProductionOrderResponse>(
    "/orders/",
    {
      method: "POST",
      body: JSON.stringify(order),
    }
  );
}
export async function runProcessTwin(
  orderId: string
): Promise<ProcessTwinResult> {
  return request<ProcessTwinResult>(
    `/process-twin/simulate/${orderId}`,
    {
      method: "POST",
    }
  );
}