import type { EarningsResponse } from "./types";

function apiBase(): string {
  return process.env.API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";
}

function earningsPath(): string {
  const base = `${apiBase()}/companies/earnings`;
  const watch = process.env.WATCHLIST_TICKERS?.trim();
  if (!watch) return base;
  const q = new URLSearchParams({ tickers: watch });
  return `${base}?${q.toString()}`;
}

export async function fetchEarnings(): Promise<EarningsResponse> {
  const res = await fetch(earningsPath(), {
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Earnings API ${res.status}: ${text || res.statusText}`);
  }
  return res.json() as Promise<EarningsResponse>;
}
