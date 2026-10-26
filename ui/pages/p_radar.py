"""Cash-Crunch Radar: daily 90-day balance risk and obligation pile-ups."""
from __future__ import annotations
from datetime import date
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from ui.tables import render_table
from ui.pages._common import page_header,common_context,disclaimer
from core.radar import cash_radar
from core.formatting import inr

def render():
    ctx,draws,res=common_context(); today=st.date_input("Start date",value=date.today(),key="radar_date"); days=st.slider("Projection horizon (days)",30,180,90,key="radar_days")
    if st.button("Run cash-crunch radar",type="primary") or "radar_result" not in st.session_state:
        with st.spinner("Projecting cash balance ranges and recurring obligation dates..."):
            st.session_state["radar_result"]=cash_radar(ctx,draws,today,days)
    r=st.session_state["radar_result"]
    verdict=f"First projected danger date: {r.first_danger_date:%d %b %Y}." if r.first_danger_date else "No day crossed the configured 15% emergency-floor breach probability in this projection."
    page_header("Cash-Crunch Radar","Look ahead day by day for a likely cash squeeze and overlapping obligations.",verdict,"warning" if r.first_danger_date else "info")
    fig=go.Figure(); x=[d.strftime("%d %b") for d in r.dates]
    fig.add_trace(go.Scatter(x=x,y=r.p90,mode="lines",line={"width":0},showlegend=False,name="P90"))
    fig.add_trace(go.Scatter(x=x,y=r.p10,mode="lines",fill="tonexty",fillcolor="rgba(183,255,114,.10)",line={"width":0},name="P10–P90 range"))
    fig.add_trace(go.Scatter(x=x,y=r.p50,mode="lines",line={"color":"#B7FF72","width":2.5},name="Median balance"))
    fig.add_hline(y=ctx.profile.emergency_months*ctx.profile.essential_monthly_spend,line_dash="dash",line_color="#F5D66E",annotation_text="Emergency floor")
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(13,22,15,.38)",font={"color":"#F0F7EF","family":"DM Sans, Inter, sans-serif"},xaxis={"gridcolor":"#263A2B"},yaxis={"gridcolor":"#263A2B"},title="Projected balance · illustrative uncertainty band",yaxis_title="INR",height=400)
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    df=pd.DataFrame([{"date":r.dates[i],"P10 balance":inr(r.p10[i]),"median balance":inr(r.p50[i]),"P90 balance":inr(r.p90[i]),"probability below floor":f"{r.breach_probability[i]:.0%}"} for i in range(len(r.dates))])
    with st.expander("Daily projection table"): render_table(df,use_container_width=True,hide_index=True)
    st.markdown("### Next steps")
    for s in r.suggestions: st.info(s)
    if r.pileups:
        st.markdown("### Obligation pile-ups")
        render_table(pd.DataFrame([{"date":x["date"],"count":x["count"],"obligations":", ".join(o["description"] for o in x["obligations"])} for x in r.pileups]),use_container_width=True,hide_index=True)
    disclaimer()
