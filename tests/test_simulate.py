from copy import deepcopy
from datetime import date
import numpy as np
from core.models import ScenarioParams, Asset, Profile, BehaviourProfile, PlanContext, Goal
from core.rng import make_draws
from core.simulate import simulate, deterministic_projection
from conftest import AS_OF, make_small_context


def test_same_seed_same_simulation(ctx):
    a=simulate(ctx,ScenarioParams(),make_draws(42,40,60)); b=simulate(ctx,ScenarioParams(),make_draws(42,40,60))
    assert np.array_equal(a.net_worth_p50,b.net_worth_p50) and np.array_equal(a.success_matrix,b.success_matrix)

def test_different_seed_changes_simulation(ctx):
    a=simulate(ctx,ScenarioParams(),make_draws(42,40,60)); b=simulate(ctx,ScenarioParams(),make_draws(43,40,60))
    assert not np.array_equal(a.net_worth_p50,b.net_worth_p50)

def test_result_fingerprint_matches_draws(ctx,draws):
    assert simulate(ctx,ScenarioParams(),draws).draws_fingerprint==draws.fingerprint()

def test_percentiles_are_ordered(ctx,draws):
    r=simulate(ctx,ScenarioParams(),draws)
    assert np.all(r.net_worth_p10<=r.net_worth_p25+1e-8)
    assert np.all(r.net_worth_p25<=r.net_worth_p50+1e-8)
    assert np.all(r.net_worth_p50<=r.net_worth_p75+1e-8)
    assert np.all(r.net_worth_p75<=r.net_worth_p90+1e-8)

def test_goal_probabilities_bounded(ctx,draws):
    r=simulate(ctx,ScenarioParams(),draws)
    assert all(0<=x<=1 for x in r.goal_probabilities.values())
    assert all(0<=x<=1 for x in r.goal_standard_errors.values())

def test_increased_income_does_not_lower_goal_probability(ctx,draws):
    high=deepcopy(ctx); high.profile.monthly_income_net*=1.25
    a=simulate(ctx,ScenarioParams(),draws); b=simulate(high,ScenarioParams(),draws)
    for gid,p in a.goal_probabilities.items(): assert b.goal_probabilities[gid]+1e-12>=p

def test_zero_income_and_zero_assets_do_not_crash(draws):
    c=make_small_context(income=0,assets=False,goals=False)
    r=simulate(c,ScenarioParams(),draws)
    assert len(r.months)>0 and np.all(np.isfinite(r.net_worth_p50))

def test_horizon_extends_past_short_draws():
    c=make_small_context()
    r=simulate(c,ScenarioParams(),make_draws(4,10,2))
    assert len(r.months)>=13

def test_locked_asset_unlocks_into_liquid_pool():
    p=Profile(AS_OF,0,"salaried",0,0,emergency_months=0,essential_monthly_spend=0)
    bp=BehaviourProfile(as_of=AS_OF,category_monthly_mean={},category_nature={},confidence="High")
    asset=Asset("Locked PPF","retirement",100000,"retirement","locked",date(2026,4,30),exp_return=0,vol=0)
    ctx=PlanContext(p,[asset],[],[],bp,None)
    r=simulate(ctx,ScenarioParams(),make_draws(4,20,20))
    assert np.median(r.liquid_p50[3:]) > np.median(r.liquid_p50[:3]) + 50000

def test_deterministic_projection_has_consistent_months(ctx):
    p=deterministic_projection(ctx,ScenarioParams())
    assert len(p.months)==len(p.liquid)==len(p.net_worth)

def test_income_cut_is_applied(ctx,draws):
    a=simulate(ctx,ScenarioParams(),draws)
    b=simulate(ctx,ScenarioParams(income_cut_pct=.3,income_cut_start=0,income_cut_months=6),draws)
    assert b.net_worth_p50[-1] < a.net_worth_p50[-1]

def test_unexpected_expense_changes_same_draw_result(ctx,draws):
    a=simulate(ctx,ScenarioParams(),draws)
    b=simulate(ctx,ScenarioParams(one_off_expenses=[(0,50000)]),draws)
    assert b.net_worth_p50[0] <= a.net_worth_p50[0]
