"""Goal editor, monthly saving requirements, competing-plan comparison and conflict map."""
from __future__ import annotations
from copy import deepcopy
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from ui.pages._common import page_header,common_context,disclaimer
from ui.state import update_goals
from ui.components import proof_drawer
from ui.tables import render_table, edit_records
from ui.charts import fan_chart,heatmap
from core.models import Goal,ScenarioParams
from core.simulate import simulate
from core.conflict import conflict_matrix,regret
from core.formatting import inr,pct,months_to_text
from core.data_gen import add_months

def render():
    ctx,draws,res=common_context()
    page_header("Goals and plan","Edit deadlines, amounts and priorities; compare alternatives without changing the baseline data.","The current plan funds higher-priority goals first; changes can improve one goal while delaying another.")
    st.markdown("### Edit goals")
    rows=[]
    for g in ctx.goals:
        rows.append({"goal_id":g.goal_id,"name":g.name,"category":g.category,"target_amount_today":g.target_amount_today,"target_date":g.target_date,"priority":g.priority,"hard":g.hard,"min_acceptable_pct":g.min_acceptable_pct,"inflation":g.inflation,"funding":g.funding,"down_payment_pct":g.down_payment_pct,"loan_rate":g.loan_rate,"loan_tenure_months":g.loan_tenure_months,"running_cost_monthly":g.running_cost_monthly,"onroad_multiplier":g.onroad_multiplier})
    gdf=pd.DataFrame(rows)
    edited=edit_records(gdf,"goal_editor",select_options={"category":["vehicle","education","home","retirement","emergency","wedding","medical","travel","other"],"priority":[1,2,3],"funding":["cash","loan"]},date_columns=["target_date"],bool_columns=["hard"],hidden_columns=["goal_id"])
    if st.button("Save goals and recalculate plan",type="primary"):
        update_goals(edited.to_dict("records")); st.success("Goal assumptions saved. The shared PlanContext and affected simulations are refreshed."); st.rerun()
    with st.expander("Add a new goal"):
        with st.form("add_goal_form"):
            a,b,c=st.columns(3); name=a.text_input("Goal name",value="New goal"); cat=b.selectbox("Category",["vehicle","education","home","retirement","emergency","wedding","medical","travel","other"]); amount=c.number_input("Amount today (₹)",min_value=1000.0,value=100000.0,step=10000.0)
            d,e,f=st.columns(3); target=d.date_input("Target date",value=add_months(ctx.profile.as_of,24)); priority=e.selectbox("Priority (1 is highest)",[1,2,3],index=1); hard=f.checkbox("Hard goal",value=True)
            minacc=st.slider("Minimum acceptable target funded",10,100,100)/100
            if st.form_submit_button("Add goal"):
                goals=[{"goal_id":g.goal_id,"name":g.name,"category":g.category,"target_amount_today":g.target_amount_today,"target_date":g.target_date,"priority":g.priority,"hard":g.hard,"min_acceptable_pct":g.min_acceptable_pct,"inflation":g.inflation,"funding":g.funding,"down_payment_pct":g.down_payment_pct,"loan_rate":g.loan_rate,"loan_tenure_months":g.loan_tenure_months,"running_cost_monthly":g.running_cost_monthly,"onroad_multiplier":g.onroad_multiplier} for g in ctx.goals]
                goals.append({"goal_id":name.lower().replace(" ","_"),"name":name,"category":cat,"target_amount_today":amount,"target_date":target,"priority":priority,"hard":hard,"min_acceptable_pct":minacc,"inflation":None,"funding":"cash","down_payment_pct":.2,"loan_rate":.12,"loan_tenure_months":36,"running_cost_monthly":0,"onroad_multiplier":None})
                update_goals(goals); st.success("Goal added."); st.rerun()
    # Refresh ctx and result after editor changes if the page reran.
    from ui.pages._common import common_context as cc
    ctx,draws,res=cc()
    st.markdown("### Goal feasibility and savings requirements")
    output=[]
    for g in ctx.goals:
        months=max(1,(g.target_date.year-ctx.profile.as_of.year)*12+g.target_date.month-ctx.profile.as_of.month)
        infl=g.inflation if g.inflation is not None else ctx.config.inflation_for(g.category)
        target=g.target_amount_today*(1+max(0,infl))**(months/12)*(g.onroad_multiplier or 1.0)
        if g.funding=="loan": target=target*g.down_payment_pct+target*ctx.config.goal_fee_fraction_for_loan
        monthly=target/months
        times=res.time_to_goal.get(g.goal_id,[]); finite=[x for x in times if x<1e9]
        earliest=months_to_text(float(pd.Series(finite).median())) if len(finite) else "Not reached in modelled horizon"
        output.append({"goal":g.name,"target":inr(g.target_amount_today),"inflated requirement":inr(target),"months left":months,"required monthly funding":inr(monthly),"estimated probability at minimum acceptable level":pct(res.goal_probabilities.get(g.goal_id,0)),"MC standard error":pct(res.goal_standard_errors.get(g.goal_id,0),1),"median shortfall":inr(res.goal_median_shortfalls.get(g.goal_id,0)),"earliest full-funding estimate":earliest,"minimum acceptable %":pct(g.min_acceptable_pct)})
    render_table(pd.DataFrame(output),use_container_width=True,hide_index=True)
    st.plotly_chart(fan_chart(res,ctx.profile.emergency_months*ctx.profile.essential_monthly_spend),use_container_width=True,config={"displayModeBar":False})
    st.markdown("### Plan A vs Plan B — identical random draws")
    goal_lookup={g.name:g.goal_id for g in ctx.goals}; selected=st.selectbox("Goal to change in Plan B",list(goal_lookup) or [""]); selected_id=goal_lookup.get(selected)
    col1,col2,col3=st.columns(3)
    with col1: new_priority=st.selectbox("Plan B priority",[1,2,3],index=1,key="plan_b_priority")
    with col2: delay=st.slider("Plan B deadline shift (months)",-12,24,6,key="plan_b_delay")
    with col3: more_saving=st.number_input("Plan B extra monthly savings (₹)",min_value=0.0,value=3000.0,step=1000.0,key="plan_b_saving")
    if st.button("Compare plans on same draws"):
        changed=deepcopy(ctx)
        g=next((g for g in changed.goals if g.goal_id==selected_id),None)
        if g:
            g.priority=int(new_priority); g.target_date=add_months(g.target_date,int(delay))
        a=simulate(ctx,ScenarioParams(),draws); b=simulate(changed,ScenarioParams(extra_monthly_saving=more_saving),draws)
        diff=[{"goal":g.name,"Plan A":pct(a.goal_probabilities.get(g.goal_id,0)),"Plan B":pct(b.goal_probabilities.get(g.goal_id,0)),"Change":f"{100*(b.goal_probabilities.get(g.goal_id,0)-a.goal_probabilities.get(g.goal_id,0)):+.1f} pp"} for g in ctx.goals]
        render_table(pd.DataFrame(diff),use_container_width=True,hide_index=True); st.success(f"Same random draws confirmed: {a.draws_fingerprint == b.draws_fingerprint} · fingerprint `{draws.fingerprint()}`")
        proof_drawer("Plan comparison","Re-simulate Plan A and Plan B using identical random-number arrays.",{"priority":new_priority,"deadline_shift_months":delay,"extra_saving":more_saving},{"A goal probability is the chance of reaching its configured minimum acceptable funding level by target date."},draws.seed,draws.fingerprint())
    with st.expander("Goal conflict map · leave-one-out simulation"):
        if st.button("Calculate goal conflict map",key="conflict_button"):
            with st.spinner("Re-simulating each goal without the others..."):
                matrix=conflict_matrix(ctx,draws); st.session_state["conflict_matrix"]=matrix
        matrix=st.session_state.get("conflict_matrix")
        if matrix is not None: st.plotly_chart(heatmap(matrix),use_container_width=True,config={"displayModeBar":False}); render_table(matrix.style.format("{:.1%}"),use_container_width=True)
    disclaimer()
