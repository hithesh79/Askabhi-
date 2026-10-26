"""Accessible HTML tables and widget-based editors that avoid Streamlit Arrow DLLs.

Some managed Windows environments block pyarrow native libraries. These helpers
render Pandas results as escaped HTML and edit important financial records with
native Streamlit widgets, avoiding st.dataframe/st.data_editor's Arrow path.
"""
from __future__ import annotations
from datetime import date, datetime
from html import escape
from typing import Any
import pandas as pd
import streamlit as st


def render_table(data: Any, *args: Any, **kwargs: Any) -> None:
    """Render tabular results as a responsive, escaped HTML table (no PyArrow)."""
    hide_index = bool(kwargs.get("hide_index", False))
    max_height = kwargs.get("height", 420)
    try:
        if data.__class__.__name__ == "Styler" and hasattr(data, "data"):
            frame = data.data.copy()
        elif isinstance(data, pd.DataFrame):
            frame = data.copy()
        elif data is None:
            frame = pd.DataFrame()
        else:
            frame = pd.DataFrame(data)
    except Exception:
        frame = pd.DataFrame({"Value": [str(data)]})
    if frame.empty:
        st.caption("No records to display.")
        return
    # Render safe HTML only; escape every supplied value and header.
    table = frame.to_html(index=not hide_index, escape=True, border=0, classes="ab-data-table", na_rep="—")
    custom_height = kwargs.get("height", None)
    if custom_height:
        try:
            h = max(180, min(900, int(custom_height)))
            height_style = f"max-height: {h}px; overflow-y: auto;"
        except (TypeError, ValueError):
            height_style = "max-height: 440px; overflow-y: auto;"
    elif len(frame) > 12:
        height_style = "max-height: 480px; overflow-y: auto;"
    else:
        height_style = "overflow-y: visible;"

    st.markdown(
        f'<div class="ab-table-wrap" style="{height_style} overflow-x: auto; clear: both; margin: 14px 0 24px 0; position: relative;">{table}</div>'
        f'<div class="ab-table-clear" style="clear: both; height: 12px;"></div>',
        unsafe_allow_html=True,
    )


def edit_records(
    frame: pd.DataFrame,
    key: str,
    *,
    select_options: dict[str, list[Any]] | None = None,
    date_columns: list[str] | None = None,
    bool_columns: list[str] | None = None,
    hidden_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Edit each record using native widgets and return a DataFrame.

    This intentionally trades the spreadsheet-like Arrow grid for dependable,
    accessible per-record controls. Original values are maintained in widget
    state during reruns; non-editable/hidden IDs are preserved.
    """
    select_options = select_options or {}
    date_columns = set(date_columns or [])
    bool_columns = set(bool_columns or [])
    hidden_columns = set(hidden_columns or [])
    if frame is None or frame.empty:
        st.info("No records yet. Use the add form below to create one.")
        return pd.DataFrame(columns=list(frame.columns) if frame is not None else [])

    records: list[dict[str, Any]] = []
    for row_idx, (_, row) in enumerate(frame.iterrows()):
        initial_name = str(row.get("name", row.get("goal", row.get("goal_id", f"Record {row_idx + 1}"))))
        with st.expander(f"{row_idx + 1:02d}  ·  {initial_name}", expanded=False):
            record: dict[str, Any] = {}
            visible = [col for col in frame.columns if col not in hidden_columns]
            for start in range(0, len(visible), 3):
                group = visible[start:start + 3]
                cols = st.columns(len(group))
                for col_ui, field in zip(cols, group):
                    raw = row[field]
                    widget_key = f"{key}_{row_idx}_{field}"
                    with col_ui:
                        if field in select_options:
                            choices = select_options[field]
                            default = raw
                            try:
                                index = choices.index(default)
                            except (ValueError, TypeError):
                                index = 0
                            value = st.selectbox(field.replace("_", " ").title(), choices, index=index, key=widget_key)
                        elif field in bool_columns or isinstance(raw, bool):
                            value = st.checkbox(field.replace("_", " ").title(), value=bool(raw), key=widget_key)
                        elif field in date_columns:
                            try:
                                parsed = pd.to_datetime(raw, errors="coerce")
                                default_date = parsed.date() if not pd.isna(parsed) else date.today()
                            except Exception:
                                default_date = date.today()
                            value = st.date_input(field.replace("_", " ").title(), value=default_date, key=widget_key)
                        elif pd.api.types.is_numeric_dtype(type(raw)) or isinstance(raw, (int, float)):
                            try:
                                number = float(raw) if pd.notna(raw) else 0.0
                            except (TypeError, ValueError):
                                number = 0.0
                            if isinstance(raw, int) and not isinstance(raw, bool):
                                value = st.number_input(field.replace("_", " ").title(), value=int(number), step=1, key=widget_key)
                            else:
                                value = st.number_input(field.replace("_", " ").title(), value=number, step=0.01 if abs(number) < 1 else 100.0, format="%.4f" if any(x in field.lower() for x in ("rate", "pct", "inflation", "vol", "return")) else "%.2f", key=widget_key)
                        else:
                            default_text = "" if pd.isna(raw) else str(raw)
                            value = st.text_input(field.replace("_", " ").title(), value=default_text, key=widget_key)
                        record[field] = value
            # Keep IDs or intentionally hidden fields unchanged.
            for field in hidden_columns:
                if field in row:
                    record[field] = row[field]
            records.append(record)
    return pd.DataFrame(records, columns=list(frame.columns))
