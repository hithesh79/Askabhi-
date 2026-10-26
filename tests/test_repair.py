from core.repair import repair_plan
from core.models import ScenarioParams
from core.rng import make_draws
from conftest import make_small_context


def test_repair_keeps_same_draw_fingerprint(ctx,draws):
    r=repair_plan(ctx,draws,target_prob=0.0)
    assert r.fingerprint_before==r.fingerprint_after==draws.fingerprint()

def test_repair_result_has_probabilities(ctx,draws):
    r=repair_plan(ctx,draws,target_prob=.1)
    assert 0<=r.before_probability<=1 and 0<=r.after_probability<=1

def test_repair_never_reduces_reported_target_probability(ctx,draws):
    r=repair_plan(ctx,draws.head(10),target_prob=.99)
    assert r.after_probability+1e-9>=r.before_probability
    assert all(x["probability_after"]+1e-9>=x["probability_before"] for x in r.repairs)

def test_repair_reports_if_target_not_reached():
    ctx=make_small_context(income=0,assets=False)
    ctx.profile.emergency_months=0
    d=make_draws(3,5,24)
    r=repair_plan(ctx,d,target_prob=1.0)
    assert isinstance(r.reached_target,bool)

def test_repair_has_alternative_package_labels(ctx,draws):
    r=repair_plan(ctx,draws,target_prob=0)
    assert {x["name"] for x in r.alternatives}=={"Least lifestyle pain","Least delay","Least rupee cost"}
