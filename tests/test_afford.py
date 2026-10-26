from copy import deepcopy
from datetime import date
import pytest
from core.afford import evaluate_purchase, explain
from core.models import PurchaseSpec
from core.rng import make_draws
from conftest import AS_OF


def spec(price=120000, months=6, mode="compare"):
    from core.data_gen import add_months
    return PurchaseSpec("Bike", "vehicle", price, add_months(AS_OF, months), mode, .2, .12, 36, 1500, 1.1)

def test_afford_returns_cash_and_loan_probabilities(ctx,draws):
    r=evaluate_purchase(ctx,spec(),draws)
    assert 0<=r.cash_probability<=1 and 0<=r.loan_probability<=1

def test_afford_uses_same_draw_fingerprint(ctx,draws):
    assert evaluate_purchase(ctx,spec(),draws).draws_fingerprint==draws.fingerprint()

def test_emi_share_is_computed(ctx,draws):
    r=evaluate_purchase(ctx,spec(),draws)
    assert r.emi>0 and r.emi_share_income==pytest.approx(r.emi/ctx.profile.monthly_income_net)

def test_higher_price_does_not_raise_cash_feasibility(ctx,draws):
    low=evaluate_purchase(ctx,spec(80000),draws)
    high=evaluate_purchase(ctx,spec(240000),draws)
    assert high.cash_probability<=low.cash_probability+1e-9

def test_levers_are_non_worsening(ctx,draws):
    r=evaluate_purchase(ctx,spec(),draws)
    assert all(x["after"]+1e-9>=x["before"] for x in r.levers)

def test_levers_are_ranked_by_pain_per_gain(ctx,draws):
    r=evaluate_purchase(ctx,spec(),draws)
    vals=[x["pain"]/max(x["gain"]*100,.1) for x in r.levers]
    assert vals==sorted(vals)

def test_binding_constraint_has_known_name(ctx,draws):
    r=evaluate_purchase(ctx,spec(),draws)
    assert r.binding_constraint["name"] in {"savings","timing","spending","liquidity"}

def test_explain_has_relaxations(ctx,draws):
    x=explain(ctx,spec(),draws)
    assert x["name"] in {"savings","timing","spending","liquidity"} and x["relaxations"]

def test_loan_mode_uses_smaller_cash_requirement(ctx,draws):
    r=evaluate_purchase(ctx,spec(),draws)
    assert r.inflated_cost>r.onroad_cost and r.emi>0
