"""Same-draw sensitivity tornado for assumptions that may change plan feasibility."""
from __future__ import annotations
from copy import deepcopy
import pandas as pd
from config import CFG
from core.models import PlanContext, Draws, ScenarioParams
from core.simulate import simulate

def tornado(ctx: PlanContext, draws: Draws, goal_id: str) -> pd.DataFrame:
    base=simulate(ctx,ScenarioParams(),draws).goal_probabilities.get(goal_id,0.0); rows=[]
    def add(name, lowctx=None, lowp=None, lowparams=None, highctx=None, highp=None, highparams=None):
        lp=simulate(lowctx or deepcopy(ctx),lowparams or ScenarioParams(),draws).goal_probabilities.get(goal_id,0.0) if lowp is None else lowp
        hp=simulate(highctx or deepcopy(ctx),highparams or ScenarioParams(),draws).goal_probabilities.get(goal_id,0.0) if highp is None else highp
        rows.append({"assumption":name,"base_probability":base,"low_probability":lp,"high_probability":hp,"low_effect_pp":(lp-base)*100,"high_effect_pp":(hp-base)*100,"max_abs_effect_pp":max(abs(lp-base),abs(hp-base))*100})
    # explicit pairs, no dynamic execution
    lo=deepcopy(ctx); lo.profile.monthly_income_net*=.9
    hi=deepcopy(ctx); hi.profile.monthly_income_net*=1.1
    add("Income ±10%",lo,highctx=hi)
    add("Expenses ±10%",lowparams=ScenarioParams(expense_cut_pct=0.10),highparams=ScenarioParams(extra_monthly_expense=max(1,ctx.profile.monthly_income_net*.10)))
    add("Inflation ±2 points",lowparams=ScenarioParams(inflation_add=-.02),highparams=ScenarioParams(inflation_add=.02))
    lo=deepcopy(ctx); hi=deepcopy(ctx)
    for a in lo.assets:
        if a.asset_class=="equity": a.exp_return-=.03
    for a in hi.assets:
        if a.asset_class=="equity": a.exp_return+=.03
    add("Equity expected return ±3 points",lo,highctx=hi)
    lo=deepcopy(ctx); hi=deepcopy(ctx); lo.profile.job_loss_prob_annual*=.5; hi.profile.job_loss_prob_annual=min(.99,hi.profile.job_loss_prob_annual*2)
    add("Job-loss probability ×0.5 / ×2",lo,highctx=hi)
    goal=next((g for g in ctx.goals if g.goal_id==goal_id),None)
    if goal:
        lo=deepcopy(ctx); hi=deepcopy(ctx)
        next(g for g in lo.goals if g.goal_id==goal_id).target_amount_today*=.9
        next(g for g in hi.goals if g.goal_id==goal_id).target_amount_today*=1.1
        add("Goal amount ±10%",lo,highctx=hi)
        import calendar
        def shift(d,m):
            i=d.year*12+d.month-1+m; y,m0=divmod(i,12); mo=m0+1; return type(d)(y,mo,min(d.day,calendar.monthrange(y,mo)[1]))
        lo=deepcopy(ctx); hi=deepcopy(ctx)
        next(g for g in lo.goals if g.goal_id==goal_id).target_date=shift(goal.target_date,-6)
        next(g for g in hi.goals if g.goal_id==goal_id).target_date=shift(goal.target_date,6)
        add("Goal date ±6 months",lo,highctx=hi)
    return pd.DataFrame(rows).sort_values("max_abs_effect_pp",ascending=False).reset_index(drop=True)
