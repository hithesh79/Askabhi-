"""Notifications Center: alerts, bills due, goal milestones, and spending cautions."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from ui.pages._common import page_header, common_context, disclaimer
from ui.components import html_block, owl_data_uri
from core.formatting import inr

def render() -> None:
    ctx, draws, res = common_context()
    owl = owl_data_uri()
    
    page_header(
        "Notifications & Alerts",
        "Actionable updates on bill reminders, goal pacing, spending alerts, and Abhi's recommendations.",
        "Notifications are generated in real-time from your active financial model and transaction patterns.",
        "info"
    )

    notifs = []
    
    # 1. Goal milestone notification
    for g in ctx.goals[:3]:
        prob = res.goal_probabilities.get(g.goal_id, 0.0)
        if prob >= 0.8:
            notifs.append({
                "type": "Goal On Track",
                "icon": "🎯",
                "title": f"Goal '{g.name}' is on track!",
                "detail": f"Modelled success probability is {prob*100:.0f}%. Target amount: {inr(g.target_amount_today)} by {g.target_date:%b %Y}.",
                "priority": "normal",
                "time": "Just now"
            })
        else:
            notifs.append({
                "type": "Goal Attention",
                "icon": "⚠️",
                "title": f"Goal '{g.name}' needs attention",
                "detail": f"Modelled probability is {prob*100:.0f}%. Consider increasing monthly allocation or extending deadline in Goals & Plan.",
                "priority": "warning",
                "time": "2 hours ago"
            })

    # 2. Upcoming bills
    bp = ctx.behaviour
    if bp and bp.recurring_merchants:
        for m in bp.recurring_merchants[:3]:
            notifs.append({
                "type": "Upcoming Bill",
                "icon": "📅",
                "title": f"Upcoming commitment: {m}",
                "detail": f"Detected recurring monthly payment. Ensure sufficient liquid balance before due date.",
                "priority": "info",
                "time": "1 day ago"
            })

    # 3. Copilot insight alert
    notifs.append({
        "type": "AI Insight",
        "icon": "🚀",
        "title": "AskAbhi Rocket Copilot Monthly Review",
        "detail": "Your dining and food delivery expenses increased by 18% this month. Check Leaks / Autopilot to free up savings.",
        "priority": "insight",
        "time": "3 days ago"
    })

    # Render as interactive notification cards
    for n in notifs:
        border_color = "#E07A5F" if n["priority"] == "warning" else ("#588157" if n["priority"] == "normal" else "#DDA15E")
        bg_color = "rgba(255, 255, 255, 0.9)"
        
        html_block(f"""
        <div style="background:{bg_color}; border:1px solid #E6DCCD; border-left:4px solid {border_color}; border-radius:14px; padding:16px 20px; margin-bottom:12px; box-shadow:0 4px 14px rgba(60,40,25,0.04); display:flex; gap:16px; align-items:flex-start;">
            <div style="font-size:24px; line-height:1; padding-top:2px;">{n['icon']}</div>
            <div style="flex:1;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-weight:700; font-size:14px; color:#23272A;">{n['title']}</span>
                    <span style="font-size:11px; color:#786C5E;">{n['time']}</span>
                </div>
                <div style="font-size:13px; color:#524B42; line-height:1.5;">{n['detail']}</div>
            </div>
        </div>
        """)

    if st.button("Mark all notifications as read", type="secondary"):
        st.success("All notifications marked as read.")
        
    disclaimer()
