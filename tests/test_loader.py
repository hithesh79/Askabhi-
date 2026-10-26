from datetime import date
import pandas as pd
from core.loader import load_transactions, load_assets, load_liabilities, load_goals


def txframe(rows):
    return pd.DataFrame(rows,columns=["date","description","amount","type","account"])

def test_valid_transaction_loaded():
    df,issues=load_transactions(txframe([["2026-01-01","Salary",1000,"credit","BANK"]]))
    assert len(df)==1 and not issues

def test_duplicate_transaction_dropped():
    row=["2026-01-01","Salary",1000,"credit","BANK"]
    df,issues=load_transactions(txframe([row,row]))
    assert len(df)==1 and any(x.field=="duplicate" for x in issues)

def test_invalid_date_row_dropped():
    df,issues=load_transactions(txframe([["bad-date","Rent",100,"debit","BANK"]]))
    assert df.empty and any(x.field=="date" for x in issues)

def test_zero_amount_row_dropped():
    df,issues=load_transactions(txframe([["2026-01-01","Rent",0,"debit","BANK"]]))
    assert df.empty and any(x.field=="amount" for x in issues)

def test_negative_amount_row_dropped():
    df,issues=load_transactions(txframe([["2026-01-01","Rent",-5,"debit","BANK"]]))
    assert df.empty and any(x.field=="amount" for x in issues)

def test_missing_description_repaired():
    df,issues=load_transactions(txframe([["2026-01-01","",100,"debit","BANK"]]))
    assert df.iloc[0].description=="Unknown transaction" and any(x.field=="description" for x in issues)

def test_missing_columns_added():
    df,issues=load_transactions(pd.DataFrame([{"date":"2026-01-01","amount":100}]))
    assert all(c in df.columns for c in ["description","type","account"]) and any(x.field=="columns" for x in issues)

def test_empty_file_friendly():
    df,issues=load_transactions(pd.DataFrame())
    assert df.empty and issues

def test_invalid_type_flagged_and_repaired():
    df,issues=load_transactions(txframe([["2026-01-01","Rent",100,"x","BANK"]]))
    assert df.iloc[0].type=="debit" and any(x.field=="type" for x in issues)

def test_valid_asset_loaded():
    vals,issues=load_assets(pd.DataFrame([{"name":"Savings","kind":"bank","value":1000,"asset_class":"cash","liquidity":"liquid"}]))
    assert vals[0].value==1000 and not issues

def test_unknown_liquidity_asset_dropped():
    vals,issues=load_assets(pd.DataFrame([{"name":"Savings","kind":"bank","value":1000,"asset_class":"cash","liquidity":"unknown"}]))
    assert not vals and issues

def test_negative_asset_dropped():
    vals,issues=load_assets(pd.DataFrame([{"name":"Savings","kind":"bank","value":-5,"asset_class":"cash","liquidity":"liquid"}]))
    assert not vals and issues

def test_valid_liability_loaded():
    vals,issues=load_liabilities(pd.DataFrame([{"name":"Loan","kind":"personal","outstanding":1000,"annual_rate":.1,"emi":100,"months_left":12}]))
    assert vals[0].outstanding==1000 and not issues

def test_valid_goal_loaded():
    vals,issues=load_goals(pd.DataFrame([{"goal_id":"bike","name":"Bike","category":"vehicle","target_amount_today":100000,"target_date":"2027-01-01","priority":1}]),date(2026,1,1))
    assert vals[0].goal_id=="bike" and not issues

def test_past_goal_date_flagged_but_retained():
    vals,issues=load_goals(pd.DataFrame([{"goal_id":"bike","name":"Bike","category":"vehicle","target_amount_today":100000,"target_date":"2025-01-01","priority":1}]),date(2026,1,1))
    assert len(vals)==1 and any(x.field=="target_date" for x in issues)

def test_invalid_goal_priority_dropped():
    vals,issues=load_goals(pd.DataFrame([{"goal_id":"bike","name":"Bike","category":"vehicle","target_amount_today":100000,"target_date":"2027-01-01","priority":4}]))
    assert not vals and issues
