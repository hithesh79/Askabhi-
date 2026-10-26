"""Optional Streamlit application smoke test.

The core suite remains runnable without Streamlit. When Streamlit is installed,
AppTest checks that the actual app entry point starts without an exception.
"""
from __future__ import annotations

import importlib.util
import pytest


@pytest.mark.skipif(importlib.util.find_spec("streamlit") is None, reason="Streamlit is not installed in this environment")
def test_app_starts_without_streamlit_exception():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file("app.py", default_timeout=30).run()
    assert not app.exception
