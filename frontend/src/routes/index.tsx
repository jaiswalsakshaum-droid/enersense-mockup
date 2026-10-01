import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  Factory,
  Gauge,
  Leaf,
  Lightbulb,
  LineChart,
  MonitorCog,
  Settings2,
  ShieldCheck,
  Sparkles,
  Target,
  TriangleAlert,
  Workflow,
  Zap,
} from "lucide-react";

import { LogoMark } from "@/components/enersense";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      {
        title: "EnerSense — Industrial Energy & Production Intelligence",
      },
      {
        name: "description",
        content:
          "EnerSense helps manufacturing teams understand energy consumption, monitor machine health, identify operational problems, and optimize production decisions.",
      },
    ],
  }),
  component: HomePage,
});

function HomePage() {
  return (
    <div className="min-h-screen overflow-x-hidden bg-background text-foreground">
      {/* =========================================================
          BACKGROUND
      ========================================================== */}

      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute left-[-15%] top-[-10%] h-[500px] w-[500px] rounded-full bg-teal/10 blur-[120px]" />
        <div className="absolute right-[-10%] top-[15%] h-[600px] w-[600px] rounded-full bg-amber/10 blur-[140px]" />
        <div className="absolute bottom-[-10%] left-[30%] h-[500px] w-[500px] rounded-full bg-emerald-500/5 blur-[130px]" />
      </div>

      {/* =========================================================
          HEADER
      ========================================================== */}

      <header className="sticky top-0 z-50 border-b border-border/70 bg-background/90 backdrop-blur-xl">
        <div className="mx-auto flex h-20 max-w-[1500px] items-center justify-between px-6 sm:px-10 lg:px-14">
          <LogoMark />

          <nav className="hidden items-center gap-8 lg:flex">
            <a
              href="#problem"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Problem
            </a>

            <a
              href="#solution"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Solution
            </a>

            <a
              href="#features"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Features
            </a>

            <a
              href="#workflow"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              How it works
            </a>

            <a
              href="#processtwin"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              ProcessTwin AI
            </a>
          </nav>

          <Link to="/dashboard">
            <Button className="h-10 bg-amber px-5 text-primary-foreground hover:bg-amber/90">
              Open Dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </header>

      {/* =========================================================
          HERO
      ========================================================== */}

      <main>
        <section className="industrial-grid relative border-b border-border">
          <div className="mx-auto max-w-[1500px] px-6 pb-24 pt-20 sm:px-10 lg:px-14 lg:pb-32 lg:pt-28">
            <div className="grid items-center gap-16 lg:grid-cols-[1.05fr_0.95fr] lg:gap-20">
              {/* LEFT */}

              <div className="rise-in">
                <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-teal/30 bg-teal-soft px-4 py-2 text-xs font-semibold tracking-wide text-teal">
                  <Sparkles className="h-4 w-4" />
                  INDUSTRIAL ENERGY INTELLIGENCE
                </div>

                <h1 className="max-w-4xl font-display text-5xl font-semibold leading-[1.02] tracking-[-0.055em] text-foreground sm:text-6xl lg:text-7xl xl:text-[82px]">
                  Turn factory data into{" "}
                  <span className="text-amber">better decisions.</span>
                </h1>

                <p className="mt-8 max-w-2xl text-lg leading-8 text-muted-foreground sm:text-xl">
                  EnerSense is an industrial intelligence platform designed to
                  help manufacturing teams understand where energy is being
                  consumed, identify machine-level problems, and make more
                  informed production decisions.
                </p>

                <div className="mt-10 flex flex-col gap-4 sm:flex-row">
                  <Link to="/dashboard">
                    <Button className="h-13 w-full bg-amber px-7 text-base text-primary-foreground hover:bg-amber/90 sm:w-auto">
                      Explore the Dashboard
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                  </Link>

                  <a href="#solution">
                    <Button
                      variant="outline"
                      className="h-13 w-full border-border bg-background/60 px-7 text-base sm:w-auto"
                    >
                      Understand the Platform
                    </Button>
                  </a>
                </div>

                <div className="mt-12 flex flex-wrap gap-x-8 gap-y-4 border-t border-border pt-7">
                  <HeroPoint
                    icon={Zap}
                    title="Energy"
                    description="Understand consumption"
                  />

                  <HeroPoint
                    icon={MonitorCog}
                    title="Machines"
                    description="Monitor equipment health"
                  />

                  <HeroPoint
                    icon={BrainCircuit}
                    title="Decisions"
                    description="Optimize production"
                  />
                </div>
              </div>

              {/* RIGHT — CONCEPTUAL PLATFORM VISUAL, NO MOCK DATA */}

              <div className="rise-in-delay-1 relative">
                <div className="absolute -inset-6 rounded-[2rem] bg-teal/5 blur-3xl" />

                <div className="relative rounded-2xl border border-border bg-panel/90 p-5 shadow-2xl sm:p-7">
                  <div className="flex items-center justify-between border-b border-border pb-5">
                    <div>
                      <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-teal">
                        ENERSENSE PLATFORM
                      </div>

                      <h2 className="mt-2 font-display text-xl font-semibold">
                        Industrial intelligence layer
                      </h2>
                    </div>

                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-soft text-amber">
                      <Factory className="h-5 w-5" />
                    </div>
                  </div>

                  <div className="mt-6 space-y-3">
                    <PlatformFlowItem
                      icon={Zap}
                      title="Energy Monitoring"
                      description="Understand where energy is being consumed."
                    />

                    <PlatformFlowItem
                      icon={MonitorCog}
                      title="Machine Health"
                      description="Combine machine signals to identify abnormal behavior."
                    />

                    <PlatformFlowItem
                      icon={TriangleAlert}
                      title="Operational Insights"
                      description="Surface conditions that may require attention."
                    />

                    <PlatformFlowItem
                      icon={BrainCircuit}
                      title="ProcessTwin AI"
                      description="Evaluate production scenarios before making decisions."
                      highlighted
                    />
                  </div>

                  <div className="mt-6 rounded-xl border border-amber/20 bg-amber/5 p-5">
                    <div className="flex gap-3">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-soft text-amber">
                        <Lightbulb className="h-5 w-5" />
                      </div>

                      <div>
                        <div className="font-semibold">
                          From observation to action
                        </div>

                        <p className="mt-1 text-sm leading-6 text-muted-foreground">
                          EnerSense connects energy, equipment and production
                          information so teams can move from raw operational
                          data toward actionable decisions.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* =========================================================
            PROBLEM
        ========================================================== */}

        <section
          id="problem"
          className="border-b border-border bg-background"
        >
          <div className="mx-auto max-w-[1500px] px-6 py-24 sm:px-10 lg:px-14 lg:py-32">
            <div className="max-w-3xl">
              <SectionEyebrow>THE PROBLEM</SectionEyebrow>

              <h2 className="mt-4 font-display text-4xl font-semibold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
                Manufacturing problems are often hidden inside the data.
              </h2>

              <p className="mt-7 text-lg leading-8 text-muted-foreground">
                A factory can collect large amounts of operational information
                without turning that information into useful decisions. Energy
                consumption, machine behavior and production constraints are
                often looked at separately.
              </p>
            </div>

            <div className="mt-16 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
              <ProblemCard
                number="01"
                icon={Zap}
                title="Energy is difficult to understand"
                description="Knowing total electricity consumption does not always explain which machines, processes or operating conditions are responsible for it."
              />

              <ProblemCard
                number="02"
                icon={TriangleAlert}
                title="Machine problems can be gradual"
                description="Changes in power, temperature or vibration may develop over time and become difficult to notice when individual signals are viewed in isolation."
              />

              <ProblemCard
                number="03"
                icon={Factory}
                title="Production decisions have trade-offs"
                description="A production plan may need to balance capacity, time, quality, energy use, cost and environmental constraints at the same time."
              />

              <ProblemCard
                number="04"
                icon={LineChart}
                title="Data does not automatically create action"
                description="The real challenge is connecting operational information to decisions that a manufacturing team can actually act upon."
              />
            </div>
          </div>
        </section>

        {/* =========================================================
            SOLUTION
        ========================================================== */}

        <section
          id="solution"
          className="industrial-grid border-b border-border"
        >
          <div className="mx-auto max-w-[1500px] px-6 py-24 sm:px-10 lg:px-14 lg:py-32">
            <div className="grid gap-16 lg:grid-cols-[0.85fr_1.15fr] lg:items-start lg:gap-24">
              <div>
                <SectionEyebrow>THE SOLUTION</SectionEyebrow>

                <h2 className="mt-4 font-display text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
                  One platform for energy, machines and production decisions.
                </h2>

                <p className="mt-7 text-lg leading-8 text-muted-foreground">
                  EnerSense brings multiple parts of factory operations into a
                  connected intelligence layer. Instead of looking at isolated
                  measurements, the platform helps users understand the
                  relationship between energy behavior, equipment condition and
                  production decisions.
                </p>

                <div className="mt-8 rounded-xl border border-teal/20 bg-teal/5 p-6">
                  <div className="flex gap-4">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-teal-soft text-teal">
                      <ShieldCheck className="h-5 w-5" />
                    </div>

                    <div>
                      <h3 className="font-semibold">
                        Decision support, not just dashboards
                      </h3>

                      <p className="mt-2 text-sm leading-6 text-muted-foreground">
                        The goal is to help users understand what is happening,
                        why it may matter, and what production option can be
                        evaluated next.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid gap-5 sm:grid-cols-2">
                <SolutionCard
                  icon={Zap}
                  title="Energy Intelligence"
                  description="Track and understand energy behavior so unusual consumption patterns and efficiency opportunities can be investigated."
                />

                <SolutionCard
                  icon={MonitorCog}
                  title="Machine Health"
                  description="Use operational signals such as power, temperature and vibration to build a clearer view of equipment condition."
                />

                <SolutionCard
                  icon={TriangleAlert}
                  title="Operational Awareness"
                  description="Bring important conditions and abnormal signals into a view that is easier for teams to understand and investigate."
                />

                <SolutionCard
                  icon={BrainCircuit}
                  title="Production Intelligence"
                  description="Evaluate production scenarios against practical constraints instead of making planning decisions blindly."
                />
              </div>
            </div>
          </div>
        </section>

        {/* =========================================================
            FEATURES
        ========================================================== */}

        <section id="features" className="border-b border-border">
          <div className="mx-auto max-w-[1500px] px-6 py-24 sm:px-10 lg:px-14 lg:py-32">
            <div className="mx-auto max-w-3xl text-center">
              <SectionEyebrow>CORE CAPABILITIES</SectionEyebrow>

              <h2 className="mt-4 font-display text-4xl font-semibold tracking-tight sm:text-5xl lg:text-6xl">
                What you can do with EnerSense
              </h2>

              <p className="mt-6 text-lg leading-8 text-muted-foreground">
                Each part of the platform focuses on a different stage of the
                manufacturing decision process.
              </p>
            </div>

            <div className="mt-16 grid gap-5 lg:grid-cols-3">
              <FeatureCard
                icon={Gauge}
                step="01"
                title="Understand energy"
                description="Get a clearer operational picture of how energy is being used across the plant and investigate areas where consumption may require attention."
                points={[
                  "Energy consumption visibility",
                  "Energy behavior analysis",
                  "Operational comparison",
                  "Efficiency opportunities",
                ]}
              />

              <FeatureCard
                icon={MonitorCog}
                step="02"
                title="Understand machines"
                description="Bring machine-level operating signals together so abnormal behavior can be easier to detect and investigate."
                points={[
                  "Machine condition signals",
                  "Power monitoring",
                  "Temperature monitoring",
                  "Vibration awareness",
                ]}
              />

              <FeatureCard
                icon={BrainCircuit}
                step="03"
                title="Optimize production"
                description="Use ProcessTwin AI to explore production allocations while considering the constraints that matter to the order."
                points={[
                  "Production allocation",
                  "Energy consideration",
                  "Quality constraints",
                  "Carbon constraints",
                ]}
              />
            </div>
          </div>
        </section>

        {/* =========================================================
            MACHINE HEALTH
        ========================================================== */}

        <section className="industrial-grid border-b border-border">
          <div className="mx-auto max-w-[1500px] px-6 py-24 sm:px-10 lg:px-14 lg:py-32">
            <div className="grid items-center gap-16 lg:grid-cols-[1fr_0.9fr] lg:gap-24">
              <div>
                <SectionEyebrow>MACHINE HEALTH</SectionEyebrow>

                <h2 className="mt-4 max-w-3xl font-display text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
                  Energy behavior can also tell you about machine behavior.
                </h2>

                <p className="mt-7 max-w-2xl text-lg leading-8 text-muted-foreground">
                  Machine health is not about looking at a single number. A
                  clearer equipment picture can come from combining multiple
                  operating signals and understanding how they behave relative
                  to expected conditions.
                </p>

                <div className="mt-10 grid gap-4 sm:grid-cols-2">
                  <SignalCard
                    icon={Zap}
                    title="Power"
                    description="Compare current electrical behavior with expected operating behavior."
                  />

                  <SignalCard
                    icon={Gauge}
                    title="Temperature"
                    description="Observe temperature behavior and identify conditions outside expected ranges."
                  />

                  <SignalCard
                    icon={Workflow}
                    title="Vibration"
                    description="Surface unusual mechanical behavior that may require investigation."
                  />

                  <SignalCard
                    icon={ShieldCheck}
                    title="Health assessment"
                    description="Bring multiple operating signals together into an easier-to-read equipment view."
                  />
                </div>
              </div>

              <div className="rounded-2xl border border-border bg-panel/80 p-6 sm:p-8">
                <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-teal">
                  SIGNAL → CONTEXT → ACTION
                </div>

                <div className="mt-7 space-y-4">
                  <FlowStep
                    number="01"
                    title="Observe"
                    description="Collect or provide relevant machine operating information."
                  />

                  <FlowStep
                    number="02"
                    title="Compare"
                    description="Understand whether the observed behavior is consistent with expected operation."
                  />

                  <FlowStep
                    number="03"
                    title="Investigate"
                    description="Use the combined context to identify conditions that may require attention."
                  />

                  <FlowStep
                    number="04"
                    title="Act"
                    description="Use the resulting information to support operational decisions."
                    last
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* =========================================================
            PROCESS TWIN
        ========================================================== */}

        <section id="processtwin" className="border-b border-border">
          <div className="mx-auto max-w-[1500px] px-6 py-24 sm:px-10 lg:px-14 lg:py-32">
            <div className="rounded-3xl border border-amber/20 bg-gradient-to-br from-amber/10 via-background to-teal/5 p-7 sm:p-10 lg:p-14">
              <div className="grid items-center gap-14 lg:grid-cols-[1fr_0.85fr] lg:gap-20">
                <div>
                  <div className="inline-flex items-center gap-2 rounded-full border border-amber/30 bg-amber/10 px-4 py-2 text-xs font-semibold text-amber">
                    <BrainCircuit className="h-4 w-4" />
                    PROCESS TWIN AI
                  </div>

                  <h2 className="mt-6 max-w-3xl font-display text-4xl font-semibold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
                    Test production decisions before committing to them.
                  </h2>

                  <p className="mt-7 max-w-2xl text-lg leading-8 text-muted-foreground">
                    ProcessTwin AI is the production intelligence component of
                    EnerSense. It evaluates possible machine allocations for a
                    production order and checks them against the constraints
                    defined for that order.
                  </p>

                  <div className="mt-9 grid gap-4 sm:grid-cols-2">
                    <TwinConstraint
                      icon={Zap}
                      title="Energy"
                      description="Consider energy required by different production allocations."
                    />

                    <TwinConstraint
                      icon={Target}
                      title="Cost"
                      description="Compare production options based on energy-related cost."
                    />

                    <TwinConstraint
                      icon={ShieldCheck}
                      title="Quality"
                      description="Ensure the selected production scenario meets the required quality level."
                    />

                    <TwinConstraint
                      icon={Leaf}
                      title="Carbon"
                      description="Consider the defined carbon constraint while evaluating production options."
                    />
                  </div>

                  <div className="mt-10">
                    <Link to="/process-twin">
                      <Button className="h-12 bg-amber px-6 text-primary-foreground hover:bg-amber/90">
                        Open ProcessTwin AI
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                </div>

                <div className="rounded-2xl border border-border bg-panel/90 p-6 shadow-xl sm:p-8">
                  <div className="border-b border-border pb-5">
                    <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-amber">
                      PRODUCTION DECISION FLOW
                    </div>

                    <h3 className="mt-2 font-display text-2xl font-semibold">
                      From order to feasible plan
                    </h3>
                  </div>

                  <div className="mt-6 space-y-3">
                    <DecisionFlow
                      icon={Factory}
                      title="Production order"
                      description="Define what needs to be produced and by when."
                    />

                    <DecisionFlow
                      icon={Settings2}
                      title="Machine capabilities"
                      description="Identify machines capable of producing the required product."
                    />

                    <DecisionFlow
                      icon={ShieldCheck}
                      title="Operational constraints"
                      description="Check quality, deadline and carbon requirements."
                    />

                    <DecisionFlow
                      icon={BrainCircuit}
                      title="Scenario evaluation"
                      description="Evaluate possible production allocations."
                    />

                    <DecisionFlow
                      icon={CheckCircle2}
                      title="Feasible plan"
                      description="Return a production allocation that satisfies the defined constraints."
                      final
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* =========================================================
            WORKFLOW
        ========================================================== */}

        <section id="workflow" className="industrial-grid border-b border-border">
          <div className="mx-auto max-w-[1500px] px-6 py-24 sm:px-10 lg:px-14 lg:py-32">
            <div className="max-w-3xl">
              <SectionEyebrow>HOW TO USE ENERSENSE</SectionEyebrow>

              <h2 className="mt-4 font-display text-4xl font-semibold tracking-tight sm:text-5xl lg:text-6xl">
                A simple flow from plant information to decisions.
              </h2>

              <p className="mt-6 text-lg leading-8 text-muted-foreground">
                The platform is designed around a practical operating
                workflow. Start with understanding the plant, move toward
                identifying conditions that matter, and then evaluate the
                production decisions that follow.
              </p>
            </div>

            <div className="mt-16 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
              <WorkflowCard
                number="01"
                icon={Factory}
                title="Set up your plant"
                description="Define the plant and operational context you want to work with."
              />

              <WorkflowCard
                number="02"
                icon={BarChart3}
                title="Understand operations"
                description="Use energy and machine information to understand what is happening."
              />

              <WorkflowCard
                number="03"
                icon={TriangleAlert}
                title="Identify what matters"
                description="Focus attention on abnormal conditions, operational signals and potential opportunities."
              />

              <WorkflowCard
                number="04"
                icon={BrainCircuit}
                title="Evaluate decisions"
                description="Use ProcessTwin AI to explore production scenarios against defined constraints."
              />
            </div>
          </div>
        </section>

        {/* =========================================================
            WHY ENERSENSE
        ========================================================== */}

        <section className="border-b border-border bg-background">
          <div className="mx-auto max-w-[1500px] px-6 py-24 sm:px-10 lg:px-14 lg:py-32">
            <div className="grid gap-16 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
              <div>
                <SectionEyebrow>WHY ENERSENSE</SectionEyebrow>

                <h2 className="mt-4 font-display text-4xl font-semibold tracking-tight sm:text-5xl">
                  Move from isolated information to connected operational
                  intelligence.
                </h2>
              </div>

              <div className="grid gap-5 sm:grid-cols-2">
                <WhyCard
                  icon={Target}
                  title="Context"
                  description="Understand energy and machine signals in the context of plant operations."
                />

                <WhyCard
                  icon={BrainCircuit}
                  title="Decision support"
                  description="Use operational information to evaluate what could happen before making a production decision."
                />

                <WhyCard
                  icon={Leaf}
                  title="Efficiency awareness"
                  description="Keep energy and carbon considerations visible while thinking about operations."
                />

                <WhyCard
                  icon={Workflow}
                  title="Connected workflow"
                  description="Bring monitoring, investigation and production planning into one platform experience."
                />
              </div>
            </div>
          </div>
        </section>

        {/* =========================================================
            FINAL CTA
        ========================================================== */}

        <section className="industrial-grid">
          <div className="mx-auto max-w-[1500px] px-6 py-24 sm:px-10 lg:px-14 lg:py-32">
            <div className="rounded-3xl border border-border bg-panel/80 px-7 py-14 text-center sm:px-12 lg:px-20 lg:py-20">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-soft text-amber">
                <Factory className="h-7 w-7" />
              </div>

              <h2 className="mx-auto mt-7 max-w-4xl font-display text-4xl font-semibold tracking-tight sm:text-5xl lg:text-6xl">
                Understand your plant.
                <br />
                Understand your machines.
                <br />
                Make better production decisions.
              </h2>

              <p className="mx-auto mt-7 max-w-2xl text-lg leading-8 text-muted-foreground">
                Explore the EnerSense workspace or open ProcessTwin AI to
                understand how the platform turns operational information into
                production intelligence.
              </p>

              <div className="mt-10 flex flex-col justify-center gap-4 sm:flex-row">
                <Link to="/dashboard">
                  <Button className="h-13 w-full bg-amber px-8 text-base text-primary-foreground hover:bg-amber/90 sm:w-auto">
                    Explore Dashboard
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>

                <Link to="/process-twin">
                  <Button
                    variant="outline"
                    className="h-13 w-full border-border px-8 text-base sm:w-auto"
                  >
                    Try ProcessTwin AI
                    <BrainCircuit className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* =========================================================
          FOOTER
      ========================================================== */}

      <footer className="border-t border-border bg-background">
        <div className="mx-auto flex max-w-[1500px] flex-col gap-5 px-6 py-8 sm:px-10 md:flex-row md:items-center md:justify-between lg:px-14">
          <div>
            <LogoMark />

            <p className="mt-3 max-w-md text-xs leading-5 text-muted-foreground">
              Industrial energy and production intelligence for understanding
              factory operations and supporting better decisions.
            </p>
          </div>

          <div className="flex flex-wrap gap-x-7 gap-y-3 text-xs text-muted-foreground">
            <a
              href="#problem"
              className="transition-colors hover:text-foreground"
            >
              Problem
            </a>

            <a
              href="#solution"
              className="transition-colors hover:text-foreground"
            >
              Solution
            </a>

            <a
              href="#features"
              className="transition-colors hover:text-foreground"
            >
              Features
            </a>

            <a
              href="#processtwin"
              className="transition-colors hover:text-foreground"
            >
              ProcessTwin AI
            </a>

            <Link
              to="/dashboard"
              className="transition-colors hover:text-foreground"
            >
              Dashboard
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

/* =============================================================
   SMALL REUSABLE COMPONENTS
============================================================= */

function SectionEyebrow({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-xs font-semibold uppercase tracking-[0.22em] text-teal">
      {children}
    </div>
  );
}

function HeroPoint({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof Zap;
  title: string;
  description: string;
}) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-teal-soft text-teal">
        <Icon className="h-5 w-5" />
      </div>

      <div>
        <div className="text-sm font-semibold text-foreground">{title}</div>

        <div className="text-xs text-muted-foreground">{description}</div>
      </div>
    </div>
  );
}

function PlatformFlowItem({
  icon: Icon,
  title,
  description,
  highlighted = false,
}: {
  icon: typeof Zap;
  title: string;
  description: string;
  highlighted?: boolean;
}) {
  return (
    <div
      className={`flex gap-4 rounded-xl border p-4 transition-colors ${
        highlighted
          ? "border-amber/30 bg-amber/5"
          : "border-border bg-background/40"
      }`}
    >
      <div
        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${
          highlighted
            ? "bg-amber-soft text-amber"
            : "bg-teal-soft text-teal"
        }`}
      >
        <Icon className="h-5 w-5" />
      </div>

      <div>
        <div className="font-semibold text-foreground">{title}</div>

        <p className="mt-1 text-sm leading-5 text-muted-foreground">
          {description}
        </p>
      </div>
    </div>
  );
}

function ProblemCard({
  number,
  icon: Icon,
  title,
  description,
}: {
  number: string;
  icon: typeof Zap;
  title: string;
  description: string;
}) {
  return (
    <div className="group rounded-2xl border border-border bg-panel/60 p-6 transition-all duration-300 hover:-translate-y-1 hover:border-teal/30">
      <div className="flex items-center justify-between">
        <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-amber-soft text-amber">
          <Icon className="h-5 w-5" />
        </div>

        <span className="font-display text-sm font-semibold text-muted-foreground/50">
          {number}
        </span>
      </div>

      <h3 className="mt-7 text-lg font-semibold text-foreground">{title}</h3>

      <p className="mt-3 text-sm leading-6 text-muted-foreground">
        {description}
      </p>
    </div>
  );
}

function SolutionCard({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof Zap;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-panel/60 p-7">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-soft text-teal">
        <Icon className="h-6 w-6" />
      </div>

      <h3 className="mt-6 text-xl font-semibold">{title}</h3>

      <p className="mt-3 text-sm leading-6 text-muted-foreground">
        {description}
      </p>
    </div>
  );
}

function FeatureCard({
  icon: Icon,
  step,
  title,
  description,
  points,
}: {
  icon: typeof Zap;
  step: string;
  title: string;
  description: string;
  points: string[];
}) {
  return (
    <div className="rounded-2xl border border-border bg-panel/70 p-7">
      <div className="flex items-center justify-between">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-soft text-amber">
          <Icon className="h-6 w-6" />
        </div>

        <span className="font-display text-sm font-semibold text-muted-foreground/50">
          {step}
        </span>
      </div>

      <h3 className="mt-7 text-2xl font-semibold">{title}</h3>

      <p className="mt-4 text-sm leading-6 text-muted-foreground">
        {description}
      </p>

      <div className="mt-7 space-y-3 border-t border-border pt-6">
        {points.map((point) => (
          <div key={point} className="flex items-center gap-3 text-sm">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-teal" />
            <span className="text-muted-foreground">{point}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function SignalCard({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof Zap;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-xl border border-border bg-panel/60 p-5">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-soft text-teal">
        <Icon className="h-5 w-5" />
      </div>

      <h3 className="mt-5 font-semibold">{title}</h3>

      <p className="mt-2 text-sm leading-6 text-muted-foreground">
        {description}
      </p>
    </div>
  );
}

function FlowStep({
  number,
  title,
  description,
  last = false,
}: {
  number: string;
  title: string;
  description: string;
  last?: boolean;
}) {
  return (
    <div className="relative flex gap-4">
      {!last && (
        <div className="absolute left-[19px] top-11 h-[calc(100%+12px)] w-px bg-border" />
      )}

      <div className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-teal/30 bg-teal-soft font-display text-sm font-semibold text-teal">
        {number}
      </div>

      <div className="pb-5">
        <h3 className="font-semibold">{title}</h3>

        <p className="mt-1 text-sm leading-6 text-muted-foreground">
          {description}
        </p>
      </div>
    </div>
  );
}

function TwinConstraint({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof Zap;
  title: string;
  description: string;
}) {
  return (
    <div className="flex gap-3 rounded-xl border border-border bg-background/50 p-4">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-teal-soft text-teal">
        <Icon className="h-4 w-4" />
      </div>

      <div>
        <h3 className="text-sm font-semibold">{title}</h3>

        <p className="mt-1 text-xs leading-5 text-muted-foreground">
          {description}
        </p>
      </div>
    </div>
  );
}

function DecisionFlow({
  icon: Icon,
  title,
  description,
  final = false,
}: {
  icon: typeof Zap;
  title: string;
  description: string;
  final?: boolean;
}) {
  return (
    <div
      className={`flex gap-4 rounded-xl border p-4 ${
        final
          ? "border-teal/30 bg-teal/5"
          : "border-border bg-background/40"
      }`}
    >
      <div
        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${
          final ? "bg-teal-soft text-teal" : "bg-amber-soft text-amber"
        }`}
      >
        <Icon className="h-5 w-5" />
      </div>

      <div>
        <h3 className="text-sm font-semibold">{title}</h3>

        <p className="mt-1 text-xs leading-5 text-muted-foreground">
          {description}
        </p>
      </div>
    </div>
  );
}

function WorkflowCard({
  number,
  icon: Icon,
  title,
  description,
}: {
  number: string;
  icon: typeof Zap;
  title: string;
  description: string;
}) {
  return (
    <div className="relative rounded-2xl border border-border bg-panel/70 p-7">
      <div className="flex items-center justify-between">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-soft text-teal">
          <Icon className="h-6 w-6" />
        </div>

        <span className="font-display text-sm font-semibold text-amber">
          {number}
        </span>
      </div>

      <h3 className="mt-7 text-xl font-semibold">{title}</h3>

      <p className="mt-3 text-sm leading-6 text-muted-foreground">
        {description}
      </p>
    </div>
  );
}

function WhyCard({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof Zap;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-panel/60 p-6">
      <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-amber-soft text-amber">
        <Icon className="h-5 w-5" />
      </div>

      <h3 className="mt-5 text-lg font-semibold">{title}</h3>

      <p className="mt-2 text-sm leading-6 text-muted-foreground">
        {description}
      </p>
    </div>
  );
}