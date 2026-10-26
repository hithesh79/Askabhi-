"""Money Time Machine: compare stated, behaviour-twin and repaired futures."""
from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from ui.tables import render_table
from ui.pages._common import page_header,common_context,disclaimer
from core.timemachine import three_futures,at_month
from core.formatting import inr,pct

def render():
    ctx,draws,base=common_context()
    page_header("Money Time Machine","Travel to a future month and compare the stated plan, actual behaviour and an illustrative repaired plan.","All three futures use the same random-draw fingerprint so differences come from assumptions, not a new random sample.")
    if st.button("Build three futures",type="primary") or "futures" not in st.session_state:
        with st.spinner("Projecting the three financial futures..."):
            st.session_state["futures"]=three_futures(ctx,draws)
    f=st.session_state["futures"]
    month=st.slider("Travel to month",0,len(f.months)-1,min(12,len(f.months)-1),key="time_month")
    snap=at_month(f,month); st.markdown(f"### Snapshot · {snap.month:%B %Y}")
    fig=go.Figure()
    for name,p10,p50,p90,color,fill in [("Stated plan",f.stated_networth_p10,f.stated_networth_p50,f.stated_networth_p90,"#B7A2FF","rgba(183,162,255,.10)"),("Behaviour twin",f.behaviour_networth_p10,f.behaviour_networth_p50,f.behaviour_networth_p90,"#71F2A2","rgba(113,242,162,.08)"),("Repaired plan",f.repaired_networth_p10,f.repaired_networth_p50,f.repaired_networth_p90,"#B7FF72","rgba(183,255,114,.10)")]:
        x=[d.strftime("%b %y") for d in f.months]
        fig.add_trace(go.Scatter(x=x,y=p90,mode="lines",line={"width":0},showlegend=False,hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=x,y=p10,mode="lines",line={"width":0},fill="tonexty",fillcolor=fill,name=f"{name} range"))
        fig.add_trace(go.Scatter(x=x,y=p50,mode="lines",line={"color":color,"width":2.6},name=name))
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(13,22,15,.38)",font={"color":"#F0F7EF","family":"DM Sans, Inter, sans-serif"},xaxis={"gridcolor":"#263A2B"},yaxis={"gridcolor":"#263A2B"},title="Three modelled median futures",yaxis_title="Net worth (₹)",height=430)
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    render_table(pd.DataFrame([{"future":k,"P10":inr(v["p10"]),"P50":inr(v["p50"]),"P90":inr(v["p90"])} for k,v in snap.values.items()]),use_container_width=True,hide_index=True)
    st.caption(f"Common random-draw fingerprint: `{f.fingerprint}`. The repaired path is an illustrative increase in monthly saving based on the current plan, not a guarantee that a recommended repair is feasible.")
    st.markdown("### Goal status at target horizon")
    for plan,probs in f.goal_probabilities.items():
        with st.expander(plan.title()+" plan"): render_table(pd.DataFrame([{"goal":g,"estimated probability":pct(p)} for g,p in probs.items()]),use_container_width=True,hide_index=True)
    disclaimer()
