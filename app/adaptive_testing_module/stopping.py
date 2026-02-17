# app/ef_ads/stopping.py

"""
Stopping logic for EF-ADS.

- Decides when a module is "settled" (weak/strong with enough certainty).
- Decides when the whole test should stop, based on:
    - per-module certainty (entropy + probabilities),
    - maximum achievable information gain,
    - hard limits on items and time.

Design follows information-theoretic CAT stopping ideas and
minimum-information rules.[web:509][web:515][web:539][web:593]
"""

from __future__ import annotations
from typing import Dict, Optional

from . import config
from .state import SessionState, ModuleStats
from . import selection
from . import rt_fatigue

# app/ef_ads/stopping.py (append)

def is_module_settled(stats: ModuleStats) -> bool:
    """
    Check if a module is 'settled' (weak/strong classification considered
    reliable enough to stop asking items in this module).
    """
    if stats.num_items < config.MIN_ITEMS_PER_MODULE:
        return False

    if stats.entropy > config.ENTROPY_THRESHOLD:
        return False

    if max(stats.p_weak, stats.p_strong) < config.P_CONFIDENT:
        return False

    return True

# app/ef_ads/stopping.py (append)

def max_possible_gain_across_modules(
    session: SessionState,
    item_pool: Dict[int, selection.CandidateItem],
) -> float:
    """
    Compute the maximum base information gain obtainable from any remaining
    item in any not-yet-settled module.
    """
    max_gain = 0.0

    for module_id, stats in session.modules.items():
        if is_module_settled(stats):
            continue

        for item_id in stats.items_remaining:
            item = item_pool.get(item_id)
            if item is None or item.module_id != module_id:
                continue

            gain = selection.information_gain_for_item(stats, module_id, item)
            if gain > max_gain:
                max_gain = gain

    return max_gain

# app/ef_ads/stopping.py (append)

def should_stop_globally(
    session: SessionState,
    item_pool: Dict[int, selection.CandidateItem],
) -> bool:
    """
    Decide whether to stop the entire test session.

    Criteria:
    - Hard limits: max total items or time reached.
    - Key modules (e.g., PA and RAN) settled.
    - OR maximum possible information gain across modules is below threshold.
    """
    # Hard caps
    total_items = sum(m.num_items for m in session.modules.values())
    if total_items >= config.MAX_ITEMS_TOTAL:
        return True

    total_minutes = session.total_time_seconds / 60.0
    if total_minutes >= config.MAX_TEST_TIME_MIN:
        return True

    # Check if key modules are settled
    pa = session.modules.get("phonemic_awareness")
    ran = session.modules.get("ran")

    key_modules_settled = False
    if pa is not None and ran is not None:
        key_modules_settled = is_module_settled(pa) and is_module_settled(ran)

    # If key modules are settled, we can allow early stopping
    if key_modules_settled:
        return True

    # Otherwise, check whether additional items can still provide meaningful gain
    max_gain = max_possible_gain_across_modules(session, item_pool)
    if max_gain < config.MIN_INFO_GAIN:
        return True

    return False

