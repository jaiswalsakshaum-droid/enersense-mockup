import { useQuery } from "@tanstack/react-query";
import { createFileRoute, Link, redirect } from "@tanstack/react-router";
import {
  AlertTriangle,
  ArrowUpRight,
  Award,
  Bolt,
  ChevronRight,
  Clock3,
  Leaf,
  ShieldAlert,
  Zap,
} from "lucide-react";
import {
  AppShell,
  Gauge,
  PageHeading,
  SectionLabel,
  StatCard,
  TrendChart,
} from "@/components/enersense";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { validateSession } from "@/lib/auth";
import { fetchDashboardSummary } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";

export const Route = createFileRoute("/dashboard")({
  beforeLoad: async () => {
    const user = await validateSession();

    if (!user) {
      throw redirect({ to: "/auth" });
    }
  },
  head: () => ({
    meta: [
      { title: "Dashboard — EnerSense" },
      {
        name: "description",
        content: "Live plant energy health, consumption, cost, and alerts overview.",
      },
      { property: "og:title", content: "Dashboard — EnerSense" },
      {
        property: "og:description",
        content: "Live plant energy health, consumption, cost, and alerts overview.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Dashboard,
});

function Dashboard() {
  const { t } = useTranslation();
  const { data, isPending, isError, error, refetch, isFetching } = useQuery({
    queryKey: ["dashboardSummary"],
    queryFn: fetchDashboardSummary,
  });

  if (isPending) {
    return (
      <AppShell>
        <div className="rise-in space-y-6" aria-label="Loading dashboard" aria-busy="true">
          <div className="flex items-center justify-between">
            <Skeleton className="h-10 w-64 bg-panel" />
            <Skeleton className="h-9 w-32 bg-panel" />
          </div>
          <div className="grid gap-5 xl:grid-cols-[310px_1fr]">
            <Skeleton className="h-[280px] rounded-xl bg-panel" />
            <div className="grid gap-5 sm:grid-cols-2">
              {Array.from({ length: 4 }, (_, index) => (
                <Skeleton key={index} className="h-36 rounded-xl bg-panel" />
              ))}
            </div>
          </div>
          <div className="grid gap-5 xl:grid-cols-[1fr_340px]">
            <Skeleton className="h-[360px] rounded-xl bg-panel" />
            <Skeleton className="h-[360px] rounded-xl bg-panel" />
          </div>
        </div>
      </AppShell>
    );
  }

  if (isError || !data) {
    return (
      <AppShell>
        <div
          className="flex flex-col items-center justify-center rounded-2xl border border-destructive/30 bg-destructive/10 p-12 text-center"
          role="alert"
        >
          <ShieldAlert className="h-12 w-12 text-critical" aria-hidden="true" />
          <h2 className="mt-4 font-display text-xl font-semibold text-foreground">
            Failed to load dashboard data
          </h2>
          <p className="mt-2 max-w-md text-sm text-muted-foreground">
            {error instanceof Error
              ? error.message
              : "Check that the EnerSense backend is running, then try again."}
          </p>
          <Button
            onClick={() => void refetch()}
            disabled={isFetching}
            className="mt-6 bg-amber text-primary-foreground hover:bg-amber/90"
          >
            {isFetching ? "Connecting…" : "Retry connection"}
          </Button>
        </div>
      </AppShell>
    );
  }

  const benchmark = data.peer_benchmark;

  return (
    <AppShell>
      <div className="rise-in">
        <PageHeading
          eyebrow="PLANT OPERATIONS · LIVE"
          title="Good morning"
          description={`Here’s the operating pulse for ${data.plant_name}.`}
          action={
            <Button variant="outline" className="gap-2 border-border bg-panel">
              <Clock3 className="h-4 w-4 text-teal" aria-hidden="true" />
              Last 7 days
            </Button>
          }
        />

        <div className="grid gap-5 xl:grid-cols-[310px_1fr]">
          <section className="glass-panel flex flex-col items-center justify-between rounded-xl border border-border p-6 sm:flex-row xl:flex-col">
            <div className="w-full">
              <SectionLabel>{t("stat.health_score", "Overall energy health")}</SectionLabel>
              <div className="mt-2 flex items-center justify-between xl:block">
                <div>
                  <h2 className="font-display text-lg font-semibold text-foreground">
                    {t("stat.plant_score", "Plant score")}
                  </h2>
                  <p className="mt-1 text-xs text-muted-foreground">Live composite calculation</p>
                </div>
                <div className="hidden text-right text-xs text-muted-foreground sm:block xl:hidden">
                  Target
                  <br />
                  <strong className="font-display text-base text-teal">{data.score_target}+</strong>
                </div>
              </div>
            </div>
            <Gauge value={data.health_score} />
            <div className="flex w-full items-center justify-between border-t border-border pt-4 text-xs">
              <span className="flex items-center gap-1.5 text-teal">
                <span className="h-1.5 w-1.5 rounded-full bg-teal" aria-hidden="true" />
                {t("stat.healthy_range", "Healthy operating range")}
              </span>
              <span className="font-semibold text-foreground">
                {data.health_change_pct > 0 ? "+" : ""}
                {data.health_change_pct}%
              </span>
            </div>
          </section>

          <div className="grid gap-5 sm:grid-cols-2">
            <StatCard
              label={t("stat.energy_use", "Today’s energy use")}
              value={data.energy_use_today_kwh.toLocaleString("en-IN")}
              unit="kWh"
              change={`${Math.abs(data.energy_use_change_pct)}% ${data.energy_use_change_pct <= 0 ? "lower" : "higher"}`}
              positive={data.energy_use_change_pct <= 0}
              icon={Zap}
            />
            <StatCard
              label={t("stat.energy_cost", "Today’s energy cost")}
              value={`₹${data.energy_cost_today_inr.toLocaleString("en-IN")}`}
              change={`${Math.abs(data.energy_cost_change_pct)}% ${data.energy_cost_change_pct <= 0 ? "lower" : "higher"}`}
              positive={data.energy_cost_change_pct <= 0}
              icon={Bolt}
              tone="amber"
            />
            <StatCard
              label={t("stat.co2_emitted", "CO₂e emitted")}
              value={data.co2e_today_tons.toString()}
              unit="t"
              change={`${Math.abs(data.co2e_change_pct)}% ${data.co2e_change_pct <= 0 ? "lower" : "higher"}`}
              positive={data.co2e_change_pct <= 0}
              icon={Leaf}
            />
            <StatCard
              label={t("stat.active_alerts", "Active alerts")}
              value={data.active_alerts_count.toString().padStart(2, "0")}
              change={data.active_alerts_change}
              icon={AlertTriangle}
              tone="critical"
            />
          </div>
        </div>

        {benchmark && (
          <section
            className="mt-5 rounded-xl border border-teal/30 bg-panel-raised p-5"
            aria-label="Peer benchmarking"
          >
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex items-start gap-3.5">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-teal-soft text-teal">
                  <Award className="h-5 w-5" aria-hidden="true" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-semibold uppercase tracking-[0.2em] text-teal">
                      {t("dash.benchmark_title", "Peer Benchmarking")}
                    </span>
                    <span className="rounded-full bg-teal-soft px-2 py-0.5 text-[10px] font-bold text-teal">
                      Top {100 - benchmark.percentile}% Tier
                    </span>
                  </div>
                  <h2 className="mt-1 font-display text-base font-semibold text-foreground">
                    {benchmark.comparison_text}
                  </h2>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    Benchmark against anonymized cohort:{" "}
                    <strong className="text-foreground">{benchmark.industry_label}</strong>
                  </p>
                </div>
              </div>
              <div className="flex min-w-[280px] flex-col gap-2 rounded-lg border border-border bg-panel p-3 text-xs">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-medium text-teal">Your plant</span>
                  <span className="font-display font-bold text-foreground">
                    {benchmark.plant_score} / 100
                  </span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                  <div
                    className="h-full rounded-full bg-teal"
                    style={{ width: `${benchmark.plant_score}%` }}
                  />
                </div>
                <div className="mt-1 flex items-center justify-between text-[11px] text-muted-foreground">
                  <span>Cluster avg ({benchmark.peer_average_score})</span>
                  <span>Top 10% ({benchmark.peer_top_quartile})</span>
                </div>
                <div className="relative h-1.5 w-full overflow-hidden rounded-full bg-secondary">
                  <div
                    className="absolute left-0 top-0 h-full bg-amber/70"
                    style={{ width: `${benchmark.peer_average_score}%` }}
                  />
                  <div
                    className="absolute top-0 h-full w-1 bg-teal"
                    style={{ left: `${benchmark.peer_top_quartile}%` }}
                    title="Top 10% benchmark"
                  />
                </div>
              </div>
            </div>
          </section>
        )}

        <div className="mt-5 grid gap-5 xl:grid-cols-[1fr_340px]">
          <section className="glass-panel rounded-xl border border-border p-6">
            <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
              <div>
                <SectionLabel>Energy consumption</SectionLabel>
                <h2 className="mt-2 font-display text-lg font-semibold text-foreground">
                  {t("dash.load_title", "Plant load over time")}
                </h2>
                <p className="mt-1 text-xs text-muted-foreground">
                  {t("dash.load_desc", "Aggregate energy use across monitored machines")}
                </p>
              </div>
              <div className="flex items-center gap-4 text-xs">
                <span className="flex items-center gap-2 text-muted-foreground">
                  <span className="h-2 w-2 rounded-full bg-teal" />
                  Actual
                </span>
                <span className="flex items-center gap-2 text-muted-foreground">
                  <span className="h-2 w-2 rounded-full bg-border" />
                  Baseline
                </span>
              </div>
            </div>
            <div className="mt-8">
              <TrendChart values={data.energy_trend_24h} baselineValues={data.baseline_trend_24h} />
            </div>
          </section>

          <section className="glass-panel rounded-xl border border-border p-6">
            <div className="flex items-start justify-between">
              <div>
                <SectionLabel>Attention needed</SectionLabel>
                <h2 className="mt-2 font-display text-lg font-semibold text-foreground">
                  {t("dash.attention_title", "Latest alerts")}
                </h2>
              </div>
              <Link to="/alerts" aria-label="View all alerts">
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-muted-foreground"
                  aria-label="View all alerts"
                >
                  <ArrowUpRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
            <div className="mt-6 space-y-5">
              {data.latest_alerts.length > 0 ? (
                data.latest_alerts.map((alert) => (
                  <div key={alert.id} className="flex gap-3">
                    <div
                      className={`mt-1 h-2 w-2 shrink-0 rounded-full ${alert.severity.toLowerCase() === "critical" ? "bg-critical" : "bg-amber"}`}
                      aria-hidden="true"
                    />
                    <div>
                      <div className="text-sm font-medium text-foreground">
                        {alert.machine_name}
                      </div>
                      <div className="mt-1 text-xs leading-5 text-muted-foreground">
                        {alert.detail}
                      </div>
                      <div className="mt-2 text-[10px] text-muted-foreground">{alert.time}</div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No recent alerts.</p>
              )}
              <div className="border-t border-border pt-5">
                <Link to="/alerts">
                  <Button
                    variant="ghost"
                    className="h-auto p-0 text-xs text-teal hover:bg-transparent hover:text-teal"
                  >
                    {t("dash.view_all_alerts", "View all alerts")}{" "}
                    <ChevronRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </div>
            </div>
          </section>
        </div>
      </div>
    </AppShell>
  );
}
