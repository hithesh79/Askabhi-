"""AskAbhi self-contained report generation and download."""
from __future__ import annotations
import streamlit as st
from ui.pages._common import page_header,common_context,disclaimer
from core.report import build_report_html

def render():
    ctx,draws,res=common_context()
    page_header("AskAbhi report","Generate a portable financial-resilience report with goal probabilities, assumptions, evidence and limitations.","The downloaded HTML is self-contained and can be printed to PDF without loading external assets.")
    report=build_report_html({"ctx":ctx,"draws":draws})
    st.download_button("Download self-contained HTML report",data=report,file_name="askabhi360_financial_resilience_report.html",mime="text/html",type="primary")
    st.markdown("### Report preview")
    st.markdown(f"**Persona:** {ctx.persona_name}  \n**Financial goals:** {len(ctx.goals)}  \n**Transactions analysed:** {len(ctx.transactions)}  \n**Random-draw fingerprint:** `{draws.fingerprint()}`")
    st.info("The downloaded report contains the current modelled score, goal feasibility, a net-worth chart, assumptions and the educational-planning disclaimer.")
    disclaimer()
