"""Rupee-to-Days Leak Detector."""
from __future__ import annotations
import pandas as pd
import plotly.express as px
import streamlit as st
from ui.tables import render_table
from ui.pages._common import page_header,common_context,disclaimer
from core.leaks import find_leaks,rupee_to_days
from core.formatting import inr,pct

def render():
    ctx,draws,res=common_context(); goals={g.name:g.goal_id for g in ctx.goals}
    page_header("Leaks · Rupee-to-Days","Translate everyday spending decisions into how much they may change a goal's timeline.","A small recurring outflow can have a large cumulative effect; AskAbhi tests a reduction on identical simulation draws.")
    goal=st.selectbox("Focus goal",list(goals),key="leak_goal") if goals else None
    extra=st.number_input("Extra monthly saving to test (₹)",min_value=0.0,value=1000.0,step=500.0)
    if goal:
        days=rupee_to_days(ctx,goals[goal],draws,extra)
        st.metric("Modelled time-to-goal gain",f"{days:.0f} days",help="Estimated median timing change; it can be zero or unavailable when target funding is not reached in the simulated horizon.")
        if st.button("Find discretionary leaks",type="primary"):
            with st.spinner("Testing category cuts using common random numbers..."):
                st.session_state["leak_results"]=find_leaks(ctx,draws,goals[goal])
    leaks=st.session_state.get("leak_results",[])
    if leaks:
        df=pd.DataFrame([{"category":x.category,"monthly spend":x.monthly_spend,"probability before":x.probability_before,"probability after":x.probability_after,"probability change":x.probability_change,"months sooner":x.months_sooner/30.4375,"what changes":x.description} for x in leaks])
        df["monthly spend"]=df["monthly spend"].map(inr); df["probability before"]=df["probability before"].map(pct); df["probability after"]=df["probability after"].map(pct); df["probability change"]=df["probability change"].map(lambda x:f"{x*100:+.1f} pp")
        render_table(df,use_container_width=True,hide_index=True)
        st.plotly_chart(px.bar(pd.DataFrame([{"category":x.category,"monthly spend":x.monthly_spend,"potential release":x.monthly_spend*.2} for x in leaks]),x="category",y="potential release",title="Illustrative monthly release from a 20% category cut",color="category"),use_container_width=True,config={"displayModeBar":False})
    else: st.caption("Run the analysis to identify categories. The result will depend on the transaction history and selected goal.")
    bp=ctx.behaviour
    if bp and bp.lifestyle_creep_slope>0: st.warning(f"Estimated lifestyle creep: {inr(bp.lifestyle_creep_slope)} per history month; statistical p-value {bp.lifestyle_creep_pvalue:.3f}. This estimate may be weak with limited history.")
    disclaimer()
