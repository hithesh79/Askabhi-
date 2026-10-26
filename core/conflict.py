"""Goal conflict map via same-draw leave-one-out simulations and regret accounting."""
from __future__ import annotations
from copy import deepcopy
import pandas as pd
from core.models import PlanContext, Draws, Regret, ScenarioParams
from core.simulate import simulate

def conflict_matrix(ctx: PlanContext, draws: Draws) -> pd.DataFrame:
    full=simulate(ctx,ScenarioParams(),draws); goals=list(ctx.goals); ids=[g.goal_id for g in goals]
    matrix=pd.DataFrame(0.0,index=ids,columns=ids)
    for a in goals:
        reduced=deepcopy(ctx); reduced.goals=[g for g in reduced.goals if g.goal_id!=a.goal_id]
        loo=simulate(reduced,ScenarioParams(),draws)
        for b in goals:
            if a.goal_id==b.goal_id: matrix.loc[a.goal_id,b.goal_id]=0.0
            else: matrix.loc[a.goal_id,b.goal_id]=max(0.0,full.goal_probabilities.get(b.goal_id,0)-loo.goal_probabilities.get(b.goal_id,0))
    matrix.index=[next(g.name for g in goals if g.goal_id==i) for i in ids]
    matrix.columns=[next(g.name for g in goals if g.goal_id==i) for i in ids]
    return matrix

def regret(change, ctx: PlanContext, draws: Draws) -> Regret:
    delay=max(0,float(change.get("delay_months",0))); goal_id=change.get("goal_id")
    priority=next((g.priority for g in ctx.goals if g.goal_id==goal_id),2)
    weight={1:1.0,2:.75,3:.5}.get(priority,.75)
    delay_cost=delay*weight; lifestyle=max(0,float(change.get("lifestyle_cut_rupees",0))); penalty=max(0,float(change.get("penalty_cost",0)))
    total=delay_cost+lifestyle+penalty
    parts={"delay_priority_months":delay_cost,"lifestyle_cut_rupees":lifestyle,"penalty_cost_rupees":penalty}
    return Regret(total,parts,f"Regret combines {delay:g} months of delay weighted by goal priority, ₹{lifestyle:,.0f} of lifestyle cuts and ₹{penalty:,.0f} in penalty costs. It is a transparent heuristic, not a universal utility measure.")
