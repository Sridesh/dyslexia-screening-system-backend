# app/ef_ads/config.py

"""
Configuration and hyperparameters for the EF-ADS engine.

These are initial values suitable for development and research.
They can be tuned later based on simulations and supervisor feedback.
"""

from __future__ import annotations
from typing import Dict, List


# -------------------------------------------------
# Modules / domains in the adaptive screening
# -------------------------------------------------

# Canonical module identifiers
MODULES: List[str] = [
    "phonemic_awareness",
    "ran",
    "object_recognition",
]

# A human-readable name for reports (optional, useful later)
MODULE_LABELS: Dict[str, str] = {
    "phonemic_awareness": "Phonemic Awareness",
    "ran": "Rapid Automatized Naming (RAN)",
    "object_recognition": "Object Recognition",
}


# -------------------------------------------------
# Latent ability grid (theta) for Bayesian updates
# -------------------------------------------------
# We approximate each module's latent ability by a small discrete grid.
# This is richer than a binary weak/strong model but still computationally light.[web:516]

THETA_GRID: List[float] = [-2.0, -1.0, 0.0, 1.0, 2.0]

# Threshold in theta space to distinguish "weak" vs "strong"
# e.g., theta < 0 => weak, theta >= 0 => strong
THETA_WEAK_THRESHOLD: float = 0.0


# -------------------------------------------------
# Item response model (2PL-like, per module)
# -------------------------------------------------
# For now we use a fixed discrimination parameter per module.
# You can refine this later or even move to item-level a_j values.[web:516]

ITEM_DISCRIMINATION: Dict[str, float] = {
    "phonemic_awareness": 1.2,
    "ran": 1.0,
    "object_recognition": 1.0,
}

# Prior mean and variance for theta (for documentation purposes)
THETA_PRIOR_MEAN: float = 0.0
THETA_PRIOR_VAR: float = 1.0


# -------------------------------------------------
# Response time and fatigue
# -------------------------------------------------
# "Slow but accurate" if RT > SLOW_RT_FACTOR * item.max_time_seconds
SLOW_RT_FACTOR: float = 1.3

# Optional: "rapid guess" if RT < RAPID_GUESS_FRACTION * item.max_time_seconds
RAPID_GUESS_FRACTION: float = 0.25

# Fatigue function: fatigue_factor = max(MIN_FATIGUE_FACTOR, 1 - FATIGUE_SLOPE * minutes)
FATIGUE_SLOPE: float = 0.05   # rate of decay per minute
MIN_FATIGUE_FACTOR: float = 0.4  # lower bound on information scaling[web:366][web:513]


# -------------------------------------------------
# Stopping rules
# -------------------------------------------------

# Minimum items that must be administered in each module before we trust a classification
MIN_ITEMS_PER_MODULE: int = 4

# Hard caps (safety limits)
MAX_ITEMS_TOTAL: int = 25
MAX_TEST_TIME_MIN: float = 25.0

# Confidence and entropy thresholds for module settlement
P_CONFIDENT: float = 0.75       # min P(weak) or P(strong) to call it settled
ENTROPY_THRESHOLD: float = 0.6  # lower entropy => higher certainty[web:509][web:512]

# Minimum adjusted information gain; below this, items are considered not worth asking
MIN_INFO_GAIN: float = 0.01     # will be tuned later[web:509][web:515]


# -------------------------------------------------
# Global risk classification
# -------------------------------------------------

# Weighting of modules when aggregating into global risk (for future use)
MODULE_WEIGHTS: Dict[str, float] = {
    "phonemic_awareness": 0.45,
    "ran": 0.35,
    "object_recognition": 0.20,
}

# Risk thresholds on some abstract risk score (to be defined in risk.py)
RISK_SCORE_HIGH: float = 0.7
RISK_SCORE_MODERATE: float = 0.4


# -------------------------------------------------
# Debug / simulation toggles
# -------------------------------------------------

DEBUG_LOGGING: bool = False  # can be toggled to trace algorithm behaviour in logs
