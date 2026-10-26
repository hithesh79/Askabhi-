"""Compare emergency-buffer top-up, debt prepayment and risky investment."""
from __future__ import annotations
import numpy as np
from config import CFG
from core.models import PlanContext, Draws, ArbiterResult

def arbitrate(ctx: PlanContext, surplus: float, draws: Draws) -> ArbiterResult:
    floor=ctx.profile.emergency_months*ctx.profile.essential_monthly_spend
    liquid=sum(max(0,a.value) for a in ctx.assets if a.liquidity=="liquid" and a.asset_class not in ("equity","retirement"))
    emergency_topup=min(max(0,surplus),max(0,floor-liquid))
    residual=max(0,surplus-emergency_topup)
    loan=max(ctx.liabilities,key=lambda l:l.annual_rate,default=None)
    loan_rate=loan.annual_rate if loan else 0.0
    eq=[a for a in ctx.assets if a.asset_class=="equity"]
    exp_return=sum(a.value*a.exp_return for a in eq)/max(1,sum(a.value for a in eq)) if eq else .07
    risk_adjusted=exp_return-CFG.loan_invest_risk_haircut
    preferred="Top up emergency buffer" if emergency_topup>0 else ("Prepay loan" if loan and loan_rate>risk_adjusted else "Compare investment with debt repayment")
    rng=np.random.default_rng(draws.seed+918); n=draws.n_sims; months=max(1,min(draws.n_months,120))
    if loan is None or residual<=0: p=0.0
    else:
        market=rng.normal(exp_return/12,.20/np.sqrt(12),(n,months))
        investments=residual*np.prod(1+market,axis=1)
        debt_cost=residual*(1+max(0,loan_rate)/12)**months
        p=float(np.mean(investments>debt_cost))
    if loan and loan_rate>risk_adjusted: expl=f"The highest-rate tracked loan is {loan_rate:.1%}; the configured risk-adjusted expected return is {risk_adjusted:.1%}. Prepayment is favoured in the deterministic comparison after emergency funding."
    elif emergency_topup>0: expl="The configured emergency reserve is below target; the comparison directs surplus there first."
    else: expl="Expected return exceeds the highest tracked loan rate after the configured risk haircut, but investment outcomes remain uncertain."
    return ArbiterResult(emergency_topup,loan_rate,risk_adjusted,loan_rate,preferred,p,expl)
