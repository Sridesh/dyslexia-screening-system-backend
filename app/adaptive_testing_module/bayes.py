# app/ef_ads/bayes.py

"""
Bayesian ability estimation for EF-ADS.

- Maintains posterior over a discrete theta grid per module.
- Uses a 2PL-like item response model:
    P(correct | theta, a, b) = 1 / (1 + exp(-a * (theta - b))).
- Updates posterior after each item response.
- Derives weak/strong probabilities and entropy from the posterior.
"""

from __future__ import annotations
from math import exp, log2
from typing import List, Dict

from . import config

from .state import ModuleStats

# app/ef_ads/bayes.py (append)

def prob_correct(theta: float, a: float, b: float, c: float = 0.0, d: float = 0.0) -> float:
    """
    4PL item response function.

    Parameters
    ----------
    theta : latent ability
    a     : discrimination parameter
    b     : item difficulty parameter
    c     : pseudo-guessing parameter (lower asymptote)
    d     : slipping parameter (1 - upper asymptote)

    Returns
    -------
    Probability of a correct response in [0, 1].
    """
    # Avoid overflow in exp by clamping the exponent
    exponent = -a * (theta - b)
    if exponent > 500:
        p_2pl = 0.0
    elif exponent < -500:
        p_2pl = 1.0
    else:
        p_2pl = 1.0 / (1.0 + exp(exponent))
        
    # Apply 4PL transformation: P = c + (1 - c - d) * P_2PL
    return c + (1.0 - c - d) * p_2pl

# app/ef_ads/bayes.py (append)

def update_theta_posterior_for_item(
    theta_posterior: List[float],
    module_id: str,
    item_difficulty: float,
    item_discrimination: float,
    is_correct: bool,
    total_time_seconds: float = 0.0,
) -> List[float]:
    """
    Update the posterior over theta for a single item response in a given module.

    Parameters
    ----------
    theta_posterior : current posterior over config.THETA_GRID
    module_id       : module identifier (e.g. "phonemic_awareness")
    item_difficulty : item difficulty parameter b_j
    is_correct      : True if response correct, False otherwise

    Returns
    -------
    new_theta_posterior : updated, normalised posterior
    """
    a = item_discrimination
    c = config.ITEM_GUESSING.get(module_id, 0.0)
    d_base = config.ITEM_SLIPPING.get(module_id, 0.0)
    from . import rt_fatigue
    slip_penalty = rt_fatigue.compute_fatigue_slip_penalty(total_time_seconds)
    d = min(1.0, d_base + slip_penalty)
    theta_grid = config.THETA_GRID

    new_posterior: List[float] = []
    total = 0.0

    # Compute unnormalised posterior
    for p_prior, theta in zip(theta_posterior, theta_grid):
        p_c = prob_correct(theta, a, item_difficulty, c, d)
        likelihood = p_c if is_correct else (1.0 - p_c)
        posterior_val = p_prior * likelihood
        new_posterior.append(posterior_val)
        total += posterior_val

    # Handle edge case: total ~ 0 (e.g. numerical underflow)
    if total <= 0.0:
        # Fall back to uniform prior to avoid degenerate state
        num = len(theta_grid)
        return [1.0 / num] * num

    # Normalise
    new_posterior = [p / total for p in new_posterior]
    return new_posterior

# app/ef_ads/bayes.py (append)

def derive_weak_strong_probs(theta_posterior: List[float]) -> Dict[str, float]:
    """
    Derive weak/strong probabilities from a theta posterior by thresholding.

    Returns
    -------
    {
        "p_weak": float,
        "p_strong": float,
    }
    """
    threshold = config.THETA_WEAK_THRESHOLD
    theta_grid = config.THETA_GRID

    p_weak = 0.0
    p_strong = 0.0

    for theta, p in zip(theta_grid, theta_posterior):
        if theta < threshold:
            p_weak += p
        else:
            p_strong += p

    # Normalisation safety (should already sum to 1.0)
    total = p_weak + p_strong
    if total > 0:
        p_weak /= total
        p_strong /= total
    else:
        # Fallback to 0.5 / 0.5 in extreme edge case
        p_weak = 0.5
        p_strong = 0.5

    return {"p_weak": p_weak, "p_strong": p_strong}

# app/ef_ads/bayes.py (append)

def entropy_weak_strong(p_weak: float, p_strong: float) -> float:
    """
    Compute Shannon entropy (base 2) for the weak/strong distribution.

    Parameters
    ----------
    p_weak, p_strong : probabilities that should sum to 1 (approx.)

    Returns
    -------
    Entropy in bits, between 0 and 1.
    """
    # Clamp probabilities to avoid log(0)
    eps = 1e-12
    p_w = max(min(p_weak, 1.0), 0.0)
    p_s = max(min(p_strong, 1.0), 0.0)

    total = p_w + p_s
    if total <= 0.0:
        return 1.0  # maximum uncertainty fallback

    p_w /= total
    p_s /= total

    entropy = 0.0
    if p_w > eps:
        entropy -= p_w * log2(p_w)
    if p_s > eps:
        entropy -= p_s * log2(p_s)

    return entropy

# app/ef_ads/bayes.py (append)

def update_module_stats_for_item(
    module_stats: ModuleStats,
    module_id: str,
    item_difficulty: float,
    item_discrimination: float,
    is_correct: bool,
    total_time_seconds: float = 0.0,
) -> None:
    """
    In-place update of ModuleStats for a single item response in a module.

    Steps:
    - Update theta posterior via 2PL-like model.
    - Derive weak/strong probabilities.
    - Update entropy.
    - Increment num_items and correct count.
    """
    # Update theta posterior
    new_posterior = update_theta_posterior_for_item(
        module_stats.theta_posterior,
        module_id=module_id,
        item_difficulty=item_difficulty,
        item_discrimination=item_discrimination,
        is_correct=is_correct,
        total_time_seconds=total_time_seconds,
    )
    module_stats.theta_posterior = new_posterior

    # Derive weak/strong probabilities
    ws = derive_weak_strong_probs(new_posterior)
    module_stats.p_weak = ws["p_weak"]
    module_stats.p_strong = ws["p_strong"]

    # Compute entropy
    module_stats.entropy = entropy_weak_strong(
        module_stats.p_weak,
        module_stats.p_strong,
    )

    # Update counts
    module_stats.num_items += 1
    if is_correct:
        module_stats.correct += 1
