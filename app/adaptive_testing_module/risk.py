# app/ef_ads/risk.py

"""
Risk classification and explanation for EF-ADS.

- Classifies each module as weak/strong/uncertain.
- Computes a global dyslexia risk category (High/Moderate/Low).
- Produces a structured explanation object for reporting.

Combines Bayesian module estimates, entropy, and response-time patterns
with explicit, theory-driven rules.[web:591][web:594]
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Literal

from . import config
from .state import SessionState, ModuleStats

# app/ef_ads/risk.py (append)

ModuleLabel = Literal["weak", "strong", "uncertain"]


@dataclass
class ModuleClassification:
    module_id: str
    label: ModuleLabel
    p_weak: float
    p_strong: float
    entropy: float
    num_items: int
    avg_rt: float
    slow_correct_ratio: float
    rapid_guess_ratio: float

# app/ef_ads/risk.py (append)

def classify_module(module_id: str, stats: ModuleStats) -> ModuleClassification:
    """
    Classify a module as weak / strong / uncertain based on posterior
    probabilities and entropy, and compute basic RT ratios.
    """
    # Determine label
    if stats.entropy <= config.ENTROPY_THRESHOLD and max(stats.p_weak, stats.p_strong) >= config.P_CONFIDENT:
        label: ModuleLabel = "weak" if stats.p_weak > stats.p_strong else "strong"
    else:
        label = "uncertain"

    # Average RT and ratios
    avg_rt = stats.sum_rt / stats.num_items if stats.num_items > 0 else 0.0
    slow_correct_ratio = (
        stats.slow_correct / stats.correct if stats.correct > 0 else 0.0
    )
    rapid_guess_ratio = (
        stats.rapid_guess / stats.num_items if stats.num_items > 0 else 0.0
    )

    return ModuleClassification(
        module_id=module_id,
        label=label,
        p_weak=stats.p_weak,
        p_strong=stats.p_strong,
        entropy=stats.entropy,
        num_items=stats.num_items,
        avg_rt=avg_rt,
        slow_correct_ratio=slow_correct_ratio,
        rapid_guess_ratio=rapid_guess_ratio,
    )

# app/ef_ads/risk.py (append)

@dataclass
class GlobalRiskResult:
    risk_category: Literal["high", "moderate", "low"]
    risk_score: float
    confidence: float
    modules: Dict[str, ModuleClassification]
    explanation: Dict

# app/ef_ads/risk.py (append)

def compute_global_risk(session: SessionState) -> GlobalRiskResult:
    """
    Compute global dyslexia risk category and explanation based on
    per-module classifications and RT patterns.
    """
    module_results: Dict[str, ModuleClassification] = {}
    for module_id, stats in session.modules.items():
        module_results[module_id] = classify_module(module_id, stats)

    # 1) Base risk score from weak probabilities (weighted)
    base_score = 0.0
    for module_id, mc in module_results.items():
        w = config.MODULE_WEIGHTS.get(module_id, 0.0)
        base_score += w * mc.p_weak

    # 2) Adjustments from RT patterns (e.g., slow RAN)
    rt_adjustment = 0.0
    ran_res = module_results.get("ran")
    if ran_res is not None:
        # If RAN is slow but still correct, we consider speed issues
        if ran_res.slow_correct_ratio > 0.5 and ran_res.label != "weak":
            rt_adjustment += 0.05  # modest increase

    # You can add more RT-based adjustments here if desired.

    risk_score = max(0.0, min(1.0, base_score + rt_adjustment))

    # 3) Map risk_score to category
    if risk_score >= config.RISK_SCORE_HIGH:
        category: Literal["high", "moderate", "low"] = "high"
    elif risk_score >= config.RISK_SCORE_MODERATE:
        category = "moderate"
    else:
        category = "low"

    # 4) Confidence: complement of average entropy (simple proxy)
    avg_entropy = (
        sum(m.entropy for m in session.modules.values())
        / max(len(session.modules), 1)
    )
    confidence = max(0.0, min(1.0, 1.0 - avg_entropy))

    explanation = build_explanation_object(category, risk_score, confidence, module_results)

    return GlobalRiskResult(
        risk_category=category,
        risk_score=risk_score,
        confidence=confidence,
        modules=module_results,
        explanation=explanation,
    )

# app/ef_ads/risk.py (append)

def build_explanation_object(
    category: str,
    risk_score: float,
    confidence: float,
    module_results: Dict[str, ModuleClassification],
) -> Dict:
    """
    Construct a structured explanation dictionary for reporting.

    Includes:
    - Global summary
    - Per-module details
    - Simple RT-related notes
    """
    module_details = {}
    for module_id, mc in module_results.items():
        label = config.MODULE_LABELS.get(module_id, module_id)
        notes = []

        if mc.label == "weak":
            notes.append(
                f"Performance in {label} suggests a likely weakness (P(weak)={mc.p_weak:.2f})."
            )
        elif mc.label == "strong":
            notes.append(
                f"Performance in {label} appears strong (P(strong)={mc.p_strong:.2f})."
            )
        else:
            notes.append(
                f"Results in {label} are still uncertain; more data would improve confidence."
            )

        if mc.slow_correct_ratio > 0.5:
            notes.append(
                "Many correct responses were slower than expected, indicating potential speed or fatigue issues."
            )

        if mc.rapid_guess_ratio > 0.2:
            notes.append(
                "Frequent very fast incorrect responses may indicate guessing or low engagement."
            )

        module_details[module_id] = {
            "label": mc.label,
            "p_weak": mc.p_weak,
            "p_strong": mc.p_strong,
            "entropy": mc.entropy,
            "num_items": mc.num_items,
            "avg_rt": mc.avg_rt,
            "slow_correct_ratio": mc.slow_correct_ratio,
            "rapid_guess_ratio": mc.rapid_guess_ratio,
            "notes": notes,
        }

    global_summary = {
        "risk_category": category,
        "risk_score": risk_score,
        "confidence": confidence,
    }

    return {
        "global": global_summary,
        "modules": module_details,
    }

# # app/ef_ads/risk.py (append)

# def is_high_risk_profile(
#     session: SessionState,
#     module_results: Dict[str, ModuleClassification],
# ) -> bool:
#     """
#     Heuristic check for a 'high-risk' profile that warrants immediate
#     referral, even if global risk score is moderate.

#     This implements the 'strong evidence' rule from the design:
#     - RAN is weak AND
#     - PA is weak OR RAN is very slow.
#     """
#     ran_res = module_results.get("ran")
#     pa_res = module_results.get("phonemic_awareness")

#     if ran_res is None or pa_res is None:
#         return False

#     # Condition 1: RAN is clearly weak
#     ran_is_weak = (
#         ran_res.label == "weak"
#         and ran_res.num_items >= config.MIN_ITEMS_PER_MODULE
#     )

#     if not ran_is_weak:
#         return False

#     # Condition 2: Either PA is also weak, OR RAN is very slow
#     pa_is_weak = (
#         pa_res.label == "weak"
#         and pa_res.num_items >= config.MIN_ITEMS_PER_MODULE
#     )

#     ran_is_very_slow = ran_res.avg_rt > (config.RT_THRESHOLD_SECONDS * 1.5)

#     return pa_is_weak or ran_is_very_slow
