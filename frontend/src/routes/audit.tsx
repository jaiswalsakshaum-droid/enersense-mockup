import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowDownRight, ArrowUpRight, Award, Banknote, CheckCircle2, ChevronRight, ExternalLink, FileText, Landmark, Lightbulb, ShieldAlert, Sparkles, Zap } from "lucide-react";
import { AppShell, PageHeading, SectionLabel } from "@/components/enersense";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchRecommendations, fetchSchemes } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";

export const Route = createFileRoute("/audit")({
  head: () => ({
    meta: [
      { title: "Energy audit — EnerSense" },
      { name: "description", content: "Prioritized energy-saving recommendations with savings estimates and payback periods." },
      { property: "og:title", content: "Energy audit — EnerSense" },
      { property: "og:description", content: "Prioritized energy-saving recommendations with savings estimates and payback periods." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Audit,
});

function Audit() {
  const { t } = useTranslation();

  const { data: recommendations, isLoading: recLoading, isError: recError, refetch: refetchRecs } = useQuery({
    queryKey: ["recommendations"],
    queryFn: fetchRecommendations,
  });

  const { data: schemes, isLoading: schemesLoading } = useQuery({
    queryKey: ["schemes"],
    queryFn: () => fetchSchemes("foundry"),
  });

  const totalMonthlySaving = (recommendations || []).reduce((acc, r) => acc + (r.monthly_saving_inr || 0), 0);
  const totalAnnualKwh = (recommendations || []).reduce((acc, r) => acc + (r.annual_saving_kwh || 0), 0);

  return (
    <AppShell>
      <div className="rise-in">
        <PageHeading
          eyebrow={`Efficiency workspace · ${recommendations ? String(recommendations.length).padStart(2, "0") : "04"} opportunities`}
          title={t("audit.title", "Energy audit")}
          description={t("audit.desc", "Turn your plant’s energy signals into a ranked action plan with clear financial impact.")}
          action={
            <Link to="/simulate">
              <Button className="gap-2 bg-amber text-primary-foreground hover:bg-amber/90">
                <Sparkles className="h-4 w-4" />
                Launch What-If Simulator
              </Button>
            </Link>
          }
        />

        {/* Top Summary Banner */}
        <div className="grid gap-5 lg:grid-cols-[1fr_310px]">
          <div className="rounded-xl border border-amber/30 bg-amber-soft p-6 sm:p-7">
            <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-start">
              <div>
                <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-amber">
                  <Lightbulb className="h-3.5 w-3.5" /> Opportunity scan complete
                </div>
                <h2 className="mt-3 max-w-xl font-display text-2xl font-semibold tracking-tight text-foreground">
                  Your plant could save up to <span className="text-amber">₹{totalMonthlySaving > 0 ? totalMonthlySaving.toLocaleString("en-IN") : "60,080"} / month</span>
                </h2>
                <p className="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">
                  Four high-return interventions identified from your recent energy telemetry and machine baseline variances.
                </p>
              </div>
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-amber/25 bg-background/30 text-amber">
                <Zap className="h-6 w-6" />
              </div>
            </div>

            <div className="mt-7 grid gap-4 border-t border-amber/25 pt-5 sm:grid-cols-3">
              <div>
                <div className="text-[10px] uppercase tracking-[0.16em] text-muted-foreground">Annual potential</div>
                <div className="mt-1 font-display text-xl font-semibold text-foreground">
                  ₹{totalMonthlySaving > 0 ? ((totalMonthlySaving * 12) / 100000).toFixed(1) : "7.2"}L
                </div>
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-[0.16em] text-muted-foreground">Energy reduction</div>
                <div className="mt-1 font-display text-xl font-semibold text-foreground">
                  {totalAnnualKwh > 0 ? totalAnnualKwh.toLocaleString("en-IN") : "8,460"}{" "}
                  <span className="text-xs font-normal text-muted-foreground">kWh / yr</span>
                </div>
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-[0.16em] text-muted-foreground">Avg. payback</div>
                <div className="mt-1 font-display text-xl font-semibold text-foreground">
                  3.8 <span className="text-xs font-normal text-muted-foreground">months</span>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-panel p-6">
            <SectionLabel>Progress</SectionLabel>
            <div className="mt-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-soft text-teal">
                <CheckCircle2 className="h-5 w-5" />
              </div>
              <div>
                <div className="text-sm font-semibold text-foreground">1 of 4 actions underway</div>
                <div className="mt-1 text-xs text-muted-foreground">Keep the momentum going</div>
              </div>
            </div>
            <div className="mt-5 h-1.5 overflow-hidden rounded-full bg-secondary">
              <div className="h-full w-1/4 rounded-full bg-teal" />
            </div>
            <div className="mt-2 flex justify-between text-[10px] text-muted-foreground">
              <span>25% complete</span>
              <span>Last updated today</span>
            </div>
          </div>
        </div>

        {/* Ranked Recommendations List */}
        <section className="mt-8">
          <div className="mb-4 flex items-end justify-between">
            <div>
              <SectionLabel>Ranked opportunities</SectionLabel>
              <h2 className="mt-2 font-display text-xl font-semibold text-foreground">Recommended interventions</h2>
            </div>
            <div className="hidden items-center gap-1 text-[11px] text-muted-foreground sm:flex">
              <ArrowDownRight className="h-3.5 w-3.5 text-teal" /> Highest impact first
            </div>
          </div>

          {recLoading && (
            <div className="space-y-3">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-24 rounded-xl bg-panel" />
              ))}
            </div>
          )}

          {recError && (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/30 bg-destructive/10 p-10 text-center">
              <ShieldAlert className="h-10 w-10 text-critical" />
              <h3 className="mt-3 font-display text-lg font-semibold text-foreground">Failed to load recommendations</h3>
              <p className="mt-1 text-xs text-muted-foreground">Please ensure backend API is running.</p>
              <Button onClick={() => refetchRecs()} className="mt-4 bg-amber text-primary-foreground hover:bg-amber/90">
                Retry
              </Button>
            </div>
          )}

          {!recLoading && !recError && recommendations && (
            <div className="space-y-3">
              {recommendations.map((item, index) => (
                <div
                  key={item.rank}
                  className="group grid gap-5 rounded-xl border border-border bg-panel p-5 transition-colors hover:border-amber/40 sm:grid-cols-[42px_1fr_200px_120px_24px] sm:items-center"
                >
                  <div className="font-display text-lg font-semibold text-muted-foreground/60">{item.rank}</div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-sm font-semibold text-foreground">{item.title}</h3>
                      <span
                        className={`rounded-full px-2 py-0.5 text-[9px] font-semibold uppercase tracking-[0.1em] ${
                          index === 0 ? "bg-teal-soft text-teal" : "bg-secondary text-muted-foreground"
                        }`}
                      >
                        {item.tag}
                      </span>
                    </div>
                    <p className="mt-1.5 text-xs leading-5 text-muted-foreground">{item.description}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4 sm:block">
                    <div>
                      <div className="text-[10px] uppercase tracking-[0.14em] text-muted-foreground">Estimated saving</div>
                      <div className="mt-1 text-sm font-semibold text-teal">{item.saving}</div>
                      <div className="mt-0.5 text-[11px] text-muted-foreground">{item.rupees}</div>
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase tracking-[0.14em] text-muted-foreground">Payback</div>
                    <div className="mt-1 text-sm font-semibold text-foreground">{item.payback}</div>
                  </div>
                  <ChevronRight className="hidden h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-1 group-hover:text-amber sm:block" />
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Feature 5: PAT / BEE Scheme Matcher Section */}
        <section className="mt-12 border-t border-border pt-8">
          <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="flex items-center gap-2">
                <Landmark className="h-4 w-4 text-amber" />
                <SectionLabel>Government & BEE Policy Incentives</SectionLabel>
              </div>
              <h2 className="mt-1 font-display text-xl font-semibold text-foreground">
                {t("audit.schemes_title", "BEE & Government Energy Schemes")}
              </h2>
              <p className="text-xs text-muted-foreground">
                Subsidies, ESCerts trading, and concessional green capital schemes applicable for your foundry plant.
              </p>
            </div>
            <div className="rounded-full border border-teal/30 bg-teal-soft px-3 py-1 text-xs font-semibold text-teal">
              4 Schemes Available
            </div>
          </div>

          {schemesLoading && (
            <div className="grid gap-4 md:grid-cols-2">
              {[1, 2].map((i) => (
                <Skeleton key={i} className="h-44 rounded-xl bg-panel" />
              ))}
            </div>
          )}

          {!schemesLoading && schemes && (
            <div className="grid gap-4 md:grid-cols-2">
              {schemes.map((scheme) => (
                <div key={scheme.id} className="glass-panel flex flex-col justify-between rounded-xl border border-border p-5 hover:border-teal/50 transition-colors">
                  <div>
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <span className="text-[10px] font-semibold uppercase tracking-[0.15em] text-amber">
                          {scheme.organization}
                        </span>
                        <h3 className="mt-1 font-display text-base font-semibold text-foreground">
                          {scheme.title}
                        </h3>
                      </div>
                      <span className="rounded-full bg-secondary px-2.5 py-0.5 text-[10px] font-semibold text-foreground shrink-0">
                        {scheme.status}
                      </span>
                    </div>

                    <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
                      {scheme.incentive}
                    </p>

                    <div className="mt-4 rounded-lg bg-panel-raised p-3 text-xs">
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Max Incentive Benefit:</span>
                        <span className="font-semibold text-teal font-display">{scheme.max_benefit_inr}</span>
                      </div>
                      <div className="mt-1 text-[11px] text-muted-foreground">
                        Eligibility: {scheme.eligibility_summary}
                      </div>
                    </div>
                  </div>

                  <div className="mt-5 flex items-center justify-between border-t border-border pt-3 text-xs">
                    <span className="text-[11px] text-muted-foreground">
                      Deadline: <strong className="text-foreground">{scheme.deadline}</strong>
                    </span>
                    <a
                      href={scheme.action_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 font-semibold text-teal hover:underline"
                    >
                      Scheme details <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </AppShell>
  );
}
