import { EarningsDashboard } from "./components/EarningsDashboard";
import { fetchEarnings } from "@/lib/api";

export default async function Home() {
  let data = null;
  let error: string | null = null;
  try {
    data = await fetchEarnings();
  } catch (e) {
    error = e instanceof Error ? e.message : String(e);
  }

  return (
    <div className="min-h-full bg-zinc-50 dark:bg-black">
      <header className="border-b border-zinc-200 bg-white/80 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/70">
        <div className="mx-auto flex max-w-5xl flex-col gap-2 px-6 py-8">
          <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
            Stock Earnings Analyzer
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            S&amp;P 500 cohort — beats, misses, and trends
          </h1>
          <p className="max-w-3xl text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
            Data is sourced from Yahoo Finance via{" "}
            <code className="rounded bg-zinc-200/60 px-1 py-0.5 text-xs dark:bg-zinc-800">
              yfinance
            </code>
            , persisted in SQL for resilience. Numbers can be incomplete or delayed;
            revenue estimates are often unavailable in free data.
          </p>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-10">
        <EarningsDashboard data={data} error={error} />
      </main>
    </div>
  );
}
