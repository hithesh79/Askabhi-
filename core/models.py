"""Typed domain models used by all AskAbhi financial engines."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Any
import numpy as np
import pandas as pd

@dataclass
class Asset:
    name: str
    kind: str
    value: float
    asset_class: str = "cash"
    liquidity: str = "liquid"
    unlock_date: date | None = None
    penalty_pct: float = 0.0
    exp_return: float = 0.03
    vol: float = 0.01

@dataclass
class Liability:
    name: str
    kind: str
    outstanding: float
    annual_rate: float = 0.0
    emi: float = 0.0
    months_left: int = 0

@dataclass
class Goal:
    goal_id: str
    name: str
    category: str
    target_amount_today: float
    target_date: date
    priority: int = 2
    hard: bool = True
    min_acceptable_pct: float = 1.0
    inflation: float | None = None
    funding: str = "cash"
    down_payment_pct: float = 0.2
    loan_rate: float = 0.12
    loan_tenure_months: int = 36
    running_cost_monthly: float = 0.0
    onroad_multiplier: float | None = None
    earmarked_assets: list[str] = field(default_factory=list)

@dataclass
class Profile:
    as_of: date
    monthly_income_net: float
    income_type: str = "salaried"
    income_growth: float = 0.05
    job_loss_prob_annual: float = 0.04
    stated_monthly_budget: float | None = None
    stated_monthly_saving: float | None = None
    emergency_months: int = 6
    essential_monthly_spend: float = 25000.0
    income_history: list[float] = field(default_factory=list)

@dataclass
class BehaviourProfile:
    as_of: date
    category_monthly_mean: dict[str, float] = field(default_factory=dict)
    category_monthly_std: dict[str, float] = field(default_factory=dict)
    category_nature: dict[str, str] = field(default_factory=dict)
    monthly_spend_history: list[float] = field(default_factory=list)
    monthly_income_history: list[float] = field(default_factory=list)
    monthly_residuals: list[float] = field(default_factory=list)
    seasonal_index: dict[int, float] = field(default_factory=dict)
    recurring_merchants: list[str] = field(default_factory=list)
    subscription_merchants: list[str] = field(default_factory=list)
    planned_monthly: float = 0.0
    unplanned_monthly: float = 0.0
    unplanned_lambda_annual: float = 2.0
    unplanned_lognormal_mu: float = 9.6
    unplanned_lognormal_sigma: float = 0.75
    weekend_weekday_ratio: float = 1.0
    payday_burst_share: float = 0.0
    month_end_squeeze: bool = False
    lifestyle_creep_slope: float = 0.0
    lifestyle_creep_pvalue: float = 1.0
    income_cv: float = 0.0
    lean_months: int = 0
    safe_income: float = 0.0
    income_label: str = "Stable"
    behaviour_gap: str = "No stated savings target supplied."
    actual_median_saving: float = 0.0
    stated_saving: float | None = None
    irregular_expense_reserve: float = 0.0
    months_of_data: int = 0
    confidence: str = "Low"
    planned_unplanned_rows: dict[str, float] = field(default_factory=dict)
    transaction_categories: pd.DataFrame = field(default_factory=pd.DataFrame)

@dataclass
class PlanContext:
    profile: Profile
    assets: list[Asset]
    liabilities: list[Liability]
    goals: list[Goal]
    behaviour: BehaviourProfile | None = None
    config: Any = None
    transactions: pd.DataFrame = field(default_factory=pd.DataFrame)
    persona_name: str = "Custom"

@dataclass
class ScenarioParams:
    income_cut_pct: float = 0.0
    income_cut_start: int = 0
    income_cut_months: int = 0
    job_loss_months: int = 0
    job_loss_start: int = 0
    one_off_expenses: list[tuple[int, float]] = field(default_factory=list)
    market_shock_pct: float = 0.0
    market_shock_month: int = 0
    extra_monthly_expense: float = 0.0
    extra_monthly_start: int = 0
    inflation_add: float = 0.0
    goal_changes: dict[str, dict[str, Any]] = field(default_factory=dict)
    extra_goals: list[Goal] = field(default_factory=list)
    interventions: list[dict[str, Any]] = field(default_factory=list)
    guardrails: list[dict[str, Any]] = field(default_factory=list)
    income_increase_pct: float = 0.0
    expense_cut_pct: float = 0.0
    extra_monthly_saving: float = 0.0
    allow_penalty_withdrawal: bool = False

@dataclass
class Draws:
    market_z: np.ndarray
    income_noise: np.ndarray
    expense_noise: np.ndarray
    job_loss_u: np.ndarray
    unplanned_u: np.ndarray
    unplanned_size_z: np.ndarray
    seed: int
    n_sims: int
    n_months: int
    def fingerprint(self) -> str:
        import hashlib
        h = hashlib.sha1()
        for arr in (self.market_z, self.income_noise, self.expense_noise, self.job_loss_u, self.unplanned_u, self.unplanned_size_z):
            h.update(np.ascontiguousarray(arr).view(np.uint8))
        return h.hexdigest()[:8]
    def head(self, n: int) -> "Draws":
        n = max(1, min(int(n), self.n_sims))
        return Draws(*(getattr(self, name)[:n].copy() for name in ("market_z","income_noise","expense_noise","job_loss_u","unplanned_u","unplanned_size_z")), self.seed, n, self.n_months)

@dataclass
class Projection:
    months: list[date]
    liquid: np.ndarray
    net_worth: np.ndarray
    goal_funds: dict[str, float] = field(default_factory=dict)
    emergency_breached: bool = False
    path: dict[str, Any] = field(default_factory=dict)

@dataclass
class SimResult:
    months: list[date]
    net_worth_p10: np.ndarray
    net_worth_p25: np.ndarray
    net_worth_p50: np.ndarray
    net_worth_p75: np.ndarray
    net_worth_p90: np.ndarray
    liquid_p10: np.ndarray
    liquid_p50: np.ndarray
    liquid_p90: np.ndarray
    goal_probabilities: dict[str, float]
    goal_standard_errors: dict[str, float]
    goal_median_shortfalls: dict[str, float]
    emergency_breach_probability: float
    expected_shortfall_months: float
    success_matrix: np.ndarray
    draws_fingerprint: str
    time_to_goal: dict[str, np.ndarray] = field(default_factory=dict)
    goal_names: dict[str, str] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)

@dataclass
class Issue:
    row: int | None
    field: str
    message: str
    action: str
    severity: str = "warning"

@dataclass
class PersonaBundle:
    name: str
    profile: Profile
    transactions: pd.DataFrame
    assets: list[Asset]
    liabilities: list[Liability]
    goals: list[Goal]
    description: str = "Synthetic demonstration persona; not real account data."
    behaviour: BehaviourProfile | None = None
    @property
    def context(self) -> PlanContext:
        from config import CFG
        return PlanContext(self.profile, self.assets, self.liabilities, self.goals, self.behaviour, CFG, self.transactions, self.name)

@dataclass
class NetWorth:
    total_assets: float
    total_liabilities: float
    net_worth: float
    by_liquidity: dict[str, float]
    by_asset_class: dict[str, float]
    by_liability_kind: dict[str, float]

@dataclass
class UsableFunds:
    available: float
    penalty_available: float
    emergency_floor: float
    excluded_illiquid: float
    components: dict[str, float]

@dataclass
class PurchaseSpec:
    name: str
    category: str
    ex_showroom_or_price: float
    target_date: date
    mode: str = "compare"
    down_payment_pct: float = 0.2
    loan_rate: float = 0.12
    tenure_months: int = 36
    running_cost_monthly: float = 3000.0
    onroad_multiplier: float | None = None

@dataclass
class AffordResult:
    verdict: str
    cash_probability: float
    loan_probability: float
    cash_se: float
    loan_se: float
    onroad_cost: float
    inflated_cost: float
    emi: float
    emi_share_income: float
    other_goal_impacts: list[dict[str, Any]]
    levers: list[dict[str, Any]]
    binding_constraint: dict[str, Any]
    draws_fingerprint: str

@dataclass
class Leak:
    category: str
    monthly_spend: float
    probability_before: float
    probability_after: float
    probability_change: float
    months_sooner: float
    creep_tax_monthly: float = 0.0
    description: str = ""

@dataclass
class BreakScenario:
    name: str
    sentence: str
    onset_month: int
    cost: float
    plausibility: str
    params: ScenarioParams
    target_probability: float

@dataclass
class RepairResult:
    repairs: list[dict[str, Any]]
    total_pain: float
    before_probability: float
    after_probability: float
    before_goal_probabilities: dict[str, float]
    after_goal_probabilities: dict[str, float]
    fingerprint_before: str
    fingerprint_after: str
    reached_target: bool
    alternatives: list[dict[str, Any]] = field(default_factory=list)

@dataclass
class ScoreCard:
    score: int
    grade: str
    hard_goals_probability: float
    emergency_floor_never_breached_probability: float
    runway_months: float
    components: dict[str, float]
    explanation: str

@dataclass
class ToolResult:
    value: Any
    evidence: dict[str, Any]

@dataclass
class Answer:
    verdict: str
    evidence: list[str]
    actions: list[str]
    caveat: str
    tool_results: list[ToolResult] = field(default_factory=list)
    numbers_verified: bool = True
    mode: str = "offline"

@dataclass
class GuardReport:
    valid: bool
    unverified_numbers: list[str]
    verified_numbers: list[str]

@dataclass
class PaydayPlan:
    salary: float
    obligations: float
    essentials: float
    emergency_topup: float
    goal_contributions: dict[str, float]
    safe_allowance: float
    days_left: int
    buckets: dict[str, float]

@dataclass
class SafeToSpend:
    allowance_remaining: float
    days_left: int
    safe_today: float
    pace: str
    overspend_goal_impact_days: dict[str, float] = field(default_factory=dict)

@dataclass
class RadarResult:
    dates: list[date]
    p10: np.ndarray
    p50: np.ndarray
    p90: np.ndarray
    breach_probability: np.ndarray
    first_danger_date: date | None
    pileups: list[dict[str, Any]]
    suggestions: list[str]

@dataclass
class Futures:
    months: list[date]
    stated_networth_p10: np.ndarray
    stated_networth_p50: np.ndarray
    stated_networth_p90: np.ndarray
    behaviour_networth_p10: np.ndarray
    behaviour_networth_p50: np.ndarray
    behaviour_networth_p90: np.ndarray
    repaired_networth_p10: np.ndarray
    repaired_networth_p50: np.ndarray
    repaired_networth_p90: np.ndarray
    goal_probabilities: dict[str, dict[str, float]]
    fingerprint: str

@dataclass
class Snapshot:
    month: date
    values: dict[str, dict[str, float]]
    goal_funded_share: dict[str, dict[str, float]]

@dataclass
class Regret:
    total: float
    components: dict[str, float]
    explanation: str

@dataclass
class ArbiterResult:
    emergency_topup: float
    loan_rate: float
    risk_adjusted_return: float
    break_even_rate: float
    preferred_option: str
    probability_invest_beats_prepay: float
    explanation: str

@dataclass
class HouseholdResult:
    rho: float
    joint_failure_probability: float
    independent_failure_probability: float
    joint_resilience: float
    notes: str

@dataclass
class BacktestResult:
    coverage: float
    nominal_coverage: float
    mean_band_width: float
    verdict: str
    origins: list[dict[str, Any]]
    warning: str

@dataclass
class Tool:
    name: str
    description: str
    function: Any
    schema: dict[str, Any] = field(default_factory=dict)
