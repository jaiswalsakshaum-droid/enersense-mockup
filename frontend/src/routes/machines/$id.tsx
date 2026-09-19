import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, CalendarDays, Cpu, Gauge, MoreHorizontal, Power, Radio, ShieldAlert, Thermometer, Vibrate, Wrench } from "lucide-react";
import { useEffect, useState } from "react";
import { AppShell, MiniSparkline, PageHeading, Readout, SectionLabel, StatusBadge, TrendChart } from "@/components/enersense";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchMachineDetail, getLiveStreamUrl, type LiveStreamPayload, type MachineStatus } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";

export const Route = createFileRoute("/machines/$id")({
  head: () => ({
    meta: [
      { title: "Machine detail — EnerSense" },
      { name: "description", content: "Real-time machine readings and maintenance history for plant equipment." },
      { property: "og:title", content: "Machine detail — EnerSense" },
      { property: "og:description", content: "Real-time machine readings and maintenance history for plant equipment." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: MachineDetail,
});

function MachineDetail() {
  const { id } = Route.useParams();
  const { t } = useTranslation();

  const { data: initialMachine, isLoading, isError, refetch } = useQuery({
    queryKey: ["machine", id],
    queryFn: () => fetchMachineDetail(id),
  });

  // Real-time live SSE stream states
  const [livePower, setLivePower] = useState<number | null>(null);
  const [liveTemp, setLiveTemp] = useState<number | null>(null);
  const [liveVibe, setLiveVibe] = useState<number | null>(null);
  const [liveScore, setLiveScore] = useState<number | null>(null);
  const [liveStatus, setLiveStatus] = useState<MachineStatus | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [liveTrend, setLiveTrend] = useState<number[]>([]);
  const [lastStreamTime, setLastStreamTime] = useState<string>("");

  // Sync initial query values to local live state
  useEffect(() => {
    if (initialMachine) {
      setLivePower(initialMachine.power_kw);
      setLiveTemp(initialMachine.temperature_c);
      setLiveVibe(initialMachine.vibration_mms);
      setLiveScore(initialMachine.score);
      setLiveStatus(initialMachine.status);
      setLiveTrend(initialMachine.history_readings_24h || [62, 68, 64, 75, 72, 80, 78, 86, 83, 90, 87, 94]);
    }
  }, [initialMachine]);

  // Subscribe to SSE Live Telemetry Stream
  useEffect(() => {
    if (!id) return;
    const url = getLiveStreamUrl(id);
    let eventSource: EventSource | null = null;

    try {
      eventSource = new EventSource(url);

      eventSource.onopen = () => {
        setIsStreaming(true);
      };

      eventSource.onmessage = (event) => {
        try {
          const payload: LiveStreamPayload = JSON.parse(event.data);
          if (payload) {
            setLivePower(payload.power_kw);
            setLiveTemp(payload.temperature_c);
            setLiveVibe(payload.vibration_mms);
            setLiveScore(payload.score);
            setLiveStatus(payload.status);
            setLastStreamTime(payload.timestamp);
            setIsStreaming(true);

            // Append new reading to live trend
            setLiveTrend((prev) => {
              const updated = [...prev.slice(1), payload.power_kw];
              return updated;
            });
          }
        } catch (err) {
          console.error("Error parsing SSE live telemetry frame", err);
        }
      };

      eventSource.onerror = () => {
        setIsStreaming(false);
      };
    } catch (err) {
      console.warn("EventSource connection error", err);
      setIsStreaming(false);
    }

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [id]);

  if (isLoading) {
    return (
      <AppShell>
        <div className="rise-in space-y-6">
          <Skeleton className="h-6 w-36 bg-panel" />
          <Skeleton className="h-14 w-80 bg-panel" />
          <Skeleton className="h-12 w-full rounded-xl bg-panel" />
          <div className="grid gap-5 md:grid-cols-3">
            <Skeleton className="h-32 rounded-xl bg-panel" />
            <Skeleton className="h-32 rounded-xl bg-panel" />
            <Skeleton className="h-32 rounded-xl bg-panel" />
          </div>
          <div className="grid gap-5 xl:grid-cols-[1fr_340px]">
            <Skeleton className="h-[360px] rounded-xl bg-panel" />
            <Skeleton className="h-[360px] rounded-xl bg-panel" />
          </div>
        </div>
      </AppShell>
    );
  }

  if (isError || !initialMachine) {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/30 bg-destructive/10 p-10 text-center">
          <ShieldAlert className="h-10 w-10 text-critical" />
          <h2 className="mt-3 font-display text-lg font-semibold text-foreground">Machine not found or API unreachable</h2>
          <p className="mt-1 text-xs text-muted-foreground">Unable to fetch details for asset ID: {id}</p>
          <div className="mt-5 flex gap-3">
            <Link to="/machines">
              <Button variant="outline">Back to machines</Button>
            </Link>
            <Button onClick={() => refetch()} className="bg-amber text-primary-foreground hover:bg-amber/90">
              Retry
            </Button>
          </div>
        </div>
      </AppShell>
    );
  }

  const currentPower = livePower ?? initialMachine.power_kw;
  const currentTemp = liveTemp ?? initialMachine.temperature_c;
  const currentVibe = liveVibe ?? initialMachine.vibration_mms;
  const currentStatus = liveStatus ?? initialMachine.status;
  const currentScore = liveScore ?? initialMachine.score;

  return (
    <AppShell>
      <div className="rise-in">
        <Link to="/machines" className="mb-6 inline-flex items-center gap-2 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground">
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to machines
        </Link>

        <PageHeading
          eyebrow={`${initialMachine.line} · ${initialMachine.type}`}
          title={initialMachine.name}
          description="Live operating telemetry and maintenance logs for this asset."
          action={
            <div className="flex gap-2">
              <Button variant="outline" size="icon" className="border-border bg-panel" aria-label="Machine options">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
              <Button className="gap-2 bg-amber text-primary-foreground hover:bg-amber/90">
                <Wrench className="h-4 w-4" />
                Schedule service
              </Button>
            </div>
          }
        />

        {/* Live SSE Connection Bar */}
        <div className="mb-5 flex flex-wrap items-center gap-3 rounded-xl border border-border bg-panel px-5 py-3">
          <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
            <span className={`pulse-dot h-2 w-2 rounded-full ${isStreaming ? "bg-teal" : "bg-amber"}`} />
            {isStreaming ? (
              <span className="text-teal font-semibold flex items-center gap-1.5">
                <Radio className="h-3.5 w-3.5 animate-pulse" />
                Live SSE Telemetry Stream Active {lastStreamTime && `(${lastStreamTime})`}
              </span>
            ) : (
              "Connecting to live sensor telemetry..."
            )}
          </div>
          <div className="h-4 w-px bg-border" />
          <StatusBadge status={currentStatus} />
          <div className="h-4 w-px bg-border" />
          <div className="text-xs text-muted-foreground">
            Health: <span className={`font-semibold ${currentScore < 70 ? "text-critical" : currentScore < 80 ? "text-amber" : "text-teal"}`}>{currentScore}/100</span>
          </div>
          <div className="ml-auto flex items-center gap-2 text-xs text-muted-foreground">
            <CalendarDays className="h-3.5 w-3.5" /> Last service {initialMachine.maintenance}
          </div>
        </div>

        {/* Real-time Live Readouts */}
        <div className="grid gap-5 md:grid-cols-3">
          <Readout
            label={t("machines.temperature", "Temperature")}
            value={currentTemp}
            unit="°C"
            icon={Thermometer}
            tone={currentTemp > 690 ? "amber" : "teal"}
          />
          <Readout
            label={t("machines.vibration", "Vibration")}
            value={currentVibe}
            unit="mm/s"
            icon={Vibrate}
            tone={currentVibe > 4.5 ? "amber" : "teal"}
          />
          <Readout
            label={t("machines.power_draw", "Power draw")}
            value={currentPower}
            unit="kW"
            icon={Power}
            tone={currentPower > (initialMachine.baseline_power_kw || 100) * 1.15 ? "amber" : "teal"}
          />
        </div>
        
        {/* Health Factors */}
<section className="mt-5 glass-panel rounded-xl border border-border p-6">
  <div className="flex items-start justify-between">
    <div>
      <SectionLabel>Health factors</SectionLabel>
      <h2 className="mt-2 font-display text-lg font-semibold text-foreground">
        Why this machine has its current health score
      </h2>
      <p className="mt-1 text-xs text-muted-foreground">
  Score contribution from the latest machine assessment.
</p>
    </div>
    <div className="rounded-lg bg-panel-raised px-3 py-2 text-right">
      <div className="text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
        Score
      </div>
      <div className="mt-1 font-display text-lg font-semibold text-foreground">
        {currentScore}/100
      </div>
    </div>
  </div>

  <div className="mt-6 grid gap-4 md:grid-cols-3">
    {/* Power */}
    <div className="rounded-lg border border-border bg-panel-raised p-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-foreground">Power</span>
        <span className="text-[10px] font-semibold text-muted-foreground">
          {initialMachine.health_factors.power.status}
        </span>
      </div>

      <div className="mt-3 font-display text-xl font-semibold text-foreground">
        {initialMachine.health_factors.power.value} kW
      </div>

      <div className="mt-1 text-xs text-muted-foreground">
        Baseline: {initialMachine.health_factors.power.baseline} kW
      </div>

      <div className="mt-3 text-xs text-muted-foreground">
        Deviation:{" "}
        <span className="font-semibold text-foreground">
          +{initialMachine.health_factors.power.deviation_pct}%
        </span>
      </div>

      <div className="mt-2 text-xs text-muted-foreground">
        Penalty:{" "}
        <span className="font-semibold text-critical">
          -{initialMachine.health_factors.power.penalty}
        </span>
      </div>
    </div>

    {/* Vibration */}
    <div className="rounded-lg border border-border bg-panel-raised p-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-foreground">Vibration</span>
        <span className="text-[10px] font-semibold text-muted-foreground">
          {initialMachine.health_factors.vibration.status}
        </span>
      </div>

      <div className="mt-3 font-display text-xl font-semibold text-foreground">
        {initialMachine.health_factors.vibration.value} mm/s
      </div>

      <div className="mt-3 text-xs text-muted-foreground">
        Penalty:{" "}
        <span className="font-semibold text-critical">
          -{initialMachine.health_factors.vibration.penalty}
        </span>
      </div>
    </div>

    {/* Temperature */}
    <div className="rounded-lg border border-border bg-panel-raised p-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-foreground">Temperature</span>
        <span className="text-[10px] font-semibold text-muted-foreground">
          {initialMachine.health_factors.temperature.status}
        </span>
      </div>

      <div className="mt-3 font-display text-xl font-semibold text-foreground">
        {initialMachine.health_factors.temperature.value}°C
      </div>

      <div className="mt-1 text-xs text-muted-foreground">
        Expected: {initialMachine.health_factors.temperature.expected}°C
      </div>

      <div className="mt-3 text-xs text-muted-foreground">
        Deviation:{" "}
        <span className="font-semibold text-foreground">
          {initialMachine.health_factors.temperature.deviation}°C
        </span>
      </div>

      <div className="mt-2 text-xs text-muted-foreground">
        Penalty:{" "}
        <span className="font-semibold text-critical">
          {initialMachine.health_factors.temperature.penalty}
        </span>
      </div>
    </div>
  </div>
</section>

        {/* Live Telemetry Chart & Maintenance Log */}
        <div className="mt-5 grid gap-5 xl:grid-cols-[1fr_340px]">
          <section className="glass-panel rounded-xl border border-border p-6">
            <div className="flex items-start justify-between">
              <div>
                <SectionLabel>{t("machines.live_telemetry", "Live telemetry")}</SectionLabel>
                <h2 className="mt-2 font-display text-lg font-semibold text-foreground">
                  Power draw · Real-time trend
                </h2>
                <p className="mt-1 text-xs text-muted-foreground">
                  Streamed via FastAPI SSE every 3 seconds
                </p>
              </div>
              <div className="flex items-center gap-2 rounded-md bg-teal-soft px-2.5 py-1 text-[10px] font-bold text-teal">
                <span className="pulse-dot h-1.5 w-1.5 rounded-full bg-teal" />
                LIVE
              </div>
            </div>

            <div className="mt-8">
              <TrendChart values={liveTrend} compact unit="kW" />
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <div className="rounded-lg bg-panel-raised p-3">
                <div className="text-[10px] uppercase tracking-[0.14em] text-muted-foreground">Current</div>
                <div className="mt-1 font-display text-lg font-semibold text-foreground">
                  {currentPower} kW
                </div>
              </div>
              <div className="rounded-lg bg-panel-raised p-3">
                <div className="text-[10px] uppercase tracking-[0.14em] text-muted-foreground">24h average</div>
                <div className="mt-1 font-display text-lg font-semibold text-foreground">
                  {initialMachine.avg_24h_power_kw || 164} kW
                </div>
              </div>
              <div className="rounded-lg bg-panel-raised p-3">
                <div className="text-[10px] uppercase tracking-[0.14em] text-muted-foreground">Peak</div>
                <div className="mt-1 font-display text-lg font-semibold text-amber">
                  {initialMachine.peak_power_kw || 214} kW
                </div>
              </div>
            </div>
          </section>

          {/* Maintenance History */}
          <section className="glass-panel rounded-xl border border-border p-6">
            <div className="flex items-start justify-between">
              <div>
                <SectionLabel>Maintenance log</SectionLabel>
                <h2 className="mt-2 font-display text-lg font-semibold text-foreground">Service history</h2>
              </div>
              <Button variant="ghost" size="icon" aria-label="View maintenance options">
                <MoreHorizontal className="h-4 w-4 text-muted-foreground" />
              </Button>
            </div>
            <div className="mt-6 space-y-6">
              {(initialMachine.maintenance_history || []).map((item, idx) => (
                <TimelineItem
                  key={idx}
                  date={item.date}
                  title={item.title}
                  detail={item.detail}
                  active={item.active}
                />
              ))}
            </div>
            <Button variant="outline" className="mt-7 w-full border-border bg-panel text-xs">
              View full maintenance history
            </Button>
          </section>
        </div>
      </div>
    </AppShell>
  );
}

function TimelineItem({ date, title, detail, active }: { date: string; title: string; detail: string; active?: boolean }) {
  return (
    <div className="relative flex gap-3 pl-1">
      <div className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${active ? "bg-teal" : "bg-muted-foreground/50"}`} />
      <div className="absolute left-[4px] top-4 h-[calc(100%+16px)] w-px bg-border last:hidden" />
      <div>
        <div className="text-[10px] font-medium uppercase tracking-[0.12em] text-muted-foreground">{date}</div>
        <div className="mt-1 text-sm font-medium text-foreground">{title}</div>
        <div className="mt-1 text-xs text-muted-foreground">{detail}</div>
      </div>
    </div>
  );
}
