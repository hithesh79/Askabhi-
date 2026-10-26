"""Streamlit Community Cloud Entry Point for AskAbhi 360.

This file serves as a transparent runner for app.py so that both default
'streamlit_app.py' and 'app.py' entry points work out of the box on Streamlit Cloud.
"""
from __future__ import annotations
import runpy
from pathlib import Path

if __name__ == "__main__":
    app_path = Path(__file__).resolve().parent / "app.py"
    runpy.run_path(str(app_path), run_name="__main__")
