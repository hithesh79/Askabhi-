"""Two-earner resilience comparison using a Gaussian-copula failure approximation."""
from __future__ import annotations
import numpy as np
from scipy.stats import norm
from core.models import PlanContext, Draws, ScenarioParams, HouseholdResult
from core.simulate import simulate

def household_resilience(ctx_a: PlanContext, ctx_b: PlanContext, rho: float, draws: Draws) -> HouseholdResult:
    rho=float(np.clip(rho,0,1)); ra=simulate(ctx_a,ScenarioParams(),draws); rb=simulate(ctx_b,ScenarioParams(),draws)
    pa=1-float(ra.extra.get("hard_goal_success_probability",0)); pb=1-float(rb.extra.get("hard_goal_success_probability",0))
    n=draws.n_sims
    independent=pa*pb
    u1=np.clip(draws.job_loss_u[:,0],1e-6,1-1e-6)
    z1=norm.ppf(u1)
    u2=np.clip(np.mod(np.abs(draws.market_z[:,0])*1000,1),1e-6,1-1e-6); z_ind=norm.ppf(u2)
    z2=rho*z1+np.sqrt(max(0,1-rho*rho))*z_ind
    joint=float(np.mean((z1<norm.ppf(np.clip(pa,1e-6,1-1e-6))) & (z2<norm.ppf(np.clip(pb,1e-6,1-1e-6)))))
    return HouseholdResult(rho,joint,independent,1-joint,"Gaussian-copula approximation illustrates correlated failure risk; it is not fitted without household history.")
