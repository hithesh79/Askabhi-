"""Regression checks for the AskAbhi 360 Neo-Mint Noir visual system."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import pandas as pd

from ui.charts import fan_chart, heatmap, radar_chart, tornado

ROOT = Path(__file__).resolve().parents[1]


def test_streamlit_theme_uses_warm_palette():
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    css = (ROOT / "ui" / "theme.py").read_text(encoding="utf-8")
    assert 'primaryColor = "#5f259f"' in config or 'primaryColor = "#5F259F"' in config
    assert 'backgroundColor = "#f4f4f8"' in config or 'backgroundColor = "#F4F4F8"' in config
    assert "--pp-purple" in css or "--pp-purple-light" in css
    assert "@import url('https://fonts.googleapis.com/css2" in css


def test_owl_and_wordmark_svg_are_well_formed():
    owl = ET.parse(ROOT / "assets" / "abhi_owl.svg").getroot()
    mark = ET.parse(ROOT / "assets" / "askabhi360_mark.svg").getroot()
    assert owl.tag.endswith("svg")
    assert mark.tag.endswith("svg")
    owl_text = (ROOT / "assets" / "abhi_owl.svg").read_text(encoding="utf-8")
    assert "Abhi" in owl_text


def test_fan_chart_serializes_with_dark_theme():
    result = SimpleNamespace(
        months=[date(2027, 1, 1), date(2027, 2, 1), date(2027, 3, 1)],
        net_worth_p10=[100, 110, 120],
        net_worth_p25=[120, 130, 140],
        net_worth_p50=[140, 150, 160],
        net_worth_p75=[160, 170, 180],
        net_worth_p90=[180, 190, 200],
    )
    fig = fan_chart(result, emergency_floor=80)
    assert fig.layout.paper_bgcolor == "rgba(0,0,0,0)"
    assert len(fig.data) >= 5
    fig.to_json()


def test_heatmap_serializes_with_valid_plotly_colorbar_contract():
    frame = pd.DataFrame([[0.0, 0.1], [0.2, 0.0]], index=["Bike", "Home"], columns=["Bike", "Home"])
    fig = heatmap(frame)
    payload = fig.to_json()
    assert "Goal conflict map" in payload
    assert "C85A32" in payload or "Drop" in payload


def test_tornado_and_radar_charts_serialize():
    tornado_df = pd.DataFrame({"assumption": ["Income", "Expenses"], "low_effect_pp": [-12, -8], "high_effect_pp": [9, 6]})
    radar_df = pd.DataFrame({"dimension": ["Savings", "Liquidity"], "p10": [30, 40], "p50": [50, 60], "p90": [70, 80]})
    tornado_fig = tornado(tornado_df)
    radar_fig = radar_chart(radar_df)
    assert len(tornado_fig.data) == 2
    assert len(radar_fig.data) == 3
    tornado_fig.to_json()
    radar_fig.to_json()
