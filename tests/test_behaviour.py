import pandas as pd
import pytest
from core.behaviour import analyse, shrinkage_weight, planned_unplanned, money_waterfall
from core.classify import classify
from core.reconcile import reconcile
from conftest import AS_OF


def test_arjun_has_12_months_and_high_confidence(analysed_arjun):
    tx,bp,bundle=analysed_arjun
    assert bp.months_of_data==12 and bp.confidence=="High"

def test_recurring_subscriptions_are_detected(analysed_arjun):
    _,bp,_=analysed_arjun
    assert any("netflix" in x for x in bp.recurring_merchants)
    assert any("netflix" in x for x in bp.subscription_merchants)

def test_weekend_spend_signal_is_computed(analysed_arjun):
    _,bp,_=analysed_arjun
    assert bp.weekend_weekday_ratio > 0

def test_lifestyle_creep_regression_is_computed(analysed_arjun):
    _,bp,_=analysed_arjun
    assert isinstance(bp.lifestyle_creep_slope,float) and 0<=bp.lifestyle_creep_pvalue<=1

def test_planned_unplanned_split_has_required_fields(analysed_arjun):
    _,bp,_=analysed_arjun
    out=planned_unplanned(bp)
    assert out["planned_monthly"]>=0 and out["unplanned_lambda_annual"]>=0
    assert "interpretation" in out

def test_empty_history_does_not_crash(ctx):
    bp=analyse(pd.DataFrame(),AS_OF,ctx.profile)
    assert bp.confidence=="Low" and bp.months_of_data==0

def test_irregular_persona_has_variable_income(meera_bundle):
    tx=classify(meera_bundle.transactions); tx,_=reconcile(tx)
    bp=analyse(tx,AS_OF,meera_bundle.profile)
    assert bp.income_label in {"Variable","Highly irregular"}
    assert bp.safe_income < (sum(bp.monthly_income_history)/max(1,len(bp.monthly_income_history)))

def test_behaviour_gap_uses_observed_saving(analysed_arjun):
    _,bp,_=analysed_arjun
    assert bp.stated_saving==25000
    assert "observed median" in bp.behaviour_gap

def test_waterfall_is_dataframe(analysed_arjun, arjun_bundle):
    _,bp,_=analysed_arjun
    result=money_waterfall(bp,arjun_bundle.profile)
    assert list(result.columns)==["bucket","amount"] and not result.empty

@pytest.mark.parametrize("n,k,expected",[(0,3,0),(3,3,.5),(30,3,10/11),(0,2,0),(2,2,.5)])
def test_shrinkage_weights(n,k,expected): assert shrinkage_weight(n,k)==pytest.approx(expected)

def test_shrinkage_zero_prior_constant(): assert shrinkage_weight(5,0)==1 and shrinkage_weight(0,0)==0

def test_income_cv_is_nonnegative(analysed_arjun): assert analysed_arjun[1].income_cv>=0

def test_data_sufficiency_changes_with_months(ctx):
    tx=pd.DataFrame([{"date":"2026-01-05","description":"Rent","amount":10000,"type":"debit","account":"SAVINGS"}])
    bp=analyse(tx,AS_OF,ctx.profile)
    assert bp.confidence=="Low"

def test_generated_persona_transactions_have_no_nested_dataframe_attrs():
    """Generated DataFrames must remain safe for pandas indexing/groupby operations."""
    from datetime import date
    from core.data_gen import generate_persona

    bundle = generate_persona("Arjun", date(2026, 10, 25), seed=42)
    assert all(not isinstance(value, pd.DataFrame) for value in bundle.transactions.attrs.values())
    bp = analyse(bundle.transactions, bundle.profile.as_of, bundle.profile)
    assert bp.months_of_data == 12
