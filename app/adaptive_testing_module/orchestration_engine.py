# app/ef_ads/engine.py

"""
High-level orchestration for EF-ADS.

Provides functions that:
- Initialise a new session state.
- Process a single item response (Bayesian + RT + time updates).
- Decide the next module and item to administer.
- Determine whether the test should stop and, if so, compute risk.

These functions are what the FastAPI layer should call.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from .state import SessionState
from .selection import CandidateItem, select_next_item_for_module
from . import bayes
from . import rt_fatigue
from . import stopping
from . import risk
from . import config

# app/ef_ads/engine.py (append)

def initialise_session(
    test_id: int,
    module_item_ids: Dict[str, list[int]],
    started_at: Optional[datetime] = None,
) -> SessionState:
    """
    Initialise a new EF-ADS SessionState for a given test.

    Parameters
    ----------
    test_id         : database id of the Test row
    module_item_ids : mapping module_id -> list of item ids available
                      for that module in this test
    started_at      : optional start time; defaults to utcnow

    Returns
    -------
    SessionState instance with uniform theta posteriors and item pools.
    """
    session = SessionState.initialise(
        test_id=test_id,
        started_at=started_at,
        module_item_ids=module_item_ids,
    )
    return session

# app/ef_ads/engine.py (append)

def choose_next_module(session: SessionState) -> Optional[str]:
    """
    Decide which module to administer next.

    Strategy:
    - Iterate modules in a fixed cyclic order starting from current_module_index.
    - Skip modules that are already 'settled'.
    - If no unsettled modules remain, return None.
    """
    module_ids = config.MODULES
    n = len(module_ids)
    if n == 0:
        return None

    # Start search from the next module index (cyclic)
    start_idx = session.current_module_index
    for offset in range(n):
        idx = (start_idx + offset) % n
        module_id = module_ids[idx]
        stats = session.modules.get(module_id)
        if stats is None:
            continue

        if not stopping.is_module_settled(stats) and stats.items_remaining:
            # Update current index and return chosen module
            session.current_module_index = idx
            return module_id

    # No unsettled modules with remaining items
    return None

# app/ef_ads/engine.py (append)

@dataclass
class ProcessResponseResult:
    session: SessionState
    should_stop: bool
    next_item: Optional[CandidateItem]
    global_risk: Optional[risk.GlobalRiskResult]

# app/ef_ads/engine.py (append)

def process_response(
    session: SessionState,
    *,
    module_id: str,
    item: CandidateItem,
    is_correct: bool,
    rt_seconds: float,
    response_timestamp: Optional[datetime],
    item_pool: Dict[int, CandidateItem],
) -> ProcessResponseResult:
    """
    Process a single item response and decide next action.

    Steps:
    - Update session time.
    - Update Bayesian posterior and entropy for the module.
    - Update RT statistics for the module.
    - Remove the administered item from items_remaining.
    - Check global stopping rules.
    - If stopping: compute global risk and return no next item.
    - Else: choose next module and next item.
    """
    # 1) Update time
    now = response_timestamp or datetime.utcnow()
    rt_fatigue.update_session_time(session, now)

    module_stats = session.modules[module_id]

    # 2) Bayesian update
    bayes.update_module_stats_for_item(
        module_stats=module_stats,
        module_id=module_id,
        item_difficulty=item.difficulty,
        is_correct=is_correct,
    )

    # 3) RT stats update
    rt_fatigue.update_module_rt_stats(
        module_stats=module_stats,
        rt_seconds=rt_seconds,
        max_time_seconds=item.max_time_seconds,
        is_correct=is_correct,
    )

    # 4) Remove item from remaining list
    if item.id in module_stats.items_remaining:
        module_stats.items_remaining.remove(item.id)

    # 5) Check global stopping rules
    should_stop = stopping.should_stop_globally(session, item_pool=item_pool)

    if should_stop:
        session.stopped = True
        global_risk = risk.compute_global_risk(session)
        return ProcessResponseResult(
            session=session,
            should_stop=True,
            next_item=None,
            global_risk=global_risk,
        )

    # 6) Choose next module and item
    next_module_id = choose_next_module(session)
    if next_module_id is None:
        # Edge case: no modules available but stopping rules did not trigger
        session.stopped = True
        global_risk = risk.compute_global_risk(session)
        return ProcessResponseResult(
            session=session,
            should_stop=True,
            next_item=None,
            global_risk=global_risk,
        )

    next_item = select_next_item_for_module(
        session=session,
        module_id=next_module_id,
        item_pool=item_pool,
    )

    if next_item is None:
        # No item with sufficient information gain; treat as stop.
        session.stopped = True
        global_risk = risk.compute_global_risk(session)
        return ProcessResponseResult(
            session=session,
            should_stop=True,
            next_item=None,
            global_risk=global_risk,
        )

    # Continue with next item
    return ProcessResponseResult(
        session=session,
        should_stop=False,
        next_item=next_item,
        global_risk=None,
    )

# app/ef_ads/engine.py (append)

@dataclass
class StartTestResult:
    session: SessionState
    first_item: Optional[CandidateItem]


def start_new_test(
    test_id: int,
    module_item_ids: Dict[str, list[int]],
    item_pool: Dict[int, CandidateItem],
    started_at: Optional[datetime] = None,
) -> StartTestResult:
    """
    Initialise a new session and select the first item to administer.

    The first module is chosen using choose_next_module (starting at index 0),
    and the first item is selected using entropy-based item selection.
    """
    session = initialise_session(
        test_id=test_id,
        module_item_ids=module_item_ids,
        started_at=started_at,
    )

    # Set current_module_index to 0 initially
    session.current_module_index = 0

    first_module_id = choose_next_module(session)
    if first_module_id is None:
        return StartTestResult(session=session, first_item=None)

    first_item = select_next_item_for_module(
        session=session,
        module_id=first_module_id,
        item_pool=item_pool,
    )

    return StartTestResult(session=session, first_item=first_item)

# app/ef_ads/engine.py (append)

# def continue_test(
#     session: SessionState,
#     item_pool: Dict[int, CandidateItem],
# ) -> StartTestResult:
#     """
#     Given a non-stopped session, select the next item to administer.

#     This is used when the test is continued after a pause or after a module
#     has just been completed.
#     """
#     # Ensure session is not marked as stopped
#     session.stopped = False

#     next_module_id = choose_next_module(session)
#     if next_module_id is None:
#         # No unsettled modules left; treat as stopped.
#         session.stopped = True
#         return StartTestResult(session=session, first_item=None)

#     next_item = select_next_item_for_module(
#         session=session,
#         module_id=next_module_id,
#         item_pool=item_pool,
#     )

#     if next_item is None:
#         # No item with sufficient information gain; treat as stopped.
#         session.stopped = True
#         return StartTestResult(session=session, first_item=None)

#     return StartTestResult(session=session, first_item=next_item)
