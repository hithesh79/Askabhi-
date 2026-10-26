"""Config-backed illustrative life-event library."""
from __future__ import annotations
from config import CFG
from core.models import ScenarioParams
_COSTS={name:(low,high) for name,low,high in CFG.event_cost_ranges_inr}
EVENT_LIBRARY={
 "wedding":{"label":"Wedding","cost_range_inr":_COSTS["wedding"],"description":"One-off wedding expense; indicative, edit these."},
 "baby":{"label":"New baby","cost_range_inr":_COSTS["baby"],"description":"Initial and recurring family costs; indicative, edit these."},
 "parents_medical":{"label":"Parents\' medical care","cost_range_inr":_COSTS["parents_medical"],"description":"Unplanned medical-support cost; indicative, edit these."},
 "job_switch":{"label":"Job switch","income_gap_months":CFG.event_job_switch_income_gap_months,"description":"Temporary income gap; indicative, edit these."},
 "relocation":{"label":"Relocation","cost_range_inr":_COSTS["relocation"],"description":"Moving cost; indicative, edit these."},
 "layoff":{"label":"Layoff","income_gap_months":CFG.event_layoff_income_gap_months,"description":"Temporary employment gap; indicative, edit these."},
 "home_renovation":{"label":"Home renovation","cost_range_inr":_COSTS["home_renovation"],"description":"Home improvement cost; indicative, edit these."},
}
def apply_event(params: ScenarioParams, event_key: str, month: int) -> ScenarioParams:
    """Return copied ScenarioParams containing an illustrative scheduled event."""
    if event_key not in EVENT_LIBRARY: raise KeyError(f"Unknown event: {event_key}")
    import copy
    out=copy.deepcopy(params); event=EVENT_LIBRARY[event_key]
    if "cost_range_inr" in event:
        low,high=event["cost_range_inr"]; out.one_off_expenses.append((int(month),float((low+high)/2)))
    else:
        lo,hi=event["income_gap_months"]; out.job_loss_start=int(month); out.job_loss_months=int(round((lo+hi)/2))
    return out
