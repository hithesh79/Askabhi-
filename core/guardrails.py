"""Rule templates for adaptive financial guardrails."""
from __future__ import annotations
from copy import deepcopy
from core.models import PlanContext, Draws, ScenarioParams
from core.simulate import simulate

GUARDRAIL_TEMPLATES={
 "emergency_pause_goal":{"label":"If emergency fund falls below X months, pause goal G contributions","fields":["months","goal_id"]},
 "income_drop_cut_discretionary":{"label":"If income drops by Y%, reduce discretionary spending by Z%","fields":["drop_pct","cut_pct"]},
 "negative_surplus_pause_sip":{"label":"If two negative-surplus months occur, pause SIP for N months","fields":["months"]},
}
def apply_rules(params: ScenarioParams, rules) -> ScenarioParams:
    out=deepcopy(params)
    out.guardrails.extend(deepcopy(list(rules or [])))
    return out

def compare_with_without(ctx: PlanContext, draws: Draws, rules):
    base=simulate(ctx,ScenarioParams(),draws)
    guarded=simulate(ctx,apply_rules(ScenarioParams(),rules),draws)
    return {"baseline":base,"guarded":guarded,"same_fingerprint":base.draws_fingerprint==guarded.draws_fingerprint,"probability_changes":{g:guarded.goal_probabilities.get(g,0)-p for g,p in base.goal_probabilities.items()},"note":"Rules are evaluated by the simulation hook. A guardrail can trade short-term goal speed for liquidity protection."}
