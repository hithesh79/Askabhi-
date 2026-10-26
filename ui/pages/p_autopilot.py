"""Payday Autopilot: obligations-first allocation and safe-to-spend pace."""
from __future__ import annotations
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from ui.tables import render_table
from ui.pages._common import page_header,common_context,disclaimer
from core.autopilot import payday_plan,safe_to_spend
from core.formatting import inr

def render():
    ctx,draws,res=common_context(); today=st.date_input("Planning date",value=date.today(),key="autopilot_date")
    plan=payday_plan(ctx,draws,today)
    page_header("Payday Autopilot","Allocate income in a deliberate order before deciding what is safe to spend.",f"After tracked obligations, essentials, emergency top-up and goal contributions, the modelled allowance is {inr(plan.safe_allowance)} for this month.")
    st.plotly_chart(px.bar(pd.DataFrame([{"bucket":k,"amount":v} for k,v in plan.buckets.items()]),x="bucket",y="amount",title="Suggested payday allocation"),use_container_width=True,config={"displayModeBar":False})
    render_table(pd.DataFrame([{"bucket":k,"amount":inr(v)} for k,v in plan.buckets.items()]),use_container_width=True,hide_index=True)
    st.markdown("### Safe-to-spend today")
    txspent=st.number_input("Discretionary spend already made this month (₹)",min_value=0.0,value=0.0,step=500.0)
    safe=safe_to_spend(ctx,plan,today,txspent)
    a,b,c=st.columns(3); a.metric("Allowance remaining",inr(safe.allowance_remaining)); b.metric("Safe per day",inr(safe.safe_today)); c.metric("Spending pace",safe.pace)
    overspend=st.number_input("What if I overspend this week? (₹)",min_value=0.0,value=5000.0,step=500.0)
    st.info(f"An extra {inr(overspend)} is a direct reduction in available cash or investments unless offset elsewhere; test the resulting scenario in Goals or Chaos Monkey. The daily allowance is a planning guide, not a bank balance feed.")
    disclaimer()
