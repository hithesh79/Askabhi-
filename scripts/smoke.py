"""Headless pipeline smoke test for both synthetic personas.

Run from the project root: python scripts/smoke.py
This checks local mechanics only; synthetic data does not validate real-world accuracy.
"""
from __future__ import annotations
from datetime import date
from time import perf_counter
from pathlib import Path
import sys
import numpy as np

# Allow the documented command to work from the repository root and from IDEs.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import CFG
from core.behaviour import analyse
from core.classify import classify
from core.data_gen import generate_all, generate_csvs
from core.models import PlanContext, ScenarioParams
from core.reconcile import reconcile
from core.rng import make_draws
from core.simulate import simulate


def build_context(bundle):
    tx = classify(bundle.transactions)
    tx, _ = reconcile(tx)
    behaviour = analyse(tx, bundle.profile.as_of, bundle.profile)
    return PlanContext(bundle.profile, bundle.assets, bundle.liabilities,
                       bundle.goals, behaviour, CFG, tx, bundle.name)


def main() -> int:
    anchor = date(2026, 10, 25)
    generate_csvs(ROOT / "data", anchor, CFG.default_seed)
    personas = generate_all(anchor, CFG.default_seed)
    draws = make_draws(CFG.default_seed, 100, CFG.max_horizon_months)
    start = perf_counter()
    for name, bundle in personas.items():
        ctx = build_context(bundle)
        result = simulate(ctx, ScenarioParams(), draws)
        probabilities = list(result.goal_probabilities.values())
        assert all(np.isfinite(p) and 0 <= p <= 1 for p in probabilities)
        for series in (result.net_worth_p10, result.net_worth_p25,
                       result.net_worth_p50, result.net_worth_p75,
                       result.net_worth_p90):
            assert np.all(np.isfinite(series))
        assert np.all(result.net_worth_p10 <= result.net_worth_p25 + 1e-8)
        assert np.all(result.net_worth_p25 <= result.net_worth_p50 + 1e-8)
        assert np.all(result.net_worth_p50 <= result.net_worth_p75 + 1e-8)
        assert np.all(result.net_worth_p75 <= result.net_worth_p90 + 1e-8)
        assert result.draws_fingerprint == draws.fingerprint()
        print(f"{name}: {len(bundle.transactions)} synthetic transactions; "
              f"{len(bundle.goals)} goals; confidence={ctx.behaviour.confidence}; "
              f"goals={result.goal_probabilities}")
    elapsed = perf_counter() - start
    print(f"SMOKE OK · deterministic local pipeline · {elapsed:.2f}s · "
          "synthetic mechanics only, not real-world validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
