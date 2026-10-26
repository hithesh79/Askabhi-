"""AskAbhi AI Financial Copilot with Abhi Owl mascot and interactive prompt cards."""
from __future__ import annotations
import streamlit as st
from ui.pages._common import page_header, common_context, disclaimer
from ui.components import proof_drawer, status_chip, html_block, owl_data_uri
from ui.state import get_session
from core.copilot.offline import answer as offline_answer
from core.copilot.llm import available, answer_llm
from core.formatting import inr

def _run_question(question):
    session = get_session()
    use_llm = st.session_state.get("copilot_llm_toggle", False) and available()
    return answer_llm(question, session) if use_llm else offline_answer(question, session)

def render():
    ctx, draws, res = common_context()
    owl = owl_data_uri()

    # Spacious Top Abhi Assistant Welcome Banner (Teal & Noir)
    html_block(f"""
    <div style="background:linear-gradient(135deg, #17252A 0%, #2B7A78 60%, #3AAFA9 100%); border-radius:22px; padding:24px 28px; box-shadow:0 8px 28px rgba(23,37,42,0.18); display:flex; align-items:center; gap:20px; margin-bottom:20px; flex-wrap:wrap; color:#FEFFFF;">
      <img src="{owl}" alt="Abhi Rocket" style="width:64px; height:64px; max-width:64px; max-height:64px; border-radius:18px; object-fit:cover; border:2.5px solid #3AAFA9; background:#FEFFFF; box-shadow:0 6px 16px rgba(0,0,0,0.25); flex-shrink:0;" />
      <div style="flex:1; min-width:260px;">
        <div style="font-size:11.5px; font-weight:800; color:#DEF2F1; letter-spacing:0.08em; text-transform:uppercase;">✦ AskAbhi Rocket Copilot · Real-Time Financial Intelligence</div>
        <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size:24px; font-weight:900; color:#FEFFFF; margin-top:2px;">Hi, {ctx.persona_name}! I'm Abhi 🚀, your financial copilot.</div>
        <div style="font-size:14px; color:#DEF2F1; margin-top:4px; line-height:1.5; opacity:0.95;">Ask me anything about your money, goals, EMI affordability, or spending leaks!</div>
      </div>
    </div>
    """)

    # Suggested Prompts
    st.markdown("<div style='font-size:15px; font-weight:850; color:#17252A; margin-bottom:10px;'>💡 Example Prompts to Get Started:</div>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3, gap="medium")
    with s1:
        if st.button("🛵 Can I afford a ₹4.5 lakh bike?", key="cp_q1", use_container_width=True):
            st.session_state["pending_q"] = "Can I afford a ₹4.5 lakh BMW bike?"
            st.rerun()
        if st.button("🌱 How can I save more money?", key="cp_q2", use_container_width=True):
            st.session_state["pending_q"] = "How can I increase my monthly savings?"
            st.rerun()
    with s2:
        if st.button("📉 Which expenses can I reduce?", key="cp_q3", use_container_width=True):
            st.session_state["pending_q"] = "Which expenses increased or are leaking money?"
            st.rerun()
        if st.button("📊 Show me my financial health", key="cp_q4", use_container_width=True):
            st.session_state["pending_q"] = "How resilient is my financial plan and health score?"
            st.rerun()
    with s3:
        if st.button("🏡 Create a plan for a house goal", key="cp_q5", use_container_width=True):
            st.session_state["pending_q"] = "How much should I save monthly for a house down payment?"
            st.rerun()
        if st.button("⚡ What if my income drops 20%?", key="cp_q6", use_container_width=True):
            st.session_state["pending_q"] = "What happens if my income drops 20% for 6 months?"
            st.rerun()

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # LLM Toggle Option
    if available():
        st.success("OpenAI API key configured.")
    else:
        st.caption("✦ Offline deterministic engine is active. Predefined intents and exact financial calculations ensure privacy and zero hallucinations.")
    
    # Conversation History
    history = st.session_state.setdefault("copilot_history", [])
    pending = st.session_state.pop("pending_q", None)
    if pending:
        history.append({"role": "user", "content": pending})
        history.append({"role": "assistant", "answer": _run_question(pending)})

    for entry in history[-20:]:
        if entry["role"] == "user":
            with st.chat_message("user"):
                st.markdown(f"<div style='font-size:15px; font-weight:600; color:#17252A;'>{entry['content']}</div>", unsafe_allow_html=True)
        else:
            ans = entry["answer"]
            with st.chat_message("assistant", avatar=owl):
                st.markdown(f"### {ans.verdict}")
                for item in ans.evidence:
                    st.markdown(f"• {item}")
                if ans.actions:
                    st.markdown("<div style='font-weight:800; font-size:14px; margin-top:8px;'>Recommended Next Steps:</div>", unsafe_allow_html=True)
                    for item in ans.actions:
                        st.markdown(f"• {item}")
                st.caption(f"💡 {ans.caveat}")
                status_chip("ok" if ans.numbers_verified else "warning", f"{ans.mode} · numbers grounded in engine evidence")
                with st.expander("Evidence Trail & Math Proof"):
                    for result in ans.tool_results:
                        st.markdown(f"**Tool:** `{result.evidence.get('tool','')}`")
                        st.json(result.evidence, expanded=False)
                    st.code(f"seed={draws.seed} | fingerprint={draws.fingerprint()}", language="text")

    # Input Box
    q = st.chat_input("Ask Abhi anything about your money...", key="copilot_chat_input")
    if q:
        history.append({"role": "user", "content": q})
        with st.spinner("Analyzing your financial data and simulating outcome..."):
            ans = _run_question(q)
        history.append({"role": "assistant", "answer": ans})
        st.rerun()

    if history:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Conversation", key="clear_copilot_history"):
            st.session_state["copilot_history"] = []
            st.rerun()

    disclaimer()
