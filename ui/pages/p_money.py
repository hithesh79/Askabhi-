"""My Money: transaction intelligence, behaviour, net worth and liquidity."""
from __future__ import annotations
from datetime import date
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from ui.pages._common import page_header,common_context,disclaimer
from ui.state import replace_transactions,update_assets_liabilities,get_ctx,ROOT
from ui.components import insight_card,proof_drawer
from ui.tables import render_table, edit_records
from core.loader import load_transactions
from core.classify import review_queue
from core.networth import net_worth,usable_funds,liquidity_ladder
from core.formatting import inr

def render():
    ctx,draws,res=common_context(); bp=ctx.behaviour; nw=net_worth(ctx.assets,ctx.liabilities)
    page_header("My Money","Trace money movements, understand spending behaviour and reconcile your financial position.",f"Recorded assets are {inr(nw.total_assets)} and liabilities are {inr(nw.total_liabilities)}; net worth is {inr(nw.net_worth)}.")
    st.markdown("### Import transaction history")
    upload=st.file_uploader("Upload CSV (date, description, amount, type, account)",type=["csv"],key="money_csv")
    c1,c2=st.columns([1,2])
    with c1:
        if st.button("Validate and import CSV",disabled=upload is None,type="primary"):
            try:
                cleaned,issues=load_transactions(pd.read_csv(upload,encoding="utf-8")); st.session_state["upload_issues"]=[i.__dict__ for i in issues]
                replace_transactions(cleaned,"Uploaded CSV"); st.success(f"Imported {len(cleaned)} validated rows. Review issues below."); st.rerun()
            except Exception as exc: st.error(f"Import failed safely: {exc}")
    with c2:
        template=ROOT/"data"/"transactions_template.csv"
        if template.exists(): st.download_button("Download transaction CSV template",template.read_bytes(),file_name="transactions_template.csv",mime="text/csv")
    if st.session_state.get("upload_issues"):
        with st.expander(f"Validation report · {len(st.session_state['upload_issues'])} issues"):
            render_table(pd.DataFrame(st.session_state["upload_issues"]),use_container_width=True,hide_index=True)
    c1,c2,c3=st.columns(3); c1.metric("Total assets",inr(nw.total_assets)); c2.metric("Total liabilities",inr(nw.total_liabilities)); c3.metric("Net worth",inr(nw.net_worth))
    st.markdown("### Editable assets and liabilities")
    a,b=st.columns(2)
    with a:
        st.markdown("**Assets**")
        aset=pd.DataFrame([{"name":x.name,"kind":x.kind,"value":x.value,"asset_class":x.asset_class,"liquidity":x.liquidity,"unlock_date":x.unlock_date,"penalty_pct":x.penalty_pct,"exp_return":x.exp_return,"vol":x.vol} for x in ctx.assets])
        aedit=edit_records(aset, "assets_editor", select_options={"liquidity":["liquid","locked","penalty","illiquid"],"asset_class":["cash","debt","equity","gold","property","retirement"]}, date_columns=["unlock_date"])
    with b:
        st.markdown("**Liabilities**")
        ldf=pd.DataFrame([{"name":x.name,"kind":x.kind,"outstanding":x.outstanding,"annual_rate":x.annual_rate,"emi":x.emi,"months_left":x.months_left} for x in ctx.liabilities])
        ledit=edit_records(ldf, "liabilities_editor")
    if st.button("Save asset and liability changes",type="primary"):
        update_assets_liabilities(aedit.to_dict("records"),ledit.to_dict("records")); st.success("Financial profile updated; affected projections will be recalculated."); st.rerun()
    st.markdown("### Liquidity ladder")
    ladder=liquidity_ladder(ctx); render_table(ladder.assign(accessible=lambda x:x["accessible_including_penalty"].map(inr),usable=lambda x:x["net_usable_after_floor"].map(inr)),use_container_width=True,hide_index=True)
    usable_date=st.date_input("Calculate usable funds by date",value=date.today(),key="usable_date")
    uf=usable_funds(ctx.assets,usable_date,ctx.profile.emergency_months*ctx.profile.essential_monthly_spend,allow_penalty=False)
    c1,c2=st.columns(2); c1.metric("Usable after emergency floor",inr(uf.available)); c2.metric("Penalty assets available at a cost",inr(uf.penalty_available))
    proof_drawer("Liquidity","Liquid assets + unlocked assets available by date − emergency floor. Penalty assets are shown separately and only included when explicitly allowed.",uf.components,{"Locked assets excluded until unlock date","Illiquid assets excluded","Asset values may be estimates"},draws.seed,draws.fingerprint())
    st.markdown("### Behaviour twin")
    cols=st.columns(4); cols[0].metric("Data confidence",bp.confidence); cols[1].metric("History",f"{bp.months_of_data} months"); cols[2].metric("Weekend/weekday ratio",f"{bp.weekend_weekday_ratio:.2f}"); cols[3].metric("Payday-burst share",f"{bp.payday_burst_share:.0%}")
    st.info(bp.behaviour_gap)
    if bp.lifestyle_creep_slope>0: insight_card("↗","Lifestyle creep",f"Discretionary spending trend is approximately {inr(bp.lifestyle_creep_slope)} per month of history; p-value {bp.lifestyle_creep_pvalue:.3f}.","warning","Test a cut in Leaks.")
    else: insight_card("◎","Lifestyle trend","No positive trend was detected in the available sample. Short histories can miss long-term changes.","info")
    insight_card("↻","Recurring payments",f"{len(bp.recurring_merchants)} recurring merchants; possible subscriptions: {', '.join(bp.subscription_merchants[:8]) or 'none identified'}.","info","Confirm descriptions in the review queue.")
    insight_card("◫","Irregular income",f"{bp.income_label}; coefficient of variation {bp.income_cv:.2f}; {bp.lean_months} lean months; conservative planning income {inr(bp.safe_income)}.","warning" if bp.income_label!="Stable" else "success")
    st.markdown("### Planned vs unplanned outflows")
    ptu=pd.DataFrame([{"type":"Fixed / essential monthly estimate","amount":bp.planned_monthly},{"type":"Unplanned event estimate","amount":bp.unplanned_monthly},{"type":"Irregular-expense reserve","amount":bp.irregular_expense_reserve}])
    st.plotly_chart(px.bar(ptu,x="type",y="amount",title="Expense estimates by planning treatment",color="type"),use_container_width=True,config={"displayModeBar":False})
    cats=pd.DataFrame([{"category":k,"monthly_mean":v,"nature":bp.category_nature.get(k,"other")} for k,v in bp.category_monthly_mean.items()])
    if not cats.empty: st.plotly_chart(px.bar(cats.sort_values("monthly_mean",ascending=False),x="category",y="monthly_mean",color="nature",title="Average monthly spending by category"),use_container_width=True,config={"displayModeBar":False})
    st.markdown("### Transaction review queue")
    queue=review_queue(ctx.transactions,.7)
    if queue.empty: st.success("No low-confidence classifications are waiting for review.")
    else:
        render_table(queue[[c for c in ["date","description","amount","category","kind","confidence","evidence"] if c in queue]],use_container_width=True,hide_index=True)
        row_choice=st.selectbox("Choose a transaction description to confirm",queue["description"].astype(str).drop_duplicates().tolist(),key="review_desc")
        category=st.selectbox("Confirmed category",["Groceries","Dining","Food delivery","Shopping","Potential asset acquisition","Income","Medical","Housing","Transport","Subscriptions","Insurance","Loan EMI","Other"],key="review_category")
        kind=st.selectbox("Financial treatment",["expense","income","transfer","investment","loan","potential_asset"],key="review_kind")
        if st.button("Save classification rule"):
            overrides=st.session_state.get("transaction_overrides",{}); overrides[row_choice]={"category":category,"kind":kind,"nature":"discretionary" if category in ("Dining","Food delivery","Shopping") else "essential"}; st.session_state["transaction_overrides"]=overrides
            from ui.state import _build_ctx
            bundle=st.session_state["persona_bundle"]; st.session_state["ctx"]=_build_ctx(bundle); st.success("Override saved for this application session."); st.rerun()
    with st.expander("Reconciliation proof"):
        report=st.session_state.get("reconcile_report"); st.write(report.messages if report else "No reconciliation report.")
        if report: st.metric("Amount of card/own transfers prevented from double-counting",inr(report.double_counting_prevented_inr))
    disclaimer()
