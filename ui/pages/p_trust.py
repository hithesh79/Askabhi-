"""Trust Center: assumptions, limits, data quality, backtest and test runner."""
from __future__ import annotations
import os, subprocess, sys
import pandas as pd
import streamlit as st
from ui.tables import render_table
from config import CFG
from ui.pages._common import page_header,common_context,disclaimer
from ui.components import ring_gauge
from core.resilience import resilience_score
from core.backtest import rolling_backtest,plan_autopsy
from core.formatting import inr,pct
from ui.state import ROOT

def render():
    ctx,draws,res=common_context(); score=resilience_score(ctx,res)
    page_header("Trust Center","Inspect assumptions, data quality, model limits and reproducibility before acting on a recommendation.","No forecast is guaranteed. Review the data and assumptions that drive every result.")
    a,b=st.columns([1,2])
    with a: ring_gauge(score.score,"Resilience Score",score.grade)
    with b:
        st.markdown("### Score breakdown")
        render_table(pd.DataFrame([{"component":k,"points":v} for k,v in score.components.items()]),use_container_width=True,hide_index=True)
        st.write(score.explanation)
    st.markdown("### Maturity labels")
    st.markdown("**BUILT:** local CSV import, classification, reconciliation, behaviour twin, net worth, goals, simulation, affordability, stress-test search, repair, offline copilot and report generation.")
    st.markdown("**SIMULATED:** financial account and UPI records in sample personas. The Pay & UPI page demonstrates a local flow only; no real transfer is sent or confirmed.")
    st.markdown("**ROADMAP:** authorised bank/UPI account connections, production payment processing, production LLM service and regional-language experiences.")
    st.markdown("### Data-quality report")
    bp=ctx.behaviour
    quality={"Persona":ctx.persona_name,"Transaction rows":len(ctx.transactions),"Months of history":bp.months_of_data if bp else 0,"Data confidence":bp.confidence if bp else "Low","Recurring merchants detected":len(bp.recurring_merchants) if bp else 0,"Review queue rows":int((ctx.transactions["confidence"]<.7).sum()) if "confidence" in ctx.transactions else 0,"Reconciliation report":str(st.session_state.get("reconcile_report"))}
    render_table(pd.DataFrame([{"measure":k,"value":v} for k,v in quality.items()]),use_container_width=True,hide_index=True)
    st.markdown("### Assumptions · indicative, verify")
    assumptions=CFG.assumptions_dict()
    render_table(pd.DataFrame([{"assumption":k,"value":str(v)} for k,v in assumptions.items()]),use_container_width=True,hide_index=True,height=420)
    st.markdown("### Honest limits")
    limits=["Synthetic data validates mechanics only; it does not prove real-world forecast accuracy.","Seasonal and unplanned-shock estimates are weak with fewer than 12 months of history; confidence is low below three months.","The Chaos search is a bounded heuristic, not a proof of the worst case.","Probabilities depend on uncertain returns, inflation, income stability and user-supplied assumptions.","Vehicle on-road costs, rates, penalties and tax placeholders are indicative and must be verified.","Do not rely on the model when income changed structurally, obligations are undisclosed, or a goal is more than 15 years away without revisiting assumptions.","The product is educational financial planning, not investment, tax, lending or other regulated financial advice."]
    for item in limits: st.warning(item)
    st.markdown("### Backtest and plan autopsy")
    if st.button("Run rolling-origin backtest and plan autopsy",key="trust_backtest"):
        st.session_state["backtest_result"]=rolling_backtest(ctx.transactions,ctx.profile.as_of,ctx.profile)
        st.session_state["autopsy_result"]=plan_autopsy(ctx,ctx.transactions)
    bt=st.session_state.get("backtest_result")
    if bt:
        st.metric("80% interval empirical coverage",pct(bt.coverage),f"nominal {pct(bt.nominal_coverage)}"); st.write(f"Verdict: **{bt.verdict}** · Mean interval width: {inr(bt.mean_band_width)}")
        render_table(pd.DataFrame(bt.origins),use_container_width=True,hide_index=True); st.caption(bt.warning)
        render_table(st.session_state["autopsy_result"],use_container_width=True,hide_index=True)
    st.markdown("### Automated test suite")
    if st.button("Run pytest for this project",type="primary"):
        with st.spinner("Running the complete automated test suite..."):
            try:
                p=subprocess.run([sys.executable,"-m","pytest","-q"],cwd=ROOT,capture_output=True,text=True,timeout=180)
                st.session_state["test_output"]={"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr}
            except Exception as exc: st.session_state["test_output"]={"returncode":-1,"stdout":"","stderr":f"Test runner could not complete: {exc}"}
    out=st.session_state.get("test_output")
    if out:
        if out["returncode"]==0: st.success("Test suite passed.")
        else: st.error("Test suite reported failures or could not run.")
        st.code((out["stdout"]+"\n"+out["stderr"]).strip() or "No output returned.")
    st.markdown("### Reproducibility")
    st.code(f"seed={draws.seed}\nn_sims={draws.n_sims}\nfingerprint={draws.fingerprint()}")
    if st.button("Delete session data and return to onboarding"):
        keep={"onboarded":False}; st.session_state.clear(); st.session_state.update(keep); st.rerun()
    disclaimer()
