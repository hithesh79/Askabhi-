"""Behaviour twin: explain actual spending, recurring payments and irregularity."""
from __future__ import annotations
from datetime import date
import numpy as np
import pandas as pd
from scipy.stats import linregress
from core.models import BehaviourProfile, Profile
from core.classify import classify
from core.reconcile import reconcile

def shrinkage_weight(n: float, k: float) -> float:
    """Return empirical-data weight n/(n+k), with safe edge handling."""
    n=max(0.0,float(n)); k=max(0.0,float(k))
    if k==0: return 1.0 if n>0 else 0.0
    return n/(n+k)

def analyse(transactions: pd.DataFrame, as_of: date, profile: Profile) -> BehaviourProfile:
    """Estimate spending distributions and behaviour signals from actual-like transactions."""
    df=transactions.copy() if transactions is not None else pd.DataFrame()
    bp=BehaviourProfile(as_of=as_of)
    if df.empty:
        bp.safe_income=float(profile.monthly_income_net); bp.income_label="Stable"; bp.confidence="Low"; bp.months_of_data=0
        bp.actual_median_saving=max(0.0,profile.monthly_income_net-profile.essential_monthly_spend)
        bp.behaviour_gap="No transaction history available; using explicit profile assumptions."
        return bp
    if "date" not in df: df["date"]=as_of.isoformat()
    df["date"]=pd.to_datetime(df["date"],errors="coerce")
    df=df[df["date"].notna()].copy()
    if df.empty:
        bp.safe_income=float(profile.monthly_income_net); bp.confidence="Low"; return bp
    if "type" not in df: df["type"]="debit"
    if "amount" not in df: df["amount"]=0.0
    df["amount"]=pd.to_numeric(df["amount"],errors="coerce").fillna(0).abs()
    classified=classify(df)
    classified, _=reconcile(classified)
    classified["month"]=classified["date"].dt.to_period("M").astype(str)
    classified["weekday"]=classified["date"].dt.dayofweek
    classified["day"]=classified["date"].dt.day
    credit=(classified["type"].astype(str).str.lower().eq("credit")) | classified["kind"].eq("income")
    spend=(~credit) & (~classified["exclude_from_spend"]) & (~classified["kind"].isin(["transfer","investment","refund","potential_asset","loan"]))
    ex=classified[spend].copy(); inc=classified[credit].copy()
    bp.transaction_categories=classified
    months=sorted(classified["month"].unique())
    bp.months_of_data=len(months)
    bp.confidence="Low" if len(months)<3 else ("Medium" if len(months)<=6 else "High")
    if len(months):
        monthly_spend=ex.groupby("month")["amount"].sum().reindex(months,fill_value=0)
        monthly_income=inc.groupby("month")["amount"].sum().reindex(months,fill_value=0)
        bp.monthly_spend_history=[float(x) for x in monthly_spend.values]
        bp.monthly_income_history=[float(x) for x in monthly_income.values]
        bp.monthly_residuals=[float(x) for x in (monthly_spend-monthly_spend.mean()).values]
        bp.planned_monthly=float(ex.loc[ex["nature"].isin(["fixed","essential"]),"amount"].sum()/max(1,len(months)))
        bp.unplanned_monthly=float(ex.loc[ex["nature"].eq("discretionary"),"amount"].sum()/max(1,len(months)))*0.08
        # Month totals by category are the basis for the simulation.
        cat_month=ex.groupby(["month","category"])["amount"].sum().unstack(fill_value=0)
        for cat in cat_month.columns:
            bp.category_monthly_mean[str(cat)]=float(cat_month[cat].mean())
            bp.category_monthly_std[str(cat)]=float(cat_month[cat].std(ddof=1) if len(cat_month)>1 else 0.0)
            natures=ex.loc[ex["category"].eq(cat),"nature"].astype(str)
            bp.category_nature[str(cat)]=str(natures.mode().iloc[0]) if not natures.empty else "discretionary"
        # Seasonal monthly index is shrunk toward 1 because each calendar month has sparse observations.
        overall=max(1.0,float(ex.groupby("month")["amount"].sum().mean()))
        by_calendar=ex.assign(calendar_month=ex["date"].dt.month).groupby("calendar_month")["amount"].mean()
        for mo in range(1,13):
            observed=float(by_calendar.get(mo,overall))/overall if overall else 1.0
            n=int((ex["date"].dt.month==mo).sum())
            w=shrinkage_weight(n,2)
            bp.seasonal_index[mo]=float(np.clip(1+w*(observed-1),.65,1.8))
    # Recurrence: 3+ observations across 25-35 day intervals and amounts within 15%.
    recurring=[]; subscriptions=[]
    for desc,g in classified[~classified["exclude_from_spend"]].groupby(classified["description"].astype(str).str.lower()):
        gg=g.sort_values("date")
        if len(gg)<3: continue
        dates=gg["date"].dt.normalize().drop_duplicates().sort_values()
        intervals=dates.diff().dt.days.dropna()
        amounts=gg["amount"].astype(float)
        if len(intervals) and float(intervals.between(25,35).mean())>=0.6 and (amounts.max()-amounts.min())/max(1.0,float(amounts.mean()))<=.15:
            recurring.append(desc)
            if any(x in desc for x in ("netflix","hotstar","spotify","prime","subscription","gym","airtel","jio")): subscriptions.append(desc)
    bp.recurring_merchants=sorted(set(recurring)); bp.subscription_merchants=sorted(set(subscriptions))
    # Weekend/weekday ratio, normalised by the number of days observed in each group.
    if not ex.empty:
        weekend=ex.loc[ex["weekday"]>=5,"amount"].sum()/max(1,(ex["weekday"]>=5).sum())
        weekday=ex.loc[ex["weekday"]<5,"amount"].sum()/max(1,(ex["weekday"]<5).sum())
        bp.weekend_weekday_ratio=float(weekend/max(1.0,weekday))
        bp.payday_burst_share=float(ex.loc[ex["day"]<=5,"amount"].sum()/max(1,ex["amount"].sum()))
        last_days=ex.loc[ex["day"]>=26,"amount"].sum()
        first_days=ex.loc[ex["day"]<=5,"amount"].sum()
        bp.month_end_squeeze=bool(last_days>first_days*.85)
        disc=ex[ex["nature"].eq("discretionary")].groupby("month")["amount"].sum().sort_index()
        if len(disc)>=3:
            lr=linregress(np.arange(len(disc),dtype=float),disc.values.astype(float))
            bp.lifestyle_creep_slope=float(lr.slope); bp.lifestyle_creep_pvalue=float(lr.pvalue)
    # Unplanned one-off estimate: unusual non-recurring purchases by category.
    recurring_set=set(bp.recurring_merchants)
    nonrec=ex[~ex["description"].astype(str).str.lower().isin(recurring_set)]
    events=[]
    if not nonrec.empty:
        for _,g in nonrec.groupby("category"):
            vals=g["amount"].astype(float)
            threshold=max(float(vals.mean()+2*(vals.std(ddof=1) if len(vals)>1 else 0)),float(profile.monthly_income_net)*.10)
            events.extend(vals[vals>=threshold].tolist())
    n_events=len(events); weight=shrinkage_weight(n_events,3)
    prior_lambda=2.0
    bp.unplanned_lambda_annual=weight*(n_events/max(1,bp.months_of_data)*12)+(1-weight)*prior_lambda
    if n_events:
        logs=np.log(np.maximum(events,1.0)); bp.unplanned_lognormal_mu=weight*float(logs.mean())+(1-weight)*np.log(15000.0)
        bp.unplanned_lognormal_sigma=max(.15,weight*(float(logs.std(ddof=1)) if len(logs)>1 else .75)+(1-weight)*.75)
        bp.irregular_expense_reserve=float(np.sum(events)/max(1,bp.months_of_data))
    else:
        bp.unplanned_lognormal_mu=float(np.log(15000)); bp.unplanned_lognormal_sigma=.75; bp.irregular_expense_reserve=0.0
    # Income stability and conservative planning income.
    income_months=bp.monthly_income_history
    positive=np.asarray([x for x in income_months if x>0],dtype=float)
    if positive.size:
        mean=float(positive.mean()); sd=float(positive.std(ddof=1)) if positive.size>1 else 0.0
        bp.income_cv=float(sd/mean) if mean>0 else 0.0
        med=float(np.median(positive)); bp.lean_months=int(np.sum(positive<.70*med))
        if profile.income_type=="irregular":
            bp.safe_income=float(np.percentile(positive,20)); bp.income_label="Highly irregular" if bp.income_cv>=.4 else ("Variable" if bp.income_cv>=.2 else "Stable")
        else:
            bp.safe_income=mean; bp.income_label="Stable" if bp.income_cv<.2 else "Variable"
    else:
        bp.safe_income=float(profile.monthly_income_net); bp.income_label="Variable" if profile.income_type=="irregular" else "Stable"
        bp.income_cv=0.0; bp.lean_months=0
    med_income=float(np.median(positive)) if positive.size else profile.monthly_income_net
    med_spend=float(np.median(bp.monthly_spend_history)) if bp.monthly_spend_history else 0.0
    bp.actual_median_saving=med_income-med_spend
    bp.stated_saving=profile.stated_monthly_saving
    if profile.stated_monthly_saving is not None:
        bp.behaviour_gap=(f"You plan to save ₹{profile.stated_monthly_saving:,.0f} monthly; observed median income minus spend is about ₹{bp.actual_median_saving:,.0f}. "
                          "AskAbhi uses observed behaviour for planning, subject to data coverage.")
    elif profile.stated_monthly_budget is not None:
        bp.behaviour_gap=f"Stated budget is ₹{profile.stated_monthly_budget:,.0f}; median observed spending is about ₹{med_spend:,.0f}."
    else: bp.behaviour_gap="No stated budget/saving target supplied."
    bp.planned_unplanned_rows={"planned":bp.planned_monthly,"unplanned_estimate":bp.unplanned_monthly,"irregular_reserve":bp.irregular_expense_reserve}
    return bp

def money_waterfall(bp: BehaviourProfile, profile: Profile) -> pd.DataFrame:
    income=bp.safe_income or profile.monthly_income_net
    return pd.DataFrame([{"bucket":"Income","amount":income},{"bucket":"Fixed/essential","amount":sum(v for k,v in bp.category_monthly_mean.items() if bp.category_nature.get(k) in ("fixed","essential"))},{"bucket":"Discretionary","amount":sum(v for k,v in bp.category_monthly_mean.items() if bp.category_nature.get(k)=="discretionary")},{"bucket":"Unplanned reserve","amount":bp.irregular_expense_reserve},{"bucket":"Median savings estimate","amount":bp.actual_median_saving}])

def planned_unplanned(bp: BehaviourProfile) -> dict:
    return {"planned_monthly":bp.planned_monthly,"unplanned_monthly":bp.unplanned_monthly,"lumpy_reserve_monthly":bp.irregular_expense_reserve,"unplanned_lambda_annual":bp.unplanned_lambda_annual,"interpretation":"Estimates are weak with short history; review classifications before relying on them."}
