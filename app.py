"""AskAbhi 360 Application Shell.

Clean, organized navigation hierarchy, safe routing, compact sidebar,
and developer controls consolidated cleanly in an expander.
"""
from __future__ import annotations
from datetime import date
import pandas as pd
import streamlit as st
from config import CFG
from ui.theme import inject_css
from ui.state import get_ctx, get_draws, get_baseline, set_persona, ROOT, DATA_DIR
from ui.components import status_chip, owl_data_uri
from ui.tables import render_table
from core.models import ScenarioParams
from core.simulate import simulate
from core.formatting import pct, inr
from core.data_gen import add_months
from ui.pages import (
    p_welcome, p_home, p_afford, p_money, p_plan, p_autopilot,
    p_leaks, p_radar, p_chaos, p_repair, p_timemachine, p_sensitivity,
    p_copilot, p_trust, p_report, p_payments, p_transactions,
    p_settings, p_notifications
)

st.set_page_config(
    page_title="AskAbhi 360 · Your Financial Rocket Copilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_css()

try:
    st.logo(str(ROOT / "assets" / "askabhi_logo.jpg"), icon_image=str(ROOT / "assets" / "abhi_mascot.jpg"))
except Exception:
    pass

# Session State Initialization
if "seed" not in st.session_state: st.session_state["seed"] = CFG.default_seed
if "n_sims" not in st.session_state: st.session_state["n_sims"] = CFG.default_n_sims
if "onboarded" not in st.session_state:
    set_persona("Arjun")
    st.session_state["onboarded"] = True

try: skip_intro = st.query_params.get("skip") == "1"
except Exception: skip_intro = False
if skip_intro and not st.session_state.get("onboarded"):
    set_persona("Arjun"); st.session_state["onboarded"] = True

if not st.session_state.get("onboarded", False):
    welcome = st.Page(p_welcome.render, title="Welcome", icon="🚀", url_path="welcome", default=True)
    st.navigation([welcome], position="hidden").run()
else:
    # Page references registered with explicit endpoints
    page_refs = {
        "home": st.Page(p_home.render, title="Dashboard", icon="🏠", url_path="home", default=True),
        "notifications": st.Page(p_notifications.render, title="Notifications", icon="🔔", url_path="notifications"),
        "payments": st.Page(p_payments.render, title="UPI Payments", icon="💸", url_path="payments"),
        "transactions": st.Page(p_transactions.render, title="Transactions", icon="📑", url_path="transactions"),
        "money": st.Page(p_money.render, title="My Money", icon="💠", url_path="money"),
        "plan": st.Page(p_plan.render, title="Goals & Planning", icon="🎯", url_path="goals"),
        "afford": st.Page(p_afford.render, title="Can I Afford It?", icon="🧮", url_path="afford"),
        "autopilot": st.Page(p_autopilot.render, title="Payday Autopilot", icon="⚖️", url_path="autopilot"),
        "copilot": st.Page(p_copilot.render, title="AskAbhi AI Rocket", icon="🚀", url_path="copilot"),
        "chaos": st.Page(p_chaos.render, title="Financial Stress Test", icon="⚡", url_path="chaos"),
        "report": st.Page(p_report.render, title="Reports", icon="📊", url_path="report"),
        "settings": st.Page(p_settings.render, title="Settings & Profile", icon="⚙️", url_path="settings"),
        "trust": st.Page(p_trust.render, title="Trust Center", icon="🔒", url_path="trust"),
    }
    # Make page references available for navigation from any page
    st.session_state["_page_refs"] = page_refs

    # Clean, 5-group organized navigation hierarchy
    nav = st.navigation({
        "CORE OVERVIEW": [page_refs["home"], page_refs["notifications"]],
        "PAYMENTS & TRANSACTIONS": [page_refs["payments"], page_refs["transactions"], page_refs["money"]],
        "PLAN AND DECIDE": [page_refs["plan"], page_refs["afford"], page_refs["autopilot"]],
        "INTELLIGENCE": [page_refs["copilot"], page_refs["chaos"], page_refs["report"]],
        "SETTINGS & PREFERENCES": [page_refs["settings"], page_refs["trust"]],
    }, position="sidebar")

    ctx = get_ctx()

    with st.sidebar:
        owl = owl_data_uri()
        # Brand Identity Matching Official Master Kit
        st.markdown(f"""
        <div class='ab-brand' style="display:flex; align-items:center; gap:12px; margin-bottom:14px; padding:4px 0;">
          <div class='ab-brand-icon' style="background:linear-gradient(135deg, #3AAFA9, #2B7A78); border-radius:14px; padding:3px; box-shadow:0 4px 14px rgba(58,175,169,0.35); flex-shrink:0;">
            <img src='{owl}' alt='Abhi Rocket' style='width:40px;height:40px;border-radius:10px;object-fit:cover'>
          </div>
          <div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:18px; font-weight:900; color:#17252A; line-height:1.2; letter-spacing:-0.02em;">AskAbhi <span style="color:#3AAFA9;">360</span></div>
            <div style="font-size:9.5px; font-weight:800; color:#2B7A78; letter-spacing:0.06em; text-transform:uppercase;">Financial Rocket Copilot 🚀</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        # User Mini Profile Card
        st.markdown(f"""
        <div style="background:#FEFFFF; border:1px solid #D1EBE8; border-radius:12px; padding:10px 12px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 6px rgba(23,37,42,0.04);">
          <div>
            <div style="font-size:12.5px; font-weight:800; color:#17252A;">{ctx.persona_name}</div>
            <div style="font-size:10px; color:#496E6B;">{ctx.profile.income_type.title()} · Active</div>
          </div>
          <span style="background:#DEF2F1; color:#2B7A78; border:1px solid #3AAFA9; font-size:10px; font-weight:800; padding:2px 8px; border-radius:99px;">PRO ✦</span>
        </div>
        """, unsafe_allow_html=True)

        # Developer / Testing Controls Consolidated in an Expander
        with st.expander("🛠️ Demo & Simulation Settings", expanded=False):
            st.caption("Change demo profile, random seed, or simulation iterations:")
            persona = st.selectbox("Active persona", ["Arjun", "Meera"], index=0 if ctx.persona_name.lower().startswith("arjun") else 1, key="persona_selection")
            if persona != ctx.persona_name and persona in ("Arjun", "Meera"):
                set_persona(persona)
                st.rerun()
            
            seed = st.number_input("Random seed", min_value=0, max_value=2**31-1, value=int(st.session_state.get("seed", CFG.default_seed)), step=1, key="seed_input")
            sims = st.select_slider("Simulation iterations", options=[500, 1000, 2000, 5000], value=int(st.session_state.get("n_sims", CFG.default_n_sims)), key="n_sims_input")
            if int(seed) != int(st.session_state.get("seed", CFG.default_seed)) or int(sims) != int(st.session_state.get("n_sims", CFG.default_n_sims)):
                st.session_state["seed"] = int(seed)
                st.session_state["n_sims"] = int(sims)
                st.session_state.pop("draws_cache", None)
                st.session_state.pop("baseline_cache", None)
                st.rerun()

            template = DATA_DIR / "transactions_template.csv"
            if template.exists():
                st.download_button("Download CSV Template", template.read_bytes(), file_name="transactions_template.csv", mime="text/csv")

        st.caption("✦ Educational personal finance platform. Zero real banking credentials stored.")

    nav.run()
