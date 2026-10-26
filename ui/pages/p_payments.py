"""AskAbhi 360 UPI & Payments: Master Fintech Experience with Dynamic Payment Animations."""
from __future__ import annotations
from datetime import datetime
from html import escape
import re
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from ui.tables import render_table
from ui.pages._common import common_context, disclaimer
from ui.components import html_block, owl_data_uri, qr_code_svg
from core.formatting import inr


def _valid_upi_id(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9._-]{2,256}@[A-Za-z][A-Za-z0-9.-]{1,63}", value.strip()))


def _record(mode: str, recipient: str, amount: float, note: str, identifier: str = "") -> dict:
    payments = st.session_state.setdefault("askabhi_demo_payments", [])
    entry = {
        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "mode": mode,
        "recipient": recipient.strip(),
        "upi_id": identifier.strip(),
        "amount": float(amount),
        "note": note.strip(),
        "status": "COMPLETED · SUCCESS",
        "reference": f"UPI-{len(payments) + 10001:05d}",
    }
    payments.insert(0, entry)
    
    # Also deduct from demo wallet balance
    curr_wallet = st.session_state.get("demo_wallet_balance", 25400.0)
    st.session_state["demo_wallet_balance"] = max(0.0, curr_wallet - float(amount))
    st.session_state["askabhi_last_demo_payment"] = entry
    # Trigger celebratory payment animation modal
    st.session_state["payment_celebration"] = entry
    return entry


def _render_celebration_overlay(payment: dict) -> None:
    """Render full celebratory payment animation with confetti, animated checkmark & sound."""
    amt_formatted = inr(payment["amount"])
    recipient = escape(payment.get("recipient", "Recipient"))
    ref = escape(payment.get("reference", "UPI-10001"))
    dt = escape(payment.get("created_at", "Just now"))
    mode = escape(payment.get("mode", "UPI Instant Transfer"))
    note = escape(payment.get("note", "Instant settlement"))

    # Confetti & Audio Component
    components.html(
        f"""
        <canvas id="ab-confetti-canvas" style="position:fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; z-index:999999;"></canvas>
        <script>
        (function() {{
            const pWin = window.parent;
            if (pWin && pWin.askabhi_play_success) {{
                pWin.askabhi_play_success();
                setTimeout(() => {{ if (pWin.askabhi_play_coins) pWin.askabhi_play_coins(); }}, 180);
            }}
            
            // Confetti Physics Explosion
            const canvas = document.getElementById("ab-confetti-canvas");
            if (!canvas) return;
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            const ctx = canvas.getContext("2d");
            
            const colors = ["#3AAFA9", "#2B7A78", "#DEF2F1", "#5F259F", "#FFD166", "#06D6A0", "#118AB2"];
            const particles = [];
            for (let i = 0; i < 90; i++) {{
                particles.push({{
                    x: canvas.width / 2 + (Math.random() * 40 - 20),
                    y: canvas.height * 0.35 + (Math.random() * 40 - 20),
                    vx: (Math.random() - 0.5) * 16,
                    vy: (Math.random() - 1.2) * 14,
                    size: Math.random() * 8 + 5,
                    color: colors[Math.floor(Math.random() * colors.length)],
                    rotation: Math.random() * 360,
                    vr: (Math.random() - 0.5) * 12,
                    opacity: 1
                }});
            }}
            
            let frame = 0;
            function animate() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                let alive = false;
                particles.forEach(p => {{
                    p.x += p.vx;
                    p.y += p.vy;
                    p.vy += 0.35; // gravity
                    p.vx *= 0.98; // drag
                    p.rotation += p.vr;
                    p.opacity -= 0.009;
                    if (p.opacity > 0) {{
                        alive = true;
                        ctx.save();
                        ctx.translate(p.x, p.y);
                        ctx.rotate(p.rotation * Math.PI / 180);
                        ctx.globalAlpha = Math.max(0, p.opacity);
                        ctx.fillStyle = p.color;
                        ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
                        ctx.restore();
                    }}
                }});
                frame++;
                if (alive && frame < 180) requestAnimationFrame(animate);
                else ctx.clearRect(0, 0, canvas.width, canvas.height);
            }}
            animate();
        }})();
        </script>
        """,
        height=0,
        width=0,
    )

    # Celebratory Receipt Card & Checkmark
    html_block(f"""
    <div style="background:linear-gradient(135deg, #FEFFFF 0%, #F4FAF9 100%); border:2px solid #3AAFA9; border-radius:24px; padding:32px 28px; text-align:center; box-shadow:0 12px 40px rgba(43, 122, 120, 0.18); margin-bottom:24px; position:relative; overflow:hidden; animation:ppScaleIn 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;">
      
      <!-- Pulsing Animated Green Checkmark -->
      <div style="position:relative; width:92px; height:92px; margin:0 auto 16px;">
        <div style="position:absolute; inset:-12px; border-radius:50%; background:rgba(58, 175, 169, 0.2); animation:ppPaymentPulseRing 2s infinite ease-out;"></div>
        <div style="position:absolute; inset:-24px; border-radius:50%; background:rgba(43, 122, 120, 0.12); animation:ppPaymentPulseRing 2s infinite ease-out 0.4s;"></div>
        <div style="width:92px; height:92px; border-radius:50%; background:linear-gradient(135deg, #3AAFA9 0%, #2B7A78 100%); display:grid; place-items:center; box-shadow:0 8px 24px rgba(58, 175, 169, 0.45); border:3px solid #FEFFFF; position:relative; z-index:2;">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#FEFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12" style="stroke-dasharray: 40; stroke-dashoffset: 0; animation: ppStrokeDraw 0.6s ease-out;"></polyline>
          </svg>
        </div>
      </div>

      <!-- Header & Amount -->
      <div style="display:inline-block; font-size:11.5px; font-weight:800; color:#2B7A78; background:#DEF2F1; border:1px solid #3AAFA9; padding:4px 14px; border-radius:99px; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:8px;">
        ✦ PAYMENT COMPLETED SUCCESSFULLY ✦
      </div>
      <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:38px; font-weight:900; color:#17252A; letter-spacing:-0.02em; margin-bottom:4px;">
        {amt_formatted}
      </div>
      <div style="font-size:14.5px; font-weight:750; color:#496E6B; margin-bottom:18px;">
        Paid to <strong style="color:#17252A;">{recipient}</strong> · Instant Settlement ⚡
      </div>

      <!-- Simulated Soundbox Announcement Banner -->
      <div style="background:#DEF2F1; border:1.5px solid #3AAFA9; border-radius:14px; padding:12px 18px; margin:0 auto 20px; max-width:540px; display:flex; align-items:center; gap:12px; text-align:left;">
        <span style="font-size:24px;">🔊</span>
        <div>
          <div style="font-size:11px; font-weight:800; color:#2B7A78; text-transform:uppercase; letter-spacing:0.04em;">AskAbhi UPI Soundbox Voice Alert</div>
          <div style="font-size:13.5px; font-weight:750; color:#17252A;">"{amt_formatted} paid successfully on AskAbhi UPI!"</div>
        </div>
      </div>

      <!-- Digital Receipt Card -->
      <div style="background:#FEFFFF; border:1.5px solid #D1EBE8; border-radius:16px; padding:18px 22px; max-width:540px; margin:0 auto 20px; text-align:left; font-size:13.5px; box-shadow:0 4px 14px rgba(23,37,42,0.03);">
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #F4FAF9;">
          <span style="color:#496E6B;">UPI Reference Number</span>
          <span style="font-weight:800; color:#17252A; font-family:'JetBrains Mono', monospace;">{ref}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #F4FAF9;">
          <span style="color:#496E6B;">Payment Mode</span>
          <span style="font-weight:750; color:#17252A;">{mode}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #F4FAF9;">
          <span style="color:#496E6B;">Date &amp; Timestamp</span>
          <span style="font-weight:750; color:#17252A;">{dt}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #F4FAF9;">
          <span style="color:#496E6B;">Note / Remark</span>
          <span style="font-weight:750; color:#17252A;">{note}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:6px 0;">
          <span style="color:#496E6B;">Security Status</span>
          <span style="font-weight:800; color:#2B7A78;">🛡️ NPCI Verified · BharatQR Compliant</span>
        </div>
      </div>

    </div>
    """)

    # Dismiss / Action Buttons
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("✓ Done & Return to Transfers", key="close_celebration", type="primary", use_container_width=True):
            st.session_state.pop("payment_celebration", None)
            st.rerun()
    with c_btn2:
        if st.button("📑 View in Transaction Records", key="view_in_records", use_container_width=True):
            st.session_state.pop("payment_celebration", None)
            refs = st.session_state.get("_page_refs", {})
            if "transactions" in refs:
                st.switch_page(refs["transactions"])
            else:
                st.rerun()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)


def render() -> None:
    ctx, _, _ = common_context()
    owl = owl_data_uri()
    
    # Wallet Balance State
    wallet_bal = st.session_state.setdefault("demo_wallet_balance", 25400.0)

    # If celebratory payment animation is triggered, render it prominently
    active_celebration = st.session_state.get("payment_celebration")
    if active_celebration:
        _render_celebration_overlay(active_celebration)

    # ══════════════════════════════════════════════
    # 1. TOP BRANDED HEADER CARD (TEAL & NOIR)
    # ══════════════════════════════════════════════
    html_block(f"""
    <div style="background:linear-gradient(135deg, #17252A 0%, #2B7A78 55%, #3AAFA9 100%); border-radius:22px; padding:24px 28px; box-shadow:0 8px 28px rgba(23,37,42,0.18); display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; color:#FEFFFF; flex-wrap:wrap; gap:18px;">
      <div style="min-width:260px;">
        <div style="font-size:11.5px; font-weight:800; color:#DEF2F1; letter-spacing:0.08em; text-transform:uppercase;">✦ INSTANT UPI &amp; WALLET PLATFORM</div>
        <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size:26px; font-weight:900; color:#FEFFFF; margin-top:3px;">UPI Payments &amp; Instant Transfers</div>
        <div style="font-size:13.5px; color:#DEF2F1; margin-top:3px; opacity:0.95;">Fast, secure, zero-fee instant transfers across banks, contacts &amp; QR merchants.</div>
      </div>
      <div style="display:flex; align-items:center; gap:18px;">
        <div style="text-align:right;">
          <div style="font-size:11px; color:#DEF2F1; font-weight:800; text-transform:uppercase; letter-spacing:0.05em; opacity:0.9;">Digital Wallet Balance</div>
          <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size:24px; font-weight:900; color:#FEFFFF;">{inr(wallet_bal)}</div>
        </div>
        <img src="{owl}" alt="Abhi Rocket" style="width:56px; height:56px; border-radius:18px; object-fit:cover; border:2.5px solid #3AAFA9; background:#FEFFFF; box-shadow:0 6px 16px rgba(0,0,0,0.25);" />
      </div>
    </div>
    """)

    # ══════════════════════════════════════════════
    # 2. MAIN TWO-COLUMN WORKFLOW HUB
    # ══════════════════════════════════════════════
    col_left, col_right = st.columns([1.25, 1], gap="large")

    with col_left:
        # Quick Transfer Hub Buttons Matching Master Kit
        html_block("""
        <div style="font-size:15px; font-weight:850; color:#17252A; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
          <span>Quick Transfer Hub</span>
          <span style="font-size:12px; color:#2B7A78; font-weight:800; background:#DEF2F1; padding:3px 10px; border-radius:99px; border:1px solid #3AAFA9;">UPI 2.0 Instant ⚡</span>
        </div>
        """)

        a1, a2, a3, a4 = st.columns(4)
        with a1:
            if st.button("📱\nTo Contact", key="pay_to_mobile", use_container_width=True):
                st.session_state["pay_demo_recipient"] = "Aarav Sharma"
                st.session_state["pay_demo_upi"] = "+91 98765 43210"
                st.rerun()
        with a2:
            if st.button("➤\nTo UPI ID", key="pay_to_upi", use_container_width=True):
                st.session_state["pay_demo_recipient"] = "Rahul Verma"
                st.session_state["pay_demo_upi"] = "rahul.verma@okhdfcbank"
                st.rerun()
        with a3:
            if st.button("🏛️\nTo Bank", key="pay_to_bank", use_container_width=True):
                st.session_state["pay_demo_recipient"] = "HDFC Bank Beneficiary"
                st.session_state["pay_demo_upi"] = "501004829104 · HDFC0001234"
                st.rerun()
        with a4:
            if st.button("⇄\nSelf Transfer", key="pay_to_self", use_container_width=True):
                st.session_state["pay_demo_recipient"] = f"{ctx.persona_name} (SBI A/C)"
                st.session_state["pay_demo_upi"] = f"{ctx.persona_name.lower()}@sbi"
                st.rerun()

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # Send Money Interactive Form with Quick Amount Chips
        with st.container(border=True):
            st.markdown("<div style='font-size:15px; font-weight:850; color:#17252A; margin-bottom:12px;'>Send Money Instantly</div>", unsafe_allow_html=True)
            
            with st.form("quick_upi_transfer_form", clear_on_submit=False):
                f_c1, f_c2 = st.columns(2)
                with f_c1:
                    recipient = st.text_input("Recipient / Merchant Name", value=st.session_state.get("pay_demo_recipient", "Rahul Verma"), max_chars=80)
                with f_c2:
                    upi_id = st.text_input("UPI ID or Mobile Number", value=st.session_state.get("pay_demo_upi", "rahul.verma@okhdfcbank"), max_chars=120)
                
                f_amt, f_note = st.columns([1, 1.2])
                with f_amt:
                    amount = st.number_input("Amount (₹)", min_value=1.0, max_value=100000.0, value=float(st.session_state.get("pay_quick_amount", 500.0)), step=50.0)
                with f_note:
                    note = st.text_input("Payment Note (optional)", value="Dinner split", max_chars=100)
                
                f_acc = st.selectbox("Pay From Account", [
                    f"AskAbhi Digital Wallet · Available: {inr(wallet_bal)}",
                    "HDFC Bank Primary (•••• 4821) · ₹1,42,850",
                    "State Bank of India (•••• 9104) · ₹45,200",
                ])

                submitted = st.form_submit_button("Review & Pay (Simulated) ➔", type="primary", use_container_width=True)

            if submitted:
                if not recipient.strip():
                    st.error("Please enter a recipient or merchant name.")
                elif "@" not in upi_id and len(upi_id) < 10:
                    st.error("Enter a valid UPI ID (e.g. name@bank) or a 10-digit mobile number.")
                elif amount > wallet_bal and "Wallet" in f_acc:
                    st.error(f"Insufficient wallet balance ({inr(wallet_bal)}). Try a lower amount or pay via linked bank.")
                else:
                    _record("UPI Transfer", recipient, amount, note, upi_id)
                    st.rerun()

            # Quick Amount Selection Pills
            st.markdown("<div style='font-size:12px; font-weight:800; color:#496E6B; margin-top:10px; margin-bottom:6px;'>Quick Amount Fill:</div>", unsafe_allow_html=True)
            q1, q2, q3, q4, q5 = st.columns(5)
            if q1.button("₹100", key="q_100", use_container_width=True):
                st.session_state["pay_quick_amount"] = 100.0
                st.rerun()
            if q2.button("₹500", key="q_500", use_container_width=True):
                st.session_state["pay_quick_amount"] = 500.0
                st.rerun()
            if q3.button("₹1,000", key="q_1000", use_container_width=True):
                st.session_state["pay_quick_amount"] = 1000.0
                st.rerun()
            if q4.button("₹2,500", key="q_2500", use_container_width=True):
                st.session_state["pay_quick_amount"] = 2500.0
                st.rerun()
            if q5.button("₹5,000", key="q_5000", use_container_width=True):
                st.session_state["pay_quick_amount"] = 5000.0
                st.rerun()

    with col_right:
        # High-Fidelity Vector QR Scanner Card Matching Master Kit
        qr_scanner_svg = qr_code_svg("upi://pay?pa=askabhi.merchant@okhdfcbank&pn=InstantQR&mc=5411", size=140, fg="#17252A", bg="#FEFFFF", show_badge=True)
        html_block(f"""
        <div style="background:linear-gradient(135deg, #17252A 0%, #1A3438 50%, #2B7A78 100%); border:1.5px solid rgba(58, 175, 169, 0.5); border-radius:22px; padding:22px; text-align:center; color:#FEFFFF; margin-bottom:16px; box-shadow:0 8px 28px rgba(23,37,42,0.3);">
          <div style="font-size:11px; font-weight:800; color:#3AAFA9; letter-spacing:0.1em; text-transform:uppercase;">✦ SCAN ANY UPI QR CODE</div>
          <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size:18px; font-weight:850; margin:4px 0 12px; color:#FEFFFF;">Instant QR Scanner</div>
          
          <div style="position:relative; width:160px; height:160px; margin:0 auto 12px; background:#0B1619; border-radius:18px; padding:10px; display:grid; place-items:center; box-shadow:0 8px 20px rgba(0,0,0,0.4); overflow:hidden;">
            <!-- Corner Viewfinder Brackets -->
            <div style="position:absolute; top:6px; left:6px; width:18px; height:18px; border-top:3px solid #3AAFA9; border-left:3px solid #3AAFA9; border-top-left-radius:6px; z-index:4;"></div>
            <div style="position:absolute; top:6px; right:6px; width:18px; height:18px; border-top:3px solid #3AAFA9; border-right:3px solid #3AAFA9; border-top-right-radius:6px; z-index:4;"></div>
            <div style="position:absolute; bottom:6px; left:6px; width:18px; height:18px; border-bottom:3px solid #3AAFA9; border-left:3px solid #3AAFA9; border-bottom-left-radius:6px; z-index:4;"></div>
            <div style="position:absolute; bottom:6px; right:6px; width:18px; height:18px; border-bottom:3px solid #3AAFA9; border-right:3px solid #3AAFA9; border-bottom-right-radius:6px; z-index:4;"></div>
            <!-- Animated Laser Scan Line -->
            <div style="position:absolute; left:8px; right:8px; height:2.5px; background:linear-gradient(90deg, transparent, #3AAFA9, #DEF2F1, #3AAFA9, transparent); box-shadow:0 0 12px #3AAFA9, 0 0 5px #DEF2F1; animation:qrLaserScan 2.2s ease-in-out infinite; z-index:3;"></div>
            <!-- High-Fidelity Vector SVG QR -->
            {qr_scanner_svg}
          </div>
          <div style="font-size:12px; color:#DEF2F1; margin-bottom:4px; font-weight:600;">Point camera or simulate instant scan below</div>
          <div style="font-size:10px; color:#A7DCD7; letter-spacing:0.04em;">BHIM UPI · BharatQR Compliant · Zero Surcharge</div>
        </div>
        """)
        
        # QR Quick Simulate Buttons
        s_c1, s_c2 = st.columns(2)
        with s_c1:
            if st.button("☕ Scan Coffee (₹180)", key="scan_coffee_demo", use_container_width=True, type="primary"):
                _record("Scan & Pay", "Bangalore Coffee House", 180.0, "Filter Coffee & Dosa", "bch@hdfcbank")
                st.rerun()
        with s_c2:
            if st.button("🛒 Scan Supermarket (₹840)", key="scan_market_demo", use_container_width=True):
                _record("Scan & Pay", "Nature's Basket", 840.0, "Weekly groceries", "nature@icicibank")
                st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Linked Accounts Widget
        with st.container(border=True):
            st.markdown("<div style='font-size:14px; font-weight:850; color:#17252A; margin-bottom:10px;'>Linked Payment Accounts</div>", unsafe_allow_html=True)
            
            html_block(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid #E5F5F3;">
              <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:36px; height:36px; border-radius:10px; background:#DEF2F1; border:1px solid #3AAFA9; display:grid; place-items:center; font-size:17px;">🏛️</div>
                <div>
                  <div style="font-size:13px; font-weight:800; color:#17252A;">HDFC Bank · Primary</div>
                  <div style="font-size:11px; color:#496E6B;">A/C •••• 4821 · Active</div>
                </div>
              </div>
              <div style="font-size:13.5px; font-weight:850; color:#17252A;">₹1,42,850</div>
            </div>
            
            <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid #E5F5F3;">
              <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:36px; height:36px; border-radius:10px; background:#DEF2F1; border:1px solid #3AAFA9; display:grid; place-items:center; font-size:17px;">🏛️</div>
                <div>
                  <div style="font-size:13px; font-weight:800; color:#17252A;">State Bank of India</div>
                  <div style="font-size:11px; color:#496E6B;">A/C •••• 9104 · Active</div>
                </div>
              </div>
              <div style="font-size:13.5px; font-weight:850; color:#17252A;">₹45,200</div>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 0;">
              <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:36px; height:36px; border-radius:10px; background:#E6F9F0; border:1px solid #A7F3D0; display:grid; place-items:center; font-size:17px;">💼</div>
                <div>
                  <div style="font-size:13px; font-weight:800; color:#17252A;">AskAbhi Digital Wallet</div>
                  <div style="font-size:11px; color:#2B7A78; font-weight:700;">Simulated Instant Liquidity</div>
                </div>
              </div>
              <div style="font-size:13.5px; font-weight:850; color:#2B7A78;">{inr(wallet_bal)}</div>
            </div>
            """)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════
    # 3. RECHARGE & BILL PAYMENTS GRID
    # ══════════════════════════════════════════════
    st.markdown("<div style='font-size:15px; font-weight:850; color:#17252A; margin-bottom:10px;'>Recharge &amp; Bill Payments (Click to Simulate Instant Payment)</div>", unsafe_allow_html=True)
    
    b1, b2, b3, b4, b5, b6, b7, b8 = st.columns(8)
    with b1:
        if st.button("📱\nMobile", key="bill_mobile", use_container_width=True):
            _record("Recharge", "Airtel Prepaid (+91 98765 43210)", 299.0, "28 Days Unlimited 5G Plan")
            st.rerun()
    with b2:
        if st.button("💡\nElectricity", key="bill_elec", use_container_width=True):
            _record("Bill Payment", "BESCOM Electricity", 1240.0, "Account #882190")
            st.rerun()
    with b3:
        if st.button("📺\nDTH TV", key="bill_dth", use_container_width=True):
            _record("Recharge", "Tata Play DTH", 450.0, "Family Mega HD Pack")
            st.rerun()
    with b4:
        if st.button("🚗\nFASTag", key="bill_fastag", use_container_width=True):
            _record("FASTag Recharge", "NHAI FASTag (KA 01 MJ 4821)", 500.0, "Toll balance top-up")
            st.rerun()
    with b5:
        if st.button("💳\nCredit Card", key="bill_cc", use_container_width=True):
            _record("Credit Card Bill", "HDFC Regalia Gold", 4500.0, "Monthly statement payment")
            st.rerun()
    with b6:
        if st.button("💧\nWater Bill", key="bill_water", use_container_width=True):
            _record("Bill Payment", "BWSSB Water Supply", 320.0, "Monthly utility bill")
            st.rerun()
    with b7:
        if st.button("🌐\nBroadband", key="bill_broadband", use_container_width=True):
            _record("Bill Payment", "JioFiber Broadband", 999.0, "300 Mbps unlimited plan")
            st.rerun()
    with b8:
        if st.button("⛽\nGas", key="bill_gas", use_container_width=True):
            _record("Bill Payment", "Indane LPG Refill", 860.0, "Cylinder Booking")
            st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════
    # 4. RECENT UPI ACTIVITY & PERSONAL QR STANDEE
    # ══════════════════════════════════════════════
    c_hist1, c_hist2 = st.columns([1.3, 1], gap="large")
    
    with c_hist1:
        st.markdown("<div style='font-size:15px; font-weight:850; color:#17252A; margin-bottom:10px;'>Recent Payments &amp; Transfers</div>", unsafe_allow_html=True)
        
        contacts = [
            ("Swiggy", "Food & Dining", "-₹420", "Today, 1:24 PM", "🍔"),
            ("Amazon", "Online Shopping", "-₹2,499", "Today, 11:02 AM", "📦"),
            ("Rahul Verma", "Direct Transfer Received", "+₹5,000", "Today, 9:14 AM", "👤"),
            ("Zomato", "Food Delivery", "-₹380", "Yesterday", "🍕"),
            ("Aarav Sharma", "Coffee split", "-₹180", "22 Oct", "☕"),
            ("BESCOM", "Electricity Bill", "-₹1,240", "20 Oct", "💡")
        ]
        
        for name, cat, amt, dt, ico in contacts:
            is_credit = amt.startswith("+")
            html_block(f"""
            <div style="background:#FEFFFF; border:1.5px solid #D1EBE8; border-radius:16px; padding:12px 16px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 8px rgba(23,37,42,0.03); transition:all 0.2s ease;">
              <div style="display:flex; align-items:center; gap:14px;">
                <div style="width:40px; height:40px; border-radius:12px; background:#DEF2F1; border:1px solid #3AAFA9; display:grid; place-items:center; font-size:18px;">
                  {ico}
                </div>
                <div>
                  <div style="font-weight:800; font-size:14px; color:#17252A;">{name}</div>
                  <div style="font-size:11.5px; color:#496E6B;">{cat} · {dt}</div>
                </div>
              </div>
              <div style="text-align:right;">
                <div style="font-family:'Plus Jakarta Sans',sans-serif; font-weight:900; font-size:15px; color:{'#2B7A78' if is_credit else '#17252A'};">
                  {amt}
                </div>
                <div style="font-size:10px; font-weight:800; color:{'#2B7A78' if is_credit else '#7E9E9C'}; letter-spacing:0.04em;">
                  {'RECEIVED' if is_credit else 'DEBITED'}
                </div>
              </div>
            </div>
            """)

    with c_hist2:
        st.markdown("<div style='font-size:15px; font-weight:850; color:#17252A; margin-bottom:10px;'>Receive via Personal QR</div>", unsafe_allow_html=True)
        personal_qr = qr_code_svg(f"upi://pay?pa={ctx.persona_name.lower()}@askabhi&pn={ctx.persona_name}", size=142, fg="#17252A", bg="#FEFFFF", show_badge=True)
        html_block(f"""
        <div style="background:#FEFFFF; border:1.5px solid #D1EBE8; border-radius:20px; padding:20px; text-align:center; box-shadow:0 4px 18px rgba(23,37,42,0.04);">
          <div style="font-size:11px; font-weight:800; color:#2B7A78; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:3px;">✦ My UPI QR Standee</div>
          <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:17px; font-weight:900; color:#17252A; margin-bottom:2px;">{ctx.persona_name}</div>
          <div style="font-size:11.5px; color:#496E6B; margin-bottom:12px;">ID: <strong style="color:#17252A;">{ctx.persona_name.lower()}@askabhi</strong> · Verified 🛡️</div>
          
          <div style="background:#FEFFFF; border:2.5px solid #3AAFA9; border-radius:18px; padding:12px; display:inline-block; margin-bottom:12px; box-shadow:0 6px 20px rgba(58,175,169,0.18);">
            {personal_qr}
          </div>
          
          <div style="font-size:12.5px; font-weight:800; color:#17252A; margin-bottom:4px;">Scan with Any UPI App</div>
          <div style="font-size:11px; color:#496E6B; margin-bottom:10px;">Instant zero-fee direct deposit to linked bank</div>
          <div style="background:#DEF2F1; border:1px solid #3AAFA9; border-radius:10px; padding:6px 12px; font-size:11.5px; font-weight:800; color:#2B7A78; display:inline-block;">
            🔊 Simulated Soundbox Alert Ready
          </div>
        </div>
        """)

        # Payment Methods Support Strip
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        html_block("""
        <div style="background:#F4FAF9; border:1.5px solid #D1EBE8; border-radius:16px; padding:12px 16px; text-align:center;">
          <div style="font-size:10.5px; font-weight:800; color:#496E6B; text-transform:uppercase; margin-bottom:6px; letter-spacing:0.06em;">Supported Payment Rails</div>
          <div style="display:flex; justify-content:center; gap:14px; font-size:12px; font-weight:800; color:#17252A; flex-wrap:wrap;">
            <span>⚡ UPI 2.0</span>
            <span>💳 RuPay UPI</span>
            <span>🏛️ IMPS / NEFT</span>
            <span>📱 Wallet</span>
          </div>
        </div>
        """)

    # Expander with Full Simulation History Table
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    with st.expander("📑 Complete Simulated Payment Records", expanded=False):
        history = st.session_state.get("askabhi_demo_payments", [])
        if not history:
            st.info("No interactive payments simulated yet. Click any button or submit a transfer above.")
        else:
            render_table(pd.DataFrame(history), use_container_width=True, hide_index=True)

    disclaimer()
