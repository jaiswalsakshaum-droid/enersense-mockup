import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Bell, CheckCircle2, Clock3, Info, MessageSquare, MoreHorizontal, Send, ShieldAlert, SlidersHorizontal, Smartphone } from "lucide-react";
import { useState } from "react";
import { AppShell, PageHeading, SectionLabel, StatusBadge } from "@/components/enersense";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchAlerts } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";

export const Route = createFileRoute("/alerts")({
  head: () => ({
    meta: [
      { title: "Alerts — EnerSense" },
      { name: "description", content: "Review machine alerts, severity, timestamps, and recommended next actions." },
      { property: "og:title", content: "Alerts — EnerSense" },
      { property: "og:description", content: "Review machine alerts, severity, timestamps, and recommended next actions." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Alerts,
});

function Alerts() {
  const { t } = useTranslation();
  const [whatsappEnabled, setWhatsappEnabled] = useState(true);

  const { data: alerts, isLoading, isError, refetch } = useQuery({
    queryKey: ["alerts"],
    queryFn: fetchAlerts,
  });

  const criticalCount = (alerts || []).filter((a) => a.severity === "Critical").length;
  const warningCount = (alerts || []).filter((a) => a.severity === "Warning").length;
  const resolvedCount = (alerts || []).filter((a) => a.severity === "Resolved").length;

  const latestCriticalAlert = (alerts || []).find((a) => a.severity === "Critical") || alerts?.[0];

  return (
    <AppShell>
      <div className="rise-in">
        <PageHeading
          eyebrow={`Operations center · ${String(criticalCount + warningCount).padStart(2, "0")} active`}
          title={t("alerts.title", "Alerts")}
          description={t("alerts.desc", "Stay ahead of issues with machine events ordered by urgency.")}
          action={
            <Button variant="outline" className="gap-2 border-border bg-panel">
              <SlidersHorizontal className="h-4 w-4" />
              Filter alerts
            </Button>
          }
        />

        {/* Summary Stat Cards */}
        <div className="grid gap-4 sm:grid-cols-3">
          <AlertSummary icon={AlertTriangle} label="Critical" value={String(criticalCount).padStart(2, "0")} tone="critical" />
          <AlertSummary icon={Clock3} label="Warning" value={String(warningCount).padStart(2, "0")} tone="amber" />
          <AlertSummary icon={CheckCircle2} label="Resolved today" value={String(resolvedCount).padStart(2, "0")} tone="teal" />
        </div>

        {/* Feature 2: WhatsApp Alert Integration & Live Preview Card */}
        <div className="mt-7 rounded-xl border border-emerald-500/30 bg-panel-raised p-5">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-400">
                <MessageSquare className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-display text-sm font-semibold text-foreground">
                  WhatsApp Instant Dispatch
                </h3>
                <p className="text-xs text-muted-foreground">
                  Instantly forward Critical anomalies to plant supervisor mobile numbers (+91-98765-XXXXX)
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <label htmlFor="wa-toggle" className="text-xs font-medium text-foreground cursor-pointer">
                {t("alerts.whatsapp_toggle", "Send critical alerts to WhatsApp")}
              </label>
              <Switch
                id="wa-toggle"
                checked={whatsappEnabled}
                onCheckedChange={setWhatsappEnabled}
              />
            </div>
          </div>

          {whatsappEnabled && latestCriticalAlert && (
            <div className="mt-4 rounded-lg border border-border/80 bg-background/60 p-4">
              <div className="flex items-center justify-between text-[11px] text-muted-foreground border-b border-border/50 pb-2 mb-3">
                <span className="flex items-center gap-1.5 font-medium text-emerald-400">
                  <Smartphone className="h-3.5 w-3.5" /> WhatsApp Message Template Preview
                </span>
                <span>Delivered via EnerSense Bot</span>
              </div>

              {/* Mock WhatsApp bubble */}
              <div className="max-w-md rounded-xl rounded-tl-none border border-emerald-500/20 bg-[#0f241a] p-3.5 text-xs text-foreground shadow-lg">
                <div className="font-bold text-red-400 flex items-center gap-1.5">
                  🚨 CRITICAL ALERT — EnerSense System
                </div>
                <div className="mt-1 font-semibold text-foreground">
                  Asset: {latestCriticalAlert.machine}
                </div>
                <div className="mt-1 text-muted-foreground leading-relaxed">
                  {latestCriticalAlert.detail}
                </div>
                {latestCriticalAlert.recommended_action && (
                  <div className="mt-2 rounded bg-black/30 p-2 text-[11px] text-amber">
                    👉 Action: {latestCriticalAlert.recommended_action}
                  </div>
                )}
                <div className="mt-2 flex items-center justify-between text-[10px] text-muted-foreground">
                  <span>Plant: Rajkot Foundry</span>
                  <span>10:18 AM ✓✓</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* All Events Table */}
        <section className="mt-7">
          <div className="mb-4 flex items-center justify-between">
            <SectionLabel>All events</SectionLabel>
            <span className="text-[11px] text-muted-foreground">
              Showing {alerts?.length || 0} alerts
            </span>
          </div>

          {isLoading && (
            <div className="space-y-3">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-20 rounded-xl bg-panel" />
              ))}
            </div>
          )}

          {isError && (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/30 bg-destructive/10 p-10 text-center">
              <ShieldAlert className="h-10 w-10 text-critical" />
              <h3 className="mt-3 font-display text-lg font-semibold text-foreground">Could not load alerts</h3>
              <p className="mt-1 text-xs text-muted-foreground">Please check backend API connection.</p>
              <Button onClick={() => refetch()} className="mt-4 bg-amber text-primary-foreground hover:bg-amber/90">
                Retry
              </Button>
            </div>
          )}

          {!isLoading && !isError && alerts && (
            <div className="overflow-hidden rounded-xl border border-border bg-panel">
              <div className="hidden grid-cols-[1.5fr_1fr_120px_100px_32px] gap-4 border-b border-border px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground md:grid">
                <span>Alert</span>
                <span>Machine</span>
                <span>Severity</span>
                <span>Time</span>
                <span />
              </div>
              {alerts.map((alert, index) => (
                <div
                  key={alert.id}
                  className={`grid gap-3 px-5 py-5 md:grid-cols-[1.5fr_1fr_120px_100px_32px] md:items-center ${
                    index < alerts.length - 1 ? "border-b border-border" : ""
                  }`}
                >
                  <div className="flex gap-3">
                    <div
                      className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                        alert.severity === "Critical"
                          ? "bg-critical/15 text-critical"
                          : alert.severity === "Warning"
                          ? "bg-amber-soft text-amber"
                          : alert.severity === "Resolved"
                          ? "bg-teal-soft text-teal"
                          : "bg-teal-soft text-info"
                      }`}
                    >
                      {alert.severity === "Critical" ? (
                        <AlertTriangle className="h-4 w-4" />
                      ) : alert.severity === "Resolved" ? (
                        <CheckCircle2 className="h-4 w-4" />
                      ) : alert.severity === "Info" ? (
                        <Info className="h-4 w-4" />
                      ) : (
                        <Bell className="h-4 w-4" />
                      )}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-foreground">{alert.title}</div>
                      <div className="mt-1 max-w-lg text-xs leading-5 text-muted-foreground">{alert.detail}</div>
                    </div>
                  </div>
                  <div className="pl-11 text-xs text-muted-foreground md:pl-0">{alert.machine}</div>
                  <div className="pl-11 md:pl-0">
                    <StatusBadge status={alert.severity} />
                  </div>
                  <div className="pl-11 text-xs text-muted-foreground md:pl-0">{alert.time}</div>
                  <Button variant="ghost" size="icon" className="hidden text-muted-foreground md:inline-flex" aria-label="Alert options">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </AppShell>
  );
}

function AlertSummary({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: typeof AlertTriangle;
  label: string;
  value: string;
  tone: "critical" | "amber" | "teal";
}) {
  const toneClass =
    tone === "critical"
      ? "bg-critical/15 text-critical"
      : tone === "amber"
      ? "bg-amber-soft text-amber"
      : "bg-teal-soft text-teal";

  return (
    <div className="flex items-center gap-4 rounded-xl border border-border bg-panel p-4">
      <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${toneClass}`}>
        <Icon className="h-[18px] w-[18px]" />
      </div>
      <div>
        <div className="text-xs text-muted-foreground">{label}</div>
        <div className="mt-0.5 font-display text-xl font-semibold text-foreground">{value}</div>
      </div>
    </div>
  );
}
