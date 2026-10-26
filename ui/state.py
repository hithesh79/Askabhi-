"""Shared Streamlit session state. All pages read a single PlanContext."""
from __future__ import annotations
from datetime import date
from pathlib import Path
import hashlib, json
import pandas as pd
import streamlit as st
from config import CFG
from core.data_gen import generate_persona, generate_csvs
from core.models import PlanContext, Profile
from core.classify import classify
from core.reconcile import reconcile
from core.behaviour import analyse
from core.rng import make_draws
from core.simulate import simulate
from core.models import ScenarioParams

ROOT=Path(__file__).resolve().parents[1]
DATA_DIR=ROOT/"data"

def _build_ctx(bundle, transactions=None, assets=None, liabilities=None, goals=None):
    tx=transactions if transactions is not None else bundle.transactions
    tx=tx.copy()
    overrides=st.session_state.get("transaction_overrides",{})
    if tx.empty: classified=classify(tx)
    else: classified=classify(tx,overrides)
    classified,report=reconcile(classified)
    bp=analyse(classified,bundle.profile.as_of,bundle.profile)
    ctx=PlanContext(bundle.profile,list(assets if assets is not None else bundle.assets),list(liabilities if liabilities is not None else bundle.liabilities),list(goals if goals is not None else bundle.goals),bp,CFG,classified,bundle.name)
    st.session_state["reconcile_report"]=report
    st.session_state["data_confidence"]=bp.confidence
    return ctx

def set_persona(name: str):
    if not DATA_DIR.exists(): DATA_DIR.mkdir(parents=True,exist_ok=True)
    if not (DATA_DIR/"transactions.csv").exists(): generate_csvs(DATA_DIR,date.today(),CFG.default_seed)
    bundle=generate_persona(name,date.today(),int(st.session_state.get("seed",CFG.default_seed)))
    st.session_state["persona_bundle"]=bundle
    st.session_state["persona"]=bundle.name
    st.session_state["ctx"]=_build_ctx(bundle)
    st.session_state.pop("baseline_cache",None)
    st.session_state.pop("draws_cache",None)

def get_ctx() -> PlanContext:
    if "ctx" not in st.session_state:
        selected=st.session_state.get("persona","Arjun")
        if selected not in ("Arjun","Meera"): selected="Arjun"
        set_persona(selected)
    return st.session_state["ctx"]

def replace_transactions(df: pd.DataFrame, name="Uploaded data"):
    from core.models import PersonaBundle
    ctx=get_ctx(); base=st.session_state["persona_bundle"]
    bundle=PersonaBundle(name,ctx.profile,df,ctx.assets,ctx.liabilities,ctx.goals,description="User-imported transaction data; review validation issues.")
    st.session_state["persona_bundle"]=bundle; st.session_state["ctx"]=_build_ctx(bundle)
    st.session_state.pop("baseline_cache",None)

def update_assets_liabilities(asset_rows, liability_rows):
    from core.models import Asset,Liability
    ctx=get_ctx(); assets=[]; liabilities=[]
    for r in asset_rows:
        try:
            if not r.get("name"): continue
            unlock=r.get("unlock_date"); unlock=None if pd.isna(unlock) or not unlock else pd.Timestamp(unlock).date()
            assets.append(Asset(str(r["name"]),str(r.get("kind","other")),max(0,float(r.get("value",0))),str(r.get("asset_class","cash")),str(r.get("liquidity","liquid")),unlock,max(0,float(r.get("penalty_pct",0))),float(r.get("exp_return",.03)),float(r.get("vol",.01))))
        except (ValueError,TypeError,KeyError): continue
    for r in liability_rows:
        try:
            if not r.get("name"): continue
            liabilities.append(Liability(str(r["name"]),str(r.get("kind","other")),max(0,float(r.get("outstanding",0))),max(0,float(r.get("annual_rate",0))),max(0,float(r.get("emi",0))),max(0,int(r.get("months_left",0)))))
        except (ValueError,TypeError,KeyError): continue
    st.session_state["ctx"]=PlanContext(ctx.profile,assets,liabilities,ctx.goals,ctx.behaviour,CFG,ctx.transactions,ctx.persona_name)
    st.session_state.pop("baseline_cache",None)

def update_goals(goal_rows):
    from core.models import Goal
    ctx=get_ctx(); goals=[]
    for r in goal_rows:
        try:
            if not r.get("name"): continue
            d=pd.Timestamp(r["target_date"]).date()
            goals.append(Goal(str(r.get("goal_id") or r["name"].lower().replace(" ","_")),str(r["name"]),str(r.get("category","other")),max(0,float(r.get("target_amount_today",0))),d,min(3,max(1,int(r.get("priority",2)))),bool(r.get("hard",True)),min(1,max(0,float(r.get("min_acceptable_pct",1)))),None if pd.isna(r.get("inflation")) else float(r.get("inflation")),str(r.get("funding","cash")),float(r.get("down_payment_pct",.2)),float(r.get("loan_rate",.12)),int(r.get("loan_tenure_months",36)),float(r.get("running_cost_monthly",0)),None if pd.isna(r.get("onroad_multiplier")) else float(r.get("onroad_multiplier"))))
        except (ValueError,TypeError,KeyError): continue
    st.session_state["ctx"]=PlanContext(ctx.profile,ctx.assets,ctx.liabilities,goals,ctx.behaviour,CFG,ctx.transactions,ctx.persona_name)
    st.session_state.pop("baseline_cache",None)

def ctx_key(ctx, params=None, seed=None, n_sims=None):
    bp=ctx.behaviour
    obj={"profile":{"as_of":ctx.profile.as_of.isoformat(),"income":ctx.profile.monthly_income_net,"type":ctx.profile.income_type,"growth":ctx.profile.income_growth,"job_loss":ctx.profile.job_loss_prob_annual,"emergency":ctx.profile.emergency_months,"essential_spend":ctx.profile.essential_monthly_spend,"income_history":ctx.profile.income_history},"assets":[(a.name,a.value,a.asset_class,a.liquidity,str(a.unlock_date),a.penalty_pct,a.exp_return,a.vol) for a in ctx.assets],"liabilities":[(l.name,l.outstanding,l.annual_rate,l.emi,l.months_left) for l in ctx.liabilities],"goals":[(g.goal_id,g.name,g.category,g.target_amount_today,str(g.target_date),g.priority,g.hard,g.min_acceptable_pct,g.inflation,g.funding,g.down_payment_pct,g.loan_rate,g.loan_tenure_months,g.running_cost_monthly,g.onroad_multiplier) for g in ctx.goals],"behaviour":{"category_monthly_mean":bp.category_monthly_mean if bp else {},"category_nature":bp.category_nature if bp else {},"seasonal_index":bp.seasonal_index if bp else {},"actual_median_saving":bp.actual_median_saving if bp else None,"months_of_data":bp.months_of_data if bp else 0},"persona":ctx.persona_name,"seed":seed,"n_sims":n_sims,"params":repr(params)}
    return hashlib.sha1(json.dumps(obj,sort_keys=True,default=str).encode()).hexdigest()

def get_draws():
    ctx=get_ctx(); seed=int(st.session_state.get("seed",CFG.default_seed)); n=int(st.session_state.get("n_sims",CFG.default_n_sims)); key=(seed,n)
    cache=st.session_state.get("draws_cache")
    if cache and cache[0]==key: return cache[1]
    draws=make_draws(seed,n,CFG.max_horizon_months)
    st.session_state["draws_cache"]=(key,draws)
    return draws

def get_baseline():
    ctx=get_ctx(); draws=get_draws(); key=ctx_key(ctx,None,draws.seed,draws.n_sims)
    cached=st.session_state.get("baseline_cache")
    if cached and cached[0]==key: return cached[1]
    result=simulate(ctx,ScenarioParams(),draws)
    st.session_state["baseline_cache"]=(key,result)
    return result

def get_session():
    ctx=get_ctx(); draws=get_draws(); return {"ctx":ctx,"draws":draws,"baseline":get_baseline()}
