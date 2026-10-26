"""Explainable financial resilience score, not a credit score or regulated rating."""
from __future__ import annotations
from core.models import PlanContext, SimResult, ScoreCard
from core.networth import usable_funds

def resilience_score(ctx: PlanContext, res: SimResult) -> ScoreCard:
    hard_p=float(res.extra.get("hard_goal_success_probability",1.0))
    floor_safe=1.0-float(res.emergency_breach_probability)
    essentials=max(1.0,float(ctx.profile.essential_monthly_spend))
    funds=usable_funds(ctx.assets,ctx.profile.as_of,0,allow_penalty=False).available
    runway=max(0.0,funds/essentials)
    runway_component=min(1.0,runway/6.0)
    raw=100*(.60*hard_p+.25*floor_safe+.15*runway_component)
    score=max(0,min(100,int(round(raw))))
    grade="Strong" if score>=80 else "Solid" if score>=60 else "Fragile" if score>=40 else "At risk"
    components={"hard_goals":100*.60*hard_p,"emergency_floor":100*.25*floor_safe,"liquid_runway":100*.15*runway_component}
    return ScoreCard(score,grade,hard_p,floor_safe,runway,components,"Explainable heuristic; not a credit score, regulated rating or guarantee.")
