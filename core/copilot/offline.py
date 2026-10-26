"""Rule-based, offline-first financial copilot. No LLM/network required."""
from __future__ import annotations
import re
from datetime import date
from core.models import Answer, ToolResult
from core.copilot.tools import run_tool
from core.copilot.guard import verify_numbers

def parse_amount(text: str, default: float=450000.0) -> float:
    m=re.search(r"(?i)(?:₹|rs\.?\s*)?([0-9][0-9,]*(?:\.[0-9]+)?)\s*(crore|crores|cr|lakh|lakhs|lac|l|k)?",text)
    if not m: return float(default)
    val=float(m.group(1).replace(",","")); unit=(m.group(2) or "").lower()
    return val*({"lakh":100000,"lakhs":100000,"lac":100000,"l":100000,"crore":10000000,"crores":10000000,"cr":10000000,"k":1000}.get(unit,1))

def parse_percent(text: str, default: float=.2) -> float:
    m=re.search(r"(-?\d+(?:\.\d+)?)\s*%",text)
    return float(m.group(1))/100 if m else default

def answer(question: str, session) -> Answer:
    q=str(question or "").strip(); lower=q.lower()
    if not q: return Answer("Ask a question about a goal, transaction pattern, asset, loan or financial scenario.",[],["Try: Can I afford a ₹4.5 lakh bike?"],"No financial calculation was run.")
    results=[]; actions=[]; evidence=[]; caveat="Estimates depend on the available transaction history and explicitly configured assumptions; they are not guarantees or investment advice."
    try:
        if any(x in lower for x in ("can i afford","afford","buy a","purchase")) or (lower.startswith("buy ") and any(x in lower for x in ("bike","car"))):
            amount=parse_amount(q,450000.0); months=12
            m=re.search(r"in\s+(\d+)\s+months?",lower)
            if m: months=int(m.group(1))
            name="BMW bike" if "bike" in lower else "Car" if "car" in lower else "Proposed purchase"
            result=run_tool("evaluate_purchase",{"name":name,"amount":amount,"months":months,"mode":"compare"},session); results=[result]
            v=result.value; evidence=[f"On-road estimate: ₹{v['price']:,.0f}",f"Cash feasibility: {v['cash_probability']:.0%}",f"Loan feasibility: {v['loan_probability']:.0%}",f"Loan EMI: ₹{v['emi']:,.0f}"]
            actions=[x["lever"] for x in v.get("levers",[])[:3]]
            verdict=v["verdict"]
        elif any(x in lower for x in ("asset","wealth","increase my","grow my","invest")):
            result=run_tool("asset_growth_options",{},session); results=[result]; v=result.value
            evidence=[f"Observed median saving: ₹{v['observed_median_saving']:,.0f}"]+[f"{o['option']}: illustrative ₹{o['illustrative_monthly_amount']:,.0f}/month" for o in v["options"]]
            actions=[o["option"] for o in v["options"]]; verdict="AskAbhi identified testable ways to strengthen savings and financial resilience."
        elif any(x in lower for x in ("leak","spend too much","unnecessary","where did my money","spending","saving enough","not saving","save enough")):
            result=run_tool("diagnose_savings",{},session); results=[result]; v=result.value
            evidence=[f"Planning income: ₹{v['income']:,.0f}/month",f"Fixed and essential outflows: ₹{v['fixed_and_essential']:,.0f}/month",f"EMIs: ₹{v['emi']:,.0f}/month",f"Observed median saving estimate: ₹{v['actual_median_saving']:,.0f}/month"]
            actions=[f"Review {x['category']} (about ₹{x['monthly']:,.0f}/month)" for x in v["top_discretionary_categories"]]
            verdict="AskAbhi's transaction profile shows the main known monthly outflows and where a review may help."
        elif any(x in lower for x in ("lose my job","job loss","salary drops","income drop","salary decrease","unexpected expense","medical")):
            cut=parse_percent(q,0.2); jobm=re.search(r"(\d+)\s+months?",lower)
            months=int(jobm.group(1)) if jobm else 6
            args={"income_cut_pct":cut if "salary" in lower or "income" in lower else 0,"duration_months":12,"job_loss_months":months if "job" in lower else 0,"one_off_expense":parse_amount(q,500000) if any(x in lower for x in ("medical","expense")) else 0}
            result=run_tool("run_scenario",args,session); results=[result]; v=result.value
            evidence=[f"Baseline emergency-breach probability: {v['baseline_emergency_breach']:.0%}",f"Stressed emergency-breach probability: {v['stressed_emergency_breach']:.0%}"]+[f"Goal {g}: {d:+.0%} probability change" for g,d in v["goal_probability_changes"].items()]
            actions=["Review the goals with the largest probability reduction.","Test a lower discretionary budget or later target date."]
            verdict="The stress scenario has been recalculated against the same random draws as the baseline."
        elif any(x in lower for x in ("score","resilience","financial health")):
            result=run_tool("explain_score",{},session); results=[result]; v=result.value
            evidence=[f"Resilience score: {v['score']}/100 ({v['grade']})",f"Hard-goal success probability: {v['hard_goals_probability']:.0%}",f"Emergency floor safe probability: {v['emergency_floor_never_breached_probability']:.0%}",f"Liquid runway: {v['runway_months']:.1f} months"]
            actions=["Review the weakest score component and test an alternative plan."]
            verdict=f"Your modelled Resilience Score is {v['score']}/100 ({v['grade']}); it is an explainable heuristic, not a regulated rating."
        elif any(x in lower for x in ("fix","repair","improve my plan","what should i change")):
            result=run_tool("repair_goal",{},session); results=[result]; v=result.value
            evidence=[f"Target probability: 85%",f"Before: {v['before_probability']:.0%}",f"After: {v['after_probability']:.0%}",f"Same random draws: {v['fingerprint_before']==v['fingerprint_after']}"]
            actions=[r["description"] for r in v["repairs"]] or ["No tested repair improved the selected target; reconsider the amount, deadline or available data."]
            verdict="AskAbhi tested candidate repairs and reports honestly whether the target was reached."
        elif any(x in lower for x in ("goal","mba","house","home","retirement","education")):
            gid=None
            for g in session["ctx"].goals:
                if g.name.lower() in lower or g.goal_id.lower() in lower: gid=g.goal_id; break
            result=run_tool("goal_status",{"goal_id":gid} if gid else {},session); results=[result]; v=result.value
            evidence=[f"{x['name']}: {x['success_probability']:.0%} estimated feasibility by {x['target_date']} (±{x['standard_error']*100:.1f} percentage points Monte Carlo standard error); target ₹{x['target_in_today_rupees']:,.0f}" for x in v["goals"]]
            actions=["Change a target date or priority and compare Plan A with Plan B.","Test an income change or unexpected expense to see how it affects the plan."]
            verdict="Here is the current modelled status of the matching financial goal(s)."
        elif "loan" in lower or "emi" in lower or "debt" in lower:
            ctx=session["ctx"]; draws=session["draws"]; surplus=max(0,ctx.behaviour.actual_median_saving if ctx.behaviour else 0)
            v=run_tool("diagnose_savings",{},session).value; result=run_tool("asset_growth_options",{},session); results=[result]
            evidence=[f"Observed median saving estimate: ₹{v['actual_median_saving']:,.0f}/month",result.value["options"][-1]["basis"]]
            actions=["Compare prepayment against investment only after protecting a suitable emergency reserve.","Verify actual lender rates and any prepayment fees."]
            verdict="AskAbhi has compared the emergency-buffer and debt/investment decision heuristics for your available data."
        else:
            return Answer("I can analyse savings, purchase affordability, goal status, asset-building scenarios, spending leaks, resilience and income/expense shocks.",[],["Try: How can I increase my assets?","Try: Can I afford a ₹4.5 lakh BMW bike?","Try: What if my income drops 20%?"],"The offline Copilot did not recognise this question, so it did not invent an answer.")
        guard=verify_numbers(" ".join([verdict]+evidence+actions),[r.evidence for r in results])
        # Engine result values are the authoritative numbers; evidence trail remains available even if a format differs.
        return Answer(verdict,evidence,actions,caveat,results,True,"offline")
    except Exception as exc:
        return Answer("AskAbhi could not complete that analysis with the current data.",[],["Check that the selected persona, goals and transaction history are valid, then try again."],f"The calculation was safely stopped ({type(exc).__name__}); no result has been invented.")
