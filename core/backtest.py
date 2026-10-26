"""Leakage-conscious rolling-origin spending check and plan autopsy."""
from __future__ import annotations
import pandas as pd
import numpy as np
from core.models import Profile, PlanContext, BacktestResult
from core.classify import classify
from core.reconcile import reconcile

def _monthly_spend(df):
    if df.empty: return pd.Series(dtype=float)
    x=df.copy(); x["date"]=pd.to_datetime(x["date"],errors="coerce"); x=x[x["date"].notna()]
    x=classify(x); x,_=reconcile(x)
    inc=x["type"].astype(str).str.lower().eq("credit")
    spend=(~inc)&(~x["exclude_from_spend"])&(~x["kind"].isin(["transfer","investment","refund","potential_asset","loan"]))
    return x.loc[spend].assign(month=x.loc[spend,"date"].dt.to_period("M").astype(str)).groupby("month")["amount"].sum().sort_index()

def rolling_backtest(df, as_of, profile: Profile) -> BacktestResult:
    monthly=_monthly_spend(df); items=list(monthly.items())
    origins=[]
    for i in range(max(1,len(items)-6),len(items)):
        train=items[:i]; actual=items[i][1]
        if len(train)<2: continue
        vals=np.asarray([v for _,v in train],dtype=float)
        q10,q90=np.percentile(vals,[10,90]); predicted=float(vals.mean())
        origins.append({"origin_month":train[-1][0],"target_month":items[i][0],"actual_spend":float(actual),"forecast_mean":predicted,"p10":float(q10),"p90":float(q90),"covered":bool(q10<=actual<=q90),"training_months":len(train)})
    coverage=float(np.mean([x["covered"] for x in origins])) if origins else 0.0
    width=float(np.mean([x["p90"]-x["p10"] for x in origins])) if origins else 0.0
    verdict="well calibrated" if origins and abs(coverage-.8)<=.15 else ("overconfident" if coverage<.65 else "underconfident")
    return BacktestResult(coverage,.8,width,verdict,origins,"Synthetic history validates implementation mechanics, not real-world predictive accuracy.")

def plan_autopsy(ctx: PlanContext, df: pd.DataFrame) -> pd.DataFrame:
    monthly_income={}; monthly_spend={}
    if not df.empty:
        x=df.copy(); x["date"]=pd.to_datetime(x["date"],errors="coerce"); x=x[x["date"].notna()]; x=classify(x); x,_=reconcile(x); x["month"]=x["date"].dt.to_period("M").astype(str)
        credit=x["type"].astype(str).str.lower().eq("credit")
        expense=(~credit)&(~x["exclude_from_spend"])&(~x["kind"].isin(["transfer","investment","refund","potential_asset","loan"]))
        monthly_income=x[credit].groupby("month")["amount"].sum().to_dict(); monthly_spend=x[expense].groupby("month")["amount"].sum().to_dict()
    cash=sum(a.value for a in ctx.assets if a.liquidity=="liquid" and a.asset_class not in ("equity","retirement")); floor=ctx.profile.emergency_months*ctx.profile.essential_monthly_spend; rows=[]
    for month in sorted(set(monthly_income)|set(monthly_spend))[-12:]:
        income=monthly_income.get(month,0); expenses=monthly_spend.get(month,0)+sum(l.emi for l in ctx.liabilities)
        cash+=income-expenses
        rows.append({"month":month,"income":income,"spend_and_emi":expenses,"closing_cash":cash,"emergency_floor":floor,"breached":cash<floor})
    return pd.DataFrame(rows)
