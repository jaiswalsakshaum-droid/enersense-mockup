import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Factory, Leaf, Zap, IndianRupee, CheckCircle2, XCircle } from "lucide-react";

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
  const [quantity, setQuantity] = useState(10000);
  const [deadline, setDeadline] = useState("2026-09-19T18:00");
  const [quality, setQuality] = useState(95);
  const [carbonBudget, setCarbonBudget] = useState(15000);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  async function generatePlan() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const orderId = `ORD-${Date.now()}`;

      const orderResponse = await fetch(
        "http://127.0.0.1:4000/api/orders/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            order_id: orderId,
            factory_id: "FAC-001",
            product_id: "PROD-001",
            quantity,
            deadline,
            minimum_quality: quality,
            carbon_budget_kg: carbonBudget,
            priority: "HIGH",
          }),
        }
      );

      if (!orderResponse.ok) {
        const message = await orderResponse.text();
        throw new Error(message || "Could not create order");
      }

      const order = await orderResponse.json();

      const planResponse = await fetch(
        `http://127.0.0.1:4000/api/plans/generate/${order.order_id}`,
        {
          method: "POST",
        }
      );

      const plan = await planResponse.json();

      if (!planResponse.ok) {
        throw new Error(
          plan.detail || "Could not generate production plan"
        );
      }

      setResult(plan);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong"
      );
    } finally {
      setLoading(false);
    }
  }

  const bestPlan = result?.optimization?.best_plan;

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

              <div>
                <label className="mb-2 block text-xs font-medium text-foreground">
                  Quantity
                </label>

                <input
                  type="number"
                  value={quantity}
                  onChange={(e) =>
                    setQuantity(Number(e.target.value))
                  }
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

                <input
                  type="datetime-local"
                  value={deadline}
                  onChange={(e) =>
                    setDeadline(e.target.value)
                  }
                  className="h-11 w-full rounded-lg border border-input bg-background px-3.5 text-sm text-foreground outline-none focus:border-amber focus:ring-1 focus:ring-amber"
                />
              </div>

              <div>
                <label className="mb-2 block text-xs font-medium text-foreground">
                  Minimum quality
                </label>

                <div className="relative">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={quality}
                    onChange={(e) =>
                      setQuality(Number(e.target.value))
                    }
                    className="h-11 w-full rounded-lg border border-input bg-background px-3.5 text-sm text-foreground outline-none focus:border-amber focus:ring-1 focus:ring-amber"
                  />

                  <span className="absolute right-3 top-3 text-xs text-muted-foreground">
                    %
                  </span>
                </div>
              </div>

              <div>
                <label className="mb-2 block text-xs font-medium text-foreground">
                  Carbon budget
                </label>

                <div className="relative">
                  <input
                    type="number"
                    value={carbonBudget}
                    onChange={(e) =>
                      setCarbonBudget(Number(e.target.value))
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
        {bestPlan && (
          <div className="mt-8">

            <PageHeading
              eyebrow="OPTIMIZATION RESULT"
              title="Recommended production plan"
              description="The lowest-cost allocation that satisfies the current production constraints."
            />

            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">

              <ResultCard
                icon={Zap}
                label="Energy"
                value={`${bestPlan.energy_kwh}`}
                unit="kWh"
              />

              <ResultCard
                icon={IndianRupee}
                label="Production cost"
                value={`₹${bestPlan.cost_inr}`}
                unit=""
              />

              <ResultCard
                icon={Leaf}
                label="Carbon"
                value={`${bestPlan.carbon_kg}`}
                unit="kg"
              />

              <ResultCard
                icon={Factory}
                label="Quality"
                value={`${bestPlan.quality_percent}`}
                unit="%"
              />

            </div>

            {/* Allocation */}
            <section className="glass-panel mt-5 rounded-xl border border-border p-6">

              <SectionLabel>Machine allocation</SectionLabel>

              <h2 className="mt-2 font-display text-lg font-semibold text-foreground">
                Recommended production split
              </h2>

              <div className="mt-5 space-y-3">

                {Object.entries(bestPlan.allocation).map(
                  ([machine, units]) => (
                    <div
                      key={machine}
                      className="flex items-center justify-between rounded-lg border border-border bg-panel-raised p-4"
                    >
                      <div>
                        <div className="text-sm font-medium text-foreground">
                          {machine}
                        </div>

                        <div className="mt-1 text-[11px] text-muted-foreground">
                          Assigned production quantity
                        </div>
                      </div>

                      <div className="font-display text-lg font-semibold text-amber">
                        {String(units)} units
                      </div>
                    </div>
                  )
                )}

              </div>

              {/* Constraint checks */}
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

              <div className="mt-5 rounded-lg border border-border bg-panel p-4">

                <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  Expected completion
                </div>

                <div className="mt-2 font-display text-lg font-semibold text-foreground">
                  {bestPlan.completion_time}
                </div>

                <div className="mt-1 text-xs text-muted-foreground">
                  Estimated production duration:{" "}
                  {bestPlan.duration_hours} hours
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