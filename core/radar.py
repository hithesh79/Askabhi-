"""90-day cash-crunch radar with balance uncertainty and obligation pile-up detection."""
from __future__ import annotations
from datetime import date, timedelta
import numpy as np
import pandas as pd
from config import CFG
from core.models import PlanContext, Draws, RadarResult

def cash_radar(ctx: PlanContext, draws: Draws, today: date, days: int=90) -> RadarResult:
    days=max(1,min(365,int(days))); n=max(200,min(draws.n_sims,2000)); rng=np.random.default_rng(draws.seed+202)
    bp=ctx.behaviour; income=bp.safe_income if bp and bp.safe_income else ctx.profile.monthly_income_net
    monthly_spend=sum(bp.category_monthly_mean.values()) if bp and bp.category_monthly_mean else ctx.profile.essential_monthly_spend
    liquid=sum(max(0,a.value) for a in ctx.assets if a.liquidity=="liquid")
    floor=ctx.profile.emergency_months*ctx.profile.essential_monthly_spend
    daily=np.zeros((n,days)); balance=np.full(n,liquid,dtype=float); income_cv=bp.income_cv if bp else .1
    # Daily credit and spending uncertainty is illustrative, fitted to the available profile.
    expense_sd=max(1,monthly_spend*.35/np.sqrt(30)); shock_prob=min(.08,(bp.unplanned_lambda_annual/365) if bp else .01)
    obligations=[]
    if not ctx.transactions.empty and "description" in ctx.transactions:
        tx=ctx.transactions.copy(); tx["date"]=pd.to_datetime(tx["date"],errors="coerce"); tx=tx[tx["date"].notna()]
        for desc,g in tx.groupby(tx["description"].astype(str).str.lower()):
            if len(g)>=3 and any(k in desc for k in ("emi","rent","insurance","lic","subscription","netflix","airtel","jio","card payment")):
                amt=float(pd.to_numeric(g["amount"],errors="coerce").median())
                last=g["date"].max().date(); nextday=max(1,last.day)
                d=today+timedelta(days=(nextday-today.day)%30 or 30)
                while (d-today).days<days:
                    obligations.append({"date":d,"description":desc,"amount":amt}); d+=timedelta(days=30)
    for day in range(days):
        d=today+timedelta(days=day)
        # Expected income at a month boundary; no guarantee of payday timing.
        if d.day==1:
            credits=np.maximum(0,rng.normal(income, max(1,income*min(.8,income_cv))))
            balance+=credits
        spend=np.maximum(0,rng.normal(monthly_spend/30,expense_sd,size=n))
        shocks=(rng.random(n)<shock_prob)*rng.lognormal(np.log(max(1000,(bp.unplanned_lognormal_mu if bp else 9.5))),.7,size=n)
        balance-=spend+shocks
        for item in obligations:
            if item["date"]==d: balance-=item["amount"]
        daily[:,day]=balance
    p10=np.percentile(daily,10,axis=0); p50=np.percentile(daily,50,axis=0); p90=np.percentile(daily,90,axis=0)
    breach=(daily<floor).mean(axis=0); danger=np.where(breach>CFG.radar_balance_breach_probability_threshold)[0]
    pileups=[]
    for i,a in enumerate(obligations):
        clustered=[b for b in obligations if abs((b["date"]-a["date"]).days)<=CFG.radar_obligation_cluster_window_days]
        if len(clustered)>=CFG.radar_obligation_cluster_count:
            key=tuple(sorted((b["date"].isoformat(),b["description"]) for b in clustered))
            if not any(x.get("key")==key for x in pileups): pileups.append({"date":a["date"],"count":len(clustered),"obligations":clustered,"key":key})
    suggestions=[]
    if danger.size: suggestions.append("Review discretionary spending and consider moving avoidable payment dates before the first projected cash-floor warning.")
    if pileups: suggestions.append("Several recurring obligations cluster within five days; review payment dates or split eligible payments.")
    if not suggestions: suggestions.append("No cash-floor warning crossed the configured threshold in the simulated 90-day range; continue monitoring actual balances.")
    return RadarResult([today+timedelta(days=i) for i in range(days)],p10,p50,p90,breach,(today+timedelta(days=int(danger[0]))) if danger.size else None,pileups,suggestions)
