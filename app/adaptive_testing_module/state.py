# app/ef_ads/state.py

"""
Session-level state for EF-ADS.

This represents the internal state of a single adaptive test session.
It is independent of HTTP and database details.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from . import config


@dataclass
class ModuleStats:
    """
    Per-module statistics and posterior state during a test session.
    """
    # Posterior over theta grid (same length as config.THETA_GRID)
    theta_posterior: List[float]

    # Derived weak/strong probabilities and entropy (computed from theta_posterior)
    p_weak: float = 0.5
    p_strong: float = 0.5
    entropy: float = 1.0

    # Item administration stats
    num_items: int = 0
    items_remaining: List[int] = field(default_factory=list)

    # Response time & engagement
    sum_rt: float = 0.0
    slow_correct: int = 0
    correct: int = 0
    rapid_guess: int = 0

    # Optional: last start time for module, to derive switch RTs
    last_started_at: Optional[datetime] = None


@dataclass
class SessionState:
    """
    EF-ADS session state for one test.
    """

    test_id: int

    # Time tracking
    started_at: datetime
    last_update_at: datetime
    total_time_seconds: float = 0.0

    # Global flow control
    round_number: int = 1
    current_module_index: int = 0
    stopped: bool = False

    # Mapping from module_id to ModuleStats
    modules: Dict[str, ModuleStats] = field(default_factory=dict)

    @classmethod
    def initialise(
        cls,
        test_id: int,
        *,
        started_at: Optional[datetime] = None,
        module_item_ids: Optional[Dict[str, List[int]]] = None,
    ) -> "SessionState":
        """
        Create a new SessionState for a test, with:
        - uniform prior over theta for each module
        - initial items_remaining lists based on module_item_ids
        """
        now = started_at or datetime.utcnow()

        modules: Dict[str, ModuleStats] = {}
        num_grid_points = len(config.THETA_GRID)
        uniform_posterior = [1.0 / num_grid_points] * num_grid_points

        for module_id in config.MODULES:
            items = (module_item_ids or {}).get(module_id, [])
            modules[module_id] = ModuleStats(
                theta_posterior=list(uniform_posterior),
                p_weak=0.5,
                p_strong=0.5,
                entropy=1.0,
                num_items=0,
                items_remaining=list(items),
                sum_rt=0.0,
                slow_correct=0,
                correct=0,
                rapid_guess=0,
                last_started_at=None,
            )

        return cls(
            test_id=test_id,
            started_at=now,
            last_update_at=now,
            total_time_seconds=0.0,
            round_number=1,
            current_module_index=0,
            stopped=False,
            modules=modules,
        )

    # ---- Snapshot helpers -------------------------------------------------

    def to_snapshot(self) -> Dict:
        """
        Convert the SessionState into a JSON-serialisable dict.
        This can be stored in the database for fast reconstruction.
        """
        # NOTE: This is only a skeleton; fields can be extended later.
        modules_snapshot: Dict[str, Dict] = {}
        for module_id, stats in self.modules.items():
            modules_snapshot[module_id] = {
                "theta_posterior": stats.theta_posterior,
                "p_weak": stats.p_weak,
                "p_strong": stats.p_strong,
                "entropy": stats.entropy,
                "num_items": stats.num_items,
                "items_remaining": stats.items_remaining,
                "sum_rt": stats.sum_rt,
                "slow_correct": stats.slow_correct,
                "correct": stats.correct,
                "rapid_guess": stats.rapid_guess,
                "last_started_at": (
                    stats.last_started_at.isoformat()
                    if stats.last_started_at
                    else None
                ),
            }

        return {
            "test_id": self.test_id,
            "started_at": self.started_at.isoformat(),
            "last_update_at": self.last_update_at.isoformat(),
            "total_time_seconds": self.total_time_seconds,
            "round_number": self.round_number,
            "current_module_index": self.current_module_index,
            "stopped": self.stopped,
            "modules": modules_snapshot,
        }

    @classmethod
    def from_snapshot(cls, snapshot: Dict) -> "SessionState":
        """
        Reconstruct a SessionState from a JSON-serialisable snapshot dict.
        """
        modules: Dict[str, ModuleStats] = {}
        for module_id, stats_dict in snapshot["modules"].items():
            last_started_at = (
                datetime.fromisoformat(stats_dict["last_started_at"])
                if stats_dict.get("last_started_at")
                else None
            )
            modules[module_id] = ModuleStats(
                theta_posterior=list(stats_dict["theta_posterior"]),
                p_weak=stats_dict["p_weak"],
                p_strong=stats_dict["p_strong"],
                entropy=stats_dict["entropy"],
                num_items=stats_dict["num_items"],
                items_remaining=list(stats_dict["items_remaining"]),
                sum_rt=stats_dict["sum_rt"],
                slow_correct=stats_dict["slow_correct"],
                correct=stats_dict["correct"],
                rapid_guess=stats_dict["rapid_guess"],
                last_started_at=last_started_at,
            )

        return cls(
            test_id=snapshot["test_id"],
            started_at=datetime.fromisoformat(snapshot["started_at"]),
            last_update_at=datetime.fromisoformat(snapshot["last_update_at"]),
            total_time_seconds=snapshot["total_time_seconds"],
            round_number=snapshot["round_number"],
            current_module_index=snapshot["current_module_index"],
            stopped=snapshot["stopped"],
            modules=modules,
        )
