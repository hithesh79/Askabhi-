from copy import deepcopy
from core.resilience import resilience_score
from core.models import ScenarioParams
from core.simulate import simulate

def test_resilience_in_range(ctx,draws):
    r=simulate(ctx,ScenarioParams(),draws); s=resilience_score(ctx,r)
    assert 0<=s.score<=100 and s.grade in {"Strong","Solid","Fragile","At risk"}

def test_resilience_components_sum_to_score_approximately(ctx,draws):
    r=simulate(ctx,ScenarioParams(),draws); s=resilience_score(ctx,r)
    assert abs(sum(s.components.values())-s.score)<=2

def test_resilience_explanation_is_not_credit_score(ctx,draws):
    s=resilience_score(ctx,simulate(ctx,ScenarioParams(),draws))
    assert "not a credit score" in s.explanation

def test_more_income_does_not_reduce_resilience(ctx,draws):
    low=resilience_score(ctx,simulate(ctx,ScenarioParams(),draws))
    raised=deepcopy(ctx); raised.profile.monthly_income_net*=1.3
    high=resilience_score(raised,simulate(raised,ScenarioParams(),draws))
    assert high.score>=low.score
