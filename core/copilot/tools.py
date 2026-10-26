"""Controlled tool registry: every numerical result comes from core calculations."""
from __future__ import annotations
from datetime import date
import calendar
import numpy as np
from core.models import Tool, ToolResult, PurchaseSpec, ScenarioParams
from core.simulate import simulate
from core.afford import evaluate_purchase
from core.leaks import find_leaks
from core.repair import repair_plan
from core.resilience import resilience_score
from core.arbiter import arbitrate
from core.formatting import inr, pct
from core.rng import make_draws

def _get(session,key,default=None):
    if isinstance(session,dict): return session.get(key,default)
    return getattr(session,key,default)
def _add_months(d,m):
    i=d.year*12+d.month-1+int(m); y,m0=divmod(i,12); mo=m0+1
    return date(y,mo,min(d.day,calendar.monthrange(y,mo)[1]))
def _draws(session):
    d=_get(session,"draws")
    if d is None: d=make_draws(42,500,240)
    return d

def diagnose_savings(args,session):
    ctx=_get(session,"ctx"); bp=ctx.behaviour; income=(bp.safe_income if bp and bp.safe_income else ctx.profile.monthly_income_net)
    categories=bp.category_monthly_mean if bp else {}; natures=bp.category_nature if bp else {}
    fixed=sum(v for k,v in categories.items() if natures.get(k) in ("essential","fixed"))
    disc=sorted([(k,v) for k,v in categories.items() if natures.get(k)=="discretionary"],key=lambda x:-x[1])
    emis=sum(l.emi for l in ctx.liabilities); unplanned=bp.irregular_expense_reserve if bp else 0
    observed=bp.actual_median_saving if bp else income-fixed-emis
    waterfall={"income":float(income),"fixed_and_essential":float(fixed),"emi":float(emis),"unplanned_reserve":float(unplanned),"actual_median_saving":float(observed),"top_discretionary_categories":[{"category":k,"monthly":float(v)} for k,v in disc[:3]],"stated_saving":ctx.profile.stated_monthly_saving}
    return ToolResult(waterfall,{"tool":"diagnose_savings","inputs":{"persona":ctx.persona_name},"outputs":waterfall,"seed":_draws(session).seed,"fingerprint":_draws(session).fingerprint()})

def goal_status(args,session):
    ctx=_get(session,"ctx"); d=_draws(session); res=simulate(ctx,ScenarioParams(),d); goal_id=args.get("goal_id")
    goals=[g for g in ctx.goals if (not goal_id or g.goal_id==goal_id or g.name.lower()==str(goal_id).lower())]
    output=[]
    for g in goals:
        months=max(0,(g.target_date.year-ctx.profile.as_of.year)*12+g.target_date.month-ctx.profile.as_of.month)
        prob=res.goal_probabilities.get(g.goal_id,0)
        output.append({"goal_id":g.goal_id,"name":g.name,"target_in_today_rupees":g.target_amount_today,"target_date":g.target_date.isoformat(),"months_remaining":months,"success_probability":prob,"standard_error":res.goal_standard_errors.get(g.goal_id,0),"median_shortfall":res.goal_median_shortfalls.get(g.goal_id,0)})
    val={"goals":output,"hard_goal_probability":res.extra.get("hard_goal_success_probability",0),"emergency_breach_probability":res.emergency_breach_probability}
    return ToolResult(val,{"tool":"goal_status","arguments":args,"outputs":val,"seed":d.seed,"fingerprint":d.fingerprint()})

def evaluate_purchase_tool(args,session):
    ctx=_get(session,"ctx"); draws=_draws(session)
    amount=float(args.get("amount",450000)); months=int(args.get("months",12)); name=str(args.get("name","Proposed purchase")); category=str(args.get("category","vehicle")); mode=str(args.get("mode","compare"))
    spec=PurchaseSpec(name,category,amount,_add_months(ctx.profile.as_of,months),mode,float(args.get("down_payment_pct",.2)),float(args.get("loan_rate",.12)),int(args.get("tenure_months",36)),float(args.get("running_cost_monthly",3000)),args.get("onroad_multiplier"))
    res=evaluate_purchase(ctx,spec,draws)
    val={"verdict":res.verdict,"price":res.onroad_cost,"inflated_cost":res.inflated_cost,"cash_probability":res.cash_probability,"cash_se":res.cash_se,"loan_probability":res.loan_probability,"loan_se":res.loan_se,"emi":res.emi,"emi_share_income":res.emi_share_income,"binding_constraint":res.binding_constraint,"levers":res.levers[:5],"other_goal_impacts":res.other_goal_impacts}
    return ToolResult(val,{"tool":"evaluate_purchase","arguments":{"name":name,"price":amount,"months":months,"mode":mode},"outputs":val,"seed":draws.seed,"fingerprint":draws.fingerprint()})

def run_scenario(args,session):
    ctx=_get(session,"ctx"); draws=_draws(session)
    p=ScenarioParams(income_cut_pct=max(0,min(.95,float(args.get("income_cut_pct",0)))),income_cut_start=max(0,int(args.get("start_month",0))),income_cut_months=max(0,int(args.get("duration_months",12))),job_loss_months=max(0,int(args.get("job_loss_months",0))),job_loss_start=max(0,int(args.get("start_month",0))),one_off_expenses=[(max(0,int(args.get("start_month",0))),max(0,float(args.get("one_off_expense",0))))] if args.get("one_off_expense") else [],extra_monthly_expense=max(0,float(args.get("extra_monthly_expense",0))))
    base=simulate(ctx,ScenarioParams(),draws); attacked=simulate(ctx,p,draws)
    val={"baseline_goal_probabilities":base.goal_probabilities,"stressed_goal_probabilities":attacked.goal_probabilities,"goal_probability_changes":{g:attacked.goal_probabilities.get(g,0)-v for g,v in base.goal_probabilities.items()},"baseline_emergency_breach":base.emergency_breach_probability,"stressed_emergency_breach":attacked.emergency_breach_probability,"scenario":args}
    return ToolResult(val,{"tool":"run_scenario","arguments":args,"outputs":val,"seed":draws.seed,"fingerprint":draws.fingerprint()})

def find_leaks_tool(args,session):
    ctx=_get(session,"ctx"); draws=_draws(session); goal=args.get("goal_id") or (ctx.goals[0].goal_id if ctx.goals else "")
    leaks=find_leaks(ctx,draws,goal)
    val=[{"category":x.category,"monthly_spend":x.monthly_spend,"success_before":x.probability_before,"success_after":x.probability_after,"months_sooner":x.months_sooner,"description":x.description} for x in leaks]
    return ToolResult(val,{"tool":"find_leaks","arguments":{"goal_id":goal},"outputs":val,"seed":draws.seed,"fingerprint":draws.fingerprint()})

def repair_goal_tool(args,session):
    ctx=_get(session,"ctx"); draws=_draws(session); res=repair_plan(ctx,draws,float(args.get("target_probability",.85)))
    val={"repairs":res.repairs,"before_probability":res.before_probability,"after_probability":res.after_probability,"reached_target":res.reached_target,"fingerprint_before":res.fingerprint_before,"fingerprint_after":res.fingerprint_after}
    return ToolResult(val,{"tool":"repair_goal","arguments":args,"outputs":val,"seed":draws.seed,"fingerprint":draws.fingerprint()})

def asset_growth_options(args,session):
    ctx=_get(session,"ctx"); draws=_draws(session); bp=ctx.behaviour
    actual=bp.actual_median_saving if bp else ctx.profile.monthly_income_net*.1
    goal=next(iter(ctx.goals),None); leaks=find_leaks(ctx,draws,goal.goal_id) if goal else []
    arb=arbitrate(ctx,max(0,actual),draws)
    options=[{"option":"Increase repeatable monthly saving","illustrative_monthly_amount":max(0,actual)*.1,"basis":"10% of observed median saving; adjust to real cash flow"},{"option":"Review discretionary categories","illustrative_monthly_amount":sum(x.monthly_spend*.2 for x in leaks[:3]),"basis":"Modelled 20% reduction in selected categories, not a directive"},{"option":arb.preferred_option,"illustrative_monthly_amount":arb.emergency_topup,"basis":arb.explanation}]
    val={"observed_median_saving":actual,"options":options,"warning":"Educational scenarios only; returns are uncertain and suitable investments depend on risk tolerance and personal circumstances."}
    return ToolResult(val,{"tool":"asset_growth_options","outputs":val,"seed":draws.seed,"fingerprint":draws.fingerprint()})

def explain_score(args,session):
    ctx=_get(session,"ctx"); draws=_draws(session); res=simulate(ctx,ScenarioParams(),draws); score=resilience_score(ctx,res)
    val={"score":score.score,"grade":score.grade,"hard_goals_probability":score.hard_goals_probability,"emergency_floor_never_breached_probability":score.emergency_floor_never_breached_probability,"runway_months":score.runway_months,"components":score.components,"explanation":score.explanation}
    return ToolResult(val,{"tool":"explain_score","outputs":val,"seed":draws.seed,"fingerprint":draws.fingerprint()})

def compare_plans(args,session):
    from copy import deepcopy
    ctx=_get(session,"ctx"); draws=_draws(session); base=simulate(ctx,ScenarioParams(),draws); changed=deepcopy(ctx)
    goal_id=args.get("goal_id")
    if goal_id and "priority" in args:
        for g in changed.goals:
            if g.goal_id==goal_id: g.priority=int(args["priority"])
    if goal_id and "delay_months" in args:
        g=next((g for g in changed.goals if g.goal_id==goal_id),None)
        if g: g.target_date=_add_months(g.target_date,int(args["delay_months"]))
    after=simulate(changed,ScenarioParams(),draws)
    val={"plan_a":base.goal_probabilities,"plan_b":after.goal_probabilities,"changes":{g:after.goal_probabilities.get(g,0)-v for g,v in base.goal_probabilities.items()},"same_draws":base.draws_fingerprint==after.draws_fingerprint}
    return ToolResult(val,{"tool":"compare_plans","arguments":args,"outputs":val,"seed":draws.seed,"fingerprint":draws.fingerprint()})

TOOLS: dict[str,Tool]={
 "diagnose_savings":Tool("diagnose_savings","Explain where monthly income goes and estimate observed savings.",diagnose_savings,{"type":"object","properties":{},"additionalProperties":False}),
 "evaluate_purchase":Tool("evaluate_purchase","Evaluate affordability for a proposed purchase.",evaluate_purchase_tool,{"type":"object","properties":{"name":{"type":"string"},"amount":{"type":"number"},"months":{"type":"integer"},"mode":{"type":"string"}},"additionalProperties":False}),
 "goal_status":Tool("goal_status","Get goal feasibility, uncertainty and shortfall.",goal_status,{"type":"object","properties":{"goal_id":{"type":"string"}},"additionalProperties":False}),
 "run_scenario":Tool("run_scenario","Compare baseline goals with an income/expense shock.",run_scenario,{"type":"object","properties":{"income_cut_pct":{"type":"number"},"duration_months":{"type":"integer"},"job_loss_months":{"type":"integer"},"one_off_expense":{"type":"number"}},"additionalProperties":False}),
 "find_leaks":Tool("find_leaks","Estimate discretionary category changes that could help a goal.",find_leaks_tool,{"type":"object","properties":{"goal_id":{"type":"string"}},"additionalProperties":False}),
 "repair_goal":Tool("repair_goal","Search for non-worsening repairs to a financial plan.",repair_goal_tool,{"type":"object","properties":{"target_probability":{"type":"number"}},"additionalProperties":False}),
 "asset_growth_options":Tool("asset_growth_options","Compare educational options for strengthening savings and assets.",asset_growth_options,{"type":"object","properties":{},"additionalProperties":False}),
 "explain_score":Tool("explain_score","Explain the resilience score and its components.",explain_score,{"type":"object","properties":{},"additionalProperties":False}),
 "compare_plans":Tool("compare_plans","Compare alternative goal priorities or deadlines on identical draws.",compare_plans,{"type":"object","properties":{"goal_id":{"type":"string"},"priority":{"type":"integer"},"delay_months":{"type":"integer"}},"additionalProperties":False}),
}

def run_tool(name: str, args: dict, session) -> ToolResult:
    if name not in TOOLS: raise KeyError(f"Unknown financial tool: {name}")
    return TOOLS[name].function(args or {},session)
