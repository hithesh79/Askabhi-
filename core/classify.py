"""Transparent transaction classification with review confidence and user overrides."""
from __future__ import annotations
import pandas as pd

RULES=[
 ("salary", "Income", "income", "fixed", ["salary","payroll","employer credit","monthly pay"]),
 ("freelance", "Income", "income", "variable", ["freelance","client payment","invoice received"]),
 ("rent", "Housing", "expense", "essential", ["rent","landlord"]),
 ("grocer", "Groceries", "expense", "essential", ["bigbasket","zepto","grocery","supermarket"]),
 ("food delivery", "Food delivery", "expense", "discretionary", ["swiggy","zomato"]),
 ("subscription", "Subscriptions", "expense", "fixed", ["netflix","hotstar","spotify","prime video","subscription"]),
 ("telecom", "Telecom", "expense", "fixed", ["airtel","jio","broadband","mobile recharge"]),
 ("utility", "Utilities", "expense", "essential", ["electricity","water bill","gas bill"]),
 ("emi", "Loan EMI", "loan", "fixed", ["emi","loan repayment","loan installment"]),
 ("card settlement", "Card settlement", "transfer", "transfer", ["credit card bill","card payment","card settlement"]),
 ("sip", "Investment", "investment", "saving", ["sip","mutual fund","investment transfer"]),
 ("gold", "Potential asset acquisition", "potential_asset", "review", ["jeweller","jewelry","jewellery","gold shop"]),
 ("medical", "Medical", "expense", "essential", ["medical","hospital","pharmacy","doctor"]),
 ("insurance", "Insurance", "expense", "fixed", ["lic premium","insurance premium","health insurance"]),
 ("transport", "Transport", "expense", "mixed", ["uber","ola","petrol","fuel","metro"]),
 ("shopping", "Shopping", "expense", "discretionary", ["amazon","flipkart","shopping","myntra"]),
 ("bar", "Discretionary purchase", "expense", "discretionary", ["wine","liquor","bar","pub"]),
 ("family", "Family support", "expense", "essential", ["family","parents","upi to family"]),
 ("refund", "Refund", "refund", "variable", ["refund","reversal"]),
 ("transfer", "Transfer", "transfer", "transfer", ["self transfer","own account","transfer to savings"]),
]

def classify(df: pd.DataFrame, overrides: dict | None=None) -> pd.DataFrame:
    result=df.copy(); overrides=overrides or {}
    cats=[]; kinds=[]; natures=[]; confs=[]; evidences=[]
    for _,row in result.iterrows():
        desc=str(row.get("description", "")); lower=desc.lower(); key=str(row.get("transaction_id", desc))
        if key in overrides:
            ov=overrides[key]; cats.append(ov.get("category","Other")); kinds.append(ov.get("kind","expense")); natures.append(ov.get("nature","discretionary")); confs.append(1.0); evidences.append("User-confirmed override"); continue
        typ=str(row.get("type","debit")).lower()
        match=None
        for rule in RULES:
            for token in rule[4]:
                if token in lower: match=rule; break
            if match: break
        if typ=="credit" and not match:
            cat,kind,nature,confidence,evidence="Other income","income","variable",.6,"Credit transaction; merchant rule not found"
        elif match:
            _,cat,kind,nature,tokens=match
            exact=any(lower.strip()==t for t in tokens)
            confidence=.95 if exact else (.75 if len(lower)>0 else .3)
            evidence=f"Description matched keyword: {next((t for t in tokens if t in lower), 'unknown')}"
        else:
            cat,kind,nature,confidence,evidence="Other","expense","discretionary",.3,"No merchant rule matched; review recommended"
        # Ensure credit-card bill payments and SIPs remain transfers/savings, not consumption.
        if "credit card" in lower and "payment" in lower: cat,kind,nature,confidence="Card settlement","transfer","transfer",.95
        cats.append(cat); kinds.append(kind); natures.append(nature); confs.append(confidence); evidences.append(evidence)
    result["category"]=cats; result["kind"]=kinds; result["nature"]=natures; result["confidence"]=confs; result["evidence"]=evidences
    return result

def review_queue(df: pd.DataFrame, threshold: float=0.7) -> pd.DataFrame:
    if df.empty or "confidence" not in df.columns: return df.iloc[0:0].copy()
    mask=pd.to_numeric(df["confidence"],errors="coerce").fillna(0)<float(threshold)
    # Potential assets require confirmation even when a merchant rule is strong.
    if "kind" in df.columns: mask |= df["kind"].eq("potential_asset")
    return df.loc[mask].copy().reset_index(drop=True)
