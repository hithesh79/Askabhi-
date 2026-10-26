from copy import deepcopy
import pandas as pd
from core.chaos import find_breaks, stress_report, _is_broken
from core.models import ScenarioParams
from core.rng import make_draws
from conftest import make_small_context


def test_stress_report_has_six_cases(ctx,draws):
    r=stress_report(ctx,draws)
    assert len(r)==6 and r["fingerprint"].nunique()==1

def test_stress_report_probabilities_bounded(ctx,draws):
    r=stress_report(ctx,draws)
    assert r.hard_goal_success_probability.between(0,1).all()
    assert r.emergency_breach_probability.between(0,1).all()

def test_unknown_target_is_not_claimed_broken(ctx):
    broken,p=_is_broken(ctx,ScenarioParams(),"no-such-goal")
    assert broken is False and p==0

def test_chaos_search_returns_at_most_three_distinct_components():
    ctx=make_small_context()
    # A deliberately constrained liquid-only context makes small shocks material.
    ctx.assets=[]; ctx.liabilities=[]; ctx.profile.monthly_income_net=1000
    ctx.profile.essential_monthly_spend=20000; ctx.profile.emergency_months=3
    ctx.goals=ctx.goals[:1]
    ctx.goals[0].target_amount_today=500000
    ctx.goals[0].target_date=ctx.profile.as_of.replace(month=7)
    d=make_draws(7,8,24)
    got=find_breaks(ctx,d,"bike")
    assert len(got)<=3 and len({x.name for x in got})==len(got)
    for scenario in got:
        broken,_=_is_broken(ctx,scenario.params,"bike")
        assert broken

def test_synthetic_scenario_default_is_no_change():
    p=ScenarioParams()
    assert p.income_cut_pct==0 and p.job_loss_months==0 and not p.one_off_expenses
