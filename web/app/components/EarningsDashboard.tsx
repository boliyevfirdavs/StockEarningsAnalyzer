"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { CompanyOut, EarningsResponse, QuarterOut, Result } from "@/lib/types";

function ResultBadge({ value }: { value: Result }) {
  const styles: Record<Result, string> = {
    beat: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
    meet: "bg-zinc-500/15 text-zinc-700 dark:text-zinc-300",
    miss: "bg-rose-500/15 text-rose-700 dark:text-rose-300",
    unknown: "bg-amber-500/15 text-amber-800 dark:text-amber-200",
  };
  return (
    <span
      className={`inline-flex rounded px-2 py-0.5 text-xs font-medium uppercase tracking-wide ${styles[value]}`}
    >
      {value}
    </span>
  );
}

function formatBillions(n: number | null | undefined): string {
  if (n == null || Number.isNaN(n)) return "—";
  return new Intl.NumberFormat(undefined, {
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(n);
}

function formatEps(n: number | null | undefined): string {
  if (n == null || Number.isNaN(n)) return "—";
  return n.toFixed(2);
}

function formatPct(n: number | null | undefined): string {
  if (n == null || Number.isNaN(n)) return "—";
  return `${n >= 0 ? "+" : ""}${n.toFixed(1)}%`;
}

function quarterLabel(q: QuarterOut): string {
  return q.fiscal_quarter_end.slice(0, 7);
}

function CompanyCard({
  company,
  freshnessHours,
}: {
  company: CompanyOut;
  freshnessHours: number;
}) {
  const latest = company.quarters[0];
  const chartRows = [...company.quarters]
    .sort(
      (a, b) =>
        new Date(a.fiscal_quarter_end).getTime() -
        new Date(b.fiscal_quarter_end).getTime(),
    )
    .map((q) => ({
      period: quarterLabel(q),
      revenue: q.revenue_actual,
      eps: q.eps_actual,
    }));

  const syncNote = company.sync.never_synced
    ? "No data ingested yet. Run the API and POST /admin/refresh (or wait for background ingest)."
    : company.sync.is_stale
      ? `Stale or last refresh had errors (freshness target: ${freshnessHours}h). Showing last good database snapshot.`
      : "Data is within the freshness window.";

  return (
    <section
      id={`company-${company.ticker}`}
      className="rounded-xl border border-zinc-200/80 bg-white/80 p-6 shadow-sm scroll-mt-24 dark:border-zinc-800 dark:bg-zinc-950/40"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">
            {company.ticker}
          </h2>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            {syncNote}
          </p>
          {company.sync.last_success_at && (
            <p className="mt-1 text-xs text-zinc-500">
              Last successful sync:{" "}
              {new Date(company.sync.last_success_at).toLocaleString()}
            </p>
          )}
          {company.sync.last_error && (
            <p className="mt-1 text-xs text-rose-600 dark:text-rose-400">
              Last error: {company.sync.last_error}
            </p>
          )}
        </div>
        {latest && (
          <div className="flex flex-wrap gap-2 text-sm">
            <span className="text-zinc-500">Latest quarter</span>
            <span className="font-medium">{latest.fiscal_quarter_end}</span>
            <ResultBadge value={latest.eps_result} />
            <ResultBadge value={latest.revenue_result} />
          </div>
        )}
      </div>

      {latest && (
        <div className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-900/50">
            <div className="text-xs uppercase text-zinc-500">EPS</div>
            <div className="mt-1 font-mono text-base">
              {formatEps(latest.eps_actual)}{" "}
              <span className="text-zinc-500">vs est</span>{" "}
              {formatEps(latest.eps_estimate)}
            </div>
            <div className="mt-1 text-xs text-zinc-500">
              Surprise {formatPct(latest.eps_surprise_pct)}
            </div>
          </div>
          <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-900/50">
            <div className="text-xs uppercase text-zinc-500">Revenue</div>
            <div className="mt-1 font-mono text-base">
              {formatBillions(latest.revenue_actual)}{" "}
              <span className="text-zinc-500">USD</span>
            </div>
            <div className="mt-1 text-xs text-zinc-500">
              Estimate often unavailable via Yahoo; trend still useful.
            </div>
          </div>
        </div>
      )}

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="h-56">
          <div className="mb-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Revenue by quarter
          </div>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartRows}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-zinc-200 dark:stroke-zinc-800" />
              <XAxis dataKey="period" tick={{ fontSize: 11 }} />
              <YAxis
                tick={{ fontSize: 11 }}
                tickFormatter={(v) => formatBillions(Number(v))}
              />
              <Tooltip
                formatter={(value) =>
                  value == null ? "—" : formatBillions(Number(value))
                }
              />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#2563eb"
                strokeWidth={2}
                dot={{ r: 3 }}
                connectNulls
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="h-56">
          <div className="mb-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Diluted EPS by quarter
          </div>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartRows}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-zinc-200 dark:stroke-zinc-800" />
              <XAxis dataKey="period" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                formatter={(value) =>
                  value == null ? "—" : formatEps(Number(value))
                }
              />
              <Line
                type="monotone"
                dataKey="eps"
                stroke="#059669"
                strokeWidth={2}
                dot={{ r: 3 }}
                connectNulls
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mt-6 overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-zinc-200 text-xs uppercase text-zinc-500 dark:border-zinc-800">
            <tr>
              <th className="py-2 pr-4">Quarter end</th>
              <th className="py-2 pr-4">EPS</th>
              <th className="py-2 pr-4">Est</th>
              <th className="py-2 pr-4">EPS Δ%</th>
              <th className="py-2 pr-4">EPS</th>
              <th className="py-2 pr-4">Revenue</th>
              <th className="py-2 pr-4">Rev</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100 dark:divide-zinc-900">
            {company.quarters.map((q) => (
              <tr key={q.fiscal_quarter_end}>
                <td className="py-2 pr-4 font-mono text-xs">
                  {q.fiscal_quarter_end}
                </td>
                <td className="py-2 pr-4 font-mono">{formatEps(q.eps_actual)}</td>
                <td className="py-2 pr-4 font-mono">{formatEps(q.eps_estimate)}</td>
                <td className="py-2 pr-4 font-mono">{formatPct(q.eps_surprise_pct)}</td>
                <td className="py-2 pr-4">
                  <ResultBadge value={q.eps_result} />
                </td>
                <td className="py-2 pr-4 font-mono">
                  {formatBillions(q.revenue_actual)}
                </td>
                <td className="py-2 pr-4">
                  <ResultBadge value={q.revenue_result} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function EarningsDashboard({
  data,
  error,
}: {
  data: EarningsResponse | null;
  error: string | null;
}) {
  if (error) {
    return (
      <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-rose-900 dark:border-rose-900 dark:bg-rose-950/40 dark:text-rose-100">
        <p className="font-medium">Could not load earnings</p>
        <p className="mt-2 text-sm opacity-90">{error}</p>
        <p className="mt-3 text-sm">
          Ensure the API is running (see repo README) and{" "}
          <code className="rounded bg-black/5 px-1 py-0.5 text-xs dark:bg-white/10">
            API_URL
          </code>{" "}
          points to it.
        </p>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="flex flex-col gap-8">
      <section className="rounded-xl border border-zinc-200/80 bg-white/90 p-4 dark:border-zinc-800 dark:bg-zinc-950/50">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h2 className="text-sm font-semibold text-zinc-800 dark:text-zinc-100">
            Cohort overview
          </h2>
          <span className="text-xs text-zinc-500">
            {data.companies.length} of {data.cohort_symbol_count} symbols — jump to a card
            or scroll. If the count is wrong, check{" "}
            <code className="rounded bg-zinc-100 px-1 text-[10px] dark:bg-zinc-800">
              STOCK_EARNINGS_DASHBOARD_TICKERS
            </code>{" "}
            in{" "}
            <code className="rounded bg-zinc-100 px-1 text-[10px] dark:bg-zinc-800">
              web/.env.local
            </code>{" "}
            (remove it to use the full API cohort) and restart{" "}
            <code className="rounded bg-zinc-100 px-1 text-[10px] dark:bg-zinc-800">
              npm run dev
            </code>
            .
          </span>
        </div>
        <div className="mt-3 max-h-48 overflow-y-auto">
          <ul className="flex flex-wrap gap-2">
            {data.companies.map((c) => {
              const qn = c.quarters.length;
              const label =
                qn === 0
                  ? "no rows yet"
                  : `${qn} quarter${qn === 1 ? "" : "s"}`;
              return (
                <li key={c.ticker}>
                  <a
                    href={`#company-${c.ticker}`}
                    className="inline-flex items-center gap-1 rounded-full border border-zinc-200 bg-zinc-50 px-2.5 py-1 text-xs font-medium text-zinc-800 hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:bg-zinc-800"
                  >
                    <span>{c.ticker}</span>
                    <span className="text-zinc-500 dark:text-zinc-400">
                      ({label})
                    </span>
                  </a>
                </li>
              );
            })}
          </ul>
        </div>
      </section>

      {data.companies.map((c) => (
        <CompanyCard
          key={c.ticker}
          company={c}
          freshnessHours={data.freshness_hours}
        />
      ))}
    </div>
  );
}
