"""Transaction Management: Complete CRUD, search, filter, CSV import/export."""
from __future__ import annotations
from datetime import date, datetime
import pandas as pd
import streamlit as st
from ui.pages._common import page_header, common_context, disclaimer
from ui.components import html_block
from ui.tables import render_table
from ui.state import replace_transactions, get_ctx
from core.formatting import inr
from core.loader import load_transactions

def render() -> None:
    ctx, _, _ = common_context()
    
    page_header(
        "Transaction Management",
        "View, search, filter, add, edit, and export your complete transaction history.",
        "Any change here recalculates your net worth, spending analytics, and dashboard metrics.",
        "info"
    )

    tx = ctx.transactions.copy() if getattr(ctx, "transactions", None) is not None else pd.DataFrame()

    t_list, t_add, t_import = st.tabs(["All Transactions", "Add Transaction", "CSV Import & Export"])

    with t_list:
        if tx.empty:
            st.info("No transactions recorded yet. Use 'Add Transaction' or 'CSV Import' to get started.")
        else:
            # Search & Filter Controls
            col1, col2, col3, col4 = st.columns([2, 1.2, 1.2, 1])
            with col1:
                search_q = st.text_input("Search description / merchant", placeholder="e.g. Swiggy, Amazon, Rent...", key="tx_search_q")
            with col2:
                categories = ["All"] + sorted(list(tx["category"].dropna().unique())) if "category" in tx.columns else ["All"]
                cat_filter = st.selectbox("Category", categories, key="tx_cat_filter")
            with col3:
                types = ["All"] + sorted(list(tx["type"].dropna().unique())) if "type" in tx.columns else ["All"]
                type_filter = st.selectbox("Type", types, key="tx_type_filter")
            with col4:
                sort_order = st.selectbox("Sort", ["Newest First", "Oldest First", "Highest Amount"], key="tx_sort")

            # Apply filters
            filtered = tx.copy()
            if search_q.strip():
                mask = False
                for c in ["description", "merchant", "account"]:
                    if c in filtered.columns:
                        mask = mask | filtered[c].astype(str).str.contains(search_q.strip(), case=False, na=False)
                filtered = filtered[mask]
            
            if cat_filter != "All" and "category" in filtered.columns:
                filtered = filtered[filtered["category"] == cat_filter]

            if type_filter != "All" and "type" in filtered.columns:
                filtered = filtered[filtered["type"] == type_filter]

            if "date" in filtered.columns:
                filtered["_date"] = pd.to_datetime(filtered["date"], errors="coerce")
                if sort_order == "Newest First":
                    filtered = filtered.sort_values("_date", ascending=False)
                elif sort_order == "Oldest First":
                    filtered = filtered.sort_values("_date", ascending=True)
                elif sort_order == "Highest Amount":
                    filtered = filtered.sort_values("amount", ascending=False)

            # Metrics
            total_debit = filtered[filtered["type"].astype(str).str.lower().isin(["debit", "expense"])]["amount"].sum() if "type" in filtered.columns else 0.0
            total_credit = filtered[filtered["type"].astype(str).str.lower().isin(["credit", "income"])]["amount"].sum() if "type" in filtered.columns else 0.0
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Matching Transactions", len(filtered))
            m2.metric("Total Debits / Expenses", inr(total_debit))
            m3.metric("Total Credits / Income", inr(total_credit))

            # Display table
            disp_cols = [c for c in ["date", "description", "category", "amount", "type", "account"] if c in filtered.columns]
            render_table(filtered[disp_cols].head(50), use_container_width=True, hide_index=True)

            # Export button
            csv_data = filtered[disp_cols].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Filtered Transactions (CSV)",
                data=csv_data,
                file_name=f"askabhi_transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    with t_add:
        st.markdown("### Record New Transaction")
        with st.form("tx_add_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                tx_date = st.date_input("Date", value=date.today())
                tx_desc = st.text_input("Description / Merchant", placeholder="e.g. Swiggy Food Delivery")
                tx_cat = st.selectbox("Category", [
                    "Food delivery", "Dining", "Groceries", "Shopping", "Transport", 
                    "Utilities", "Housing", "Subscriptions", "Medical", "Loan EMI", 
                    "Salary credit", "Investment", "Other"
                ])
            with f2:
                tx_amt = st.number_input("Amount (₹)", min_value=1.0, value=500.0, step=50.0)
                tx_type = st.selectbox("Transaction Type", ["debit", "credit"])
                tx_account = st.selectbox("Account", ["SAVINGS", "CREDIT_CARD", "WALLET", "INVESTMENT"])

            add_btn = st.form_submit_button("Add Transaction", type="primary")
            if add_btn:
                if not tx_desc.strip():
                    st.error("Please provide a description.")
                else:
                    new_row = pd.DataFrame([{
                        "date": str(tx_date),
                        "description": tx_desc.strip(),
                        "category": tx_cat,
                        "amount": float(tx_amt),
                        "type": tx_type,
                        "account": tx_account
                    }])
                    updated = pd.concat([new_row, tx], ignore_index=True)
                    replace_transactions(updated, "Added manual transaction")
                    st.success(f"Added transaction: {tx_desc} ({inr(tx_amt)}). Metrics updated.")
                    st.rerun()

    with t_import:
        st.markdown("### Bulk CSV Import & Export")
        uploaded_file = st.file_uploader("Upload CSV file (columns: date, description, amount, type, account)", type=["csv"], key="manage_tx_csv")
        if uploaded_file is not None:
            if st.button("Validate and Import Uploaded CSV", type="primary"):
                try:
                    df = pd.read_csv(uploaded_file, encoding="utf-8")
                    cleaned, issues = load_transactions(df)
                    replace_transactions(cleaned, "Bulk CSV Import")
                    st.success(f"Successfully imported {len(cleaned)} transactions. Dashboard recalculated.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error importing CSV: {e}")

    disclaimer()
