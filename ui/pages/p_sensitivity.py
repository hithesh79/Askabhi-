"""What Really Matters: same-draw sensitivity tornado."""
from __future__ import annotations
import streamlit as st
from ui.tables import render_table
from ui.pages._common import page_header,common_context,disclaimer
from core.sensitivity import tornado
from ui.charts import tornado as tornado_chart
from core.formatting import pct

def render():
    ctx,draws,res=common_context(); options={g.name:g.goal_id for g in ctx.goals}
    page_header("What really matters","Find which assumptions have the greatest impact on a selected goal's feasibility.","The sensitivity analysis changes one assumption at a time and reuses the same random draws.")
    if not options: st.info("Add a goal in Goals and Plan first."); return
    selected=st.selectbox("Goal to test",list(options),key="sensitivity_goal")
    if st.button("Run sensitivity tornado",type="primary") or "sensitivity_results" not in st.session_state:
        with st.spinner("Re-running the selected goal under alternate assumptions..."):
            st.session_state["sensitivity_results"]=tornado(ctx,draws,options[selected]); st.session_state["sensitivity_goal_id"]=options[selected]
    df=st.session_state["sensitivity_results"]
    if not df.empty:
        st.plotly_chart(tornado_chart(df),use_container_width=True,config={"displayModeBar":False})
        render_table(df,use_container_width=True,hide_index=True)
        top=df.iloc[0]
        st.info(f"The plan is most sensitive in this tested set to **{top['assumption']}**, which changes feasibility by up to {top['max_abs_effect_pp']:.1f} percentage points.")
        if float(df["max_abs_effect_pp"].max())>20: st.warning("This plan is fragile under the configured sensitivity rule: a single tested assumption moves probability by more than 20 percentage points.")
    disclaimer()
