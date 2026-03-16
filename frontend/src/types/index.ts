// ──────────────────────────────────────────────
// Core domain types mirroring backend schemas
// ──────────────────────────────────────────────

export interface Child {
  id: number;
  external_id?: string | null;
  name?: string | null;
  dob?: string | null; // ISO date string
  gender?: string | null;
  language?: string | null;
  notes?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface ChildCreate {
  name?: string;
  dob?: string;
  gender?: string;
  language?: string;
  notes?: string;
  external_id?: string;
}

// ──────────────────────────────────────────────
// Test / Session types
// ──────────────────────────────────────────────

export interface Test {
  id: number;
  child_id?: number | null;
  start_time?: string | null;
  end_time?: string | null;
  final_risk_label?: string | null;
  final_risk_score?: number | null;
  final_risk_entropy?: number | null;
  total_items?: number | null;
  total_time_s?: number | null;
  final_fatigue_level?: number | null;
  device_id?: string | null;
  status?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

// ──────────────────────────────────────────────
// Item (returned by adaptive engine)
// ──────────────────────────────────────────────

export interface ItemOption {
  id: string;
  text: string;
}

export interface AdaptiveItem {
  id: number;
  module_id: string;
  difficulty: number;
  max_time_seconds: number;
  prompt_text?: string | null;
  prompt_media?: string | null;
  correct_option?: string | null;
  options_json?: string | null; // JSON string: array of {id, text}
}

// ──────────────────────────────────────────────
// Adaptive test control flow
// ──────────────────────────────────────────────

export interface StartTestResponse {
  test_id: number;
  first_item?: AdaptiveItem | null;
  message?: string;
  active?: boolean;
}

export interface SubmitResponsePayload {
  item_id: number;
  is_correct: boolean;
  response_time_s: number;
  test_id: number;
}

export interface RiskResult {
  category: "high" | "moderate" | "low";
  score: number;
  confidence: number;
  explanation?: Record<string, unknown>;
}

export interface SubmitResponseResult {
  status: "in_progress" | "completed" | "completed_fallback";
  next_item?: AdaptiveItem | null;
  risk?: RiskResult | null;
}

// ──────────────────────────────────────────────
// Module summaries (from /module-summaries/)
// ──────────────────────────────────────────────

export interface ModuleSummary {
  id: number;
  test_id?: number | null;
  module_id?: string | null;
  num_items?: number | null;
  num_correct?: number | null;
  avg_rt_s?: number | null;
  theta_mean?: number | null;
  p_weak?: number | null;
  p_strong?: number | null;
  entropy?: number | null;
  final_label?: string | null;
  slow_correct_ratio?: number | null;
  rapid_guess_ratio?: number | null;
}

// ──────────────────────────────────────────────
// XAI (explainability) from /xai/
// ──────────────────────────────────────────────

export interface TestXAI {
  id: number;
  test_id?: number | null;
  subtype?: string | null;
  explanation_json?: string | null; // JSON string
  risk_score?: number | null;
  confidence?: number | null;
}
