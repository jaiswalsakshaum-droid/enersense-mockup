
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Eye,
  EyeOff,
  Factory,
  LockKeyhole,
  Mail,
  ShieldCheck,
  Zap,
} from "lucide-react";

export const Route = createFileRoute("/auth")({
  head: () => ({
    meta: [
      { title: "Sign in — EnerSense" },
      {
        name: "description",
        content: "Sign in to your EnerSense industrial intelligence workspace.",
      },
    ],
  }),
  component: LoginPage,
});

function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState("");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(
      "The login interface is ready, but authentication has not been connected yet.",
    );
  }

  return (
    <main className="industrial-grid relative min-h-screen overflow-hidden bg-background text-foreground">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_75%_15%,color-mix(in_oklab,var(--color-teal)_13%,transparent),transparent_30rem)]" />

      <div className="relative mx-auto flex min-h-screen max-w-[1440px] flex-col px-6 py-6 sm:px-10 lg:px-16">
        <header className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-amber/20 bg-amber-soft text-amber">
              <Factory className="h-6 w-6" />
            </div>
            <div>
              <div className="font-display text-lg font-semibold tracking-tight">
                EnerSense
              </div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-muted-foreground">
                Industrial Intelligence
              </div>
            </div>
          </Link>

          <Link
            to="/"
            className="flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to home
          </Link>
        </header>

        <div className="grid flex-1 items-center gap-12 py-12 lg:grid-cols-[1fr_460px] lg:gap-24 lg:py-16">
          <section className="mx-auto w-full max-w-xl lg:mx-0">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-teal/30 bg-teal-soft px-3 py-1.5 text-[11px] font-semibold text-teal">
              <Zap className="h-3.5 w-3.5" />
              INDUSTRIAL ENERGY INTELLIGENCE
            </div>

            <h1 className="max-w-xl font-display text-5xl font-semibold leading-[1.05] tracking-[-0.05em] sm:text-6xl">
              Your plant.
              <br />
              Your data.
              <br />
              <span className="text-amber">Your decisions.</span>
            </h1>

            <p className="mt-6 max-w-lg text-base leading-7 text-muted-foreground">
              Access your industrial workspace to monitor energy consumption,
              track machine health, investigate alerts, and make smarter
              operational decisions.
            </p>

            <div className="mt-10 space-y-4 border-t border-border pt-7">
              <div className="flex items-start gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-teal-soft text-teal">
                  <Zap className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-sm font-semibold">Energy intelligence</p>
                  <p className="mt-1 text-xs leading-5 text-muted-foreground">
                    Understand consumption, costs, and efficiency.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-soft text-amber">
                  <Factory className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-sm font-semibold">Machine monitoring</p>
                  <p className="mt-1 text-xs leading-5 text-muted-foreground">
                    Keep track of equipment health and operational alerts.
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section className="glass-panel mx-auto w-full max-w-[460px] rounded-2xl border border-border p-6 shadow-2xl sm:p-9">
            <div className="mb-8">
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-amber-soft text-amber">
                <LockKeyhole className="h-5 w-5" />
              </div>

              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-amber">
                SECURE WORKSPACE
              </p>

              <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight">
                Welcome back
              </h2>

              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                Sign in to access your plant workspace.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label
                  htmlFor="email"
                  className="mb-2 block text-xs font-medium"
                >
                  Work email
                </label>

                <div className="relative">
                  <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(event) => {
                      setEmail(event.target.value);
                      setMessage("");
                    }}
                    placeholder="you@company.com"
                    className="h-12 w-full rounded-lg border border-input bg-background pl-10 pr-3.5 text-sm outline-none transition-colors placeholder:text-muted-foreground focus:border-amber focus:ring-1 focus:ring-amber"
                  />
                </div>
              </div>

              <div>
                <div className="mb-2 flex items-center justify-between">
                  <label
                    htmlFor="password"
                    className="block text-xs font-medium"
                  >
                    Password
                  </label>
                  <span className="text-[11px] text-muted-foreground">
                    Account access
                  </span>
                </div>

                <div className="relative">
                  <LockKeyhole className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

                  <input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(event) => {
                      setPassword(event.target.value);
                      setMessage("");
                    }}
                    placeholder="Enter your password"
                    className="h-12 w-full rounded-lg border border-input bg-background pl-10 pr-11 text-sm outline-none transition-colors placeholder:text-muted-foreground focus:border-amber focus:ring-1 focus:ring-amber"
                  />

                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {message && (
                <p
                  role="status"
                  className="rounded-lg border border-amber/30 bg-amber-soft p-3 text-xs leading-5 text-foreground"
                >
                  {message}
                </p>
              )}

              <button
                type="submit"
                className="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-amber px-4 text-sm font-semibold text-primary-foreground transition-colors hover:bg-amber/90"
              >
                Sign in
                <ArrowRight className="h-4 w-4" />
              </button>
            </form>

            <div className="mt-6 flex items-start gap-2 border-t border-border pt-5">
              <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-teal" />
              <p className="text-[11px] leading-5 text-muted-foreground">
                Your industrial workspace is designed to keep plant operations
                and monitoring data organized.
              </p>
            </div>

            <p className="mt-6 text-center text-xs text-muted-foreground">
              Exploring EnerSense?{" "}
              <Link
                to="/"
                className="font-semibold text-amber transition-colors hover:underline"
              >
                View the platform
              </Link>
            </p>
          </section>
        </div>

        <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-border py-5 text-[11px] text-muted-foreground">
          <span>© 2026 EnerSense Systems</span>
          <span className="flex items-center gap-2">
            <ShieldCheck className="h-3.5 w-3.5 text-teal" />
            Industrial intelligence for real plants
          </span>
        </footer>
      </div>
    </main>
  );
}
