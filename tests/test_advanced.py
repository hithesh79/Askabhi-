from copy import deepcopy
from datetime import date
import numpy as np
import pandas as pd
import pytest
from core.autopilot import payday_plan, safe_to_spend
from core.radar import cash_radar
from core.timemachine import three_futures, at_month
from core.sensitivity import tornado
from core.conflict import conflict_matrix, regret
from core.events import EVENT_LIBRARY, apply_event
from core.guardrails import apply_rules, compare_with_without
from core.arbiter import arbitrate
from core.household import household_resilience
from core.backtest import rolling_backtest, plan_autopsy
from core.copilot.guard import verify_numbers
from core.copilot.offline import answer, parse_amount, parse_percent
from core.report import build_report_html
from core.models import ScenarioParams
from core.simulate import simulate
from core.resilience import resilience_score
from core.rng import make_draws
from conftest import AS_OF, make_small_context


def session_for(ctx,draws):
    base=simulate(ctx,ScenarioParams(),draws)
    return {"ctx":ctx,"draws":draws,"baseline":base}

def test_payday_buckets_balance_to_salary(ctx,draws):
    p=payday_plan(ctx,draws,AS_OF)
    assert abs(sum(p.buckets[k] for k in ["Loan EMIs","Essentials","Emergency top-up","Goal contributions","Safe-to-spend allowance"])-p.salary)<1.01

def test_safe_to_spend_is_nonnegative(ctx,draws):
    p=payday_plan(ctx,draws,AS_OF); s=safe_to_spend(ctx,p,AS_OF,5000)
    assert s.safe_today>=0 and s.allowance_remaining>=0

def test_cash_radar_has_daily_series(ctx,draws):
    r=cash_radar(ctx,draws,AS_OF,30)
    assert len(r.dates)==30 and len(r.p10)==30 and len(r.p90)==30
    assert np.all(r.p10<=r.p50+1e-8) and np.all(r.p50<=r.p90+1e-8)

def test_time_machine_has_three_futures(ctx,draws):
    f=three_futures(ctx,draws); s=at_month(f,3)
    assert f.fingerprint==draws.fingerprint() and s.month==f.months[3]
    assert set(s.values)=={"stated","behaviour","repaired"}

def test_sensitivity_is_sorted(ctx,draws):
    t=tornado(ctx,draws,"bike")
    assert not t.empty and t.max_abs_effect_pp.is_monotonic_decreasing

def test_conflict_matrix_diagonal_zero(ctx,draws):
    m=conflict_matrix(ctx,draws)
    assert all(abs(m.loc[i,i])<1e-12 for i in m.index)

def test_regret_is_nonnegative(ctx,draws):
    r=regret({"goal_id":"bike","delay_months":6,"lifestyle_cut_rupees":12000,"penalty_cost":1000},ctx,draws)
    assert r.total>=13000 and "heuristic" in r.explanation

def test_event_library_has_wedding_and_layoff():
    assert "wedding" in EVENT_LIBRARY and "layoff" in EVENT_LIBRARY

def test_event_adds_scheduled_expense():
    p=apply_event(ScenarioParams(),"wedding",3)
    assert p.one_off_expenses and p.one_off_expenses[0][0]==3

def test_event_unknown_key_rejected():
    with pytest.raises(KeyError): apply_event(ScenarioParams(),"unknown",0)

def test_guardrails_do_not_mutate_original():
    p=ScenarioParams(); changed=apply_rules(p,[{"type":"emergency_pause_goal","goal_id":"bike","months":3}])
    assert not p.guardrails and len(changed.guardrails)==1

def test_guardrail_comparison_uses_same_draws(ctx,draws):
    r=compare_with_without(ctx,draws,[{"type":"income_drop_cut_discretionary","drop_pct":.2,"cut_pct":.15}])
    assert r["same_fingerprint"] is True
    assert r["baseline"].draws_fingerprint==r["guarded"].draws_fingerprint

def test_arbiter_prefers_prepay_when_loan_rate_above_risk_adjusted(ctx,draws):
    c=deepcopy(ctx); c.liabilities[0].annual_rate=.40
    r=arbitrate(c,50000,draws)
    assert r.loan_rate>r.risk_adjusted_return
    assert r.preferred_option=="Prepay loan" or r.preferred_option=="Top up emergency buffer"

def test_household_correlation_bounds(ctx,draws):
    r=household_resilience(ctx,ctx,1.0,draws)
    assert 0<=r.joint_failure_probability<=1 and 0<=r.independent_failure_probability<=1

def test_household_high_correlation_not_less_joint_risk_than_independent(ctx,draws):
    r=household_resilience(ctx,ctx,1.0,draws)
    assert r.joint_failure_probability+0.1>=r.independent_failure_probability

def test_backtest_returns_report(ctx):
    rows=[]
    for m in range(1,13):
        rows.append({"date":f"2025-{m:02d}-01","description":"Groceries","amount":2000+m*10,"type":"debit","account":"BANK"})
        rows.append({"date":f"2025-{m:02d}-05","description":"Salary credit","amount":95000,"type":"credit","account":"BANK"})
    df=pd.DataFrame(rows)
    result=rolling_backtest(df,AS_OF,ctx.profile)
    assert result.nominal_coverage==.8 and len(result.origins)>0

def test_plan_autopsy_returns_rows(ctx):
    r=plan_autopsy(ctx,ctx.transactions)
    assert isinstance(r,pd.DataFrame) and "breached" in r.columns

def test_number_guard_accepts_evidence_numbers():
    r=verify_numbers("Balance ₹1,000; probability 50%",{"balance":1000,"probability":"50%"})
    assert r.valid

def test_number_guard_flags_injected_number():
    r=verify_numbers("Your balance is ₹99,999",{"balance":1000})
    assert not r.valid and r.unverified_numbers

@pytest.mark.parametrize("text,expected",[("4.5 lakh",450000),("2 cr",20000000),("60k",60000),("₹95,000",95000)])
def test_copilot_amount_parser(text,expected): assert parse_amount(text)==expected

def test_copilot_percent_parser(): assert parse_percent("income drops 20%") == .2

def test_offline_copilot_diagnoses_savings(ctx,draws):
    a=answer("Why am I unable to save enough for my bike?",session_for(ctx,draws))
    assert a.verdict and a.evidence and a.mode=="offline"

def test_offline_copilot_rejects_nonsense_without_inventing(ctx,draws):
    a=answer("Explain my quantum spaceship finance",session_for(ctx,draws))
    assert "did not recognise" in a.caveat

def test_report_is_self_contained_html(ctx,draws):
    h=build_report_html(session_for(ctx,draws))
    assert h.startswith("<!doctype html>") and "AskAbhi 360" in h and "<svg" in h
    assert "#070B09" in h and "#B7FF72" in h
    assert "#F7F4EE" not in h and "#C66B46" not in h

def test_optional_llm_unavailable_by_default(monkeypatch):
    monkeypatch.delenv("ASKABHI_LLM_API_KEY",raising=False)
    from core.copilot.llm import available
    assert available() is False

def test_xfail_structural_income_break_limitation():
    pytest.xfail("A structural income break cannot be inferred from only two months of otherwise stable transaction history; the model needs updated user assumptions.")
