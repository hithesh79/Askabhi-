"""Payday allocation and safe-to-spend calculations."""
from __future__ import annotations
from datetime import date
import calendar
import pandas as pd
from config import CFG
from core.models import PlanContext, Draws, PaydayPlan, SafeToSpend
from core.networth import emi
from core.leaks import rupee_to_days

def payday_plan(ctx: PlanContext, draws: Draws, today: date) -> PaydayPlan:
    salary=max(0,ctx.behaviour.safe_income if ctx.behaviour and ctx.behaviour.safe_income else ctx.profile.monthly_income_net)
    bp=ctx.behaviour
    monthly_categories=bp.category_monthly_mean if bp else {}
    nature=bp.category_nature if bp else {}
    essentials=sum(v for k,v in monthly_categories.items() if nature.get(k) in ("essential","fixed")) or ctx.profile.essential_monthly_spend
    discretionary=sum(v for k,v in monthly_categories.items() if nature.get(k)=="discretionary")
    obligations=sum(l.emi for l in ctx.liabilities)
    current_liquid=sum(a.value for a in ctx.assets if a.liquidity=="liquid")
    floor=ctx.profile.emergency_months*ctx.profile.essential_monthly_spend
    topup=max(0,floor-current_liquid)
    available=max(0,salary-obligations-essentials)
    emergency=min(available,topup); available-=emergency
    ordered=sorted(ctx.goals,key=lambda g:(g.priority,g.target_date))
    needs={}
    for g in ordered:
        month=max(1,(g.target_date.year-today.year)*12+g.target_date.month-today.month)
        required=g.target_amount_today*(1+(g.inflation if g.inflation is not None else CFG.inflation_for(g.category)))**(month/12)
        needs[g.goal_id]=required/month
    total=sum(needs.values()); contributions={}; remaining=available
    for g in ordered:
        amount=min(remaining,needs[g.goal_id] if total<=remaining else (available*needs[g.goal_id]/total if total else 0))
        contributions[g.goal_id]=amount; remaining-=amount
    safe=max(0,remaining)
    days_left=max(1,calendar.monthrange(today.year,today.month)[1]-today.day+1)
    buckets={"Net income":salary,"Loan EMIs":obligations,"Essentials":essentials,"Emergency top-up":emergency,"Goal contributions":sum(contributions.values()),"Safe-to-spend allowance":safe}
    return PaydayPlan(salary,obligations,essentials,emergency,contributions,safe,days_left,buckets)

def safe_to_spend(ctx: PlanContext, plan: PaydayPlan, today: date, tx_this_month) -> SafeToSpend:
    if isinstance(tx_this_month,pd.DataFrame):
        tx=tx_this_month.copy()
        if "date" in tx:
            parsed=pd.to_datetime(tx["date"],errors="coerce")
            tx=tx.loc[parsed.notna() & (parsed.dt.month==today.month) & (parsed.dt.year==today.year)].copy()
        if "type" in tx: tx=tx[tx["type"].astype(str).str.lower().eq("debit")]
        if "exclude_from_spend" in tx: tx=tx[~tx["exclude_from_spend"].fillna(False).astype(bool)]
        if "kind" in tx: tx=tx[~tx["kind"].astype(str).isin(["transfer","investment","refund","potential_asset","loan"])]
        if "nature" in tx and tx["nature"].astype(str).eq("discretionary").any():
            tx=tx[tx["nature"].astype(str).eq("discretionary")]
        if "amount" in tx: spent=float(pd.to_numeric(tx["amount"],errors="coerce").fillna(0).clip(lower=0).sum())
        else: spent=0.0
    else: spent=max(0,float(tx_this_month or 0))
    remaining=max(0,plan.safe_allowance-spent); days=max(1,plan.days_left)
    planned_daily=plan.safe_allowance/days
    pace="On track" if spent<=planned_daily*max(0,calendar.monthrange(today.year,today.month)[1]-plan.days_left+1)*1.1 else "Over"
    if spent<planned_daily*max(0,calendar.monthrange(today.year,today.month)[1]-plan.days_left+1)*.8: pace="Ahead"
    impacts={g.goal_id:rupee_to_days(ctx,g.goal_id,make_small_draws(ctx),5000.0) for g in []}
    return SafeToSpend(remaining,days,remaining/days,pace,impacts)

def make_small_draws(ctx):
    from core.rng import make_draws
    return make_draws(CFG.default_seed,200,120)
