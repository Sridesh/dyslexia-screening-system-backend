# app/ef_ads/selection.py

"""
Item selection for EF-ADS.

- Computes expected entropy reduction (information gain) for candidate items
  within a module, using the current theta posterior.
- Adjusts information gain with a fatigue factor based on total test time.
- Selects the next item for administration.

This is an entropy-based, myopic selection rule similar to standard CAT
approaches but tailored to the weak/strong decision space and response-time
considerations.[web:580][web:582][web:584]
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Dict, Optional

from . import config
from .state import SessionState, ModuleStats
from . import bayes
from . import rt_fatigue

# app/ef_ads/selection.py (append)

@dataclass
class CandidateItem:
    """
    Lightweight representation of an item for selection purposes.

    Only contains fields needed by the EF-ADS engine.
    """
    id: int
    module_id: str
    difficulty: float
    max_time_seconds: float

# app/ef_ads/selection.py (append)

def expected_entropy_after_item(
    module_stats: ModuleStats,
    module_id: str,
    item: CandidateItem,
) -> float:
    """
    Compute the expected weak/strong entropy for a module if we administer
    a given item next.

    Steps:
    - Use current theta posterior and 2PL model to get P(correct), P(incorrect).
    - Simulate posterior updates for both outcomes.
    - Convert each posterior to weak/strong probabilities and entropy.
    - Return expectation: P(c)*H(correct) + P(i)*H(incorrect).
    """
    theta_posterior = module_stats.theta_posterior
    theta_grid = config.THETA_GRID
    a = config.ITEM_DISCRIMINATION.get(module_id, 1.0)
    b = item.difficulty

    # 1) Compute P(correct) and P(incorrect) under current posterior
    p_correct = 0.0
    for p_theta, theta in zip(theta_posterior, theta_grid):
        p_c = bayes.prob_correct(theta, a, b)
        p_correct += p_theta * p_c

    p_correct = max(0.0, min(1.0, p_correct))
    p_incorrect = 1.0 - p_correct

    # Guard against degenerate case
    if p_correct < 1e-12 or p_incorrect < 1e-12:
        # If one of them is effectively zero, entropy is dominated by the other
        outcome = True if p_correct >= p_incorrect else False
        posterior = bayes.update_theta_posterior_for_item(
            theta_posterior,
            module_id=module_id,
            item_difficulty=b,
            is_correct=outcome,
        )
        ws = bayes.derive_weak_strong_probs(posterior)
        return bayes.entropy_weak_strong(ws["p_weak"], ws["p_strong"])

    # 2) Simulate posterior if correct
    posterior_correct = bayes.update_theta_posterior_for_item(
        theta_posterior,
        module_id=module_id,
        item_difficulty=b,
        is_correct=True,
    )
    ws_correct = bayes.derive_weak_strong_probs(posterior_correct)
    H_correct = bayes.entropy_weak_strong(ws_correct["p_weak"], ws_correct["p_strong"])

    # 3) Simulate posterior if incorrect
    posterior_incorrect = bayes.update_theta_posterior_for_item(
        theta_posterior,
        module_id=module_id,
        item_difficulty=b,
        is_correct=False,
    )
    ws_incorrect = bayes.derive_weak_strong_probs(posterior_incorrect)
    H_incorrect = bayes.entropy_weak_strong(
        ws_incorrect["p_weak"], ws_incorrect["p_strong"]
    )

    # 4) Expected entropy
    expected_entropy = p_correct * H_correct + p_incorrect * H_incorrect
    return expected_entropy

# app/ef_ads/selection.py (append)

def information_gain_for_item(
    module_stats: ModuleStats,
    module_id: str,
    item: CandidateItem,
) -> float:
    """
    Compute base information gain (entropy reduction) for a given item in
    a specific module.

    Returns
    -------
    G_base = H_current - E[H_after_item]
    """
    H_current = module_stats.entropy
    expected_H = expected_entropy_after_item(module_stats, module_id, item)
    gain = H_current - expected_H
    # Ensure non-negative (tiny numerical negatives are set to zero)
    return max(0.0, gain)

# app/ef_ads/selection.py (append)

def adjusted_gain_for_item(
    session: SessionState,
    module_stats: ModuleStats,
    module_id: str,
    item: CandidateItem,
) -> float:
    """
    Compute adjusted information gain for an item by scaling base entropy
    reduction with a fatigue factor.

    Optionally, this can later incorporate time-efficiency adjustments
    (information per expected time unit).
    """
    base_gain = information_gain_for_item(module_stats, module_id, item)
    if base_gain <= 0.0:
        return 0.0

    fatigue_factor = rt_fatigue.compute_fatigue_factor(session.total_time_seconds)

    # Optionally include a simple time-efficiency adjustment:
    #   gain_per_time = base_gain / max(item.max_time_seconds, eps)
    # For now we only apply fatigue; you can uncomment time scaling later.
    adjusted = base_gain * fatigue_factor

    return adjusted

# app/ef_ads/selection.py (append)

def select_best_item_for_module(
    session: SessionState,
    module_id: str,
    candidate_items: Iterable[CandidateItem],
) -> Optional[CandidateItem]:
    """
    Among candidate items for a module, select the item with the highest
    adjusted information gain.

    Returns
    -------
    The chosen CandidateItem, or None if no candidate has meaningful gain.
    """
    module_stats = session.modules[module_id]

    best_item: Optional[CandidateItem] = None
    best_gain: float = 0.0

    for item in candidate_items:
        # Safety: only consider items of the correct module and still remaining
        if item.module_id != module_id:
            continue
        if item.id not in module_stats.items_remaining:
            continue

        gain = adjusted_gain_for_item(session, module_stats, module_id, item)

        # Only consider items with gain above a small threshold
        if gain < config.MIN_INFO_GAIN:
            continue

        # Prefer highest gain; if tie, you can add tie-breaker logic later
        if gain > best_gain:
            best_gain = gain
            best_item = item

    return best_item

# app/ef_ads/selection.py (append)

def select_next_item_for_module(
    session: SessionState,
    module_id: str,
    item_pool: Dict[int, CandidateItem],
) -> Optional[CandidateItem]:
    """
    Select the next item for a module from a global item_pool.

    Parameters
    ----------
    session   : current SessionState
    module_id : module identifier
    item_pool : mapping item_id -> CandidateItem for all items in the system

    Returns
    -------
    CandidateItem or None if no suitable item found (e.g., pool exhausted
    or all gains below threshold).
    """
    module_stats = session.modules[module_id]

    # Build a list of CandidateItem objects for remaining items in this module
    candidates: List[CandidateItem] = []
    for item_id in module_stats.items_remaining:
        item = item_pool.get(item_id)
        if item is not None and item.module_id == module_id:
            candidates.append(item)

    if not candidates:
        return None

    best_item = select_best_item_for_module(session, module_id, candidates)
    return best_item
