"""Shared page helpers."""
from __future__ import annotations
import streamlit as st
from ui.components import hero, verdict_banner
from ui.state import get_ctx,get_draws,get_baseline,get_session
from core.formatting import inr,pct

def page_header(title,subtitle,verdict=None,tone="info",next_step=None):
    hero(title,subtitle)
    if verdict: verdict_banner(tone,verdict,next_step or "Review the evidence below and change assumptions to test an alternative.")

def common_context(): return get_ctx(),get_draws(),get_baseline()

def goal_options(ctx): return {g.name:g.goal_id for g in ctx.goals}

def disclaimer():
    st.caption("AskAbhi 360 is an educational financial-planning tool, not investment advice. Simulated outcomes depend on assumptions and are not guarantees.")
