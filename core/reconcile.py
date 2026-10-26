"""Reconcile account transfers and card settlements to prevent double-counting."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from core.models import Issue

@dataclass
class ReconcileReport:
    own_transfer_count: int = 0
    card_payment_count: int = 0
    sip_count: int = 0
    double_counting_prevented_inr: float = 0.0
    messages: list[str] | None = None

def reconcile(df: pd.DataFrame):
    out=df.copy(); report=ReconcileReport(messages=[])
    if out.empty:
        for col in ("category","kind","nature","confidence","evidence","exclude_from_spend","reconciled_as"): 
            if col not in out.columns: out[col]=pd.Series(dtype=object)
        return out,report
    if "kind" not in out.columns:
        from core.classify import classify
        out=classify(out)
    out["exclude_from_spend"]=False; out["reconciled_as"]=""
    desc=out["description"].fillna("").astype(str).str.lower()
    account=out.get("account",pd.Series("",index=out.index)).fillna("").astype(str).str.lower()
    # Exclude transfers that are not consumption; source and destination records may both exist.
    own=desc.str.contains(r"self transfer|own account|own a/c|transfer to savings|between my accounts",regex=True)
    out.loc[own,"exclude_from_spend"]=True; out.loc[own,"kind"]="transfer"; out.loc[own,"reconciled_as"]="Own-account transfer"
    report.own_transfer_count=int(own.sum())
    cards=desc.str.contains(r"credit card bill|card payment|card settlement",regex=True)
    out.loc[cards,"exclude_from_spend"]=True; out.loc[cards,"kind"]="transfer"; out.loc[cards,"reconciled_as"]="Credit-card settlement; purchase counted at purchase time"
    report.card_payment_count=int(cards.sum())
    sip=desc.str.contains(r"\bsip\b|mutual fund transfer|investment transfer",regex=True)
    out.loc[sip,"exclude_from_spend"]=True; out.loc[sip,"kind"]="investment"; out.loc[sip,"nature"]="saving"; out.loc[sip,"reconciled_as"]="Investment contribution counted as saving"
    report.sip_count=int(sip.sum())
    report.double_counting_prevented_inr=float(pd.to_numeric(out.loc[cards|own,"amount"],errors="coerce").fillna(0).sum())
    report.messages.extend([f"Excluded {report.own_transfer_count} own-account transfers from consumption.",f"Excluded {report.card_payment_count} card settlements; purchases remain counted at purchase time.",f"Classified {report.sip_count} SIP/investment transfers as saving rather than consumption."])
    return out,report
