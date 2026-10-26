import pandas as pd
from core.classify import classify, review_queue


def frame(desc, typ="debit"):
    return pd.DataFrame([{"date":"2026-01-01","description":desc,"amount":100,"type":typ,"account":"SAVINGS"}])

def test_salary_classified_as_income(): assert classify(frame("Salary credit","credit")).iloc[0].kind=="income"
def test_food_delivery_discretionary():
    r=classify(frame("Swiggy order")).iloc[0]; assert r.category=="Food delivery" and r.nature=="discretionary"
def test_gold_is_reviewable_potential_asset():
    r=classify(frame("Sai Baba Jewellers purchase")); assert r.iloc[0].kind=="potential_asset"; assert len(review_queue(r))==1
def test_sip_is_investment(): assert classify(frame("SIP mutual fund transfer")).iloc[0].kind=="investment"
def test_loan_emi_is_loan_kind(): assert classify(frame("Personal loan EMI")).iloc[0].kind=="loan"
def test_unknown_has_low_confidence(): assert classify(frame("XYZ marketplace mystery payment")).iloc[0].confidence<.7
def test_override_respected():
    df=frame("XYZ marketplace mystery payment"); r=classify(df,{"XYZ marketplace mystery payment":{"category":"Groceries","kind":"expense","nature":"essential"}})
    assert r.iloc[0].category=="Groceries" and r.iloc[0].confidence==1.0
def test_empty_frame_supported():
    r=classify(pd.DataFrame()); assert len(r)==0 and "kind" in r.columns
