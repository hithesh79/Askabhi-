"""Purchase affordability, loan comparison, levers and binding-constraint diagnosis."""
from __future__ import annotations
from copy import deepcopy
from datetime import date
import calendar
from config import CFG
from core.models import PurchaseSpec, AffordResult, Goal, PlanContext, ScenarioParams, Draws
from core.networth import emi
from core.simulate import simulate

def _add_goal(ctx,spec,mode,price=None,target_date=None,goal_id="purchase"):
    cloned=deepcopy(ctx); cost=float(price if price is not None else spec.ex_showroom_or_price)
    multiplier=spec.onroad_multiplier
    if multiplier is None: multiplier=CFG.bike_onroad_multiplier if spec.category.lower() in ("bike","vehicle","motorcycle") else (CFG.car_onroad_multiplier if spec.category.lower()=="car" else 1.0)
    # If the plan already contains this purchase goal, replace it instead of double-counting it.
    match=next((g for g in cloned.goals if g.category.lower()==spec.category.lower() and (spec.category.lower() in ("vehicle","bike","car","motorcycle") or g.name.lower()==spec.name.lower())),None)
    actual_id=match.goal_id if match else goal_id
    goal=Goal(actual_id,spec.name,spec.category,cost,target_date or spec.target_date,1,True,.95,None,mode,spec.down_payment_pct,spec.loan_rate,spec.tenure_months,spec.running_cost_monthly,multiplier)
    cloned.goals=[g for g in cloned.goals if g.goal_id not in (goal_id,actual_id)]+[goal]
    return cloned,goal

def _prob(ctx,params,draws,gid):
    return simulate(ctx,params,draws).goal_probabilities.get(gid,0.0)

def _date_add(d,months):
    idx=d.year*12+d.month-1+months; y,m0=divmod(idx,12); mo=m0+1
    return date(y,mo,min(d.day,calendar.monthrange(y,mo)[1]))

def explain(ctx, spec: PurchaseSpec, draws: Draws) -> dict:
    """Relax plausible constraints separately and name the largest probability lift."""
    baseline_ctx,baseline_goal=_add_goal(ctx,spec,"cash")
    gid=baseline_goal.goal_id
    base=simulate(baseline_ctx,ScenarioParams(),draws).goal_probabilities.get(gid,0)
    tests=[]
    for name,desc,params in [
        ("savings","increase monthly savings",ScenarioParams(extra_monthly_saving=max(1000,ctx.profile.monthly_income_net*.05))),
        ("timing","wait six months",ScenarioParams(goal_changes={gid:{"target_date":_date_add(spec.target_date,6)}})),
        ("spending","cut discretionary spending 15%",ScenarioParams(expense_cut_pct=.15)),
    ]:
        p=simulate(baseline_ctx,params,draws).goal_probabilities.get(gid,0)
        tests.append({"name":name,"description":desc,"probability":p,"gain":p-base})
    usable=sum(max(0,a.value) for a in ctx.assets if a.liquidity=="liquid")
    tests.append({"name":"liquidity","description":"liquid assets are limited after protecting the emergency floor","probability":base,"gain":0.0,"available_liquid":usable})
    best=max(tests,key=lambda x:x["gain"])
    return {"name":best["name"],"description":best["description"],"base_probability":base,"best_probability":best["probability"],"relaxations":tests,"message":f"Your biggest tested lever is {best['description']}; estimated purchase-goal probability changes from {base:.0%} to {best['probability']:.0%}."}

def evaluate_purchase(ctx: PlanContext, spec: PurchaseSpec, draws: Draws) -> AffordResult:
    """Evaluate cash and loan purchase variants on identical random draws."""
    if spec.ex_showroom_or_price<0: raise ValueError("price cannot be negative")
    multiplier=spec.onroad_multiplier
    if multiplier is None: multiplier=CFG.bike_onroad_multiplier if spec.category.lower() in ("bike","vehicle","motorcycle") else (CFG.car_onroad_multiplier if spec.category.lower()=="car" else 1.0)
    onroad=spec.ex_showroom_or_price*multiplier
    months=max(0,(spec.target_date.year-ctx.profile.as_of.year)*12+spec.target_date.month-ctx.profile.as_of.month)
    infl=CFG.inflation_for(spec.category)
    inflated=onroad*(1+infl)**(months/12)
    cash_ctx,cash_goal=_add_goal(ctx,spec,"cash",spec.ex_showroom_or_price)
    loan_ctx,loan_goal=_add_goal(ctx,spec,"loan",spec.ex_showroom_or_price,goal_id="purchase")
    cash_id=cash_goal.goal_id; loan_id=loan_goal.goal_id
    params=ScenarioParams()
    cash_res=simulate(cash_ctx,params,draws); loan_res=simulate(loan_ctx,params,draws)
    cashp=cash_res.goal_probabilities.get(cash_id,0); loanp=loan_res.goal_probabilities.get(loan_id,0)
    cashse=cash_res.goal_standard_errors.get(cash_id,0); loanse=loan_res.goal_standard_errors.get(loan_id,0)
    payment=emi(max(0,inflated*(1-spec.down_payment_pct)),spec.loan_rate,spec.tenure_months)
    emi_share=payment/max(1,ctx.profile.monthly_income_net)
    base=simulate(ctx,params,draws)
    impacts=[]
    for g in ctx.goals:
        impacts.append({"goal_id":g.goal_id,"goal":g.name,"baseline_probability":base.goal_probabilities.get(g.goal_id,0),"cash_probability":cash_res.goal_probabilities.get(g.goal_id,0),"loan_probability":loan_res.goal_probabilities.get(g.goal_id,0),"cash_change":cash_res.goal_probabilities.get(g.goal_id,0)-base.goal_probabilities.get(g.goal_id,0),"loan_change":loan_res.goal_probabilities.get(g.goal_id,0)-base.goal_probabilities.get(g.goal_id,0)})
    levers=[]
    for save_pct in (0.02,.05,.10,.15,.20):
        p=simulate(cash_ctx,ScenarioParams(extra_monthly_saving=ctx.profile.monthly_income_net*save_pct),draws).goal_probabilities.get(cash_id,0)
        levers.append({"lever":f"Save {save_pct:.0%} more of income","cost_monthly":ctx.profile.monthly_income_net*save_pct,"before":cashp,"after":p,"gain":p-cashp,"pain":ctx.profile.monthly_income_net*save_pct})
    for cut in (.10,.20,.30):
        cc=deepcopy(cash_ctx)
        cheap,cheap_goal=_add_goal(cc,spec,"cash",spec.ex_showroom_or_price*(1-cut))
        p=simulate(cheap,params,draws).goal_probabilities.get(cheap_goal.goal_id,0)
        levers.append({"lever":f"Reduce price by {cut:.0%}","cost_monthly":0,"before":cashp,"after":p,"gain":p-cashp,"pain":cut*onroad})
    for delay in (3,6,9,12):
        delayed_ctx,delayed_goal=_add_goal(ctx, spec,"cash",spec.ex_showroom_or_price,_date_add(spec.target_date,delay))
        p=simulate(delayed_ctx,params,draws).goal_probabilities.get(delayed_goal.goal_id,0)
        levers.append({"lever":f"Wait {delay} months","cost_monthly":0,"before":cashp,"after":p,"gain":p-cashp,"pain":delay*1000})
    levers=[x for x in levers if x["gain"]>=-1e-9]
    levers.sort(key=lambda x: x["pain"]/max(x["gain"]*100,0.1))
    binding=explain(ctx,spec,draws)
    p=loanp if spec.mode=="loan" else cashp if spec.mode=="cash" else max(loanp,cashp)
    label="Very likely" if p>=.85 else "Likely" if p>=.65 else "Stretch" if p>=.40 else "Unlikely"
    return AffordResult(f"Your purchase is {label.lower()} under these assumptions ({p:.0%} simulated feasibility).",cashp,loanp,cashse,loanse,onroad,inflated,payment,emi_share,impacts,levers,binding,draws.fingerprint())
