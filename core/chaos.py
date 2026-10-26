"""Reverse stress testing: search bounded shock scenarios and report uncertainty."""
from __future__ import annotations
from copy import deepcopy
from datetime import date
import numpy as np
import pandas as pd
from config import CFG
from core.models import PlanContext, Draws, ScenarioParams, BreakScenario
from core.simulate import simulate, deterministic_projection

def _is_broken(ctx,params,target):
    proj=deterministic_projection(ctx,params)
    matrix=proj.path.get("success_matrix")
    if matrix is None or matrix.size==0: return False,0.0
    if target in (None,"all","whole plan","my whole plan"):
        hard=[i for i,g in enumerate(list(ctx.goals)+params.extra_goals) if g.hard]
        failed=not bool(matrix[:,hard].all()) if hard else False
        p=float(matrix[:,hard].all(axis=1).mean()) if hard else 1.0
    else:
        idx=next((i for i,g in enumerate(list(ctx.goals)+params.extra_goals) if g.goal_id==target or g.name==target),None)
        if idx is None: return False,0.0
        p=float(matrix[:,idx].mean()); failed=p<1.0
    return failed,p

def _cost(params):
    c=0.0
    c+=(params.job_loss_months/max(1,CFG.chaos_job_loss_cost_scale_months))**2
    c+=(params.income_cut_pct/max(.01,CFG.chaos_income_cut_cost_scale_pct))**2
    med=sum(a for _,a in params.one_off_expenses)
    c+=(med/max(1,CFG.chaos_medical_cost_scale_inr))**2
    c+=(params.market_shock_pct/max(.01,CFG.chaos_market_drop_cost_scale_pct))**2
    c+=(params.extra_monthly_expense/max(1,CFG.chaos_support_cost_scale_pct*100000))**2
    c+=(params.inflation_add/max(.001,CFG.chaos_inflation_spike_cost_scale))**2
    return float(c)

def find_breaks(ctx: PlanContext, draws: Draws, target: str | None) -> list[BreakScenario]:
    """Try a bounded deterministic grid; returned scenarios are confirmed with the full simulator."""
    nmonths=max(1,len(draws.monthly) if hasattr(draws,"monthly") else draws.n_months)
    candidates=[]
    for onset in range(0,min(36,nmonths),CFG.chaos_onset_step_months):
        for jm in (3,6,9):
            candidates.append(("job loss",onset,ScenarioParams(job_loss_months=jm,job_loss_start=onset)))
        for cut in (.2,.3,.4):
            candidates.append(("income reduction",onset,ScenarioParams(income_cut_pct=cut,income_cut_start=onset,income_cut_months=12)))
        for medical in (150000.0,300000.0,500000.0,1000000.0):
            candidates.append(("medical expense",onset,ScenarioParams(one_off_expenses=[(onset,medical)])))
        for market in (.2,.3,.5):
            candidates.append(("market decline",onset,ScenarioParams(market_shock_pct=market,market_shock_month=onset)))
    # Keep only breaking scenarios, selecting lowest heuristic cost and distinct dominant shocks.
    found=[]
    for name,onset,params in candidates:
        broken,det_p=_is_broken(ctx,params,target)
        if not broken: continue
        cost=_cost(params)
        prob=simulate(ctx,params,draws)
        if target in (None,"all","whole plan","my whole plan"):
            p=float(prob.extra.get("hard_goal_success_probability",1-prob.emergency_breach_probability))
        else: p=float(prob.goal_probabilities.get(target,0.0))
        date_idx=min(max(onset,0),len(prob.months)-1); d=prob.months[date_idx]
        plaus="Likely" if cost<=CFG.chaos_likely_cost_max else "Possible" if cost<=CFG.chaos_possible_cost_max else "Remote"
        if name=="job loss": sentence=f"A {params.job_loss_months}-month job loss starting {d:%b %Y} breaks the selected plan in the deterministic test."
        elif name=="income reduction": sentence=f"A {params.income_cut_pct:.0%} income reduction for 12 months starting {d:%b %Y} breaks the selected plan."
        elif name=="medical expense": sentence=f"A ₹{params.one_off_expenses[0][1]:,.0f} unexpected medical expense in {d:%b %Y} breaks the selected plan."
        else: sentence=f"A {params.market_shock_pct:.0%} market decline in {d:%b %Y} breaks the selected plan."
        found.append(BreakScenario(name,sentence,onset,cost,plaus,params,p))
    found.sort(key=lambda b:b.cost)
    distinct=[]; seen=set()
    for b in found:
        if b.name not in seen: distinct.append(b); seen.add(b.name)
        if len(distinct)>=CFG.chaos_max_scenarios: break
    return distinct

def stress_report(ctx: PlanContext, draws: Draws) -> pd.DataFrame:
    scenarios=[
        ("6-month job loss",ScenarioParams(job_loss_months=6,job_loss_start=0)),
        ("₹5 lakh medical expense",ScenarioParams(one_off_expenses=[(0,500000.0)])),
        ("30% income cut for a year",ScenarioParams(income_cut_pct=.30,income_cut_start=0,income_cut_months=12)),
        ("30% market decline",ScenarioParams(market_shock_pct=.30,market_shock_month=0)),
        ("20% expense rise",ScenarioParams(extra_monthly_expense=max(1,ctx.profile.monthly_income_net*.20),extra_monthly_start=0)),
        ("Combined shocks at half strength",ScenarioParams(job_loss_months=3,job_loss_start=0,one_off_expenses=[(0,250000.0)],income_cut_pct=.15,income_cut_start=0,income_cut_months=12,market_shock_pct=.15,market_shock_month=0,extra_monthly_expense=max(1,ctx.profile.monthly_income_net*.10))),
    ]
    rows=[]
    for name,p in scenarios:
        r=simulate(ctx,p,draws)
        rows.append({"scenario":name,"hard_goal_success_probability":r.extra.get("hard_goal_success_probability",0),"emergency_breach_probability":r.emergency_breach_probability,"expected_shortfall_months":r.expected_shortfall_months,"fingerprint":draws.fingerprint()})
    return pd.DataFrame(rows)
