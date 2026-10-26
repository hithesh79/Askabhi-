"""Monte Carlo financial plan simulation using common random numbers.

Allocation policy: monthly surplus first tops the emergency pool to the target,
then funds goals priority 1 first and earlier deadline first, split in proportion
to remaining required monthly funding. Negative cash flow draws the liquid pool,
then lower-priority goal funds; any residual becomes high-interest debt. Goal
probability is an estimate under stated assumptions, not a promise.
"""
from __future__ import annotations
from datetime import date
import calendar
import numpy as np
import pandas as pd
from config import CFG
from core.models import PlanContext, ScenarioParams, Draws, SimResult, Projection
from core.rng import make_draws

def _add_months(d: date, m: int) -> date:
    idx=d.year*12+d.month-1+int(m); y,m0=divmod(idx,12); mo=m0+1
    return date(y,mo,min(d.day,calendar.monthrange(y,mo)[1]))

def _months_between(a: date,b: date) -> int:
    return (b.year-a.year)*12+(b.month-a.month)

def _goal_full_cost(g, due_month: int, params: ScenarioParams) -> float:
    """Inflate today's target and apply any on-road multiplier before funding choice."""
    inflation=g.inflation if g.inflation is not None else CFG.inflation_for(g.category)
    target=max(0.0,g.target_amount_today)*(1+max(0,inflation+params.inflation_add))**(max(0,due_month)/12)*(g.onroad_multiplier or 1.0)
    return float(max(0.0,target))

def _goal_target(g, due_month: int, params: ScenarioParams) -> float:
    """Return required goal cash; loan-funded goals require down payment plus illustrative fees."""
    full_cost=_goal_full_cost(g,due_month,params)
    if g.funding=="loan":
        return float(max(0.0,full_cost*max(0,g.down_payment_pct)+full_cost*CFG.goal_fee_fraction_for_loan))
    return full_cost

def _goals(ctx,params):
    goals=[]
    for g in list(ctx.goals)+list(getattr(params,"extra_goals",[]) or []):
        clone=type(g)(**{k:getattr(g,k) for k in g.__dataclass_fields__})
        ch=(params.goal_changes or {}).get(clone.goal_id,{})
        for k,v in ch.items():
            if hasattr(clone,k): setattr(clone,k,v)
        goals.append(clone)
    return goals

def _ctx_behaviour(ctx):
    bp=ctx.behaviour
    if bp is None:
        from core.models import BehaviourProfile
        bp=BehaviourProfile(as_of=ctx.profile.as_of)
        bp.category_monthly_mean={"Essential expenses":ctx.profile.essential_monthly_spend,"Discretionary expenses":max(0,ctx.profile.monthly_income_net*.2)}
        bp.category_nature={"Essential expenses":"essential","Discretionary expenses":"discretionary"}
        bp.safe_income=ctx.profile.monthly_income_net; bp.confidence="Low"
    return bp

def _asset_return(ctx):
    liquid=[a for a in ctx.assets if a.liquidity=="liquid" and a.asset_class not in ("equity","retirement")]
    val=sum(max(0,a.value) for a in liquid)
    if not val: return CFG.default_liquid_asset_return_annual,.05
    ret=sum(max(0,a.value)*a.exp_return for a in liquid)/val
    vol=sum(max(0,a.value)*a.vol for a in liquid)/val
    return float(ret),max(.005,float(vol))

def simulate(ctx: PlanContext, params: ScenarioParams | None, draws: Draws) -> SimResult:
    """Simulate all paths; vectorised over simulations and looped over months."""
    params=params or ScenarioParams(); profile=ctx.profile; bp=_ctx_behaviour(ctx); goals=_goals(ctx,params)
    latest=max([_months_between(profile.as_of,g.target_date) for g in goals]+[0])
    horizon=max(1,min(CFG.max_horizon_months,max(latest,0)+CFG.post_goal_buffer_months))
    n=int(draws.n_sims)
    if draws.n_months < horizon:
        # Deterministically extend with a derived seed so edge cases cannot index past the draw arrays.
        extension=make_draws(draws.seed+991,horizon-draws.n_months,horizon) if False else None
        all_draws=make_draws(draws.seed,n,horizon)
    else:
        all_draws=draws
    arrays={k:getattr(all_draws,k)[:,:horizon] for k in ("market_z","income_noise","expense_noise","job_loss_u","unplanned_u","unplanned_size_z")}
    locked_assets=[a for a in ctx.assets if a.liquidity=="locked"]
    penalty_assets=[a for a in ctx.assets if a.liquidity=="penalty"]
    illiquid_assets=[a for a in ctx.assets if a.liquidity=="illiquid"]
    locked0=sum(max(0,a.value) for a in locked_assets)
    penalty0=sum(max(0,a.value) for a in penalty_assets)
    illiquid0=sum(max(0,a.value) for a in illiquid_assets)
    debt0=sum(max(0,l.outstanding) for l in ctx.liabilities)
    emi_by_month=np.zeros(horizon)
    for t in range(horizon): emi_by_month[t]=sum(l.emi for l in ctx.liabilities if l.months_left>t)
    existing_liability_balances={id(l):np.full(n,max(0.0,float(l.outstanding)),dtype=float) for l in ctx.liabilities}
    goal_loan_balances={g.goal_id:np.zeros(n,dtype=float) for g in goals}
    goal_loan_emis={g.goal_id:np.zeros(n,dtype=float) for g in goals}
    running_cost_active=np.zeros(n,dtype=float)
    goal_funds=np.zeros((n,len(goals)),dtype=float)
    funding_at_target=np.zeros((n,len(goals)),dtype=float)
    success=np.zeros((n,len(goals)),dtype=bool)
    evaluated=np.zeros(len(goals),dtype=bool)
    times={g.goal_id:np.full(n,np.inf) for g in goals}
    goal_idx={g.goal_id:i for i,g in enumerate(goals)}
    goal_months=np.array([max(0,min(horizon-1,_months_between(profile.as_of,g.target_date))) for g in goals],dtype=int)
    # Past-due goals are evaluated at month zero and remain flagged through their probability.
    debt=np.full(n,0.0); emergency_target=max(0,profile.emergency_months*max(0,profile.essential_monthly_spend))
    emergency_breached=np.zeros(n,dtype=bool); shortfall_months=np.zeros(n,dtype=float)
    income_hist=np.asarray([v for v in (bp.monthly_income_history or profile.income_history) if v>0],dtype=float)
    txcats=bp.transaction_categories
    sip_monthly=0.0
    if txcats is not None and not txcats.empty and "kind" in txcats.columns:
        sip_monthly=float(pd.to_numeric(txcats.loc[txcats["kind"].eq("investment"),"amount"],errors="coerce").fillna(0).sum()/max(1,bp.months_of_data))
    prior_income=[]
    negative_streak=np.zeros(n,dtype=int)
    sip_pause=np.zeros(n,dtype=int)
    invested_pool0=sum(max(0,a.value) for a in ctx.assets if a.liquidity=="liquid" and a.asset_class in ("equity","retirement"))
    pool0=sum(max(0,a.value) for a in ctx.assets if a.liquidity=="liquid" and a.asset_class not in ("equity","retirement"))
    pool=np.full(n,pool0,dtype=float)
    investment_pool=np.full(n,invested_pool0,dtype=float)
    locked_pools=[np.full(n,max(0.0,float(a.value)),dtype=float) for a in locked_assets]
    penalty_pool=np.full(n,penalty0,dtype=float)
    illiquid_pool=np.full(n,illiquid0,dtype=float)
    if params.allow_penalty_withdrawal and penalty_assets:
        penalty_net=sum(max(0,a.value)*(1-min(1.0,max(0.0,a.penalty_pct))) for a in penalty_assets)
        pool += penalty_net
        penalty_pool[:] = 0.0
    cat_values=np.array(list(bp.category_monthly_mean.values()),dtype=float)
    cat_names=list(bp.category_monthly_mean.keys())
    category_natures=bp.category_nature
    if cat_values.size==0: cat_values=np.array([max(0,profile.essential_monthly_spend)]); cat_names=["Essential"]
    if bp.confidence=="Low": expense_sigma=.25*CFG.low_confidence_noise_multiplier
    else: expense_sigma=.18
    mean_return,return_vol=_asset_return(ctx); monthly_ret=(1+mean_return)**(1/12)-1; monthly_vol=return_vol/np.sqrt(12)
    equity_mean,equity_vol=CFG.asset_return_volatility("equity")
    equity_monthly_ret=(1+equity_mean)**(1/12)-1; equity_monthly_vol=equity_vol/np.sqrt(12)
    penalty_monthly={id(a):((1+max(-.99,a.exp_return))**(1/12)-1,max(.0,a.vol)/np.sqrt(12)) for a in penalty_assets}
    illiquid_monthly={id(a):((1+max(-.99,a.exp_return))**(1/12)-1,max(.0,a.vol)/np.sqrt(12)) for a in illiquid_assets}
    locked_monthly={id(a):((1+max(-.99,a.exp_return))**(1/12)-1,max(.0,a.vol)/np.sqrt(12)) for a in locked_assets}
    total_liab=np.full(n,debt0,dtype=float)
    net_worth_paths=np.zeros((n,horizon)); liquid_paths=np.zeros((n,horizon)); goal_remaining_months=np.maximum(1,goal_months+1)
    active_job=np.zeros(n,dtype=int); job_start=max(0,int(params.job_loss_start)); job_end=job_start+max(0,int(params.job_loss_months))
    for t in range(horizon):
        # Employment hazard; one triggered job loss lasts for a configurable random duration.
        new_loss=(arrays["job_loss_u"][:,t] < profile.job_loss_prob_annual/12.0) & (active_job<=0)
        durations=CFG.job_loss_duration_min_months+(np.abs(arrays["unplanned_size_z"][:,t])*100).astype(int)%(CFG.job_loss_duration_max_months-CFG.job_loss_duration_min_months+1)
        active_job=np.where(new_loss,durations,np.maximum(0,active_job-1))
        growth=(1+profile.income_growth)**(t/12)
        if profile.income_type=="irregular" and income_hist.size:
            idx=(np.abs(arrays["income_noise"][:,t])*1000).astype(int)%income_hist.size
            income=income_hist[idx]*growth
        else:
            sigma=.06 if profile.income_type=="salaried" else .25
            income=max(0,profile.monthly_income_net)*growth*np.exp(sigma*arrays["income_noise"][:,t]-.5*sigma*sigma)
        income=np.where(active_job>0,income*CFG.income_fraction_during_job_loss,income)
        if params.job_loss_months>0 and job_start<=t<job_end: income[:]=income*CFG.income_fraction_during_job_loss
        if params.income_cut_months>0 and params.income_cut_start<=t<params.income_cut_start+params.income_cut_months:
            income*=max(0,1-params.income_cut_pct)
        income*=max(0,1+params.income_increase_pct)
        income += max(0.0, params.extra_monthly_saving)
        # Existing liabilities amortise on their scheduled EMI. The principal component
        # reduces the recorded liability; interest is already contained in each EMI.
        for liability in ctx.liabilities:
            if t < liability.months_left:
                balance=existing_liability_balances[id(liability)]
                interest=balance*max(0.0,liability.annual_rate)/12.0
                principal_paid=np.minimum(balance,np.maximum(0.0,liability.emi-interest))
                existing_liability_balances[id(liability)]=np.maximum(0.0,balance-principal_paid)
        # Loan-funded goals purchased in an earlier month now pay their EMI and amortise.
        for g in goals:
            loan_balance=goal_loan_balances[g.goal_id]
            if np.any(loan_balance>0):
                interest=loan_balance*max(0.0,g.loan_rate)/12.0
                principal_paid=np.minimum(loan_balance,np.maximum(0.0,goal_loan_emis[g.goal_id]-interest))
                goal_loan_balances[g.goal_id]=np.maximum(0.0,loan_balance-principal_paid)
        # Category based expense baseline with category-specific inflation.
        spend=0.0
        season=bp.seasonal_index.get(_add_months(profile.as_of,t).month,1.0)
        trend=np.exp(expense_sigma*arrays["expense_noise"][:,t]-.5*expense_sigma**2)
        base_expense=0.0
        discretionary_expense=0.0
        for val,cat in zip(cat_values,cat_names):
            nature=category_natures.get(cat,"discretionary")
            infl=CFG.essential_inflation_annual if nature in ("essential","fixed") else CFG.discretionary_inflation_annual
            annual_infl=max(0,infl+params.inflation_add)
            amount=max(0,val)*(1+annual_infl)**(t/12)*season
            if nature=="discretionary": amount*=max(0,1-params.expense_cut_pct)
            base_expense+=amount
            if nature=="discretionary": discretionary_expense+=amount
        expenses=base_expense*trend + running_cost_active
        event_prob=min(.95,max(0,bp.unplanned_lambda_annual/12.0))
        occurs=arrays["unplanned_u"][:,t] < event_prob
        shock=np.exp(np.clip(bp.unplanned_lognormal_mu+bp.unplanned_lognormal_sigma*arrays["unplanned_size_z"][:,t],0,18))
        expenses+=occurs*shock
        # Adaptive guardrails are explicit templates, applied before allocation.
        for rule in params.guardrails:
            rtype=rule.get("type", "")
            if rtype=="income_drop_cut_discretionary" and prior_income:
                trail=np.mean(np.stack(prior_income[-3:]),axis=0)
                drop=float(rule.get("drop_pct",.20)); cut=float(rule.get("cut_pct",.15))
                expenses-=np.where(income < trail*(1-drop), discretionary_expense*trend*cut, 0.0)
            elif rtype=="emergency_pause_goal":
                # handled by filtering goal allocation below; threshold is in essential-spend months
                pass
        if params.extra_monthly_expense>0 and t>=params.extra_monthly_start: expenses+=params.extra_monthly_expense
        for month_idx,amount in params.one_off_expenses:
            if int(month_idx)==t: expenses+=max(0,float(amount))
        existing_emi=emi_by_month[t]
        active_goal_emi=sum(goal_loan_emis.values(),start=np.zeros(n,dtype=float))
        em=existing_emi+active_goal_emi
        # Grow accessible, restricted and illiquid assets separately. Locked assets become
        # cash only on/after their recorded unlock date; penalty and illiquid assets never
        # silently become available to meet goals.
        market_z=arrays["market_z"][:,t]
        ret=np.clip(monthly_ret+monthly_vol*market_z,CFG.monthly_return_clip_min,CFG.monthly_return_clip_max)
        pool=np.maximum(0,pool*(1+ret))
        equity_ret=np.clip(equity_monthly_ret+equity_monthly_vol*market_z,CFG.monthly_return_clip_min,CFG.monthly_return_clip_max)
        current_date=_add_months(profile.as_of,t)
        for idx,asset in enumerate(locked_assets):
            rmean,rvol=locked_monthly[id(asset)]
            locked_pools[idx]=np.maximum(0,locked_pools[idx]*(1+np.clip(rmean+rvol*market_z,CFG.monthly_return_clip_min,CFG.monthly_return_clip_max)))
            if asset.unlock_date is not None and asset.unlock_date<=current_date:
                pool+=locked_pools[idx]
                locked_pools[idx][:]=0.0
        for asset in penalty_assets:
            rmean,rvol=penalty_monthly[id(asset)]
            penalty_pool=np.maximum(0,penalty_pool*(1+np.clip(rmean+rvol*market_z,CFG.monthly_return_clip_min,CFG.monthly_return_clip_max)))
        for asset in illiquid_assets:
            rmean,rvol=illiquid_monthly[id(asset)]
            illiquid_pool=np.maximum(0,illiquid_pool*(1+np.clip(rmean+rvol*market_z,CFG.monthly_return_clip_min,CFG.monthly_return_clip_max)))
        # Negative-surplus guardrail can pause a modelled recurring SIP and keep that cash available.
        negative_streak=np.where(income-expenses-em<0,negative_streak+1,0)
        for rule in params.guardrails:
            if rule.get("type")=="negative_surplus_pause_sip":
                trigger=int(rule.get("trigger_months",2)); pause=int(rule.get("months",3))
                sip_pause=np.where(negative_streak>=trigger,np.maximum(sip_pause,pause),np.maximum(0,sip_pause-1))
        sip_contribution=np.where(sip_pause>0,0.0,sip_monthly)
        investment_pool=np.maximum(0,investment_pool*(1+equity_ret)+sip_contribution)
        if params.market_shock_pct>0 and t==params.market_shock_month:
            investment_pool*=max(0,1-params.market_shock_pct)
        net=income-expenses-em-debt*CFG.high_interest_debt_annual_rate/12-sip_contribution
        prior_income.append(income.copy())
        surplus=np.maximum(0,net)
        deficit=np.maximum(0,-net)
        # Protect the emergency reserve first, then allocate any cash above the floor
        # to the goal system. Sweeping excess on every month also makes newly unlocked
        # assets available to planned goals without counting the same rupee twice.
        topup=np.minimum(surplus,np.maximum(0,emergency_target-pool))
        pool+=topup; surplus-=topup
        initial_excess=np.maximum(0,pool-emergency_target)
        pool-=initial_excess
        surplus+=initial_excess
        order=sorted(range(len(goals)),key=lambda j:(goals[j].priority,goals[j].target_date))
        pause_thresholds={str(rule.get("goal_id","")):max(0,float(rule.get("months",3)))*max(0,profile.essential_monthly_spend) for rule in params.guardrails if rule.get("type")=="emergency_pause_goal"}
        active=[j for j in order if not evaluated[j] and goal_months[j]>=t and goals[j].category!="emergency"]
        # Lower-priority goals receive contributions only after higher-priority goals are fully funded.
        for priority in sorted(set(goals[j].priority for j in active)):
            tier=[j for j in active if goals[j].priority==priority]
            if not tier: continue
            needs=[]; caps=[]
            for j in tier:
                target_cost=_goal_target(goals[j],int(goal_months[j]),params)
                remaining=max(1,int(goal_months[j])-t+1)
                gap=np.maximum(0,target_cost-goal_funds[:,j])
                needs.append(gap/remaining); caps.append(gap)
            need_matrix=np.stack(needs,axis=1)
            sums=need_matrix.sum(axis=1,keepdims=True)
            weights=np.divide(need_matrix,sums,out=np.zeros_like(need_matrix),where=sums>0)
            allocations=np.minimum(surplus[:,None]*weights,np.stack(caps,axis=1))
            for ix,j in enumerate(tier):
                if goals[j].goal_id in pause_thresholds:
                    allocations[:,ix]=np.where(pool < pause_thresholds[goals[j].goal_id],0.0,allocations[:,ix])
            goal_funds[:,tier]+=allocations
            surplus-=allocations.sum(axis=1)
        pool+=surplus
        # In a deficit, draw cash then reduce the lowest-priority goal funds before carrying high-interest debt.
        cash_draw=np.minimum(pool,deficit); pool-=cash_draw; deficit-=cash_draw
        for j in sorted(range(len(goals)),key=lambda j:(goals[j].priority,goals[j].target_date),reverse=True):
            draw=np.minimum(goal_funds[:,j],deficit); goal_funds[:,j]-=draw; deficit-=draw
        debt+=deficit
        shortfall_months+=(deficit>0)
        emergency_breached |= pool < emergency_target
        # Evaluate goals at their target month; successful funds are spent to avoid double use.
        for j,g in enumerate(goals):
            if not evaluated[j] and goal_months[j]<=t:
                required=_goal_target(g,int(goal_months[j]),params)
                if g.category=="emergency":
                    funding_at_target[:,j]=pool
                    passed=pool>=required*max(0,g.min_acceptable_pct)
                else:
                    funded=goal_funds[:,j]
                    funding_at_target[:,j]=funded
                    passed=(funded>=required*max(0,g.min_acceptable_pct)) & (pool>=emergency_target)
                success[:,j]=passed; times[g.goal_id][passed & (~np.isfinite(times[g.goal_id]))]=t
                if g.category!="emergency":
                    goal_funds[:,j]=np.where(passed,np.maximum(0,goal_funds[:,j]-required),goal_funds[:,j])
                    # A confirmed purchase creates a running cost from the following month.
                    running_cost_active += passed.astype(float)*max(0.0,g.running_cost_monthly)
                    if g.funding=="loan":
                        principal=max(0.0,_goal_full_cost(g,int(goal_months[j]),params)*(1-max(0.0,g.down_payment_pct)))
                        if principal>0 and g.loan_tenure_months>0:
                            from core.networth import emi as calc_emi
                            monthly_payment=calc_emi(principal,max(0.0,g.loan_rate),g.loan_tenure_months)
                            goal_loan_balances[g.goal_id] += passed.astype(float)*principal
                            goal_loan_emis[g.goal_id] += passed.astype(float)*monthly_payment
                evaluated[j]=True
        # Earliest feasible month is the first month the full inflated target is funded.
        for j,g in enumerate(goals):
            if not evaluated[j] and g.category!="emergency" and not np.all(np.isfinite(times[g.goal_id])):
                required_early=_goal_target(g,int(goal_months[j]),params)
                newly=(goal_funds[:,j]>=required_early*max(0,g.min_acceptable_pct)) & (pool>=emergency_target) & (~np.isfinite(times[g.goal_id]))
                times[g.goal_id][newly]=t
        total_goal_funds=goal_funds.sum(axis=1)
        existing_liability_total=sum(existing_liability_balances.values(),start=np.zeros(n,dtype=float))
        goal_loan_total=sum(goal_loan_balances.values(),start=np.zeros(n,dtype=float))
        locked_total=sum(locked_pools, start=np.zeros(n,dtype=float))
        net_worth_paths[:,t]=pool+investment_pool+total_goal_funds+locked_total+penalty_pool+illiquid_pool-existing_liability_total-goal_loan_total-debt
        liquid_paths[:,t]=pool
    # A goal purchase is only successful if the emergency floor stays intact for
    # the following three months. This check is applied after all monthly paths exist.
    for j,g in enumerate(goals):
        if g.category == "emergency":
            continue
        due=int(goal_months[j]); last=min(horizon-1,due+CFG.goal_purchase_post_floor_check_months)
        protected=np.min(liquid_paths[:,due:last+1],axis=1)>=emergency_target
        success[:,j] &= protected
        times[g.goal_id][~success[:,j]]=np.inf
    # Success matrix has one column per goal, all probabilities are bounded.
    probs={g.goal_id:float(success[:,j].mean()) for j,g in enumerate(goals)}
    ses={g.goal_id:float(np.sqrt(probs[g.goal_id]*(1-probs[g.goal_id])/n)) for g in goals}
    shortfalls={}
    for j,g in enumerate(goals):
        required=_goal_target(g,int(goal_months[j]),params)
        failed=~success[:,j]
        if g.category=="emergency":
            shortfalls[g.goal_id]=float(np.median(np.maximum(0,required-np.minimum(funding_at_target[failed,j],required)))) if failed.any() else 0.0
        else:
            shortfalls[g.goal_id]=float(np.median(np.maximum(0,required-np.maximum(0,funding_at_target[failed,j])))) if failed.any() else 0.0
    months=[_add_months(profile.as_of,t) for t in range(horizon)]
    hard_idxs=[j for j,g in enumerate(goals) if g.hard]
    hard_success=success[:,hard_idxs].all(axis=1) if hard_idxs else np.ones(n,dtype=bool)
    extra={"hard_goal_success_probability":float(hard_success.mean()),"shortfall_paths":shortfall_months,"locked_assets_start":locked0,"penalty_assets_start":penalty0,"illiquid_assets_start":illiquid0,"initial_liquid":pool0,"horizon_months":horizon,"goal_target_months":{g.goal_id:int(goal_months[j]) for j,g in enumerate(goals)},"goal_funds_final":goal_funds.copy(),"funding_at_target":funding_at_target.copy(),"existing_liabilities_final":sum(existing_liability_balances.values(),start=np.zeros(n,dtype=float)),"goal_loan_balances_final":sum(goal_loan_balances.values(),start=np.zeros(n,dtype=float))}
    return SimResult(months,*[np.percentile(net_worth_paths,p,axis=0) for p in (10,25,50,75,90)],np.percentile(liquid_paths,10,axis=0),np.percentile(liquid_paths,50,axis=0),np.percentile(liquid_paths,90,axis=0),probs,ses,shortfalls,float(emergency_breached.mean()),float(shortfall_months.mean()),success,draws.fingerprint(),times,{g.goal_id:g.name for g in goals},extra)

def deterministic_projection(ctx: PlanContext, params: ScenarioParams | None) -> Projection:
    """Expected-value projection with no random shocks, useful for quick stress search."""
    from core.rng import make_draws
    params=params or ScenarioParams()
    horizon=min(CFG.max_horizon_months,max([_months_between(ctx.profile.as_of,g.target_date) for g in list(ctx.goals)+list(params.extra_goals)]+[0])+CFG.post_goal_buffer_months)
    d=make_draws(0,1,max(1,horizon))
    # Reduce stochastic noise by replacing the draws with zeros and event uniforms above event probability.
    d.market_z[:]=0; d.income_noise[:]=0; d.expense_noise[:]=0; d.job_loss_u[:]=1; d.unplanned_u[:]=1; d.unplanned_size_z[:]=0
    res=simulate(ctx,params,d)
    return Projection(res.months,res.liquid_p50.copy(),res.net_worth_p50.copy(),{},res.emergency_breach_probability>0,{"goal_probabilities":res.goal_probabilities,"success_matrix":res.success_matrix,"fingerprint":res.draws_fingerprint})
