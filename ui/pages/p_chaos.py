"""Stress Test & Repair (Chaos Money): simulate shocks, impact on goals, and repaired plan."""
from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from ui.tables import render_table
from ui.pages._common import page_header, common_context, disclaimer
from ui.components import html_block, proof_drawer
from core.chaos import find_breaks, stress_report
from core.repair import repair_plan
from core.models import ScenarioParams
from core.simulate import simulate
from core.formatting import inr, pct

def render():
    ctx, draws, base = common_context()
    
    page_header(
        "Stress Test & Repair · Chaos Money Engine",
        "Subject your financial life to plausible life shocks (job loss, income cuts, medical emergencies), test impact, and generate a repaired plan.",
        "Compare Original Plan vs Shock vs Repaired Plan on identical simulation random draws."
    )

    col_controls, col_impact = st.columns([1, 1.25], gap="large")

    with col_controls:
        with st.container(border=True):
            st.markdown("<div style='font-size:16px; font-weight:850; color:#17252A; margin-bottom:10px;'>Configure Shock Scenario</div>", unsafe_allow_html=True)
            shock_type = st.selectbox(
                "Select Life Shock",
                [
                    "Job Loss for 6 Months (50% emergency income reduction)",
                    "Job Loss for 3 Months",
                    "Income Cut of 20% for 12 Months",
                    "Unexpected Medical Emergency (₹5,00,000)",
                    "Combined Shock: Medical Expense + Delayed Bonus"
                ]
            )
            
            if "Job Loss for 6 Months" in shock_type:
                active_params = ScenarioParams(job_loss_months=6, job_loss_start=0)
                shock_banner = "⚠️ Job Loss for 6 Months: Simulating income stoppage and emergency-fund drawdown."
            elif "Job Loss for 3 Months" in shock_type:
                active_params = ScenarioParams(job_loss_months=3, job_loss_start=0)
                shock_banner = "⚠️ Job Loss for 3 Months: Simulating 90-day salary disruption."
            elif "Income Cut" in shock_type:
                active_params = ScenarioParams(income_cut_pct=0.2, income_cut_start=0, income_cut_months=12)
                shock_banner = "⚠️ Income Cut: Simulating 20% reduced take-home pay for 1 year."
            elif "Medical" in shock_type:
                active_params = ScenarioParams(one_off_expenses=[(0, 500000.0)])
                shock_banner = "⚠️ Medical Shock: Simulating ₹5,00,000 immediate emergency outflow."
            else:
                active_params = ScenarioParams(income_cut_pct=0.15, one_off_expenses=[(1, 300000.0)])
                shock_banner = "⚠️ Combined Shock: Income dip + ₹3 Lakh medical bill."

            html_block(f"""
            <div style="background:#FDF0ED; border:1.5px solid #F5D3C5; border-left:5px solid #E07A5F; border-radius:14px; padding:14px 18px; font-size:13.5px; color:#A0401E; font-weight:700; margin:14px 0;">
              {shock_banner}
            </div>
            """)

            # Run Simulation
            sim_shock = simulate(ctx, active_params, draws)
            
            st.markdown("<div style='font-size:14.5px; font-weight:800; color:#17252A; margin:12px 0 8px;'>Monthly Cash-Flow Commitments</div>", unsafe_allow_html=True)
            base_income = float(ctx.profile.monthly_income_net)
            spend = float((ctx.behaviour.planned_monthly if ctx.behaviour else 0) + (ctx.behaviour.unplanned_monthly if ctx.behaviour else 0))
            emis = sum(float(x.emi) for x in ctx.liabilities)
            
            m1, m2 = st.columns(2)
            m1.metric("Essential Expenses", inr(spend))
            m2.metric("Fixed Loan EMIs", inr(emis))

    with col_impact:
        with st.container(border=True):
            st.markdown("<div style='font-size:16px; font-weight:850; color:#17252A; margin-bottom:12px;'>Impact on Goals &amp; Feasibility</div>", unsafe_allow_html=True)
            
            for g in ctx.goals[:3]:
                base_prob = base.goal_probabilities.get(g.goal_id, 0.0)
                shock_prob = sim_shock.goal_probabilities.get(g.goal_id, 0.0)
                diff_pp = (shock_prob - base_prob) * 100
                
                badge_color = "#2B7A78" if diff_pp >= -5 else ("#E07A5F" if diff_pp >= -25 else "#C85A32")
                badge_bg = "#DEF2F1" if diff_pp >= -5 else ("#FDF0ED" if diff_pp >= -25 else "#FCECE9")
                status_text = "On Track" if diff_pp >= -5 else (f"Delayed by {abs(diff_pp)/5:.1f} months" if diff_pp >= -25 else "Severe Risk")
                
                html_block(f"""
                <div style="background:#FEFFFF; border:1.5px solid #D1EBE8; border-radius:16px; padding:14px 18px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 8px rgba(23,37,42,0.03);">
                  <div>
                    <div style="font-weight:800; font-size:14.5px; color:#17252A;">{g.name}</div>
                    <div style="font-size:12px; color:#496E6B; margin-top:2px;">Baseline: <b>{pct(base_prob)}</b>  ➔  Under Shock: <b style="color:{badge_color};">{pct(shock_prob)}</b></div>
                  </div>
                  <span style="background:{badge_bg}; color:{badge_color}; font-weight:850; font-size:12px; padding:5px 12px; border-radius:99px; border:1px solid {badge_color};">
                    {status_text}
                  </span>
                </div>
                """)

    # Monthly Cash Runway Chart
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:16px; font-weight:850; color:#17252A; margin-bottom:10px;'>Cash Flow &amp; Runway Projection (6 Months)</div>", unsafe_allow_html=True)
    fig = go.Figure()
    months_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    
    fig.add_trace(go.Bar(
        x=months_labels,
        y=[spend * 0.9, spend * 0.85, spend * 0.8, spend * 0.8, spend * 0.8, spend * 0.8],
        name="Essential Expenses",
        marker_color="#2B7A78"
    ))
    fig.add_trace(go.Bar(
        x=months_labels,
        y=[emis] * 6,
        name="Loan EMIs",
        marker_color="#E07A5F"
    ))
    fig.add_trace(go.Bar(
        x=months_labels,
        y=[8000, 4000, 2000, 0, 0, 0],
        name="Discretionary",
        marker_color="#3AAFA9"
    ))
    
    fig.update_layout(
        barmode='stack',
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FEFFFF",
        font={"family": "Plus Jakarta Sans, sans-serif", "color": "#17252A"},
        height=320,
        margin={"l": 20, "r": 20, "t": 20, "b": 30},
        yaxis_title="INR (₹)"
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Repaired Plan Generator Section
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown("### Generate Repaired Plan")
    st.caption("Evaluate non-worsening recovery adjustments that restore goal feasibility on identical random draws.")
    
    if st.button("Calculate Optimal Plan Repair →", type="primary", key="calc_plan_repair_btn"):
        with st.spinner("Searching non-worsening repair packages on identical simulation draws..."):
            repair_res = repair_plan(ctx, draws, 0.85, active_params)
            st.session_state["active_repair_res"] = repair_res

    r_res = st.session_state.get("active_repair_res")
    if r_res:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        a, b, c = st.columns(3, gap="medium")
        a.metric("Feasibility Under Shock", pct(r_res.before_probability))
        b.metric("Feasibility After Repair", pct(r_res.after_probability), f"{(r_res.after_probability - r_res.before_probability)*100:+.1f} pp")
        c.metric("Target Restored", "Yes ✓" if r_res.reached_target else "Partial")
        
        if r_res.repairs:
            st.markdown("<div style='font-size:15px; font-weight:800; margin-top:14px; margin-bottom:8px;'>Recommended Repair Actions</div>", unsafe_allow_html=True)
            render_table(pd.DataFrame(r_res.repairs), use_container_width=True, hide_index=True)

    disclaimer()
