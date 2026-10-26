"""Plotly charts styled in the official PhonePe purple and white fintech palette."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

PP_PALETTE = {
    "purple": "#5F259F",
    "purple_light": "#6739B7",
    "purple_soft": "#F2EAFA",
    "charcoal": "#1D162B",
    "muted": "#6B627A",
    "green": "#1B9E5A",
    "green_soft": "#E9F7F0",
    "grid": "rgba(220, 215, 230, 0.45)",
    "pie_colors": ["#5F259F", "#6739B7", "#8E44AD", "#1B9E5A", "#2196F3", "#FF9800", "#78909C"]
}


def _base(fig, height=280):
    """Apply the PhonePe purple chart styling with auto-fitting width."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255, 255, 255, 0.7)",
        font={"family": "Plus Jakarta Sans, sans-serif", "color": PP_PALETTE["charcoal"], "size": 11},
        height=height,
        autosize=True,
        margin={"l": 15, "r": 15, "t": 35, "b": 25},
        legend={"orientation": "h", "y": 1.15, "font": {"color": PP_PALETTE["charcoal"]}},
        xaxis={"gridcolor": PP_PALETTE["grid"], "zerolinecolor": PP_PALETTE["grid"], "ticks": "outside", "tickfont": {"color": PP_PALETTE["muted"]}},
        yaxis={"gridcolor": PP_PALETTE["grid"], "zerolinecolor": PP_PALETTE["grid"], "ticks": "outside", "tickfont": {"color": PP_PALETTE["muted"]}},
        hoverlabel={"bgcolor": "#FFFFFF", "bordercolor": "#E2CEF7", "font": {"color": PP_PALETTE["charcoal"]}},
    )
    return fig


def fan_chart(res, emergency_floor=None, goal_markers=None):
    """Show the range and median of simulated future net worth."""
    x = [d.strftime("%b %y") for d in res.months]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=res.net_worth_p90, mode="lines", line={"width": 0}, showlegend=False, name="P90"))
    fig.add_trace(go.Scatter(x=x, y=res.net_worth_p10, mode="lines", line={"width": 0}, fill="tonexty", fillcolor="rgba(95,37,159,0.08)", name="P10–P90 range"))
    fig.add_trace(go.Scatter(x=x, y=res.net_worth_p75, mode="lines", line={"width": 0}, showlegend=False, name="P75"))
    fig.add_trace(go.Scatter(x=x, y=res.net_worth_p25, mode="lines", line={"width": 0}, fill="tonexty", fillcolor="rgba(95,37,159,0.18)", name="P25–P75 range"))
    fig.add_trace(go.Scatter(x=x, y=res.net_worth_p50, mode="lines", line={"color": PP_PALETTE["purple"], "width": 2.5}, name="Median (P50)"))
    if emergency_floor is not None:
        fig.add_hline(y=emergency_floor, line_dash="dash", line_color=PP_PALETTE["green"], annotation_text="Emergency floor", annotation_font_color=PP_PALETTE["green"])
    if goal_markers:
        for marker in goal_markers:
            fig.add_vline(x=marker, line_dash="dot", line_color=PP_PALETTE["purple_light"])
    return _base(fig, 320).update_layout(title="Future net worth · modelled ranges", yaxis_title="INR")


def spending_overview_chart(months: list[str], spend_values: list[float]):
    """Bar chart for Monthly spending overview in PhonePe purple."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months,
        y=spend_values,
        marker_color=PP_PALETTE["purple"],
        marker_line_width=0,
        opacity=0.9,
        name="Monthly Spend"
    ))
    return _base(fig, 240).update_layout(
        title="Monthly Spending Trend",
        yaxis_title="₹",
        xaxis_title=""
    )


def category_donut_chart(categories: dict[str, float]):
    """Donut chart for expense category breakdown."""
    labels = list(categories.keys())
    values = list(categories.values())
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker_colors=PP_PALETTE["pie_colors"][:len(labels)],
        textinfo='percent',
        insidetextorientation='radial'
    )])
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Plus Jakarta Sans, sans-serif", "color": PP_PALETTE["charcoal"]},
        height=240,
        autosize=True,
        margin={"l": 10, "r": 10, "t": 25, "b": 10},
        showlegend=True,
        legend={"orientation": "v", "x": 1.02, "y": 0.5, "font": {"size": 10}}
    )
    return fig


def waterfall(bp, profile):
    """Show monthly money allocation as category bars."""
    from core.behaviour import money_waterfall
    df = money_waterfall(bp, profile)
    palette = [PP_PALETTE["purple"], PP_PALETTE["purple_light"], PP_PALETTE["green"], "#2196F3", "#78909C"]
    fig = px.bar(df, x="bucket", y="amount", color="bucket", title="Monthly financial flow · estimates", color_discrete_sequence=palette)
    return _base(fig, 280).update_layout(showlegend=False, yaxis_title="INR", xaxis_title="")


def tornado(df):
    """Show goal-probability sensitivity for lower and higher assumptions."""
    if df.empty:
        return _base(go.Figure(), 260)
    fig = go.Figure()
    fig.add_trace(go.Bar(y=df["assumption"], x=df["low_effect_pp"], orientation="h", name="Lower case (pp)", marker_color=PP_PALETTE["purple_soft"], marker_line_width=0))
    fig.add_trace(go.Bar(y=df["assumption"], x=df["high_effect_pp"], orientation="h", name="Higher case (pp)", marker_color=PP_PALETTE["purple"], marker_line_width=0))
    return _base(fig, max(260, 36 * len(df))).update_layout(barmode="relative", title="What really matters · same-draw sensitivity", xaxis_title="Percentage points change")


def heatmap(df):
    """Show how one goal's presence changes another goal's success probability."""
    if df.empty:
        return _base(go.Figure(), 260)
    fig = go.Figure(go.Heatmap(z=df.values, x=list(df.columns), y=list(df.index), colorscale=[[0, "#FFFFFF"], [0.5, "#F2EAFA"], [1, "#5F259F"]], zmin=0, zmax=max(.01, float(np.nanmax(df.values))), colorbar={"title": {"text": "Drop", "font": {"color": PP_PALETTE["charcoal"]}}, "tickfont": {"color": PP_PALETTE["muted"]}}, hoverongaps=False))
    return _base(fig, max(260, 38 * len(df))).update_layout(title="Goal conflict map · leave-one-out effect")


def radar_chart(df):
    """Show lower, median and upper resilience dimensions."""
    if df.empty:
        return _base(go.Figure(), 280)
    colors = {"p10": PP_PALETTE["purple_light"], "p50": PP_PALETTE["purple"], "p90": PP_PALETTE["green"]}
    fig = go.Figure()
    for key in ("p10", "p50", "p90"):
        if key in df:
            fig.add_trace(go.Scatterpolar(r=df[key], theta=df["dimension"], fill="toself" if key == "p50" else None, name=key.upper(), line={"color": colors[key], "width": 2}, fillcolor="rgba(95,37,159,0.14)" if key == "p50" else None))
    return _base(fig, 280).update_layout(polar={"bgcolor": "rgba(255,255,255,0.7)", "radialaxis": {"gridcolor": PP_PALETTE["grid"], "tickfont": {"color": PP_PALETTE["muted"]}, "linecolor": PP_PALETTE["grid"]}, "angularaxis": {"gridcolor": PP_PALETTE["grid"], "linecolor": PP_PALETTE["grid"], "tickfont": {"color": PP_PALETTE["charcoal"]}}})
