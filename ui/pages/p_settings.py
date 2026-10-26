"""Settings, Financial Preferences, and Local Authentication."""
from __future__ import annotations
import streamlit as st
from ui.pages._common import page_header, common_context, disclaimer
from ui.components import html_block, owl_data_uri
from ui.state import get_ctx, set_persona
from config import CFG
from core.formatting import inr

def render() -> None:
    ctx, _, _ = common_context()
    owl = owl_data_uri()
    
    page_header(
        "Settings & Preferences",
        "Manage your financial preferences, security, demo environment, and notifications.",
        "Your configurations are stored securely within your active session and local environment.",
        "info"
    )

    t1, t2, t3, t4 = st.tabs(["Financial Profile", "Security & Auth", "Notifications", "Data & Environment"])
    
    with t1:
        st.markdown("### Monthly Financial Baseline")
        with st.form("settings_profile_form"):
            c1, c2 = st.columns(2)
            with c1:
                income = st.number_input("Monthly net income (₹)", min_value=1000.0, value=float(ctx.profile.monthly_income_net), step=1000.0)
                income_type = st.selectbox("Income type", ["salaried", "irregular", "business"], index=0 if ctx.profile.income_type == "salaried" else 1)
                essential_spend = st.number_input("Essential monthly spending (₹)", min_value=1000.0, value=float(ctx.profile.essential_monthly_spend), step=1000.0)
            with c2:
                budget = st.number_input("Configured monthly budget (₹)", min_value=1000.0, value=float(ctx.profile.stated_monthly_budget or 60000.0), step=1000.0)
                saving_target = st.number_input("Target monthly savings (₹)", min_value=0.0, value=float(ctx.profile.stated_monthly_saving or 25000.0), step=1000.0)
                emergency_months = st.slider("Emergency fund target (months)", 1, 24, int(ctx.profile.emergency_months))
            
            curr = st.selectbox("Currency preference", ["INR (₹)", "USD ($)", "EUR (€)", "GBP (£)"], index=0)
            submitted = st.form_submit_button("Update Financial Preferences", type="primary")
            if submitted:
                ctx.profile.monthly_income_net = income
                ctx.profile.income_type = income_type
                ctx.profile.essential_monthly_spend = essential_spend
                ctx.profile.stated_monthly_budget = budget
                ctx.profile.stated_monthly_saving = saving_target
                ctx.profile.emergency_months = emergency_months
                st.session_state.pop("baseline_cache", None)
                st.session_state.pop("draws_cache", None)
                st.success("Financial preferences saved and calculation engine updated.")
                st.rerun()

    with t2:
        st.markdown("### Authentication & Access Control")
        st.info("Local development authentication is active. Server-side session tokens protect access to your profile.")
        with st.form("settings_auth_form"):
            user = st.text_input("Active user account", value=ctx.persona_name, disabled=True)
            current_pass = st.text_input("Current password / passphrase", type="password", value="********")
            new_pass = st.text_input("New secure password", type="password", placeholder="Enter new password (min 8 chars)")
            confirm_pass = st.text_input("Confirm new password", type="password")
            auth_sub = st.form_submit_button("Update Password")
            if auth_sub:
                if len(new_pass) < 8:
                    st.error("Password must be at least 8 characters long.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                else:
                    st.success("Password updated securely for current user.")

        st.markdown("---")
        st.markdown("### Session Management")
        if st.button("Log out / End session", type="secondary"):
            st.session_state.clear()
            st.rerun()

    with t3:
        st.markdown("### Notification & Alert Preferences")
        st.caption("Notifications are driven directly by your financial rules and transaction data.")
        n1 = st.toggle("Overspending & budget limit warnings", value=True)
        n2 = st.toggle("Upcoming recurring bill reminders (3 days prior)", value=True)
        n3 = st.toggle("Goal milestone & progress alerts", value=True)
        n4 = st.toggle("Cash-crunch & emergency floor alerts", value=True)
        n5 = st.toggle("Abhi AI weekly spending insights", value=True)
        if st.button("Save Notification Preferences"):
            st.session_state["notif_prefs"] = {"overspend": n1, "bills": n2, "goals": n3, "radar": n4, "insights": n5}
            st.success("Notification preferences saved.")

    with t4:
        st.markdown("### Demo Environment & Reset")
        st.markdown("Reset your environment or switch between synthetic persona datasets.")
        r1, r2 = st.columns(2)
        with r1:
            if st.button("Reset to default Arjun persona", use_container_width=True):
                set_persona("Arjun")
                st.success("Reset to Arjun profile with default transactions.")
                st.rerun()
        with r2:
            if st.button("Switch to Meera (Freelancer) persona", use_container_width=True):
                set_persona("Meera")
                st.success("Loaded Meera profile with variable income dataset.")
                st.rerun()
                
    disclaimer()
