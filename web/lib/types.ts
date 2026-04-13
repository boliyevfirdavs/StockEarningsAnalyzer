export type Result = "beat" | "meet" | "miss" | "unknown";

export interface QuarterOut {
  fiscal_quarter_end: string;
  eps_actual: number | null;
  eps_estimate: number | null;
  revenue_actual: number | null;
  revenue_estimate: number | null;
  eps_surprise_pct: number | null;
  revenue_surprise_pct: number | null;
  eps_result: Result;
  revenue_result: Result;
}

export interface SyncOut {
  last_attempt_at: string | null;
  last_success_at: string | null;
  last_error: string | null;
  is_stale: boolean;
  never_synced: boolean;
}

export interface CompanyOut {
  ticker: string;
  sync: SyncOut;
  quarters: QuarterOut[];
}

export interface EarningsResponse {
  freshness_hours: number;
  companies: CompanyOut[];
}
