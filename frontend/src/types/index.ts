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
  version?: string | null;
  notes?: string | null;
  session_state?: Record<string, unknown> | null;
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
  round_number?: number;
  message?: string;
  active?: boolean;
}

export interface SubmitResponsePayload {
  item_id: number;
  is_correct: boolean;
  response_time_s: number;
  test_id: number;
  module: string;
  started_at: string; // ISO timestamp
  submitted_at: string; // ISO timestamp
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
  round_number?: number;
  risk?: RiskResult | null;
}

// ──────────────────────────────────────────────
// Module summaries (from /module-summaries/)
// ──────────────────────────────────────────────

export interface ModuleSummary {
  id: number;
  test_id?: number | null;
  module?: string | null;
  num_items?: number | null;
  total_correct_count?: number | null;
  avg_time_s?: number | null;
  avg_switch_rt_s?: number | null;
  p_weak_final?: number | null;
  p_strong_final?: number | null;
  entropy_final?: number | null;
  risk_label?: string | null;
  slow_correct_ratio?: number | null;
  rapid_guess_ratio?: number | null;
}

// ──────────────────────────────────────────────
// XAI (explainability) from /xai/
// ──────────────────────────────────────────────

export interface TestXAI {
  id: number;
  test_id?: number | null;
  method?: string | null;
  payload_json?: string | null;
  created_at?: string | null;
}

// ──────────────────────────────────────────────
// TestItemLog
// ──────────────────────────────────────────────

export interface TestItemLog {
  id: number;
  test_id: number;
  item_id: number;
  round_number?: number | null;
  within_round_idx?: number | null;
  global_index?: number | null;
  module: string;
  difficulty?: number | null;
  response?: string | null;
  is_correct?: boolean | null;
  response_time_s?: number | null;
  started_at?: string | null;
  submitted_at?: string | null;
  is_switch_question: boolean;
  was_slow_correct: boolean;
  fatigue_factor_used?: number | null;
  p_module_weak_before?: number | null;
  p_module_strong_before?: number | null;
  p_module_weak_after?: number | null;
  p_module_strong_after?: number | null;
  p_risk_atrisk_before?: number | null;
  p_risk_atrisk_after?: number | null;
  created_at?: string | null;
}
// ──────────────────────────────────────────────
// Intervention Plan (RAG)
// ──────────────────────────────────────────────

export interface InterventionPlan {
  test_id: number;
  intervention_plan: {
    source: string;
    plan_markdown: string;
  };
}
