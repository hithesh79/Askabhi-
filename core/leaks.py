"""Rupee-to-Days Leak Detector: translate spend choices into goal timing."""
from __future__ import annotations
from copy import deepcopy
import numpy as np
from core.models import PlanContext, Draws, ScenarioParams, Leak
from core.simulate import simulate

def _time_stat(res,goal_id):
    arr=res.time_to_goal.get(goal_id,np.array([np.inf])); finite=arr[np.isfinite(arr)]
    return float(np.median(finite)) if finite.size else float("inf")

def rupee_to_days(ctx, goal_id: str, draws: Draws, extra_monthly: float=1000.0) -> float:
    """Approximate median days gained by allocating an extra monthly amount to saving."""
    base=simulate(ctx,ScenarioParams(),draws); after=simulate(ctx,ScenarioParams(extra_monthly_saving=max(0,extra_monthly)),draws)
    b=_time_stat(base,goal_id); a=_time_stat(after,goal_id)
    if not np.isfinite(b): return max(0.0,(draws.n_months*30.4375) if np.isfinite(a) else 0.0)
    return max(0.0,(b-a)*30.4375) if np.isfinite(a) else 0.0

def find_leaks(ctx, draws, focus_goal_id) -> list[Leak]:
    bp=ctx.behaviour
    if bp is None: return []
    base=simulate(ctx,ScenarioParams(),draws); basep=base.goal_probabilities.get(focus_goal_id,0)
    base_time=_time_stat(base,focus_goal_id); leaks=[]
    for cat,monthly in bp.category_monthly_mean.items():
        if bp.category_nature.get(cat)!="discretionary" or monthly<=0: continue
        c=deepcopy(ctx); c.behaviour.category_monthly_mean[cat]=monthly*.8
        after=simulate(c,ScenarioParams(),draws); ap=after.goal_probabilities.get(focus_goal_id,0); at=_time_stat(after,focus_goal_id)
        sooner=max(0,(base_time-at)) if np.isfinite(base_time) and np.isfinite(at) else 0.0
        leaks.append(Leak(cat,monthly,basep,ap,ap-basep,sooner*30.4375,bp.lifestyle_creep_slope if "discretionary" in cat.lower() else 0,f"A 20% reduction would release about ₹{monthly*.2:,.0f}/month under the model."))
    return sorted(leaks,key=lambda x:(-x.probability_change,-x.monthly_spend))
