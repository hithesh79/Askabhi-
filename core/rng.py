"""Reproducible common random numbers for comparable financial scenarios."""
from __future__ import annotations
import numpy as np
from core.models import Draws

def make_draws(seed: int, n_sims: int, n_months: int) -> Draws:
    """Create all random arrays from one seeded Generator for paired comparisons."""
    if n_sims < 1 or n_months < 1:
        raise ValueError("n_sims and n_months must be positive")
    rng = np.random.default_rng(int(seed))
    shape = (int(n_sims), int(n_months))
    return Draws(rng.standard_normal(shape), rng.standard_normal(shape), rng.standard_normal(shape), rng.random(shape), rng.random(shape), rng.standard_normal(shape), int(seed), int(n_sims), int(n_months))
