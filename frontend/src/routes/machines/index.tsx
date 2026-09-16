import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Cpu, Filter, Plus, Search, ShieldAlert, SlidersHorizontal } from "lucide-react";
import { useState } from "react";
import { AppShell, MachineCard, PageHeading, SectionLabel } from "@/components/enersense";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchMachines } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";

export const Route = createFileRoute("/machines/")({
  head: () => ({
    meta: [
      { title: "Machines — EnerSense" },
      { name: "description", content: "Monitor health scores, status, power draw, and maintenance dates for every machine." },
      { property: "og:title", content: "Machines — EnerSense" },
      { property: "og:description", content: "Monitor health scores, status, power draw, and maintenance dates for every machine." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Machines,
});

function Machines() {
  const { t } = useTranslation();
  const [search, setSearch] = useState("");
  const [tab, setTab] = useState<"all" | "attention" | "healthy">("all");

  const { data: machines, isLoading, isError, refetch } = useQuery({
    queryKey: ["machines"],
    queryFn: fetchMachines,
  });

  const filteredMachines = (machines || []).filter((machine) => {
    const matchesSearch =
      machine.name.toLowerCase().includes(search.toLowerCase()) ||
      machine.type.toLowerCase().includes(search.toLowerCase()) ||
      machine.line.toLowerCase().includes(search.toLowerCase());

    if (!matchesSearch) return false;

    if (tab === "attention") {
      return machine.status === "Critical" || machine.status === "Warning" || machine.score < 80;
    }
    if (tab === "healthy") {
      return machine.status === "Normal" && machine.score >= 80;
    }
    return true;
  });

  const attentionCount = (machines || []).filter((m) => m.status === "Critical" || m.status === "Warning").length;
  const healthyCount = (machines || []).filter((m) => m.status === "Normal").length;

  return (
    <AppShell>
      <div className="rise-in">
        <PageHeading
          eyebrow={`Equipment registry · ${machines?.length ? String(machines.length).padStart(2, "0") : "05"} monitored assets`}
          title={t("machines.title", "Machines")}
          description={t("machines.desc", "A clear view of health, operating status, and service readiness across the plant.")}
          action={
            <Button className="gap-2 bg-amber text-primary-foreground hover:bg-amber/90">
              <Plus className="h-4 w-4" />
              Add machine
            </Button>
          }
        />

        {/* Search & Filter Bar */}
        <div className="mb-6 flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t("machines.search", "Search machines")}
              className="h-10 w-full rounded-lg border border-input bg-panel pl-10 pr-3 text-sm text-foreground outline-none transition-colors focus:border-amber"
            />
          </div>
          <Button variant="outline" className="gap-2 border-border bg-panel">
            <Filter className="h-4 w-4" />
            All lines
          </Button>
          <Button variant="outline" size="icon" className="hidden border-border bg-panel sm:inline-flex" aria-label="More filters">
            <SlidersHorizontal className="h-4 w-4" />
          </Button>
        </div>

        {/* Status Filter Tabs */}
        <div className="mb-5 flex items-center gap-6 border-b border-border pb-3 text-xs">
          <button
            onClick={() => setTab("all")}
            className={`pb-3 font-semibold transition-colors ${tab === "all" ? "border-b-2 border-amber text-foreground" : "text-muted-foreground hover:text-foreground"}`}
          >
            {t("machines.all", "All machines")}{" "}
            <span className="ml-1 text-muted-foreground">{machines ? String(machines.length).padStart(2, "0") : "05"}</span>
          </button>
          <button
            onClick={() => setTab("attention")}
            className={`pb-3 font-semibold transition-colors ${tab === "attention" ? "border-b-2 border-amber text-foreground" : "text-muted-foreground hover:text-foreground"}`}
          >
            {t("machines.attention", "Needs attention")}{" "}
            <span className="ml-1 text-amber">{String(attentionCount).padStart(2, "0")}</span>
          </button>
          <button
            onClick={() => setTab("healthy")}
            className={`pb-3 font-semibold transition-colors ${tab === "healthy" ? "border-b-2 border-amber text-foreground" : "text-muted-foreground hover:text-foreground"}`}
          >
            {t("machines.healthy", "Healthy")}{" "}
            <span className="ml-1 text-teal">{String(healthyCount).padStart(2, "0")}</span>
          </button>
        </div>

        <div className="mb-5 flex items-center justify-between">
          <SectionLabel>All equipment</SectionLabel>
          <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
            <Cpu className="h-3.5 w-3.5" /> Sorted by health score
          </div>
        </div>

        {/* Loading state */}
        {isLoading && (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Skeleton key={i} className="h-44 rounded-xl bg-panel" />
            ))}
          </div>
        )}

        {/* Error state */}
        {isError && (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/30 bg-destructive/10 p-10 text-center">
            <ShieldAlert className="h-10 w-10 text-critical" />
            <h3 className="mt-3 font-display text-lg font-semibold text-foreground">Could not load machines</h3>
            <p className="mt-1 text-xs text-muted-foreground">Check your connection to FastAPI backend.</p>
            <Button onClick={() => refetch()} className="mt-4 bg-amber text-primary-foreground hover:bg-amber/90">
              Retry
            </Button>
          </div>
        )}

        {/* Machine Cards */}
        {!isLoading && !isError && (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {filteredMachines.map((machine) => (
              <MachineCard key={machine.id} machine={machine} />
            ))}
            {filteredMachines.length === 0 && (
              <div className="col-span-full py-12 text-center text-sm text-muted-foreground">
                No machines found matching "{search}".
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
