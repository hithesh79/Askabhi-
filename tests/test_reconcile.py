import pandas as pd
from core.classify import classify
from core.reconcile import reconcile

def test_card_payment_excluded_from_spend():
    df=classify(pd.DataFrame([{"date":"2026-01-01","description":"Credit card bill payment","amount":3000,"type":"debit","account":"SAVINGS"}]))
    r,report=reconcile(df); assert r.iloc[0].exclude_from_spend and report.card_payment_count==1

def test_own_transfer_excluded():
    df=classify(pd.DataFrame([{"date":"2026-01-01","description":"Transfer to savings own account","amount":1000,"type":"debit","account":"SAVINGS"}]))
    r,report=reconcile(df); assert r.iloc[0].exclude_from_spend and report.own_transfer_count==1

def test_sip_is_saving_not_expense():
    df=classify(pd.DataFrame([{"date":"2026-01-01","description":"SIP mutual fund transfer","amount":5000,"type":"debit","account":"SAVINGS"}]))
    r,report=reconcile(df); assert r.iloc[0].kind=="investment" and r.iloc[0].exclude_from_spend and report.sip_count==1

def test_purchase_itself_is_not_excluded():
    df=classify(pd.DataFrame([{"date":"2026-01-01","description":"Amazon card purchase","amount":1000,"type":"debit","account":"CREDIT_CARD"}]))
    r,_=reconcile(df); assert not r.iloc[0].exclude_from_spend

def test_empty_reconcile_returns_columns():
    r,report=reconcile(pd.DataFrame()); assert "exclude_from_spend" in r and report.card_payment_count==0
