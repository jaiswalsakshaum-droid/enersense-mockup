import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { ArrowRight, Check, Factory, LockKeyhole, ShieldCheck, Sparkles, Zap } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LogoMark } from "@/components/enersense";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "EnerSense — Set up your plant" },
      {
        name: "description",
        content:
          "Start monitoring energy and machine health for your manufacturing plant with EnerSense.",
      },
      {
        property: "og:title",
        content: "EnerSense — Set up your plant",
      },
      {
        property: "og:description",
        content:
          "Start monitoring energy and machine health for your manufacturing plant with EnerSense.",
      },
      {
        property: "og:type",
        content: "website",
      },
      {
        name: "twitter:card",
        content: "summary_large_image",
      },
    ],
  }),
  component: Onboarding,
});

function Onboarding() {
  const navigate = useNavigate();

  const [plant, setPlant] = useState("Rajkot Foundry Unit");
  const [industry, setIndustry] = useState("foundry");

  return (
    <div className="industrial-grid relative min-h-screen overflow-hidden bg-background">
      {/* Background glow */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_75%_15%,color-mix(in_oklab,var(--color-teal)_13%,transparent),transparent_30rem)]" />

      <div className="relative mx-auto flex min-h-screen max-w-[1380px] flex-col px-6 py-7 sm:px-10 lg:px-14">
        {/* Header */}
        <header className="flex items-center justify-between">
          <LogoMark />

          <div className="hidden max-w-xs items-center gap-2 text-right text-xs text-muted-foreground sm:flex">
            <LockKeyhole className="h-3.5 w-3.5 shrink-0 text-teal" />
            <span>Your data stays on your plant workspace</span>
          </div>
        </header>

        {/* Main */}
        <div className="grid flex-1 items-center gap-10 py-12 lg:grid-cols-[minmax(0,1fr)_460px] lg:gap-14 lg:py-16">
          {/* Left side */}
          <div className="rise-in max-w-2xl">
            {/* Eyebrow */}
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-teal/30 bg-teal-soft px-3 py-1.5 text-[11px] font-semibold text-teal">
              <Sparkles className="h-3.5 w-3.5" />
              ENERGY INTELLIGENCE FOR REAL PLANTS
            </div>

            {/* Main heading */}
            <h1 className="max-w-xl font-display text-5xl font-semibold leading-[1.03] tracking-[-0.05em] text-foreground sm:text-6xl">
              Make every unit of energy <span className="text-amber">count.</span>
            </h1>

            {/* Description */}
            <p className="mt-6 max-w-lg text-base leading-7 text-muted-foreground">
              EnerSense brings your plant’s energy, equipment health, and next best actions into one
              clear operating view.
            </p>

            {/* Feature cards */}
            <div className="mt-10 grid max-w-lg grid-cols-1 gap-4 border-t border-border pt-6 sm:grid-cols-3">
              <div className="rounded-lg border border-border/60 bg-card/40 p-4 transition-colors hover:border-amber/30">
                <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-md bg-amber-soft text-amber">
                  <Zap className="h-4 w-4" />
                </div>

                <div className="font-display text-sm font-semibold text-foreground">Energy</div>

                <div className="mt-1 text-[11px] leading-4 text-muted-foreground">
                  Track consumption and efficiency
                </div>
              </div>

              <div className="rounded-lg border border-border/60 bg-card/40 p-4 transition-colors hover:border-teal/30">
                <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-md bg-teal-soft text-teal">
                  <ShieldCheck className="h-4 w-4" />
                </div>

                <div className="font-display text-sm font-semibold text-foreground">
                  Machine health
                </div>

                <div className="mt-1 text-[11px] leading-4 text-muted-foreground">
                  Monitor equipment condition
                </div>
              </div>

              <div className="rounded-lg border border-border/60 bg-card/40 p-4 transition-colors hover:border-amber/30">
                <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-md bg-amber-soft text-amber">
                  <Sparkles className="h-4 w-4" />
                </div>

                <div className="font-display text-sm font-semibold text-foreground">
                  AI insights
                </div>

                <div className="mt-1 text-[11px] leading-4 text-muted-foreground">
                  Turn plant data into actions
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="mt-7 grid max-w-lg grid-cols-3 gap-5">
              <div>
                <div className="font-display text-2xl font-semibold text-foreground">
                  18<span className="text-amber">%</span>
                </div>

                <div className="mt-1 text-[11px] leading-4 text-muted-foreground">
                  typical energy
                  <br />
                  savings found
                </div>
              </div>

              <div>
                <div className="font-display text-2xl font-semibold text-foreground">
                  24<span className="text-amber">/7</span>
                </div>

                <div className="mt-1 text-[11px] leading-4 text-muted-foreground">
                  machine health
                  <br />
                  visibility
                </div>
              </div>

              <div>
                <div className="font-display text-2xl font-semibold text-foreground">₹0</div>

                <div className="mt-1 text-[11px] leading-4 text-muted-foreground">
                  hardware to
                  <br />
                  get started
                </div>
              </div>
            </div>
          </div>

          {/* Right side — Plant setup */}
          <div className="rise-in-delay-1 glass-panel w-full rounded-2xl border border-border p-6 shadow-2xl sm:p-8">
            {/* Card heading */}
            <div className="mb-8 flex items-start justify-between">
              <div>
                <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-amber">
                  01 / PLANT PROFILE
                </div>

                <h2 className="mt-3 font-display text-2xl font-semibold tracking-tight text-foreground">
                  Set up your workspace
                </h2>

                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  Tell us a little about the plant you want to monitor.
                </p>
              </div>

              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-soft text-amber">
                <Factory className="h-[18px] w-[18px]" />
              </div>
            </div>

            {/* Form */}
            <div className="space-y-5">
              {/* Plant name */}
              <div>
                <label
                  htmlFor="plant-name"
                  className="mb-2 block text-xs font-medium text-foreground"
                >
                  Plant name
                </label>

                <input
                  id="plant-name"
                  value={plant}
                  onChange={(event) => setPlant(event.target.value)}
                  className="h-11 w-full rounded-lg border border-input bg-background px-3.5 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground focus:border-amber focus:ring-1 focus:ring-amber"
                  placeholder="e.g. Rajkot Foundry Unit"
                />
              </div>

              {/* Industry */}
              <div>
                <label className="mb-2 block text-xs font-medium text-foreground">
                  Industry type
                </label>

                <Select value={industry} onValueChange={setIndustry}>
                  <SelectTrigger className="h-11 border-input bg-background">
                    <SelectValue placeholder="Select industry" />
                  </SelectTrigger>

                  <SelectContent>
                    <SelectItem value="foundry">Foundry</SelectItem>
                    <SelectItem value="textile">Textile</SelectItem>
                    <SelectItem value="ceramics">Ceramics</SelectItem>
                    <SelectItem value="chemicals">Chemicals</SelectItem>
                    <SelectItem value="food-processing">Food processing</SelectItem>
                    <SelectItem value="brick-kiln">Brick kiln</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Enter workspace */}
              <Button
                className="h-11 w-full bg-amber text-primary-foreground hover:bg-amber/90"
                onClick={() => navigate({ to: "/dashboard" })}
              >
                Enter plant workspace
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>

            {/* Trust indicators */}
            <div className="mt-6 flex items-center justify-center gap-5 border-t border-border pt-5 text-[10px] text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="h-3.5 w-3.5 text-teal" />
                Secure workspace
              </span>

              <span className="flex items-center gap-1.5">
                <Check className="h-3.5 w-3.5 text-teal" />
                No hardware required
              </span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="flex items-center justify-between border-t border-border py-5 text-[11px] text-muted-foreground">
          <span>© 2026 EnerSense Systems</span>

          <Link to="/dashboard" className="transition-colors hover:text-foreground">
            View demo workspace
            <Zap className="ml-1 inline h-3 w-3 text-amber" />
          </Link>
        </footer>
      </div>
    </div>
  );
}