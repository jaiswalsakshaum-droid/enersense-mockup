import { Link, useLocation } from "@tanstack/react-router";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  ArrowUpRight,
  Bell,
  Bolt,
  Calculator,
  CalendarDays,
  Check,
  ChevronRight,
  CircleHelp,
  Cpu,
  Factory,
  Gauge as GaugeIcon,
  Globe,
  Leaf,
  Lightbulb,
  Menu,
  MoreHorizontal,
  Settings2,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Thermometer,
  TrendingDown,
  TrendingUp,
  UserRound,
  Wrench,
  X,
  Zap,
} from "lucide-react";
import { useState, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { type Machine, type MachineStatus } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";

export const navItems = [
  { to: "/dashboard", key: "nav.dashboard", defaultLabel: "Dashboard", icon: GaugeIcon },
  { to: "/machines", key: "nav.machines", defaultLabel: "Machines", icon: Cpu },
  { to: "/alerts", key: "nav.alerts", defaultLabel: "Alerts", icon: Bell },
  { to: "/audit", key: "nav.audit", defaultLabel: "Energy audit", icon: Lightbulb },
  { to: "/simulate", key: "nav.simulate", defaultLabel: "Simulator", icon: Sparkles },
];

export function LogoMark() {
  return (
    <Link to="/dashboard" className="flex items-center gap-3">
      <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-amber/35 bg-amber-soft text-amber">
        <Bolt className="h-5 w-5" strokeWidth={2.5} />
      </div>
      <div>
        <div className="font-display text-[17px] font-semibold tracking-tight text-foreground">EnerSense</div>
        <div className="text-[10px] font-medium uppercase tracking-[0.18em] text-muted-foreground">Industrial intelligence</div>
      </div>
    </Link>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const location = useLocation();
  const { language, setLanguage, t } = useTranslation();
  const [open, setOpen] = useState(false);
  const currentPath = location.pathname;

  const currentItem = navItems.find((item) => currentPath === item.to || (item.to !== "/dashboard" && currentPath.startsWith(item.to)));
  const pageName = currentPath.includes("machines/")
    ? (language === "hi" ? "मशीन विवरण" : "Machine detail")
    : currentItem ? t(currentItem.key, currentItem.defaultLabel) : t("nav.dashboard", "Dashboard");

  return (
    <div className="page-shell min-h-screen">
      <div className="flex min-h-screen">
        <aside className={`fixed inset-y-0 left-0 z-40 flex w-[248px] -translate-x-full flex-col border-r border-border bg-panel px-4 py-5 transition-transform lg:static lg:translate-x-0 ${open ? "translate-x-0" : ""}`}>
          <div className="flex items-center justify-between px-2">
            <LogoMark />
            <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setOpen(false)} aria-label="Close menu"><X /></Button>
          </div>
          <div className="mt-10 px-3 text-[10px] font-semibold uppercase tracking-[0.2em] text-muted-foreground">Workspace</div>
          <nav className="mt-3 space-y-1" aria-label="Main navigation">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = currentPath === item.to || (item.to === "/machines" && currentPath.startsWith("/machines"));
              const label = t(item.key, item.defaultLabel);
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  onClick={() => setOpen(false)}
                  className={`group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground ${active ? "nav-active" : ""}`}
                >
                  <Icon className="h-[17px] w-[17px]" />
                  {label}
                  {item.to === "/alerts" && <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-critical/15 px-1.5 text-[10px] font-bold text-critical">2</span>}
                  {item.to === "/simulate" && <span className="ml-auto rounded bg-amber-soft px-1.5 py-0.5 text-[9px] font-semibold uppercase text-amber">New</span>}
                </Link>
              );
            })}
          </nav>
          <div className="mt-auto space-y-1">
            <div className="mb-5 rounded-xl border border-border bg-panel-raised p-3.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-muted-foreground">{t("plant.status", "Plant status")}</span>
                <span className="flex items-center gap-1.5 text-[11px] font-semibold text-teal"><span className="pulse-dot h-1.5 w-1.5 rounded-full bg-teal" /> {t("plant.live", "Live")}</span>
              </div>
              <div className="mt-3 font-display text-sm font-semibold text-foreground">{t("plant.name", "Rajkot Foundry Unit")}</div>
              <div className="mt-1 text-[11px] text-muted-foreground">Last synced 32 sec ago</div>
            </div>
            <Link to="/" className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"><Settings2 className="h-[17px] w-[17px]" />{t("nav.plant_settings", "Plant settings")}</Link>
            <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"><CircleHelp className="h-[17px] w-[17px]" />{t("nav.help_center", "Help center")}</button>
          </div>
        </aside>
        {open && <button className="fixed inset-0 z-30 bg-background/70 backdrop-blur-sm lg:hidden" onClick={() => setOpen(false)} aria-label="Close navigation" />}
        <main className="min-w-0 flex-1">
          <header className="sticky top-0 z-20 flex h-[72px] items-center justify-between border-b border-border bg-background/90 px-5 backdrop-blur-md sm:px-8 lg:px-10">
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setOpen(true)} aria-label="Open menu"><Menu /></Button>
              <div>
                <div className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">{t("plant.name", "Rajkot Foundry Unit")}</div>
                <div className="mt-0.5 font-display text-lg font-semibold tracking-tight text-foreground">{pageName}</div>
              </div>
            </div>
            <div className="flex items-center gap-2.5">
              {/* Language Switcher */}
              <button
                type="button"
                onClick={() => setLanguage(language === "en" ? "hi" : "en")}
                className="flex items-center gap-1.5 rounded-lg border border-border bg-panel px-2.5 py-1.5 text-xs font-semibold text-foreground transition-colors hover:border-amber/50 hover:bg-accent"
                title="Toggle Language"
              >
                <Globe className="h-3.5 w-3.5 text-amber" />
                <span>{language === "en" ? "हिन्दी" : "EN"}</span>
              </button>

              <div className="hidden items-center gap-2 rounded-full border border-border bg-panel px-3 py-1.5 text-xs text-muted-foreground sm:flex">
                <span className="h-1.5 w-1.5 rounded-full bg-teal" />
                {t("header.data_refreshed", "Data refreshed 32s ago")}
              </div>
              <Link to="/alerts">
                <Button variant="ghost" size="icon" aria-label="Notifications" className="relative">
                  <Bell className="h-[18px] w-[18px]" />
                  <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-critical" />
                </Button>
              </Link>
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-soft text-xs font-semibold text-teal">RS</div>
            </div>
          </header>
          <div className="mx-auto max-w-[1440px] p-5 sm:p-8 lg:p-10">{children}</div>
        </main>
      </div>
    </div>
  );
}

export function PageHeading({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
      <div>
        {eyebrow && <div className="mb-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-amber">{eyebrow}</div>}
        <h1 className="font-display text-3xl font-semibold tracking-tight text-foreground sm:text-[34px]">{title}</h1>
        {description && <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">{description}</p>}
      </div>
      {action}
    </div>
  );
}

export function StatusBadge({ status }: { status: MachineStatus | "Resolved" | "Info" }) {
  const className = status === "Normal" || status === "Resolved" ? "status-normal" : status === "Warning" ? "status-warning" : status === "Critical" ? "status-critical" : "status-info";
  return <Badge variant="outline" className={`gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold ${className}`}><span className="h-1.5 w-1.5 rounded-full bg-current" />{status}</Badge>;
}

export function StatCard({ label, value, unit, change, positive, icon: Icon, tone = "teal" }: { label: string; value: string; unit?: string; change: string; positive?: boolean; icon: typeof Zap; tone?: "teal" | "amber" | "critical" }) {
  const toneClass = tone === "amber" ? "bg-amber-soft text-amber" : tone === "critical" ? "bg-critical/15 text-critical" : "bg-teal-soft text-teal";
  return (
    <div className="glass-panel rounded-xl border border-border p-5">
      <div className="flex items-start justify-between">
        <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${toneClass}`}>
          <Icon className="h-[18px] w-[18px]" />
        </div>
        <MoreHorizontal className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="mt-5 text-xs font-medium text-muted-foreground">{label}</div>
      <div className="mt-1 flex items-baseline gap-1.5">
        <span className="font-display text-[27px] font-semibold tracking-tight text-foreground tabular-nums">{value}</span>
        {unit && <span className="text-xs text-muted-foreground">{unit}</span>}
      </div>
      <div className={`mt-3 flex items-center gap-1.5 text-[11px] font-medium ${positive ? "text-teal" : "text-critical"}`}>
        {positive ? <TrendingDown className="h-3.5 w-3.5" /> : <TrendingUp className="h-3.5 w-3.5" />}
        {change}
        <span className="text-muted-foreground">vs. last week</span>
      </div>
    </div>
  );
}

function pointsFor(values: number[], width = 700, height = 220) {
  if (!values || values.length === 0) return "0,0";
  const max = Math.max(...values);
  const min = Math.min(...values);
  return values.map((value, index) => `${(index / Math.max(values.length - 1, 1)) * width},${height - ((value - min) / (max - min || 1)) * (height - 24) - 12}`).join(" ");
}

export function TrendChart({ values, baselineValues, compact = false, unit = "kWh" }: { values: number[]; baselineValues?: number[]; compact?: boolean; unit?: string }) {
  const safeValues = values && values.length > 0 ? values : [50, 60, 55, 70, 65, 80, 75];
  const h = compact ? 140 : 220;
  const points = pointsFor(safeValues, 700, h);
  const last = points.split(" ").at(-1)?.split(",") ?? ["700", "20"];
  const area = `0,${h} ${points} 700,${h}`;

  const baselinePoints = baselineValues && baselineValues.length > 0 ? pointsFor(baselineValues, 700, h) : null;

  return (
    <div className={compact ? "h-[150px]" : "h-[270px]"}>
      <svg viewBox={`0 0 700 ${h}`} className="h-full w-full overflow-visible" preserveAspectRatio="none" role="img" aria-label={`Energy trend in ${unit}`}>
        <defs>
          <linearGradient id="chartFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="var(--color-teal)" stopOpacity=".22" />
            <stop offset="100%" stopColor="var(--color-teal)" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[0.25, 0.5, 0.75].map((ratio) => (
          <line key={ratio} x1="0" x2="700" y1={h * ratio} y2={h * ratio} stroke="var(--color-border)" strokeDasharray="3 6" />
        ))}
        {baselinePoints && (
          <polyline points={baselinePoints} fill="none" stroke="var(--color-border)" strokeWidth="2" strokeDasharray="4 4" />
        )}
        <polygon className="chart-area" points={area} />
        <polyline className="chart-line" points={points} strokeWidth="3" />
        <circle cx={last[0]} cy={last[1]} r="5" fill="var(--color-background)" stroke="var(--color-teal)" strokeWidth="3" />
      </svg>
      {!compact && (
        <div className="mt-3 flex justify-between text-[10px] text-muted-foreground">
          <span>00:00</span>
          <span>04:00</span>
          <span>08:00</span>
          <span>12:00</span>
          <span>16:00</span>
          <span>20:00</span>
          <span>23:59</span>
        </div>
      )}
    </div>
  );
}

export function Gauge({ value }: { value: number }) {
  const circumference = 2 * Math.PI * 82;
  const dash = circumference * (Math.min(100, Math.max(0, value)) / 100);
  return (
    <div className="relative h-[220px] w-[220px]">
      <svg viewBox="0 0 200 200" className="h-full w-full -rotate-90">
        <circle cx="100" cy="100" r="82" fill="none" className="gauge-track" strokeWidth="13" />
        <circle cx="100" cy="100" r="82" fill="none" className="gauge-value" strokeWidth="13" strokeLinecap="round" strokeDasharray={`${dash} ${circumference}`} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-[52px] font-semibold leading-none tracking-[-0.05em] text-foreground">{value}</span>
        <span className="mt-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">out of 100</span>
      </div>
    </div>
  );
}

export function MachineCard({ machine }: { machine: Machine }) {
  return (
    <Link to="/machines/$id" params={{ id: machine.id }} className="group glass-panel block rounded-xl border border-border p-5 transition-colors hover:border-amber/45">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary text-muted-foreground">
            <Cpu className="h-5 w-5" />
          </div>
          <div>
            <div className="font-display text-sm font-semibold text-foreground">{machine.name}</div>
            <div className="mt-1 text-[11px] text-muted-foreground">{machine.type}</div>
          </div>
        </div>
        <StatusBadge status={machine.status} />
      </div>
      <div className="mt-6 grid grid-cols-2 gap-4 border-t border-border pt-4">
        <div>
          <div className="text-[10px] uppercase tracking-[0.16em] text-muted-foreground">Health score</div>
          <div className="mt-1 flex items-baseline gap-1">
            <span className={`font-display text-xl font-semibold ${machine.score < 70 ? "text-critical" : machine.score < 80 ? "text-amber" : "text-teal"}`}>
              {machine.score}
            </span>
            <span className="text-[11px] text-muted-foreground">/100</span>
          </div>
        </div>
        <div>
          <div className="text-[10px] uppercase tracking-[0.16em] text-muted-foreground">Power draw</div>
          <div className="mt-1 font-display text-xl font-semibold text-foreground">{machine.reading}</div>
        </div>
      </div>
      <div className="mt-4 flex items-center justify-between text-[11px] text-muted-foreground">
        <span className="flex items-center gap-1.5">
          <CalendarDays className="h-3.5 w-3.5" /> Maintained {machine.maintenance}
        </span>
        <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1 group-hover:text-amber" />
      </div>
    </Link>
  );
}

export function Readout({ icon: Icon, label, value, unit, tone = "teal" }: { icon: typeof Thermometer; label: string; value: string | number; unit: string; tone?: "teal" | "amber" }) {
  return (
    <div className="rounded-xl border border-border bg-panel-raised p-4">
      <div className={`flex h-8 w-8 items-center justify-center rounded-md ${tone === "amber" ? "bg-amber-soft text-amber" : "bg-teal-soft text-teal"}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="mt-4 text-xs text-muted-foreground">{label}</div>
      <div className="mt-1 font-display text-2xl font-semibold text-foreground">
        {value}
        <span className="ml-1 text-xs font-normal text-muted-foreground">{unit}</span>
      </div>
      <div className="mt-2 flex items-center gap-1.5 text-[10px] font-medium text-teal">
        <span className="pulse-dot h-1.5 w-1.5 rounded-full bg-teal" />
        Live reading
      </div>
    </div>
  );
}

export function MiniSparkline({ values, tone = "teal" }: { values: number[]; tone?: "teal" | "amber" }) {
  const points = pointsFor(values && values.length > 0 ? values : [10, 20, 15, 25], 160, 55);
  return (
    <svg viewBox="0 0 160 55" className="h-12 w-full" preserveAspectRatio="none">
      <polyline points={points} fill="none" stroke={tone === "amber" ? "var(--color-amber)" : "var(--color-teal)"} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function SectionLabel({ children }: { children: ReactNode }) {
  return <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-muted-foreground">{children}</div>;
}

export {
  Activity,
  AlertTriangle,
  ArrowLeft,
  ArrowUpRight,
  Calculator,
  CalendarDays,
  Check,
  Factory,
  Globe,
  Leaf,
  Menu,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Thermometer,
  TrendingDown,
  TrendingUp,
  UserRound,
  Wrench,
  Zap,
};
