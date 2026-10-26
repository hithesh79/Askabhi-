"""Repair Lab: compare non-worsening plan repairs on common random numbers."""
from __future__ import annotations
import pandas as pd
import plotly.express as px
import streamlit as st
from ui.tables import render_table
from ui.pages._common import page_header,common_context,disclaimer
from core.repair import repair_plan
from core.models import ScenarioParams
from core.formatting import inr,pct
from ui.components import proof_drawer

def render():
    ctx,draws,base=common_context()
    page_header("Repair Lab","Test practical repairs, rank their costs and prove the before/after difference on identical random draws.","Repairs are accepted only when they do not reduce the selected feasibility probability.")
    saved=st.session_state.get("repair_scenario")
    if saved: st.info("A stress scenario from Chaos Monkey is selected. The scenario is stored in this session.")
    target=st.slider("Desired success probability",50,95,85)/100
    col1,col2=st.columns(2)
    with col1: expense_cut=st.slider("Allow discretionary cut up to",0,30,20)/100
    with col2: save_max=st.number_input("Maximum suggested extra monthly saving (₹)",min_value=1000.0,value=10000.0,step=1000.0)
    if st.button("Repair my plan",type="primary"):
        with st.spinner("Evaluating repairs with the same random draws..."):
            st.session_state["repair_result"]=repair_plan(ctx,draws,target,saved)
    r=st.session_state.get("repair_result")
    if r:
        a,b,c=st.columns(3); a.metric("Before",pct(r.before_probability)); b.metric("After",pct(r.after_probability),f"{(r.after_probability-r.before_probability)*100:+.1f} pp"); c.metric("Target reached","Yes" if r.reached_target else "Not reached")
        st.write(f"Draw fingerprints: **before `{r.fingerprint_before}`** · **after `{r.fingerprint_after}`** · identical = {r.fingerprint_before==r.fingerprint_after}")
        if r.repairs: render_table(pd.DataFrame(r.repairs),use_container_width=True,hide_index=True)
        else: st.info("No candidate repair improved the selected target under the current assumptions. Try changing a goal's amount or date in Goals and Plan.")
        df=pd.DataFrame([{"goal":g,"before":r.before_goal_probabilities.get(g,0)*100,"after":r.after_goal_probabilities.get(g,0)*100} for g in r.before_goal_probabilities])
        if not df.empty: st.plotly_chart(px.bar(df,x="goal",y=["before","after"],barmode="group",title="Goal probability before vs after repair"),use_container_width=True,config={"displayModeBar":False})
        st.markdown("### Alternative repair packages")
        render_table(pd.DataFrame([{"package":x["name"],"suggested actions":len(x["actions"])} for x in r.alternatives]),use_container_width=True,hide_index=True)
        proof_drawer("Repair proof","Each candidate is re-simulated with identical random arrays; candidates that reduce the target probability are discarded.",{"target_probability":target,"repairs":r.repairs},{"Repair pain weights are indicative and configurable","If target is unreachable, the report says so honestly"},draws.seed,draws.fingerprint())
    disclaimer()
