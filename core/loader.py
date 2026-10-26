"""Strict, forgiving CSV/dataframe validation with explicit handling reports."""
from __future__ import annotations
from pathlib import Path
from datetime import date
import pandas as pd
from core.models import Issue, Asset, Liability, Goal

TX_COLUMNS=["date","description","amount","type","account"]

def _read(src):
    if isinstance(src,pd.DataFrame): return src.copy()
    if hasattr(src,"read"): return pd.read_csv(src,encoding="utf-8")
    p=Path(src)
    if not p.exists(): raise FileNotFoundError(str(p))
    return pd.read_csv(p,encoding="utf-8")

def load_transactions(src):
    issues=[]
    try: df=_read(src)
    except Exception as exc: return pd.DataFrame(columns=TX_COLUMNS),[Issue(None,"file",f"Could not read transaction file: {exc}","Returned an empty clean transaction table.","error")]
    if df.empty: return pd.DataFrame(columns=TX_COLUMNS),[Issue(None,"file","File is empty.","Kept an empty clean table; import transactions to continue.")]
    missing=[c for c in TX_COLUMNS if c not in df.columns]
    if missing:
        issues.append(Issue(None,"columns",f"Missing required columns: {', '.join(missing)}","Added missing columns as blank values."))
        for col in missing: df[col]=None
    original_len=len(df)
    df=df.drop_duplicates().copy()
    if len(df)<original_len: issues.append(Issue(None,"duplicate",f"Detected {original_len-len(df)} duplicate rows.","Dropped exact duplicate rows."))
    parsed=pd.to_datetime(df["date"],errors="coerce")
    invalid=parsed.isna()
    for idx in df.index[invalid]: issues.append(Issue(int(idx)+2,"date","Date is missing or unparseable.","Dropped the row."))
    df=df.loc[~invalid].copy(); parsed=parsed.loc[~invalid]
    df["date"]=parsed.dt.date.astype(str)
    amounts=pd.to_numeric(df["amount"],errors="coerce")
    bad=amounts.isna() | (amounts<=0)
    for idx in df.index[bad]: issues.append(Issue(int(idx)+2,"amount","Amount is not a positive number.","Dropped the row."))
    df=df.loc[~bad].copy(); df["amount"]=amounts.loc[~bad].astype(float)
    missing_desc=df["description"].isna() | df["description"].astype(str).str.strip().eq("")
    for idx in df.index[missing_desc]: issues.append(Issue(int(idx)+2,"description","Description is missing.","Replaced with 'Unknown transaction' and flagged for review."))
    df.loc[missing_desc,"description"]="Unknown transaction"
    df["type"]=df["type"].fillna("debit").astype(str).str.lower().str.strip()
    df["type"]=df["type"].replace({"credit_in":"credit","income":"credit","expense":"debit","outflow":"debit"})
    invalid_type=~df["type"].isin(["debit","credit"])
    for idx in df.index[invalid_type]: issues.append(Issue(int(idx)+2,"type","Unknown transaction type.","Flagged and defaulted to debit."))
    df.loc[invalid_type,"type"]="debit"
    df["account"]=df["account"].fillna("UNKNOWN").astype(str).str.strip().replace("","UNKNOWN")
    df=df[TX_COLUMNS].reset_index(drop=True)
    if df.empty and not issues: issues.append(Issue(None,"file","No valid rows remain.","Import corrected transactions."))
    return df,issues

def _load_records(src, columns, converter, type_name):
    issues=[]
    try: df=_read(src)
    except Exception as exc: return [],[Issue(None,"file",f"Could not read {type_name}: {exc}","Returned an empty list.","error")]
    if df.empty: return [],[Issue(None,"file",f"{type_name.title()} file is empty.","Kept an empty list.")]
    missing=[c for c in columns if c not in df.columns]
    if missing:
        issues.append(Issue(None,"columns",f"Missing {type_name} columns: {', '.join(missing)}","Added blank columns; rows requiring them may be dropped."))
        for c in missing: df[c]=None
    result=[]
    for i,row in df.iterrows():
        try: result.append(converter(row))
        except Exception as exc: issues.append(Issue(int(i)+2,"row",f"Invalid {type_name} row: {exc}","Dropped the row."))
    return result,issues

def load_assets(src):
    allowed={"liquid","locked","penalty","illiquid"}
    cols=["name","kind","value","asset_class","liquidity"]
    def convert(r):
        name=str(r.name if False else r["name"]).strip()
        if not name or name.lower()=="nan": raise ValueError("name is missing")
        value=float(r["value"])
        if value<0: raise ValueError("value cannot be negative")
        liq=str(r["liquidity"]).lower().strip()
        if liq not in allowed: raise ValueError(f"unknown liquidity class {liq!r}")
        un=r.get("unlock_date")
        if pd.isna(un) or un in (None,""): un=None
        else: un=pd.Timestamp(un).date()
        return Asset(name,str(r.get("kind","other")),value,str(r.get("asset_class","cash")),liq,un,float(r.get("penalty_pct",0) or 0),float(r.get("exp_return",.03) or 0),float(r.get("vol",.01) or 0))
    return _load_records(src,cols,convert,"assets")

def load_liabilities(src):
    cols=["name","kind","outstanding"]
    def convert(r):
        outstanding=float(r["outstanding"])
        if outstanding<0: raise ValueError("outstanding cannot be negative")
        return Liability(str(r["name"]),str(r["kind"]),outstanding,float(r.get("annual_rate",0) or 0),float(r.get("emi",0) or 0),int(r.get("months_left",0) or 0))
    return _load_records(src,cols,convert,"liabilities")

def load_goals(src, as_of: date | None=None):
    cols=["goal_id","name","category","target_amount_today","target_date","priority"]
    issues=[]; goals=[]
    try: df=_read(src)
    except Exception as exc: return [],[Issue(None,"file",f"Could not read goals: {exc}","Returned an empty list.","error")]
    if df.empty: return [],[Issue(None,"file","Goals file is empty.","Add at least one goal.")]
    for c in cols:
        if c not in df.columns: df[c]=None; issues.append(Issue(None,"columns",f"Missing goal column: {c}","Added blank column; affected rows may be dropped."))
    for i,r in df.iterrows():
        try:
            d=pd.Timestamp(r["target_date"]).date()
            if as_of and d<as_of: issues.append(Issue(int(i)+2,"target_date","Goal date is in the past.","Flagged the goal; date retained for user review."))
            amount=float(r["target_amount_today"])
            if amount<=0: raise ValueError("target amount must be positive")
            priority=int(r["priority"])
            if priority not in (1,2,3): raise ValueError("priority must be 1, 2 or 3")
            goals.append(Goal(str(r["goal_id"]),str(r["name"]),str(r["category"]),amount,d,priority,bool(r.get("hard",True)),float(r.get("min_acceptable_pct",1) or 1),None if pd.isna(r.get("inflation")) else float(r["inflation"]),str(r.get("funding","cash")),float(r.get("down_payment_pct",.2) or .2),float(r.get("loan_rate",.12) or .12),int(r.get("loan_tenure_months",36) or 36)))
        except Exception as exc: issues.append(Issue(int(i)+2,"row",f"Invalid goal row: {exc}","Dropped the row."))
    return goals,issues
