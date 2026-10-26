"""First-open onboarding for AskAbhi 360.

The welcome screen introduces Abhi the Owl and clearly distinguishes the
fully working offline planning demo from simulated account feeds and future
live financial integrations.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import streamlit as st
from ui.components import html_block, owl_data_uri, stepper, status_chip
from ui.state import set_persona, replace_transactions


def render() -> None:
    """Render a compact, product-like onboarding experience."""
    owl = owl_data_uri()
    html_block(f"""
    <section class="ab-welcome ab-welcome-v2">
      <div class="ab-welcome-layout" style="display:grid;grid-template-columns:minmax(0,1.1fr) minmax(230px,.9fr);align-items:center;gap:28px">
        <div>
          <div class="ab-kicker" style="color:rgba(255,255,255,0.9); font-weight:800; font-size:11px; letter-spacing:0.08em;">✦ ASKABHI 360 INTELLIGENCE</div>
          <div class="ab-welcome-title" style="color:#FFFFFF; font-weight:900;">Your Money.<br><span style="color:#FFF3D6;">Smarter Decisions.</span></div>
          <div class="ab-welcome-sub" style="color:rgba(255,255,255,0.95); font-size:15px;">One intelligent space to master payments, balance life goals, and build a brighter tomorrow with Abhi 🚀.</div>
          <div class="ab-welcome-actions-note" style="color:rgba(255,255,255,0.9);"><span style="background:rgba(255,255,255,0.25);color:#FFFFFF; font-weight:800;">🚀</span> Built around your real-life choices and financial freedom</div>
        </div>
        <div class="ab-welcome-character">
          <div class="ab-welcome-orbit"></div>
          <div class="ab-welcome-glow"></div>
          <img class="ab-welcome-owl" src="{owl}" alt="Abhi 🚀, your AskAbhi 360 Rocket companion" />
          <div class="ab-welcome-speech" style="background:#FEFFFF; border:1px solid #D1EBE8; box-shadow:0 8px 24px rgba(23,37,42,0.12);"><div class="ab-welcome-speech-title" style="color:#17252A; font-weight:800;">Hey, I'm Abhi 🚀 <span style="color:#3AAFA9;">✦</span></div><div class="ab-welcome-speech-copy" style="color:#496E6B;">Let's launch your brighter financial future, together.</div></div>
        </div>
      </div>
      <div class="ab-welcome-bottomline" style="border-top:1px solid rgba(255,255,255,0.2); color:rgba(255,255,255,0.95);"><span><i style="background:#3AAFA9;box-shadow:0 0 10px #3AAFA9;"></i> Private &amp; Offline Default</span><span><i style="background:#3AAFA9;box-shadow:0 0 10px #3AAFA9;"></i> Evidence-led Insights</span><span><i style="background:#3AAFA9;box-shadow:0 0 10px #3AAFA9;"></i> Goals that Adapt to Life</span></div>
    </section>
    """)
    html_block("""
    <style>
    .ab-welcome-v2{padding:clamp(22px,4vw,44px);min-height:360px;background:linear-gradient(135deg, #17252A 0%, #2B7A78 50%, #3AAFA9 100%);border-radius:24px;box-shadow:0 10px 32px rgba(23,37,42,0.25);}
    .ab-welcome-v2 .ab-welcome-title{font-size:clamp(42px,5.3vw,68px);line-height:.98;max-width:650px;margin:18px 0 16px;font-weight:800;}
    .ab-welcome-character{position:relative;display:flex;align-items:center;justify-content:center;flex-direction:column;min-height:285px;isolation:isolate;}
    .ab-welcome-character .ab-welcome-orbit{position:absolute;inset:8% 6%;background:radial-gradient(circle,rgba(255,255,255,.25),rgba(222,242,241,.15) 42%,transparent 70%);border-radius:50%;}
    .ab-welcome-glow{position:absolute;width:210px;height:210px;border-radius:50%;background:#3AAFA9;opacity:.25;filter:blur(42px);z-index:-1;}
    .ab-welcome-v2 .ab-welcome-owl{width:min(100%,285px);max-height:250px;animation:abhi-float 5s ease-in-out infinite;filter:drop-shadow(0 12px 24px rgba(0,0,0,0.25));}
    .ab-welcome-v2 .ab-welcome-speech{margin-top:-2px;max-width:250px;border-radius:14px;padding:12px 14px;}
    .ab-welcome-actions-note{margin-top:23px;font-size:12px;letter-spacing:.02em;}
    .ab-welcome-actions-note span{display:inline-grid;place-items:center;width:23px;height:23px;border-radius:8px;margin-right:7px;}
    .ab-welcome-bottomline{display:flex;gap:20px;flex-wrap:wrap;margin-top:20px;padding-top:15px;font-size:11px;font-weight:650;}
    .ab-welcome-bottomline span{display:flex;align-items:center;gap:7px}.ab-welcome-bottomline i{display:inline-block;width:6px;height:6px;border-radius:50%;}
    @keyframes abhi-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
    @media(max-width:700px){.ab-welcome-v2 .ab-welcome-layout{grid-template-columns:1fr!important}.ab-welcome-character{min-height:210px}.ab-welcome-v2 .ab-welcome-owl{max-height:190px}.ab-welcome-v2 .ab-welcome-title{font-size:42px}.ab-welcome-bottomline{gap:10px 16px}}
    @media(prefers-reduced-motion:reduce){.ab-welcome-v2 .ab-welcome-owl{animation:none}}
    </style>
    """)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='ab-kicker'>LET'S GET YOU SET UP</div>", unsafe_allow_html=True)
    st.markdown("## Choose your starting point")
    choice = st.radio(
        "Select a profile",
        ["Arjun — salaried", "Meera — freelance", "Import my transactions"],
        horizontal=True,
        key="welcome_choice",
        label_visibility="collapsed",
    )
    if choice.startswith("Arjun"):
        html_block("<div class='ab-card'><div class='ab-card-title'>Arjun · Salaried professional</div><div class='ab-card-sub'>₹95,000 illustrative monthly income · BMW bike, education and home goals · 12 months of synthetic transaction history</div></div>")
    elif choice.startswith("Meera"):
        html_block("<div class='ab-card'><div class='ab-card-title'>Meera · Freelance professional</div><div class='ab-card-sub'>Variable income, lean months and changing expenses · designed to explore safer planning under uncertainty</div></div>")
    else:
        html_block("<div class='ab-card'><div class='ab-card-title'>Bring your financial data</div><div class='ab-card-sub'>Import a transaction CSV to review spending, reconcile transfers and build a personalised plan.</div></div>")
        up = st.file_uploader("Choose transaction CSV", type=["csv"], key="welcome_csv")
        if up is not None:
            st.session_state["welcome_csv_bytes"] = up.getvalue()
        template = Path(__file__).resolve().parents[2] / "data" / "transactions_template.csv"
        if template.exists():
            st.download_button("Download CSV template", template.read_bytes(), "askabhi_transactions_template.csv", "text/csv", key="welcome_download_template")

    c1, c2 = st.columns([1.2, 1])
    with c1:
        if st.button("Build my financial twin  ↗", type="primary", use_container_width=True, key="welcome_build_twin"):
            if choice.startswith("Arjun"):
                set_persona("Arjun")
            elif choice.startswith("Meera"):
                set_persona("Meera")
            else:
                set_persona("Arjun")
                raw = st.session_state.get("welcome_csv_bytes")
                if not raw:
                    st.error("Choose a CSV file first, or select a sample profile.")
                    return
                try:
                    df = pd.read_csv(pd.io.common.BytesIO(raw), encoding="utf-8")
                    replace_transactions(df, "Uploaded CSV")
                except Exception as exc:
                    st.error(f"Could not import CSV: {exc}")
                    return
            st.session_state["onboarded"] = True
            st.session_state["start_here_done"] = []
            st.rerun()
    with c2:
        if st.button("Explore interactive demo", use_container_width=True, key="welcome_demo"):
            set_persona("Arjun")
            st.session_state["onboarded"] = True
            st.session_state["start_here_done"] = []
            st.rerun()
    st.caption("Demo profiles use synthetic data. CSV imports are processed locally. Pay & UPI is a demonstration and does not move money.")
