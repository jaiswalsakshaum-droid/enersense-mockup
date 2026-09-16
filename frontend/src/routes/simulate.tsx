import { createFileRoute, Link } from "@tanstack/react-router";
import { useMutation } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, Banknote, Calculator, CheckCircle2, ChevronRight, Clock3, Cpu, Gauge, Leaf, Loader2, Sparkles, TrendingDown, Wrench, Zap } from "lucide-react";
import { useState, useEffect } from "react";
import { AppShell, PageHeading, SectionLabel, StatCard } from "@/components/enersense";
import { Button } from "@/components/ui/button";
import { runSimulation, type InterventionType, type SimulateResponse } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";

export const Route = createFileRoute("/simulate")({
  head: () => ({
    meta: [
      { title: "What-If Simulator — EnerSense" },
      { name: "description", content: "Model the financial and energy savings of plant interventions before capital expenditure." },
      { property: "og:title", content: "What-If Simulator — EnerSense" },
      { property: "og:description", content: "Model the financial and energy savings of plant interventions before capital expenditure." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: SimulatorPage,
});

function SimulatorPage() {
  const { t } = useTranslation();
  const [interventionType, setInterventionType] = useState<InterventionType>("load_shift");

  // Form params for different intervention types
  const [shiftKwh, setShiftKwh] = useState(450);
  const [peakTariff, setPeakTariff] = useState(9.8);
  const [offPeakTariff, setOffPeakTariff] = useState(4.4);

  const [connectedLoadKw, setConnectedLoadKw] = useState(75);
  const [efficiencyGainPct, setEfficiencyGainPct] = useState(18);
  const [equipmentCapex, setEquipmentCapex] = useState(115000);

  const [leakCount, setLeakCount] = useState(6);
  const [repairCapex, setRepairCapex] = useState(9500);

  const mutation = useMutation({
    mutationFn: runSimulation,
  });

  // Trigger calculation on parameters change or initial load
  const triggerSimulation = (type = interventionType) => {
    let params: Record<string, any> = { baseline_kwh: 72000 };
    if (type === "load_shift") {
      params = {
        ...params,
        shift_kwh_per_day: Number(shiftKwh),
        peak_tariff_inr: Number(peakTariff),
        off_peak_tariff_inr: Number(offPeakTariff),
        operating_days_per_month: 26,
        automation_capex_inr: 15000,
      };
    } else if (type === "equipment_upgrade") {
      params = {
        ...params,
        connected_load_kw: Number(connectedLoadKw),
        efficiency_gain_pct: Number(efficiencyGainPct),
        capex_inr: Number(equipmentCapex),
        operating_hours_per_day: 16,
        avg_tariff_inr: 8.5,
      };
    } else if (type === "process_change") {
      params = {
        ...params,
        leak_count: Number(leakCount),
        repair_capex_inr: Number(repairCapex),
        avg_tariff_inr: 8.5,
      };
    }

    mutation.mutate({ intervention_type: type, params });
  };

  useEffect(() => {
    triggerSimulation(interventionType);
  }, [interventionType]);

  const result: SimulateResponse | undefined = mutation.data;

  return (
    <AppShell>
      <div className="rise-in">
        <PageHeading
          eyebrow="Predictive Energy ROI Engine"
          title={t("sim.title", "What-If Simulator")}
          description={t(
            "sim.desc",
            "Model the financial & energy impact of load shifting, VFD retrofits, and leak fixes before investing."
          )}
          action={
            <Button
              onClick={() => triggerSimulation()}
              disabled={mutation.isPending}
              className="gap-2 bg-amber text-primary-foreground hover:bg-amber/90"
            >
              {mutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Calculator className="h-4 w-4" />}
              Recalculate Scenario
            </Button>
          }
        />

        <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
          {/* Left Column: Interactive Scenario Controls */}
          <div className="space-y-6">
            <div className="glass-panel rounded-xl border border-border p-5">
              <SectionLabel>Intervention Strategy</SectionLabel>
              <div className="mt-3 space-y-2">
                <button
                  type="button"
                  onClick={() => setInterventionType("load_shift")}
                  className={`w-full text-left rounded-lg p-3 border text-xs transition-colors flex items-start gap-3 ${
                    interventionType === "load_shift"
                      ? "border-amber bg-amber-soft/40 text-foreground font-semibold"
                      : "border-border bg-panel text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Clock3 className="h-4 w-4 text-amber shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium text-foreground">1. ToD Tariff Load Shift</div>
                    <div className="text-[11px] text-muted-foreground mt-0.5">Shift batch ramp-up to night off-peak tariff</div>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => setInterventionType("equipment_upgrade")}
                  className={`w-full text-left rounded-lg p-3 border text-xs transition-colors flex items-start gap-3 ${
                    interventionType === "equipment_upgrade"
                      ? "border-amber bg-amber-soft/40 text-foreground font-semibold"
                      : "border-border bg-panel text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Cpu className="h-4 w-4 text-teal shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium text-foreground">2. VFD & Motor Upgrade</div>
                    <div className="text-[11px] text-muted-foreground mt-0.5">Install inverter drive on fans/pumps</div>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => setInterventionType("process_change")}
                  className={`w-full text-left rounded-lg p-3 border text-xs transition-colors flex items-start gap-3 ${
                    interventionType === "process_change"
                      ? "border-amber bg-amber-soft/40 text-foreground font-semibold"
                      : "border-border bg-panel text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Wrench className="h-4 w-4 text-critical shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium text-foreground">3. Leak & Heat Loss Fix</div>
                    <div className="text-[11px] text-muted-foreground mt-0.5">Fix air manifold leaks & door seals</div>
                  </div>
                </button>
              </div>

              {/* Dynamic Parameter Sliders / Inputs */}
              <div className="mt-6 border-t border-border pt-5 space-y-4">
                <SectionLabel>Scenario Parameters</SectionLabel>

                {interventionType === "load_shift" && (
                  <>
                    <div>
                      <div className="flex justify-between text-xs mb-1.5">
                        <span className="text-muted-foreground">Shifted Load per Day</span>
                        <span className="font-semibold text-foreground font-display">{shiftKwh} kWh / day</span>
                      </div>
                      <input
                        type="range"
                        min="100"
                        max="1200"
                        step="50"
                        value={shiftKwh}
                        onChange={(e) => setShiftKwh(Number(e.target.value))}
                        className="w-full accent-amber"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-3 pt-2">
                      <div>
                        <label className="text-[10px] uppercase tracking-wider text-muted-foreground">Peak Tariff</label>
                        <input
                          type="number"
                          step="0.1"
                          value={peakTariff}
                          onChange={(e) => setPeakTariff(Number(e.target.value))}
                          className="mt-1 h-9 w-full rounded-md border border-input bg-background px-2 text-xs font-semibold text-foreground"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] uppercase tracking-wider text-muted-foreground">Off-Peak Tariff</label>
                        <input
                          type="number"
                          step="0.1"
                          value={offPeakTariff}
                          onChange={(e) => setOffPeakTariff(Number(e.target.value))}
                          className="mt-1 h-9 w-full rounded-md border border-input bg-background px-2 text-xs font-semibold text-teal"
                        />
                      </div>
                    </div>
                  </>
                )}

                {interventionType === "equipment_upgrade" && (
                  <>
                    <div>
                      <div className="flex justify-between text-xs mb-1.5">
                        <span className="text-muted-foreground">Motor Rating</span>
                        <span className="font-semibold text-foreground font-display">{connectedLoadKw} kW</span>
                      </div>
                      <input
                        type="range"
                        min="20"
                        max="250"
                        step="5"
                        value={connectedLoadKw}
                        onChange={(e) => setConnectedLoadKw(Number(e.target.value))}
                        className="w-full accent-teal"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1.5">
                        <span className="text-muted-foreground">Efficiency Gain</span>
                        <span className="font-semibold text-teal font-display">{efficiencyGainPct}%</span>
                      </div>
                      <input
                        type="range"
                        min="5"
                        max="35"
                        step="1"
                        value={efficiencyGainPct}
                        onChange={(e) => setEfficiencyGainPct(Number(e.target.value))}
                        className="w-full accent-teal"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] uppercase tracking-wider text-muted-foreground">Estimated Capex (₹)</label>
                      <input
                        type="number"
                        step="5000"
                        value={equipmentCapex}
                        onChange={(e) => setEquipmentCapex(Number(e.target.value))}
                        className="mt-1 h-9 w-full rounded-md border border-input bg-background px-2 text-xs font-semibold text-foreground"
                      />
                    </div>
                  </>
                )}

                {interventionType === "process_change" && (
                  <>
                    <div>
                      <div className="flex justify-between text-xs mb-1.5">
                        <span className="text-muted-foreground">Pneumatic Leak Points</span>
                        <span className="font-semibold text-foreground font-display">{leakCount} points</span>
                      </div>
                      <input
                        type="range"
                        min="1"
                        max="20"
                        step="1"
                        value={leakCount}
                        onChange={(e) => setLeakCount(Number(e.target.value))}
                        className="w-full accent-amber"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] uppercase tracking-wider text-muted-foreground">Repair Cost (₹)</label>
                      <input
                        type="number"
                        step="1000"
                        value={repairCapex}
                        onChange={(e) => setRepairCapex(Number(e.target.value))}
                        className="mt-1 h-9 w-full rounded-md border border-input bg-background px-2 text-xs font-semibold text-foreground"
                      />
                    </div>
                  </>
                )}

                <Button
                  onClick={() => triggerSimulation()}
                  className="w-full bg-accent text-foreground hover:bg-accent/80 text-xs mt-2"
                >
                  Apply & Recalculate
                </Button>
              </div>
            </div>
          </div>

          {/* Right Column: Projected Before/After & Financial ROI Results */}
          <div className="space-y-6">
            {result && (
              <>
                {/* Highlight Hero Card */}
                <div className="rounded-xl border border-teal/40 bg-teal-soft/30 p-6 sm:p-7">
                  <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-teal">
                    <Sparkles className="h-3.5 w-3.5" /> Simulation Result · {result.intervention_title}
                  </div>
                  <h2 className="mt-3 font-display text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
                    Save <span className="text-teal">₹{result.projected_savings_rupees_per_month.toLocaleString("en-IN")} / month</span>
                  </h2>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {result.summary}
                  </p>

                  <div className="mt-6 grid gap-4 border-t border-teal/20 pt-5 sm:grid-cols-3">
                    <div>
                      <div className="text-[10px] uppercase tracking-[0.16em] text-muted-foreground">Payback Time</div>
                      <div className="mt-1 font-display text-2xl font-semibold text-amber">
                        {result.payback_months} <span className="text-xs font-normal text-muted-foreground">months</span>
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] uppercase tracking-[0.16em] text-muted-foreground">Monthly Energy Reduction</div>
                      <div className="mt-1 font-display text-2xl font-semibold text-foreground">
                        {result.kwh_saved_monthly > 0 ? `${result.kwh_saved_monthly.toLocaleString("en-IN")} kWh` : "Tariff Delta"}
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] uppercase tracking-[0.16em] text-muted-foreground">CO₂ Avoided</div>
                      <div className="mt-1 font-display text-2xl font-semibold text-teal">
                        {result.co2_reduction_tons_per_year} <span className="text-xs font-normal text-muted-foreground">t / yr</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Before vs After Comparison Grid */}
                <div className="grid gap-5 sm:grid-cols-2">
                  <div className="glass-panel rounded-xl border border-border p-5">
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span className="font-semibold uppercase tracking-wider">Baseline (Current)</span>
                      <span className="h-2 w-2 rounded-full bg-border" />
                    </div>
                    <div className="mt-4 font-display text-3xl font-semibold text-foreground">
                      ₹{result.baseline_cost_rupees_per_month.toLocaleString("en-IN")}
                      <span className="text-xs text-muted-foreground font-normal ml-1">/ mo</span>
                    </div>
                    <div className="mt-2 text-xs text-muted-foreground">
                      Monthly consumption: <strong className="text-foreground">{result.baseline_kwh.toLocaleString("en-IN")} kWh</strong>
                    </div>
                  </div>

                  <div className="glass-panel rounded-xl border border-teal/40 bg-panel-raised p-5">
                    <div className="flex items-center justify-between text-xs text-teal">
                      <span className="font-semibold uppercase tracking-wider">Projected (After Fix)</span>
                      <span className="h-2 w-2 rounded-full bg-teal" />
                    </div>
                    <div className="mt-4 font-display text-3xl font-semibold text-teal">
                      ₹{result.projected_cost_rupees_per_month.toLocaleString("en-IN")}
                      <span className="text-xs text-muted-foreground font-normal ml-1">/ mo</span>
                    </div>
                    <div className="mt-2 text-xs text-teal flex items-center gap-1.5 font-medium">
                      <TrendingDown className="h-3.5 w-3.5" />
                      ₹{result.projected_savings_rupees_per_month.toLocaleString("en-IN")} / month net reduction
                    </div>
                  </div>
                </div>

                {/* Action Card */}
                <div className="glass-panel flex flex-col items-start justify-between gap-4 rounded-xl border border-border p-5 sm:flex-row sm:items-center">
                  <div>
                    <h4 className="font-display text-sm font-semibold text-foreground">
                      Ready to implement this recommendation?
                    </h4>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Check government scheme eligibility to co-fund up to 35% of capex.
                    </p>
                  </div>
                  <Link to="/audit">
                    <Button variant="outline" className="gap-2 border-border bg-panel text-xs">
                      View Matching Subsidies <ChevronRight className="h-3.5 w-3.5" />
                    </Button>
                  </Link>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
