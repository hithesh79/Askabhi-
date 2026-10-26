"""Greedy repair search; no selected change may reduce target probability."""
from __future__ import annotations
from copy import deepcopy
from datetime import date
from config import CFG
from core.models import PlanContext, Draws, ScenarioParams, RepairResult
from core.simulate import simulate

def _goal_prob(res, target):
    if target in (None,"all","whole plan","my whole plan"): return float(res.extra.get("hard_goal_success_probability",0.0))
    return float(res.goal_probabilities.get(target,0.0))

def _target_clone(ctx, goal_id, change):
    c=deepcopy(ctx); c.goals=[g for g in c.goals if g.goal_id!=goal_id]+[g for g in c.goals if g.goal_id==goal_id]
    for g in c.goals:
        if g.goal_id==goal_id:
            for k,v in change.items(): setattr(g,k,v)
    return c

def repair_plan(ctx: PlanContext, draws: Draws, target_prob: float=0.85, scenario: ScenarioParams | None=None) -> RepairResult:
    scenario=scenario or ScenarioParams(); before=simulate(ctx,scenario,draws); target_id=min(ctx.goals,key=lambda g:(g.priority,g.target_date)).goal_id if ctx.goals else "all"
    p_before=_goal_prob(before,target_id); current_ctx=deepcopy(ctx); current_params=deepcopy(scenario); current=before; repairs=[]; total_pain=0.0
    for _ in range(CFG.repair_max_steps):
        p_current=_goal_prob(current,target_id)
        if p_current>=target_prob: break
        candidates=[]
        # Add savings using same draws.
        for amount in CFG.repair_extra_saving_candidates_inr:
            pp=deepcopy(current_params); pp.extra_monthly_saving+=amount
            res=simulate(current_ctx,pp,draws); gain=_goal_prob(res,target_id)-p_current
            if gain>CFG.repair_minimum_probability_gain: candidates.append((gain/max(1,amount*CFG.repair_lifestyle_cut_pain_per_inr),gain,amount,"Increase monthly saving",current_ctx,pp,res,amount))
        # Delay target goal.
        goal=next((g for g in current_ctx.goals if g.goal_id==target_id),None)
        if goal:
            for months in CFG.repair_delay_candidates_months:
                newdate=_add_months(goal.target_date,months); cc=_target_clone(current_ctx,target_id,{"target_date":newdate})
                res=simulate(cc,current_params,draws); gain=_goal_prob(res,target_id)-p_current; pain=months*max(.5,4-goal.priority)
                if gain>CFG.repair_minimum_probability_gain: candidates.append((gain/max(1,pain),gain,months,"Delay goal",cc,current_params,res,pain))
        # Discretionary spending cut.
        for cut in CFG.repair_discretionary_cut_candidates_pct:
            pp=deepcopy(current_params); pp.expense_cut_pct=min(.8,pp.expense_cut_pct+cut)
            res=simulate(current_ctx,pp,draws); gain=_goal_prob(res,target_id)-p_current; pain=cut*max(1,ctx.profile.monthly_income_net)
            if gain>CFG.repair_minimum_probability_gain: candidates.append((gain/max(1,pain),gain,cut,"Reduce discretionary spending",current_ctx,pp,res,pain))
        if not candidates: break
        candidates.sort(key=lambda x:(-x[0],-x[1])); _,gain,amount,label,next_ctx,next_params,next_res,pain=candidates[0]
        if _goal_prob(next_res,target_id)<p_current-1e-12: continue
        repairs.append({"action":label,"amount":amount,"probability_before":p_current,"probability_after":_goal_prob(next_res,target_id),"gain":gain,"pain":pain,"description":f"{label}: {amount:g}"})
        current_ctx=next_ctx; current_params=next_params; current=next_res; total_pain+=pain
    p_after=_goal_prob(current,target_id)
    before_all=before.goal_probabilities; after_all=current.goal_probabilities
    alternatives=[{"name":"Least lifestyle pain","actions":[r for r in repairs if r["action"]!="Reduce discretionary spending"]},{"name":"Least delay","actions":[r for r in repairs if r["action"]!="Delay goal"]},{"name":"Least rupee cost","actions":sorted(repairs,key=lambda r:r["pain"])}]
    return RepairResult(repairs,total_pain,p_before,p_after,before_all,after_all,draws.fingerprint(),draws.fingerprint(),p_after>=target_prob,alternatives)

def _add_months(d: date, m: int) -> date:
    import calendar
    i=d.year*12+d.month-1+m; y,m0=divmod(i,12); mo=m0+1
    return date(y,mo,min(d.day,calendar.monthrange(y,mo)[1]))
