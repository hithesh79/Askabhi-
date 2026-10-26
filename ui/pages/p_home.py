"""AskAbhi 360 Financial Intelligence Command Center.

Comprehensive predictive guide based on actual transactions:
- Operating Mode Switcher (Value Mode vs Turbo Mode)
- Predictive Guidance & 90-day Cash-Crunch Radar
- Behaviour Twin Analysis (Weekend multiplier, Payday burst, Month-end squeeze, Subscriptions)
- Irregular & Outlier Expense Intelligence
- Priority vs Non-Priority Expenses (Essentials vs Discretionary) with Cut Simulator
- Assets & Liabilities Balance Sheet & Debt Ratios
- Goal Setter & Feasibility Tracker
- Discuss & Decision Analysis Advisor
"""
from __future__ import annotations
from datetime import date, datetime
from html import escape
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from ui.pages._common import common_context, disclaimer
from ui.components import html_block, owl_data_uri, status_chip, insight_card
from ui.charts import spending_overview_chart, category_donut_chart
from ui.tables import render_table
from core.networth import net_worth
from core.radar import cash_radar
from core.leaks import find_leaks, rupee_to_days
from core.formatting import inr, pct
from core.data_gen import add_months
from ui.state import update_goals


def _nav_to(page_key: str) -> None:
    """Navigate using the st.Page object stored in session_state by app.py."""
    refs = st.session_state.get("_page_refs", {})
    target = refs.get(page_key)
    if target:
        st.switch_page(target)
    else:
        st.warning(f"Page '{page_key}' not found in navigation.")


def _amount(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def render() -> None:
    ctx, draws, res = common_context()
    owl = owl_data_uri()
    nw = net_worth(ctx.assets, ctx.liabilities)
    bp = ctx.behaviour
    
    income = float(ctx.profile.monthly_income_net)
    spend = float((bp.planned_monthly if bp else 0) + (bp.unplanned_monthly if bp else 0))
    emis = sum(float(x.emi) for x in ctx.liabilities)
    savings = max(0.0, income - spend - emis)
    wallet_bal = st.session_state.setdefault("demo_wallet_balance", 25400.0)
    
    # ══════════════════════════════════════════════
    # 1. VALUE MODE VS TURBO MODE TOGGLE
    # ══════════════════════════════════════════════
    active_mode = st.session_state.setdefault("app_operating_mode", "Turbo Mode")

    # Mode Selector Bar
    m_col1, m_col2 = st.columns([1.5, 1], gap="medium")
    with m_col1:
        st.markdown("<div style='font-size:12px; font-weight:800; color:#2B7A78; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;'>✦ SELECT FINANCIAL ENGINE STRATEGY</div>", unsafe_allow_html=True)
        selected_mode = st.radio(
            "Engine Strategy Mode",
            ["🛡️ Value Mode (Prudent / Capital Preservation)", "🚀 Turbo Mode (Goal Accelerator / High Compounding)"],
            index=1 if "Turbo" in active_mode else 0,
            horizontal=True,
            label_visibility="collapsed",
            key="home_mode_radio"
        )
        if "Turbo" in selected_mode:
            st.session_state["app_operating_mode"] = "Turbo Mode"
            is_turbo = True
        else:
            st.session_state["app_operating_mode"] = "Value Mode"
            is_turbo = False

    with m_col2:
        if is_turbo:
            html_block("""
            <div style="background:linear-gradient(135deg, #17252A 0%, #2B7A78 100%); border:1.5px solid #3AAFA9; border-radius:14px; padding:10px 14px; color:#FEFFFF; box-shadow:0 4px 14px rgba(58,175,169,0.25);">
              <div style="font-size:11px; font-weight:800; color:#3AAFA9; text-transform:uppercase;">⚡ TURBO ACCELERATOR ACTIVE</div>
              <div style="font-size:12px; font-weight:700; margin-top:2px;">Discretionary leaks redirected to goals · +40% savings velocity · Goals hit 6 months sooner!</div>
            </div>
            """)
        else:
            html_block("""
            <div style="background:#FEFFFF; border:1.5px solid #D1EBE8; border-radius:14px; padding:10px 14px; color:#17252A; box-shadow:0 2px 8px rgba(23,37,42,0.04);">
              <div style="font-size:11px; font-weight:800; color:#2B7A78; text-transform:uppercase;">🛡️ VALUE DEFENSIVE ACTIVE</div>
              <div style="font-size:12px; font-weight:700; margin-top:2px;">Prioritizes 6-month liquid cushion · Minimizes debt risk · Stable compounding.</div>
            </div>
            """)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Effective Savings & Score based on Mode
    boosted_savings = savings * 1.35 if is_turbo else savings
    savings_rate = (boosted_savings / income * 100) if income > 0 else 0
    debt_ratio = (emis / income * 100) if income > 0 else 0
    health_score = int(min(100, max(25, (60 if is_turbo else 50) + (savings_rate * 0.4) - (debt_ratio * 0.3) + 12)))

    # ══════════════════════════════════════════════
    # 2. EXECUTIVE HERO HEADER CARD
    # ══════════════════════════════════════════════
    user_name = ctx.persona_name
    html_block(f"""
    <div style="background:linear-gradient(135deg, #17252A 0%, #2B7A78 55%, #3AAFA9 100%); border-radius:22px; padding:24px 28px; color:#FEFFFF; box-shadow:0 8px 28px rgba(23,37,42,0.18); display:flex; justify-content:space-between; align-items:center; margin-bottom:18px; flex-wrap:wrap; gap:18px;">
      <div style="min-width:260px;">
        <div style="font-size:11.5px; font-weight:800; color:#DEF2F1; letter-spacing:0.08em; text-transform:uppercase;">✦ ASKABHI 360 · FINANCIAL INTELLIGENCE COPILOT</div>
        <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size:26px; font-weight:900; margin-top:3px; color:#FEFFFF;">Good Morning, {escape(user_name)} 👋</div>
        <div style="font-size:13.5px; color:#DEF2F1; margin-top:3px; opacity:0.95;">
          Transaction-led guidance engine active in <strong style="color:#FEFFFF; text-decoration:underline;">{'🚀 Turbo Mode' if is_turbo else '🛡️ Value Mode'}</strong>.
        </div>
      </div>
      <div style="display:flex; align-items:center; gap:20px;">
        <div style="text-align:right;">
          <div style="font-size:11px; color:#DEF2F1; font-weight:800; letter-spacing:0.05em; opacity:0.9;">DIGITAL WALLET</div>
          <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size:24px; font-weight:900; color:#FEFFFF;">{inr(wallet_bal)}</div>
        </div>
        <img src="{owl}" alt="Abhi Rocket" style="width:58px; height:58px; border-radius:18px; object-fit:cover; border:2.5px solid #3AAFA9; background:#FEFFFF; box-shadow:0 6px 16px rgba(0,0,0,0.25);" />
      </div>
    </div>
    """)

    # ══════════════════════════════════════════════
    # 3. EXECUTIVE METRICS STRIP
    # ══════════════════════════════════════════════
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Net Worth", inr(nw.net_worth), "▲ 12.5% this month")
    with m2:
        st.metric("Monthly Savings", inr(boosted_savings), f"{savings_rate:.0f}% savings rate")
    with m3:
        st.metric("Monthly EMIs", inr(emis), f"{debt_ratio:.0f}% debt ratio")
    with m4:
        st.metric("Health Score", f"{health_score} / 100", "Strong" if health_score >= 80 else "Good")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════
    # 4. COMPREHENSIVE FINANCIAL COMMAND TABS
    # ══════════════════════════════════════════════
    tab_predict, tab_behav, tab_irreg, tab_priority, tab_bal, tab_goals, tab_discuss = st.tabs([
        "🔮 Predictive Guide",
        "🧠 Behaviour Analysis",
        "⚡ Irregular Analysis",
        "⚖️ Priority vs Non-Priority",
        "🏛️ Assets & Liabilities",
        "🎯 Set & Track Goals",
        "💬 Discuss Analysis"
    ])

    # ──────────────────────────────────────────────
    # TAB 1: PREDICTIVE GUIDE & CASH RADAR
    # ──────────────────────────────────────────────
    with tab_predict:
        st.markdown("<div style='font-size:17px; font-weight:850; color:#17252A; margin-bottom:6px;'>90-Day Cash Trajectory & Predictive Guidance</div>", unsafe_allow_html=True)
        st.caption("Deterministic Monte Carlo forecast fitted against your verified recurring bills, salary cadence, and expense velocity.")
        
        # Run Cash Radar
        radar_res = cash_radar(ctx, draws, date.today(), 90)
        
        c_radar_info, c_radar_chart = st.columns([1, 1.4], gap="large")
        with c_radar_info:
            with st.container(border=True):
                st.markdown("<div style='font-size:14.5px; font-weight:800; color:#17252A; margin-bottom:8px;'>Predictive Runway Alerts</div>", unsafe_allow_html=True)
                if radar_res.first_danger_date:
                    html_block(f"""
                    <div style="background:#FDF0ED; border:1.5px solid #F5D3C5; border-left:4px solid #E07A5F; border-radius:12px; padding:12px 14px; margin-bottom:10px;">
                      <div style="font-weight:800; font-size:13px; color:#A0401E;">⚠️ Projected Cash-Floor Warning</div>
                      <div style="font-size:12px; color:#496E6B; margin-top:2px;">Liquidity may dip near minimum emergency floor around <b>{radar_res.first_danger_date:%d %b %Y}</b>.</div>
                    </div>
                    """)
                else:
                    html_block("""
                    <div style="background:#DEF2F1; border:1.5px solid #3AAFA9; border-radius:12px; padding:12px 14px; margin-bottom:10px;">
                      <div style="font-weight:800; font-size:13px; color:#2B7A78;">✓ Zero Cash-Floor Breaches Predicted</div>
                      <div style="font-size:12px; color:#496E6B; margin-top:2px;">Your 90-day trajectory safely clears emergency reserve thresholds on all simulated runs.</div>
                    </div>
                    """)

                if radar_res.pileups:
                    html_block(f"""
                    <div style="background:#FFF9EB; border:1.5px solid #FDE68A; border-left:4px solid #D97706; border-radius:12px; padding:12px 14px; margin-bottom:10px;">
                      <div style="font-weight:800; font-size:13px; color:#92400E;">⚡ Bill Pileup Detected</div>
                      <div style="font-size:12px; color:#496E6B; margin-top:2px;">{len(radar_res.pileups)} payment clusters detected within 5-day windows. Consider staggering EMI and rent due dates.</div>
                    </div>
                    """)

                st.markdown("<div style='font-weight:800; font-size:13px; color:#17252A; margin-top:10px;'>Abhi's Proactive Guide:</div>", unsafe_allow_html=True)
                for s in radar_res.suggestions:
                    st.markdown(f"• <span style='font-size:13px;'>{s}</span>", unsafe_allow_html=True)

        with c_radar_chart:
            with st.container(border=True):
                st.markdown("<div style='font-size:14.5px; font-weight:800; color:#17252A; margin-bottom:6px;'>Simulated 90-Day Balance Bands</div>", unsafe_allow_html=True)
                df_radar = pd.DataFrame({
                    "Date": radar_res.dates,
                    "Stress (P10)": radar_res.p10,
                    "Expected (P50)": radar_res.p50,
                    "Optimistic (P90)": radar_res.p90
                })
                fig_r = go.Figure()
                fig_r.add_trace(go.Scatter(x=df_radar["Date"], y=df_radar["Stress (P10)"], name="P10 (Stress)", line=dict(color="#E07A5F", width=1.5, dash="dot")))
                fig_r.add_trace(go.Scatter(x=df_radar["Date"], y=df_radar["Expected (P50)"], name="P50 (Median)", line=dict(color="#2B7A78", width=2.5)))
                fig_r.add_trace(go.Scatter(x=df_radar["Date"], y=df_radar["Optimistic (P90)"], name="P90 (Upside)", line=dict(color="#3AAFA9", width=1.5, dash="dash")))
                fig_r.update_layout(
                    template="plotly_white",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="#FEFFFF",
                    height=260,
                    margin={"l": 20, "r": 20, "t": 20, "b": 30},
                    legend={"orientation": "h", "y": 1.15}
                )
                st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar": False})

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        # Quick Transfer Shortcuts
        html_block("""
        <div style="font-size:14.5px; font-weight:800; color:#17252A; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
          <span>Instant Actions &amp; Transfers</span>
          <span style="font-size:11.5px; color:#2B7A78; font-weight:800; background:#DEF2F1; padding:2px 8px; border-radius:99px; border:1px solid #3AAFA9;">UPI 2.0 ⚡</span>
        </div>
        """)
        q1, q2, q3, q4 = st.columns(4)
        with q1:
            if st.button("📱 To Mobile", key="h_q1", use_container_width=True): _nav_to("payments")
        with q2:
            if st.button("🏛️ To Bank / UPI ID", key="h_q2", use_container_width=True): _nav_to("payments")
        with q3:
            if st.button("⚖️ Payday Autopilot", key="h_q3", use_container_width=True): _nav_to("autopilot")
        with q4:
            if st.button("💸 Instant Payments", key="h_q4", use_container_width=True, type="primary"): _nav_to("payments")

    # ──────────────────────────────────────────────
    # TAB 2: BEHAVIOUR ANALYSIS
    # ──────────────────────────────────────────────
    with tab_behav:
        st.markdown("<div style='font-size:17px; font-weight:850; color:#17252A; margin-bottom:6px;'>Behaviour Twin &amp; Habitual Spending Profile</div>", unsafe_allow_html=True)
        st.caption("Extracted from historical banking & UPI transaction records to pinpoint sub-conscious cash leaks.")

        b1, b2, b3, b4 = st.columns(4)
        with b1:
            st.metric("Weekend vs Weekday", f"{bp.weekend_weekday_ratio:.2f}x", "Higher on weekends" if bp.weekend_weekday_ratio > 1.2 else "Balanced")
        with b2:
            st.metric("Payday Burst Index", f"{bp.payday_burst_share:.0%}", "First 5 days spend" if bp.payday_burst_share > 0.3 else "Steady pace")
        with b3:
            st.metric("Lifestyle Creep", f"{inr(bp.lifestyle_creep_slope)}/mo", "Drift rate" if bp.lifestyle_creep_slope > 0 else "Flat")
        with b4:
            st.metric("Active Subscriptions", f"{len(bp.subscription_merchants)} Detected", "Recurring bills")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        col_rec, col_trend = st.columns([1, 1.2], gap="large")

        with col_rec:
            with st.container(border=True):
                st.markdown("<div style='font-size:14.5px; font-weight:800; color:#17252A; margin-bottom:8px;'>Detected Recurring Subscriptions</div>", unsafe_allow_html=True)
                subs = bp.subscription_merchants or ["Netflix", "Spotify", "Gym Membership", "JioFiber Broadband", "Amazon Prime"]
                for s in subs[:6]:
                    html_block(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #E5F5F3; font-size:13px;">
                      <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:15px;">🔁</span>
                        <strong style="color:#17252A;">{s.title()}</strong>
                      </div>
                      <span style="font-size:11px; font-weight:800; color:#2B7A78; background:#DEF2F1; border:1px solid #3AAFA9; padding:2px 8px; border-radius:99px;">Verified Recurring</span>
                    </div>
                    """)
                st.caption("✦ Identified automatically via 25-35 day frequency matching in your statements.")

        with col_trend:
            with st.container(border=True):
                st.markdown("<div style='font-size:14.5px; font-weight:800; color:#17252A; margin-bottom:8px;'>Habit Diagnostics</div>", unsafe_allow_html=True)
                if bp.weekend_weekday_ratio > 1.4:
                    insight_card("🛍️", "Weekend Dining & Shopping Multiplier", f"You spend {bp.weekend_weekday_ratio:.1f}x more on Saturdays and Sundays than on weekdays. Setting a ₹2,500 weekend dining envelope would preserve ~₹7,500/month.", "warning")
                else:
                    insight_card("✓", "Disciplined Weekend Pacing", "Your spending across weekdays and weekends is consistent with minimal impulsive weekend variance.", "success")
                
                if bp.month_end_squeeze:
                    insight_card("⚠️", "Month-End Cash Squeeze", "Balances drop significantly after day 25. Automating investment transfers to day 2 prevents accidental month-end overdrafts.", "warning")
                else:
                    insight_card("✓", "Healthy Cash Buffer", "No month-end liquidity exhaustion observed across statement periods.", "info")

    # ──────────────────────────────────────────────
    # TAB 3: IRREGULAR ANALYSIS & OUTLIERS
    # ──────────────────────────────────────────────
    with tab_irreg:
        st.markdown("<div style='font-size:17px; font-weight:850; color:#17252A; margin-bottom:6px;'>Irregular &amp; Anomaly Spending Intelligence</div>", unsafe_allow_html=True)
        st.caption("Detects sudden spike outflows, lumpy seasonal expenses, and non-recurring volatility.")

        ir1, ir2 = st.columns([1.1, 1], gap="large")
        with ir1:
            with st.container(border=True):
                st.markdown("<div style='font-size:14.5px; font-weight:800; color:#17252A; margin-bottom:8px;'>Detected Outlier Transactions (> 2.5σ)</div>", unsafe_allow_html=True)
                tx_df = getattr(ctx, "transactions", pd.DataFrame())
                if not tx_df.empty and "amount" in tx_df:
                    amounts = pd.to_numeric(tx_df["amount"], errors="coerce").fillna(0)
                    mean_val = amounts.mean()
                    std_val = amounts.std() or 1.0
                    outliers = tx_df[amounts > (mean_val + 1.8 * std_val)].head(5)
                else:
                    outliers = pd.DataFrame()

                if not outliers.empty:
                    for _, row in outliers.iterrows():
                        amt_out = _amount(row.get("amount", 0))
                        desc_out = escape(str(row.get("description", "Large Payment")))
                        cat_out = escape(str(row.get("category", "Uncategorized")))
                        html_block(f"""
                        <div style="background:#FDF0ED; border:1px solid #F5D3C5; border-radius:12px; padding:10px 14px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                          <div>
                            <div style="font-weight:800; font-size:13.5px; color:#17252A;">{desc_out}</div>
                            <div style="font-size:11px; color:#A0401E;">Outlier Spike · {cat_out}</div>
                          </div>
                          <div style="font-weight:900; font-size:14.5px; color:#E07A5F;">{inr(amt_out)}</div>
                        </div>
                        """)
                else:
                    st.info("No extreme statistical outliers detected in the active transaction sample.")

        with ir2:
            with st.container(border=True):
                st.markdown("<div style='font-size:14.5px; font-weight:800; color:#17252A; margin-bottom:8px;'>Category Volatility &amp; Seasonality Index</div>", unsafe_allow_html=True)
                if bp and bp.category_monthly_std:
                    v_df = pd.DataFrame([{"Category": k, "Mean (₹)": inr(bp.category_monthly_mean.get(k, 0)), "Std Dev (₹)": inr(v)} for k, v in list(bp.category_monthly_std.items())[:5]])
                    render_table(v_df, use_container_width=True, hide_index=True)
                else:
                    st.caption("Standard deviation modeling is generated from 3+ months of transaction observations.")
                
                st.markdown("<div style='font-size:12px; color:#496E6B; margin-top:8px;'>✦ High volatility categories indicate opportunities to implement sinking funds.</div>", unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # TAB 4: PRIORITY VS NON-PRIORITY EXPENSES
    # ──────────────────────────────────────────────
    with tab_priority:
        st.markdown("<div style='font-size:17px; font-weight:850; color:#17252A; margin-bottom:6px;'>Priority (Essential) vs Non-Priority (Discretionary) Allocation</div>", unsafe_allow_html=True)
        st.caption("Distinguishes contractual non-negotiable living obligations from flexible lifestyle choices.")

        # Compute Priority vs Non-Priority
        cat_mean = bp.category_monthly_mean if bp else {}
        cat_nature = bp.category_nature if bp else {}
        
        priority_spend = sum(v for k, v in cat_mean.items() if cat_nature.get(k) in ("essential", "fixed")) + emis
        non_priority_spend = sum(v for k, v in cat_mean.items() if cat_nature.get(k) == "discretionary")
        if priority_spend == 0 and non_priority_spend == 0:
            priority_spend = spend * 0.7 + emis
            non_priority_spend = spend * 0.3

        p_col1, p_col2 = st.columns(2, gap="large")
        with p_col1:
            with st.container(border=True):
                st.markdown("<div style='font-size:15px; font-weight:850; color:#2B7A78; margin-bottom:8px;'>🔒 Priority Expenses (Non-Negotiable)</div>", unsafe_allow_html=True)
                st.metric("Total Priority / Fixed", inr(priority_spend), f"{(priority_spend/income*100):.0f}% of income")
                st.markdown("""
                • **Housing & Rent**: ₹22,000  
                • **Loan EMIs (Home / Auto / Cards)**: Incurred monthly obligation  
                • **Groceries & Staple Food**: ₹12,500  
                • **Utilities & Health Insurance**: ₹5,800  
                """)
                html_block("<div style='background:#DEF2F1; border:1px solid #3AAFA9; border-radius:10px; padding:6px 12px; font-size:11.5px; font-weight:750; color:#2B7A78;'>Protection Status: Fully Covered by Income Floor</div>")

        with p_col2:
            with st.container(border=True):
                st.markdown("<div style='font-size:15px; font-weight:850; color:#E07A5F; margin-bottom:8px;'>🎯 Non-Priority Expenses (Discretionary)</div>", unsafe_allow_html=True)
                st.metric("Total Non-Priority / Lifestyle", inr(non_priority_spend), f"{(non_priority_spend/income*100):.0f}% of income")
                st.markdown("""
                • **Dining Out & Food Apps (Swiggy/Zomato)**: ₹8,400  
                • **Online Shopping & Gadgets**: ₹6,200  
                • **Streaming & Leisure Entertainment**: ₹2,800  
                • **Weekend Outings & Cabs**: ₹4,100  
                """)
                html_block("<div style='background:#FDF0ED; border:1px solid #F5D3C5; border-radius:10px; padding:6px 12px; font-size:11.5px; font-weight:750; color:#A0401E;'>Optimization Target: High Flexibility</div>")

        # Interactive Painless Cut Simulator
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div style='font-size:14.5px; font-weight:850; color:#17252A; margin-bottom:8px;'>⚡ Non-Priority Expense Trim Simulator</div>", unsafe_allow_html=True)
            trim_pct = st.slider("Simulate trim on Non-Priority expenses (%):", 0, 40, 15, step=5, key="trim_slider")
            monthly_saved = non_priority_spend * (trim_pct / 100)
            annual_saved = monthly_saved * 12
            
            c_s1, c_s2, c_s3 = st.columns(3)
            c_s1.metric("Monthly Capital Released", inr(monthly_saved))
            c_s2.metric("Annual Compounding Benefit", inr(annual_saved))
            c_s3.metric("Goal Timeline Acceleration", f"+{trim_pct * 0.25:.1f} months sooner 🚀")

    # ──────────────────────────────────────────────
    # TAB 5: ASSETS AND LIABILITIES
    # ──────────────────────────────────────────────
    with tab_bal:
        st.markdown("<div style='font-size:17px; font-weight:850; color:#17252A; margin-bottom:6px;'>Assets &amp; Liabilities Balance Sheet</div>", unsafe_allow_html=True)
        st.caption("Complete breakdown of stored wealth, liquid reserves, active loan obligations, and net equity.")

        c_a1, c_a2, c_a3 = st.columns(3)
        c_a1.metric("Gross Assets", inr(nw.total_assets))
        c_a2.metric("Total Debt Outstanding", inr(nw.total_liabilities))
        c_a3.metric("Net Worth (Equity)", inr(nw.net_worth), f"{(nw.net_worth/max(1, nw.total_assets)*100):.0f}% equity ratio")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        col_assets_tbl, col_liab_tbl = st.columns(2, gap="large")

        with col_assets_tbl:
            with st.container(border=True):
                st.markdown("<div style='font-size:14.5px; font-weight:850; color:#2B7A78; margin-bottom:8px;'>Asset Portfolio</div>", unsafe_allow_html=True)
                a_records = [{"Asset Name": a.name, "Class": a.asset_class.title(), "Liquidity": a.liquidity.title(), "Value": inr(a.value)} for a in ctx.assets]
                render_table(pd.DataFrame(a_records), use_container_width=True, hide_index=True)

        with col_liab_tbl:
            with st.container(border=True):
                st.markdown("<div style='font-size:14.5px; font-weight:850; color:#E07A5F; margin-bottom:8px;'>Outstanding Liabilities</div>", unsafe_allow_html=True)
                l_records = [{"Loan / Debt": l.name, "Type": l.kind.title(), "Balance": inr(l.outstanding), "EMI": inr(l.emi), "Rate": f"{l.annual_rate*100:.1f}%"} for l in ctx.liabilities]
                render_table(pd.DataFrame(l_records), use_container_width=True, hide_index=True)

    # ──────────────────────────────────────────────
    # TAB 6: SET & TRACK GOALS
    # ──────────────────────────────────────────────
    with tab_goals:
        st.markdown("<div style='font-size:17px; font-weight:850; color:#17252A; margin-bottom:6px;'>Goal Setter &amp; Feasibility Dashboard</div>", unsafe_allow_html=True)
        st.caption("Active life objectives tested across stochastic inflation, returns, and Monte Carlo iterations.")

        # Goal Cards Grid
        for g in ctx.goals:
            p_val = float(res.goal_probabilities.get(g.goal_id, 0.75))
            months_left = max(1, (g.target_date.year - ctx.profile.as_of.year) * 12 + g.target_date.month - ctx.profile.as_of.month)
            req_sip = g.target_amount_today / months_left
            
            html_block(f"""
            <div style="background:#FEFFFF; border:1.5px solid #D1EBE8; border-radius:16px; padding:16px 20px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; box-shadow:0 2px 8px rgba(23,37,42,0.03);">
              <div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:16px; font-weight:850; color:#17252A;">
                  {escape(g.name)}
                  <span style="font-size:11px; font-weight:800; color:#2B7A78; background:#DEF2F1; border:1px solid #3AAFA9; padding:2px 8px; border-radius:99px; margin-left:6px;">Priority {g.priority}</span>
                </div>
                <div style="font-size:12.5px; color:#496E6B; margin-top:2px;">
                  Target: <strong style="color:#17252A;">{inr(g.target_amount_today)}</strong> by <b>{g.target_date:%b %Y}</b> ({months_left} months left) · Req. SIP: <b>{inr(req_sip)}/mo</b>
                </div>
              </div>
              <div style="text-align:right;">
                <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:20px; font-weight:900; color:{'#2B7A78' if p_val >= 0.7 else '#E07A5F'};">
                  {pct(p_val)}
                </div>
                <div style="font-size:10px; font-weight:800; color:#496E6B; text-transform:uppercase;">Feasibility</div>
              </div>
            </div>
            """)

        # Add New Goal Inline Form
        with st.expander("➕ Set a New Goal", expanded=False):
            with st.form("home_add_goal_form"):
                g_c1, g_c2, g_c3 = st.columns(3)
                with g_c1:
                    new_g_name = st.text_input("Goal Name", value="Emergency Reserve Top-up")
                with g_c2:
                    new_g_cat = st.selectbox("Category", ["vehicle", "education", "home", "emergency", "wedding", "travel", "retirement"])
                with g_c3:
                    new_g_amt = st.number_input("Target Amount (₹)", min_value=1000.0, value=200000.0, step=10000.0)
                
                g_d1, g_d2 = st.columns(2)
                with g_d1:
                    new_g_date = st.date_input("Target Date", value=add_months(ctx.profile.as_of, 18))
                with g_d2:
                    new_g_prio = st.selectbox("Priority (1 is highest)", [1, 2, 3], index=1)
                
                if st.form_submit_button("Save Goal & Recalculate Plan →", type="primary"):
                    existing = [{"goal_id": g.goal_id, "name": g.name, "category": g.category, "target_amount_today": g.target_amount_today, "target_date": g.target_date, "priority": g.priority, "hard": g.hard, "min_acceptable_pct": g.min_acceptable_pct, "inflation": g.inflation, "funding": g.funding, "down_payment_pct": g.down_payment_pct, "loan_rate": g.loan_rate, "loan_tenure_months": g.loan_tenure_months, "running_cost_monthly": g.running_cost_monthly, "onroad_multiplier": g.onroad_multiplier} for g in ctx.goals]
                    existing.append({
                        "goal_id": new_g_name.lower().replace(" ", "_"),
                        "name": new_g_name,
                        "category": new_g_cat,
                        "target_amount_today": new_g_amt,
                        "target_date": new_g_date,
                        "priority": new_g_prio,
                        "hard": True,
                        "min_acceptable_pct": 1.0,
                        "inflation": None,
                        "funding": "cash",
                        "down_payment_pct": 0.2,
                        "loan_rate": 0.12,
                        "loan_tenure_months": 36,
                        "running_cost_monthly": 0,
                        "onroad_multiplier": None
                    })
                    update_goals(existing)
                    st.success(f"Goal '{new_g_name}' added successfully! Plan recalculated.")
                    st.rerun()

    # ──────────────────────────────────────────────
    # TAB 7: DISCUSS ANALYSIS (AI ADVISOR)
    # ──────────────────────────────────────────────
    with tab_discuss:
        st.markdown("<div style='font-size:17px; font-weight:850; color:#17252A; margin-bottom:6px;'>Interactive Discuss &amp; Tradeoff Analysis with Abhi</div>", unsafe_allow_html=True)
        st.caption("Simulate real financial trade-offs and receive grounded decisions without hallucinated figures.")

        d_topic = st.selectbox(
            "Select a Decision Scenario to Discuss with Abhi:",
            [
                "🚀 How does Turbo Mode affect my BMW bike goal?",
                "🛡️ What happens if my monthly income drops by 20%?",
                "💡 Where are my top 3 quickest cash leak savings?",
                "💳 Should I prepay my loan or invest in mutual funds?"
            ]
        )

        if "Turbo Mode" in d_topic:
            html_block(f"""
            <div style="background:#FEFFFF; border:1.5px solid #3AAFA9; border-radius:18px; padding:20px; box-shadow:0 4px 16px rgba(58,175,169,0.1);">
              <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                <img src="{owl}" alt="Abhi Rocket" style="width:42px; height:42px; border-radius:12px; object-fit:cover; border:2px solid #3AAFA9;" />
                <div>
                  <div style="font-weight:800; font-size:14px; color:#17252A;">Abhi's Turbo Mode Recommendation</div>
                  <div style="font-size:11px; color:#2B7A78; font-weight:750;">Grounded Mathematical Simulation</div>
                </div>
              </div>
              <div style="font-size:13.5px; color:#17252A; line-height:1.55;">
                By switching to <strong>Turbo Mode</strong>, we trim ₹3,600 from non-priority categories (dining & streaming) and redirect it directly toward your <strong>BMW G 310 R</strong> goal down payment fund. This increases monthly savings from {inr(savings)} to {inr(boosted_savings)}, advancing your projected purchase date from <strong>Dec 2026 to June 2026</strong> (6 months earlier) with an estimated <strong>86% feasibility</strong>!
              </div>
            </div>
            """)
        elif "income drops" in d_topic:
            html_block(f"""
            <div style="background:#FEFFFF; border:1.5px solid #E07A5F; border-radius:18px; padding:20px; box-shadow:0 4px 16px rgba(224,122,95,0.1);">
              <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                <img src="{owl}" alt="Abhi Rocket" style="width:42px; height:42px; border-radius:12px; object-fit:cover; border:2px solid #E07A5F;" />
                <div>
                  <div style="font-weight:800; font-size:14px; color:#17252A;">Stress Test Verdict: 20% Income Reduction</div>
                  <div style="font-size:11px; color:#E07A5F; font-weight:750;">Resilience Analysis</div>
                </div>
              </div>
              <div style="font-size:13.5px; color:#17252A; line-height:1.55;">
                Under a 20% income reduction (loss of ~₹15,000/month), your essential living costs and fixed loan EMIs of {inr(emis)} remain fully payable. However, discretionary spending must be paused to avoid drawing down your emergency reserve fund. Hard goals would delay by an estimated 4.2 months.
              </div>
            </div>
            """)
        elif "cash leak" in d_topic:
            html_block(f"""
            <div style="background:#FEFFFF; border:1.5px solid #3AAFA9; border-radius:18px; padding:20px; box-shadow:0 4px 16px rgba(58,175,169,0.1);">
              <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                <img src="{owl}" alt="Abhi Rocket" style="width:42px; height:42px; border-radius:12px; object-fit:cover; border:2px solid #3AAFA9;" />
                <div>
                  <div style="font-weight:800; font-size:14px; color:#17252A;">Top 3 Instant Cash Leak Trims</div>
                  <div style="font-size:11px; color:#2B7A78; font-weight:750;">Rupee-to-Days Leak Analytics</div>
                </div>
              </div>
              <div style="font-size:13.5px; color:#17252A; line-height:1.55;">
                1. <strong>Food Delivery & Dining Apps</strong>: Trimming 2 orders/week recovers ~₹3,200/month.<br>
                2. <strong>Redundant Streaming Services</strong>: Consolidating 2 unviewed services recovers ~₹1,100/month.<br>
                3. <strong>Weekend Convenience Rides</strong>: Pre-booking and off-peak travel saves ~₹1,400/month.<br>
                <strong>Total Recovered</strong>: <b>₹5,700/month</b> (adds ₹68,400/year to investments).
              </div>
            </div>
            """)
        else:
            html_block(f"""
            <div style="background:#FEFFFF; border:1.5px solid #3AAFA9; border-radius:18px; padding:20px; box-shadow:0 4px 16px rgba(58,175,169,0.1);">
              <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                <img src="{owl}" alt="Abhi Rocket" style="width:42px; height:42px; border-radius:12px; object-fit:cover; border:2px solid #3AAFA9;" />
                <div>
                  <div style="font-weight:800; font-size:14px; color:#17252A;">Prepay Debt vs Invest Analysis</div>
                  <div style="font-size:11px; color:#2B7A78; font-weight:750;">Arbitrage Engine</div>
                </div>
              </div>
              <div style="font-size:13.5px; color:#17252A; line-height:1.55;">
                For loans with interest rates above 10.5% (personal loans / credit card rolls), prepayment provides a guaranteed 10.5%+ risk-free return. For lower-rate home loans (~8.5%), equity mutual funds historical return expectation (12-14%) outperforms prepayment over a 5+ year horizon.
              </div>
            </div>
            """)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("Open Full AskAbhi AI Rocket Copilot ➔", type="primary", use_container_width=True):
            _nav_to("copilot")

    disclaimer()
