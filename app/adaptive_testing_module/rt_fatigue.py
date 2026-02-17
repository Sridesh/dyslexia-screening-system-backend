# app/ef_ads/rt_fatigue.py

"""
Response-time and fatigue modeling for EF-ADS.

- Flags slow-but-correct and rapid-guess responses.
- Updates per-module RT statistics.
- Computes a global fatigue factor based on elapsed time.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

from . import config
from .state import SessionState, ModuleStats

# app/ef_ads/rt_fatigue.py (append)

def classify_response_time(
    rt_seconds: float,
    max_time_seconds: float,
    is_correct: bool,
) -> Tuple[bool, bool]:
    """
    Classify a response into slow-but-correct and rapid-guess flags.

    Parameters
    ----------
    rt_seconds       : observed response time for this item
    max_time_seconds : expected/allowed maximum time for this item
    is_correct       : correctness of the response

    Returns
    -------
    (is_slow_correct, is_rapid_guess)
    """
    # Guard against zero or negative max_time
    if max_time_seconds <= 0:
        return False, False

    # "Slow but correct": correct answer, RT substantially above expected max
    is_slow_correct = is_correct and (
        rt_seconds > config.SLOW_RT_FACTOR * max_time_seconds
    )

    # "Rapid guess": very fast response relative to max_time and incorrect
    is_rapid_guess = (not is_correct) and (
        rt_seconds < config.RAPID_GUESS_FRACTION * max_time_seconds
    )

    return is_slow_correct, is_rapid_guess

# app/ef_ads/rt_fatigue.py (append)

def update_module_rt_stats(
    module_stats: ModuleStats,
    rt_seconds: float,
    max_time_seconds: float,
    is_correct: bool,
) -> None:
    """
    Update response-time-related statistics for a module after one item.

    - Accumulates sum of RTs.
    - Flags slow-but-correct and rapid-guess responses.
    - Updates counts for later ratios.
    """
    is_slow_correct, is_rapid_guess = classify_response_time(
        rt_seconds=rt_seconds,
        max_time_seconds=max_time_seconds,
        is_correct=is_correct,
    )

    module_stats.sum_rt += rt_seconds

    if is_correct:
        module_stats.correct += 1
        if is_slow_correct:
            module_stats.slow_correct += 1

    if is_rapid_guess:
        module_stats.rapid_guess += 1

# app/ef_ads/rt_fatigue.py (append)

def compute_fatigue_factor(total_time_seconds: float) -> float:
    """
    Compute a multiplicative fatigue factor based on total test time.

    The factor decreases linearly with time, bounded below by MIN_FATIGUE_FACTOR.

    Parameters
    ----------
    total_time_seconds : elapsed time since test start

    Returns
    -------
    fatigue_factor in [MIN_FATIGUE_FACTOR, 1.0]
    """
    minutes = total_time_seconds / 60.0
    raw_factor = 1.0 - config.FATIGUE_SLOPE * minutes
    return max(config.MIN_FATIGUE_FACTOR, min(1.0, raw_factor))

# app/ef_ads/rt_fatigue.py (append)

def update_session_time(
    session: SessionState,
    response_timestamp: datetime,
) -> None:
    """
    Update total_time_seconds and last_update_at for a session, given the
    timestamp when the latest response was received.

    Assumes session.started_at is set at test creation.
    """
    session.last_update_at = response_timestamp
    elapsed = (response_timestamp - session.started_at).total_seconds()
    if elapsed < 0:
        elapsed = 0.0
    session.total_time_seconds = elapsed
