"""Can I Afford It? — purchase and loan calculator matching AskAbhi 360 design board."""
from __future__ import annotations
from datetime import date
import streamlit as st
from ui.tables import render_table
from ui.pages._common import page_header, common_context, disclaimer
from ui.components import prob_gauge, proof_drawer, lever_row, html_block, bike_image_uri
from core.models import PurchaseSpec
from core.afford import evaluate_purchase
from core.networth import emi
from core.formatting import inr, pct

def render():
    ctx, draws, base = common_context()
    bike_img = bike_image_uri()
    
    page_header(
        "Can I Afford It? · Purchase & Loan Engine",
        "Simulate major purchases (motorcycle, phone, car, home) with realistic EMI, down payment, and goal trade-offs.",
        "A purchase is truly affordable only if your down payment, EMI, and remaining financial goals remain feasible."
    )

    col_preview, col_form = st.columns([1, 1.25], gap="large")

    with col_preview:
        html_block(f"""
        <div style="background:#FEFFFF; border:1.5px solid #D1EBE8; border-radius:22px; padding:24px; box-shadow:0 8px 24px rgba(43,122,120,0.06); text-align:center;">
          <div style="font-size:11.5px; font-weight:800; color:#2B7A78; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">✦ Selected Dream Purchase</div>
          <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size:24px; font-weight:900; color:#17252A;">BMW G 310 R</div>
          <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size:28px; font-weight:900; color:#2B7A78; margin:4px 0 16px;">₹4,50,000</div>
          {f'<img src="{bike_img}" alt="BMW Bike" style="width:100%; max-height:220px; object-fit:contain; border-radius:16px; margin-bottom:16px; background:#F4FAF9; padding:12px; border:1.5px solid #D1EBE8;" />' if bike_img else ''}
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; text-align:left; font-size:13px; border-top:1.5px solid #E5F5F3; padding-top:16px;">
            <div><span style="color:#496E6B; font-weight:600;">Target Date:</span> <b style="color:#17252A;">Dec 2026</b></div>
            <div><span style="color:#496E6B; font-weight:600;">Down Payment:</span> <b style="color:#17252A;">₹1,00,000</b></div>
            <div><span style="color:#496E6B; font-weight:600;">Loan Amount:</span> <b style="color:#17252A;">₹3,50,000</b></div>
            <div><span style="color:#496E6B; font-weight:600;">Interest Rate:</span> <b style="color:#17252A;">9.5% p.a.</b></div>
            <div><span style="color:#496E6B; font-weight:600;">Loan Tenure:</span> <b style="color:#17252A;">3 Years (36m)</b></div>
            <div><span style="color:#496E6B; font-weight:600;">Monthly EMI:</span> <b style="color:#2B7A78; font-weight:900;">~₹11,215</b></div>
          </div>
        </div>
        """)

    with col_form:
        with st.form("afford_form"):
            st.markdown("<div style='font-size:16px; font-weight:850; color:#17252A; margin-bottom:12px;'>Configure Purchase Parameters</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            name = c1.text_input("What do you want to buy?", value="BMW G 310 R")
            price = c2.number_input("On-road purchase price (₹)", min_value=0.0, value=450000.0, step=10000.0)
            
            c3, c4 = st.columns(2)
            category = c3.selectbox("Purchase Category", ["vehicle", "car", "education", "home", "gadget", "other"], index=0)
            months = c4.slider("Buy in how many months?", 0, 60, 12)
            
            c5, c6 = st.columns(2)
            down = c5.slider("Down payment (%)", 0, 100, 25) / 100
            mode = c6.selectbox("Evaluation mode", ["compare", "cash", "loan"])
            
            c7, c8, c9 = st.columns(3)
            rate = c7.number_input("Annual loan rate (%)", min_value=0.0, max_value=40.0, value=9.5, step=0.5) / 100
            tenure = c8.selectbox("Tenure (months)", [12, 24, 36, 48, 60, 72], index=2)
            running = c9.number_input("Monthly running cost (₹)", min_value=0.0, value=3500.0, step=500.0)
            
            submitted = st.form_submit_button("Calculate Affordability →", type="primary", use_container_width=True)

    if submitted or "afford_result" not in st.session_state:
        from core.data_gen import add_months
        spec = PurchaseSpec(name, category, price, add_months(ctx.profile.as_of, months), mode, down, rate, tenure, running, None)
        with st.spinner("Testing cash, loan, and goal trade-offs on reproducible simulation draws..."):
            try:
                st.session_state["afford_result"] = evaluate_purchase(ctx, spec, draws)
                st.session_state["afford_spec"] = spec
            except Exception as exc:
                st.error(f"Could not evaluate this purchase: {exc}")
                return

    res = st.session_state["afford_result"]
    spec = st.session_state["afford_spec"]
    
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(f"## Verdict: {res.verdict}")
    
    a, b = st.columns(2, gap="large")
    with a:
        prob_gauge(res.cash_probability, res.cash_se, "Full Cash Feasibility")
    with b:
        prob_gauge(res.loan_probability, res.loan_se, "Loan (EMI) Feasibility")
        
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="medium")
    c1.metric("Estimated on-road cost", inr(res.onroad_cost))
    c2.metric("Inflated cost at target date", inr(res.inflated_cost))
    c3.metric("Calculated monthly EMI", inr(res.emi), f"{res.emi_share_income:.1%} of take-home income")

    if res.emi_share_income > 0.40:
        st.warning("⚠️ High EMI Burden: Monthly EMI exceeds 40% of your take-home income. Consider a larger down payment or longer tenure.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("### Hidden Impact on Your Other Goals")
    render_table([{
        **x,
        "baseline": pct(x["baseline_probability"]),
        "cash after purchase": pct(x["cash_probability"]),
        "loan after purchase": pct(x["loan_probability"]),
        "cash change": f"{x['cash_change']*100:+.1f} pp",
        "loan change": f"{x['loan_change']*100:+.1f} pp"
    } for x in res.other_goal_impacts], use_container_width=True, hide_index=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown("### Suggested Levers to Make It Comfortable")
    if res.levers:
        for item in res.levers[:6]:
            lever_row(item["lever"], item["before"], item["after"], f"pain index {item['pain']:,.0f}")
    else:
        st.info("No tested lever improved the probability without reducing other goals.")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown("### Binding Constraint")
    st.info(f"💡 {res.binding_constraint['message']}")
    
    proof_drawer("Affordability Math", "Purchase affordability evaluated against liquid funds, emergency reserves, and competing goals.", {"price": price, "category": category, "months": months, "down_payment_pct": down, "rate": rate, "tenure": tenure}, {"On-road multiplier varies by state", "Returns and inflation are stochastic", "Monte Carlo standard error shown"}, draws.seed, draws.fingerprint())
    disclaimer()
