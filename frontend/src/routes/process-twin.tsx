import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Clock } from "lucide-react";
import {
  Factory,
  Leaf,
  Zap,
  IndianRupee,
  CheckCircle2,
  XCircle,
} from "lucide-react";

import {
  createProductionOrder,
  runProcessTwin,
  type ProcessTwinResult,
} from "@/lib/api";
import {
  AppShell,
  PageHeading,
  SectionLabel,
} from "@/components/enersense";

import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/process-twin")({
  component: ProcessTwin,
});

function ProcessTwin() {
const [quantity, setQuantity] = useState("10000");
const [quality, setQuality] = useState("95");
const [carbonBudget, setCarbonBudget] = useState("15000");

  // User-friendly format: DD-MM-YYYY HH:MM
  const [deadlineDate, setDeadlineDate] = useState("2026-09-29");
  const [deadlineTime, setDeadlineTime] = useState("23:59");
  

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProcessTwinResult | null>(null);
  const [error, setError] = useState("");

  async function generatePlan() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const orderId = `ORD-${Date.now()}`;

      const order = await createProductionOrder({
        order_id: orderId,
        factory_id: "FAC-001",
        product_id: "PROD-001",
        quantity: Number(quantity),
        deadline: formatDeadline(deadlineDate, deadlineTime),
        minimum_quality: Number(quality),
        carbon_budget_kg: Number(carbonBudget),
        priority: "HIGH",
      });

      const plan = await runProcessTwin(order.order_id);

      setResult(plan);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong"
      );
    } finally {
      setLoading(false);
    }
  }

  const bestPlan = result?.best_scenario;
  const completionDate = bestPlan
  ? new Date(bestPlan.completion_time)
  : null;

const deadlineDateTime = new Date(
  formatDeadline(deadlineDate, deadlineTime)
);

const isWithinDeadline =
  completionDate !== null &&
  completionDate.getTime() <= deadlineDateTime.getTime();

const timeDifferenceHours = completionDate
  ? Math.abs(
      deadlineDateTime.getTime() - completionDate.getTime()
    ) / (1000 * 60 * 60)
  : 0;

const differenceDays = Math.floor(timeDifferenceHours / 24);
const differenceHours = Math.round(timeDifferenceHours % 24);

  return (
    <AppShell>
      <div className="rise-in">
        <PageHeading
          eyebrow="PRODUCTION INTELLIGENCE"
          title="ProcessTwin AI"
          description="Simulate production decisions and find an energy-efficient plan that satisfies cost, quality, carbon and deadline constraints."
        />

        {/* Main configuration */}
        <div className="grid gap-5 xl:grid-cols-[1fr_360px]">

          {/* Order form */}
          <section className="glass-panel rounded-xl border border-border p-6">
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-soft text-amber">
                <Factory className="h-5 w-5" />
              </div>

              <div>
                <SectionLabel>Production order</SectionLabel>

                <h2 className="mt-2 font-display text-lg font-semibold text-foreground">
                  Configure your next production run
                </h2>

                <p className="mt-1 text-xs text-muted-foreground">
                  ProcessTwin will evaluate possible machine allocations.
                </p>
              </div>
            </div>

            <div className="mt-7 grid gap-5 sm:grid-cols-2">

              {/* Quantity */}
              <div>
                <label className="mb-2 block text-xs font-medium text-foreground">
                  Quantity
                </label>

               <input
               type="text"
               inputMode="numeric"
               value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  className="h-11 w-full rounded-lg border border-input bg-background px-3.5 text-sm text-foreground outline-none focus:border-amber focus:ring-1 focus:ring-amber"
                />

                <p className="mt-1.5 text-[10px] text-muted-foreground">
                  Units to manufacture
                </p>
              </div>

              <div>
  <label className="mb-2 block text-xs font-medium text-foreground">
    Deadline
  </label>

  <div className="grid grid-cols-[1fr_120px] gap-2">
    <input
      type="date"
      value={deadlineDate}
      onChange={(e) => setDeadlineDate(e.target.value)}
      className="h-11 w-full rounded-lg border border-input bg-background px-3.5 text-sm text-foreground outline-none focus:border-amber focus:ring-1 focus:ring-amber"
    />

    <input
      type="time"
      value={deadlineTime}
      onChange={(e) => setDeadlineTime(e.target.value)}
      className="h-11 w-full rounded-lg border border-input bg-background px-3.5 text-sm text-foreground outline-none focus:border-amber focus:ring-1 focus:ring-amber"
    />
  </div>

  <p className="mt-1.5 text-[10px] text-muted-foreground">
    Date and time by which production must be completed
  </p>
</div>
              {/* Minimum quality */}
              <div>
                <label className="mb-2 block text-xs font-medium text-foreground">
                  Minimum quality
                </label>

                <div className="relative">
                    <input
                  type="text"
                  inputMode="numeric"
                  value={quality}
                    onChange={(e) => setQuality(e.target.value)}
                    className="h-11 w-full rounded-lg border border-input bg-background px-3.5 text-sm text-foreground outline-none focus:border-amber focus:ring-1 focus:ring-amber"
                  />

                  <span className="absolute right-3 top-3 text-xs text-muted-foreground">
                    %
                  </span>
                </div>
              </div>

              {/* Carbon budget */}
              <div>
                <label className="mb-2 block text-xs font-medium text-foreground">
                  Carbon budget
                </label>

                <div className="relative">
                  <input
                   type="text"
                   inputMode="numeric"
                   value={carbonBudget}
                    onChange={(e) =>
                      setCarbonBudget(e.target.value)
                    }
                    className="h-11 w-full rounded-lg border border-input bg-background px-3.5 text-sm text-foreground outline-none focus:border-amber focus:ring-1 focus:ring-amber"
                  />

                  <span className="absolute right-3 top-3 text-xs text-muted-foreground">
                    kg
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-7 border-t border-border pt-5">
              <Button
                onClick={generatePlan}
                disabled={loading}
                className="h-11 bg-amber px-6 text-primary-foreground hover:bg-amber/90"
              >
                {loading
                  ? "Optimizing production..."
                  : "Generate Optimized Plan"}
              </Button>

              <span className="ml-4 text-xs text-muted-foreground">
                Evaluates energy, cost, quality & carbon
              </span>
            </div>

            {error && (
              <div className="mt-5 rounded-lg border border-critical/30 bg-critical/10 p-4 text-sm text-critical">
                {error}
              </div>
            )}
          </section>

          {/* Decision explanation */}
          <section className="rounded-xl border border-teal/30 bg-panel-raised p-6">
            <SectionLabel>Decision engine</SectionLabel>

            <h2 className="mt-2 font-display text-lg font-semibold text-foreground">
              What ProcessTwin evaluates
            </h2>

            <div className="mt-6 space-y-5">
              <DecisionItem
                icon={Zap}
                title="Energy"
                description="Minimize electricity consumed by the production run."
              />

              <DecisionItem
                icon={IndianRupee}
                title="Cost"
                description="Find the lowest-cost feasible machine allocation."
              />

              <DecisionItem
                icon={Leaf}
                title="Carbon"
                description="Keep production within the defined carbon budget."
              />

              <DecisionItem
                icon={Factory}
                title="Capacity"
                description="Distribute production according to machine capacity."
              />
            </div>
          </section>
        </div>

        {/* Results */}
                    {!bestPlan && result && (
          <div className="mt-8">
            <section className="glass-panel rounded-xl border border-border p-6">
              <div className="flex items-start gap-4">
                <div className="mt-1 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-amber/10 text-amber">
                  <XCircle size={20} />
                </div>

                <div>
                  <h2 className="font-display text-lg font-semibold text-foreground">
                    No feasible production plan
                  </h2>

                  <p className="mt-2 text-sm text-muted-foreground">
                    None of the available machine allocations satisfy all of
                    the selected production constraints.
                  </p>

                  <p className="mt-2 text-xs text-muted-foreground">
                    Try increasing the carbon budget, reducing the minimum
                    quality requirement, or adjusting the deadline.
                  </p>
                </div>
              </div>
            </section>
          </div>
        )}
        {bestPlan && (
          <div className="mt-8">
            <PageHeading
              eyebrow="OPTIMIZATION RESULT"
              title="Recommended production plan"
              description={result?.recommendation ?? ""}
            />

            <section className="glass-panel mt-5 rounded-xl border border-border p-5">
              <SectionLabel>Production requirements</SectionLabel>

              <div className="mt-4 grid gap-4 sm:grid-cols-4">
                <div>
                  <div className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
                    Quantity
                  </div>
                  <div className="mt-1 font-semibold text-foreground">
                    {quantity} units
                  </div>
                </div>

                <div>
                  <div className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
                    Minimum quality
                  </div>
                  <div className="mt-1 font-semibold text-foreground">
                    {quality}%
                  </div>
                </div>

                <div>
                  <div className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
                    Carbon budget
                  </div>
                  <div className="mt-1 font-semibold text-foreground">
                    {carbonBudget} kg
                  </div>
                </div>

                <div>
                  <div className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
                    Deadline
                  </div>
                  <div className="mt-1 font-semibold text-foreground">
                    {deadlineDate} {deadlineTime}
                  </div>
                </div>
              </div>
            </section>

           <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
  <div className="glass-panel rounded-xl border border-border p-5 transition-all hover:-translate-y-0.5 hover:border-amber/40">
    <div className="flex items-center justify-between">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-soft text-amber">
        <Zap className="h-5 w-5" />
      </div>
      <span className="text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
        Efficiency
      </span>
    </div>

    <div className="mt-5 text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground">
      Energy
    </div>

    <div className="mt-1 font-display text-2xl font-semibold text-foreground">
      {bestPlan.energy_kwh}
      <span className="ml-1 text-sm font-medium text-muted-foreground">
        kWh
      </span>
    </div>
  </div>

  <div className="glass-panel rounded-xl border border-border p-5 transition-all hover:-translate-y-0.5 hover:border-amber/40">
    <div className="flex items-center justify-between">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-soft text-amber">
        <IndianRupee className="h-5 w-5" />
      </div>
      <span className="text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
        Cost
      </span>
    </div>

    <div className="mt-5 text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground">
      Production cost
    </div>

    <div className="mt-1 font-display text-2xl font-semibold text-foreground">
      ₹{bestPlan.energy_cost_inr}
    </div>
  </div>

  <div className="glass-panel rounded-xl border border-border p-5 transition-all hover:-translate-y-0.5 hover:border-amber/40">
    <div className="flex items-center justify-between">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-soft text-amber">
        <Leaf className="h-5 w-5" />
      </div>
      <span className="text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
        Sustainability
      </span>
    </div>

    <div className="mt-5 text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground">
      Carbon
    </div>

    <div className="mt-1 font-display text-2xl font-semibold text-foreground">
      {bestPlan.carbon_kg}
      <span className="ml-1 text-sm font-medium text-muted-foreground">
        kg
      </span>
    </div>
  </div>

  <div className="glass-panel rounded-xl border border-border p-5 transition-all hover:-translate-y-0.5 hover:border-amber/40">
    <div className="flex items-center justify-between">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-soft text-amber">
        <Factory className="h-5 w-5" />
      </div>
      <span className="text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
        Quality
      </span>
    </div>

    <div className="mt-5 text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground">
      Quality score
    </div>

    <div className="mt-1 font-display text-2xl font-semibold text-foreground">
      {bestPlan.quality_percent}
      <span className="ml-1 text-sm font-medium text-muted-foreground">
        %
      </span>
    </div>
  </div>
</div>
            <section className="glass-panel mt-5 rounded-xl border border-border p-6">
              <SectionLabel>Machine allocation</SectionLabel>

              <h2 className="mt-2 font-display text-lg font-semibold text-foreground">
                Recommended production run
              </h2>

              <div className="mt-5 rounded-lg border border-border bg-panel-raised p-4">
                <div className="text-sm font-medium text-foreground">
                  {bestPlan.machine_name}
                </div>

                <div className="mt-1 text-[11px] text-muted-foreground">
                  Machine selected by ProcessTwin
                </div>

                <div className="mt-4 grid gap-4 sm:grid-cols-3">
                  <div>
                    <div className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
                      Quantity
                    </div>

                    <div className="mt-1 font-display text-lg font-semibold text-foreground">
                      {bestPlan.quantity} units
                    </div>
                  </div>

                  <div>
                    <div className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
                      Duration
                    </div>

                    <div className="mt-1 font-display text-lg font-semibold text-foreground">
                      {bestPlan.duration_hours} hours
                    </div>
                  </div>

                  <div>
                    <div className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
                      Expected defects
                    </div>

                    <div className="mt-1 font-display text-lg font-semibold text-foreground">
                      {bestPlan.expected_defects}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                <Constraint
                  label="Deadline"
                  passed={bestPlan.deadline_met}
                />

                <Constraint
                  label="Quality"
                  passed={bestPlan.quality_met}
                />

                <Constraint
                  label="Carbon budget"
                  passed={bestPlan.carbon_budget_met}
                />
              </div>

             <div className="mt-5 rounded-xl border border-border bg-panel p-5">
  <div className="flex items-center justify-between">
    <div>
      <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
        Expected completion
      </div>

      <div className="mt-2 font-display text-xl font-semibold text-foreground">
        {new Date(bestPlan.completion_time).toLocaleDateString("en-IN", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        })}
      </div>

      <div className="mt-1 text-sm text-muted-foreground">
        {new Date(bestPlan.completion_time).toLocaleTimeString("en-IN", {
          hour: "2-digit",
          minute: "2-digit",
        })}
      </div>
    </div>

    <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
      <Clock size={20} />
    </div>
  </div>

  <div className="mt-4 border-t border-border pt-3">
    <div className="text-xs text-muted-foreground">
      Production duration
    </div>

    <div className="mt-1 text-sm font-medium text-foreground">
      {bestPlan.duration_hours} hours
    </div>
  </div>
      <div
  className={`mt-4 rounded-lg px-3 py-2.5 ${
    isWithinDeadline
      ? "bg-primary/10 text-primary"
      : "bg-amber/10 text-amber"
  }`}
>
  <div className="flex items-center gap-2 text-sm font-medium">
    <Clock size={16} />

    {isWithinDeadline
      ? "Within deadline"
      : "Deadline exceeded"}
  </div>

  <div className="mt-1 text-xs opacity-80">
    {isWithinDeadline
      ? differenceDays > 0
        ? `Finishes ${differenceDays} day${
            differenceDays > 1 ? "s" : ""
          } ${
            differenceHours > 0
              ? `${differenceHours} hour${
                  differenceHours > 1 ? "s" : ""
                }`
              : ""
          } early`
        : `Finishes ${differenceHours} hour${
            differenceHours !== 1 ? "s" : ""
          } early`
      : `Finishes ${differenceDays > 0 ? `${differenceDays} day${differenceDays > 1 ? "s" : ""} ` : ""}${differenceHours} hour${
          differenceHours !== 1 ? "s" : ""
        } late`}
  </div>
</div>
</div>
            </section>
          </div>
        )}
      </div>
    </AppShell>
  );
}

function DecisionItem({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof Zap;
  title: string;
  description: string;
}) {
  return (
    <div className="flex gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-teal-soft text-teal">
        <Icon className="h-4 w-4" />
      </div>

      <div>
        <div className="text-sm font-medium text-foreground">
          {title}
        </div>

        <div className="mt-1 text-[11px] leading-5 text-muted-foreground">
          {description}
        </div>
      </div>
    </div>
  );
}

function ResultCard({
  icon: Icon,
  label,
  value,
  unit,
}: {
  icon: typeof Zap;
  label: string;
  value: string;
  unit: string;
}) {
  return (
    <div className="glass-panel rounded-xl border border-border p-5">
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-soft text-teal">
        <Icon className="h-[18px] w-[18px]" />
      </div>

      <div className="mt-5 text-xs font-medium text-muted-foreground">
        {label}
      </div>

      <div className="mt-1 flex items-baseline gap-1.5">
        <span className="font-display text-[27px] font-semibold tracking-tight text-foreground">
          {value}
        </span>

        {unit && (
          <span className="text-xs text-muted-foreground">
            {unit}
          </span>
        )}
      </div>
    </div>
  );
}

function Constraint({
  label,
  passed,
}: {
  label: string;
  passed: boolean;
}) {
  return (
    <div
      className={`flex items-center gap-2 rounded-lg border p-3 text-xs ${
        passed
          ? "border-teal/30 bg-teal-soft text-teal"
          : "border-critical/30 bg-critical/10 text-critical"
      }`}
    >
      {passed ? (
        <CheckCircle2 className="h-4 w-4" />
      ) : (
        <XCircle className="h-4 w-4" />
      )}

      <span className="font-medium">
        {label} {passed ? "met" : "not met"}
      </span>
    </div>
  );
}

/*
  Converts the user-friendly deadline format:

  DD-MM-YYYY HH:MM

  into the ISO format expected by the backend:

  YYYY-MM-DDTHH:MM
*/
function formatDeadline(date: string, time: string) {
  if (!date || !time) {
    throw new Error("Please select a deadline date and time.");
  }

  return `${date}T${time}`;
}
  
