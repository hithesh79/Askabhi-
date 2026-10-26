"""Compare stated, observed-behaviour and repaired financial futures."""
from __future__ import annotations
import numpy as np
from core.models import PlanContext, Draws, ScenarioParams, Futures, Snapshot
from core.simulate import simulate
from core.repair import repair_plan

def three_futures(ctx: PlanContext, draws: Draws) -> Futures:
    actual=simulate(ctx,ScenarioParams(),draws)
    stated=max(0,ctx.profile.stated_monthly_saving or (ctx.profile.monthly_income_net*.2))
    observed=ctx.behaviour.actual_median_saving if ctx.behaviour else ctx.profile.monthly_income_net*.1
    stated_res=simulate(ctx,ScenarioParams(extra_monthly_saving=max(-ctx.profile.monthly_income_net*.5,stated-observed)),draws)
    repair_amount=max(0,(ctx.profile.stated_monthly_saving or ctx.profile.monthly_income_net*.25)-observed)
    repaired_res=simulate(ctx,ScenarioParams(extra_monthly_saving=repair_amount),draws)
    return Futures(actual.months,stated_res.net_worth_p10,stated_res.net_worth_p50,stated_res.net_worth_p90,actual.net_worth_p10,actual.net_worth_p50,actual.net_worth_p90,repaired_res.net_worth_p10,repaired_res.net_worth_p50,repaired_res.net_worth_p90,{"stated":stated_res.goal_probabilities,"behaviour":actual.goal_probabilities,"repaired":repaired_res.goal_probabilities},draws.fingerprint())

def at_month(futures: Futures, m: int) -> Snapshot:
    idx=max(0,min(len(futures.months)-1,int(m)))
    values={"stated":{"p10":float(futures.stated_networth_p10[idx]),"p50":float(futures.stated_networth_p50[idx]),"p90":float(futures.stated_networth_p90[idx])},"behaviour":{"p10":float(futures.behaviour_networth_p10[idx]),"p50":float(futures.behaviour_networth_p50[idx]),"p90":float(futures.behaviour_networth_p90[idx])},"repaired":{"p10":float(futures.repaired_networth_p10[idx]),"p50":float(futures.repaired_networth_p50[idx]),"p90":float(futures.repaired_networth_p90[idx])}}
    funded={k:dict(v) for k,v in futures.goal_probabilities.items()}
    return Snapshot(futures.months[idx],values,funded)
