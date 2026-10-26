"""AskAbhi 360 configuration.

All financial rates, thresholds, illustrative costs, multipliers, and model
assumptions are centralised here. They are indicative, verify before real use.
The dataclass is frozen so a running plan cannot silently mutate its assumptions.

No Indian tax treatment is encoded as fact. Tax-related fields are placeholders
and disabled by default. This product provides educational planning, not
investment advice or a regulated credit/risk rating.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any


@dataclass(frozen=True, slots=True)
class Config:
    """Immutable, centrally managed product and financial-model assumptions."""

    # ── Runtime, reproducibility and performance ─────────────────────────────
    default_seed: int = 42  # indicative, verify: reproducible demo seed
    default_n_sims: int = 2000  # indicative, verify: interactive simulation count
    full_n_sims_option: int = 5000  # indicative, verify: higher-precision UI option
    search_screen_sims: int = 600  # indicative, verify: fast screening count for optimisers
    max_horizon_months: int = 480  # indicative, verify: cap long-run simulation at 40 years
    post_goal_buffer_months: int = 12  # indicative, verify: simulation buffer after last goal
    target_simulation_seconds: float = 3.0  # indicative, verify: performance objective, not guarantee
    low_confidence_noise_multiplier: float = 1.50  # indicative, verify: widen noise with sparse history
    min_transactions_for_low_confidence: int = 3  # indicative, verify: below this history is low confidence
    medium_confidence_max_months: int = 6  # indicative, verify: medium confidence history upper bound

    # ── Demo personas and default profile ───────────────────────────────────
    arjun_age: int = 28  # indicative, verify: synthetic demo persona only
    arjun_monthly_net_income: float = 95000.0  # indicative, verify: synthetic demo income in INR
    arjun_income_growth_annual: float = 0.05  # indicative, verify: illustrative nominal income growth
    arjun_job_loss_probability_annual: float = 0.04  # indicative, verify: illustrative annual hazard
    arjun_emergency_months: int = 6  # indicative, verify: illustrative emergency reserve target
    meera_age: int = 31  # indicative, verify: synthetic demo persona only
    meera_monthly_mean_income: float = 85000.0  # indicative, verify: synthetic average, not a market estimate
    meera_income_coefficient_of_variation: float = 0.40  # indicative, verify: target variability for synthetic data
    demo_history_months: int = 12  # indicative, verify: synthetic transaction-history length
    demo_starting_cash: float = 100000.0  # indicative, verify: illustrative balance in INR
    demo_starting_liquid_fund: float = 140000.0  # indicative, verify: illustrative asset value in INR
    demo_starting_equity: float = 220000.0  # indicative, verify: illustrative investment value in INR
    demo_starting_epf: float = 350000.0  # indicative, verify: illustrative locked retirement value in INR
    demo_starting_ppf: float = 120000.0  # indicative, verify: illustrative locked asset value in INR
    demo_starting_fd: float = 100000.0  # indicative, verify: illustrative penalty asset value in INR
    demo_starting_gold: float = 90000.0  # indicative, verify: illustrative illiquid asset value in INR
    demo_personal_loan_outstanding: float = 180000.0  # indicative, verify: illustrative liability in INR
    demo_personal_loan_annual_rate: float = 0.12  # indicative, verify: illustrative loan rate
    demo_personal_loan_emi: float = 8500.0  # indicative, verify: illustrative monthly EMI in INR
    demo_personal_loan_months_left: int = 24  # indicative, verify: illustrative remaining tenure
    demo_credit_card_outstanding: float = 18000.0  # indicative, verify: illustrative card balance in INR
    demo_bike_goal_amount: float = 450000.0  # indicative, verify: illustrative ex-showroom goal amount in INR
    demo_bike_goal_months: int = 12  # indicative, verify: target horizon for demo bike goal
    demo_mba_goal_amount_today: float = 2500000.0  # indicative, verify: illustrative goal amount in today's INR
    demo_mba_goal_months: int = 48  # indicative, verify: target horizon for demo MBA goal
    demo_home_down_payment_today: float = 2000000.0  # indicative, verify: illustrative goal amount in today's INR
    demo_home_goal_months: int = 72  # indicative, verify: target horizon for home goal
    demo_retirement_age: int = 60  # indicative, verify: illustrative retirement age

    # ── Financial inflation assumptions by goal category ─────────────────────
    # Tuple-based mappings retain immutability; rates are annual decimal rates.
    inflation_by_category: tuple[tuple[str, float], ...] = (
        ("vehicle", 0.06),  # indicative, verify: annual vehicle-cost inflation
        ("education", 0.08),  # indicative, verify: annual education-cost inflation
        ("home", 0.06),  # indicative, verify: annual home-cost inflation
        ("retirement", 0.06),  # indicative, verify: annual long-term cost inflation
        ("emergency", 0.05),  # indicative, verify: annual emergency-budget inflation
        ("wedding", 0.06),  # indicative, verify: annual wedding-cost inflation
        ("medical", 0.08),  # indicative, verify: annual medical-cost inflation
        ("travel", 0.05),  # indicative, verify: annual travel-cost inflation
        ("other", 0.05),  # indicative, verify: generic annual goal inflation
    )
    essential_inflation_annual: float = 0.06  # indicative, verify: annual essential-expense inflation
    discretionary_inflation_annual: float = 0.07  # indicative, verify: annual discretionary-expense inflation
    general_inflation_annual: float = 0.05  # indicative, verify: fallback annual inflation assumption

    # ── Asset-class return and volatility assumptions ────────────────────────
    # Expected returns and volatilities are annual decimal rates, not promises.
    asset_return_volatility_by_class: tuple[tuple[str, float, float], ...] = (
        ("cash", 0.03, 0.01),  # indicative, verify: nominal cash return and annual volatility
        ("debt", 0.06, 0.06),  # indicative, verify: illustrative debt-asset return and volatility
        ("equity", 0.10, 0.20),  # indicative, verify: illustrative equity return and volatility
        ("gold", 0.06, 0.15),  # indicative, verify: illustrative gold return and volatility
        ("property", 0.07, 0.10),  # indicative, verify: illustrative property return and volatility
        ("retirement", 0.08, 0.12),  # indicative, verify: illustrative retirement-asset return and volatility
    )
    default_liquid_asset_return_annual: float = 0.03  # indicative, verify: fallback liquid-pool return
    shared_equity_market_factor_weight: float = 0.75  # indicative, verify: shared factor strength across equity assets
    monthly_return_clip_min: float = -0.80  # indicative, verify: numerical guardrail on simulated monthly return
    monthly_return_clip_max: float = 1.00  # indicative, verify: numerical guardrail on simulated monthly return

    # ── Income and employment uncertainty ───────────────────────────────────
    salaried_income_noise_sigma: float = 0.06  # indicative, verify: lognormal income variability
    irregular_income_bootstrap_enabled: bool = True  # indicative, verify: bootstrap observed income history
    irregular_income_safe_percentile: float = 20.0  # indicative, verify: planning income percentile (P20)
    lean_month_fraction_of_median: float = 0.70  # indicative, verify: lean month threshold
    income_growth_default: float = 0.05  # indicative, verify: fallback annual income growth
    job_loss_probability_annual_default: float = 0.04  # indicative, verify: fallback annual job-loss probability
    job_loss_duration_min_months: int = 3  # indicative, verify: minimum simulated job-loss duration
    job_loss_duration_max_months: int = 9  # indicative, verify: maximum simulated job-loss duration
    income_fraction_during_job_loss: float = 0.00  # indicative, verify: assumed replacement income during job loss
    job_loss_hazard_divisor: float = 12.0  # indicative, verify: convert annual probability to monthly hazard approximation

    # ── Expense and behaviour estimation ────────────────────────────────────
    recurring_interval_min_days: int = 25  # indicative, verify: lower monthly-recurring interval bound
    recurring_interval_max_days: int = 35  # indicative, verify: upper monthly-recurring interval bound
    recurring_amount_tolerance: float = 0.15  # indicative, verify: relative amount tolerance for recurrence
    recurring_min_occurrences: int = 3  # indicative, verify: minimum observations for recurring detection
    annual_item_min_history_months: int = 12  # indicative, verify: history needed to identify annual items
    weekend_spend_ratio_warning: float = 1.20  # indicative, verify: weekend/weekday ratio worth surfacing
    payday_burst_days: int = 5  # indicative, verify: days after salary credit used for burst analysis
    month_end_squeeze_days: int = 5  # indicative, verify: final days of month for squeeze indicator
    unplanned_category_sigma_multiple: float = 2.0  # indicative, verify: category mean-plus-standard-deviation rule
    unplanned_fraction_of_monthly_income: float = 0.10  # indicative, verify: alternative one-off threshold
    unplanned_poisson_prior_events_per_year: float = 2.0  # indicative, verify: prior annual event frequency
    unplanned_lognormal_prior_median: float = 15000.0  # indicative, verify: prior event size in INR
    unplanned_lognormal_prior_sigma: float = 0.75  # indicative, verify: log-size dispersion prior
    unplanned_shrinkage_k: float = 3.0  # indicative, verify: prior shrinkage constant n/(n+K)
    seasonality_shrinkage_k: float = 2.0  # indicative, verify: seasonality shrinkage constant
    lifestyle_creep_significance_p: float = 0.05  # indicative, verify: threshold used for statistical-language interpretation
    stated_savings_gap_warning_fraction: float = 0.20  # indicative, verify: stated/actual savings gap worth highlighting
    irregular_income_cv_variable: float = 0.20  # indicative, verify: CV above which income is not labelled stable
    irregular_income_cv_highly_irregular: float = 0.40  # indicative, verify: CV threshold for highly irregular label
    irregular_lean_month_warning_count: int = 3  # indicative, verify: lean months that trigger a warning
    annual_lumpy_expense_divisor: float = 12.0  # indicative, verify: convert annual lumpy expenses to monthly reserve

    # ── Liquidity, assets, liabilities and emergency reserve ──────────────────
    emergency_months_default: int = 6  # indicative, verify: default emergency-fund target in months
    emergency_months_min: int = 0  # indicative, verify: minimum selectable emergency-fund months
    emergency_months_max: int = 24  # indicative, verify: maximum selectable emergency-fund months
    penalty_asset_early_withdrawal_pct: float = 0.10  # indicative, verify: generic early-withdrawal penalty assumption
    allow_penalty_withdrawal_by_default: bool = False  # indicative, verify: penalty assets excluded unless explicitly allowed
    liquidity_ladder_months: tuple[int, ...] = (1, 6, 12, 60)  # indicative, verify: ladder horizons plus retirement horizon
    credit_card_payment_reconciliation_window_days: int = 2  # indicative, verify: card/transfer matching window
    own_account_transfer_window_days: int = 2  # indicative, verify: matching window for own-account transfers
    own_transfer_amount_tolerance_inr: float = 1.0  # indicative, verify: allowed amount difference for matched transfers
    credit_card_default_interest_annual: float = 0.36  # indicative, verify: illustrative card rate, not a provider quote
    high_interest_debt_annual_rate: float = 0.24  # indicative, verify: simulated residual deficit debt rate

    # ── Loans, affordability and purchase assumptions ────────────────────────
    bike_onroad_multiplier: float = 1.15  # indicative, verify: varies by state and vehicle; not a quote
    car_onroad_multiplier: float = 1.15  # indicative, verify: varies by state and vehicle; not a quote
    default_purchase_loan_rate_annual: float = 0.12  # indicative, verify: illustrative loan rate
    default_purchase_loan_tenure_months: int = 36  # indicative, verify: illustrative loan tenure
    default_down_payment_pct: float = 0.20  # indicative, verify: illustrative default down payment share
    common_emi_to_net_income_guideline: float = 0.40  # indicative, verify: configurable heuristic, not a rule
    affordability_very_likely_threshold: float = 0.85  # indicative, verify: label threshold
    affordability_likely_threshold: float = 0.65  # indicative, verify: label threshold
    affordability_stretch_threshold: float = 0.40  # indicative, verify: label threshold
    affordability_lever_saving_pct_min: float = 0.02  # indicative, verify: lowest share of income tested as extra saving
    affordability_lever_saving_pct_max: float = 0.20  # indicative, verify: highest share of income tested as extra saving
    affordability_lever_saving_grid_points: int = 10  # indicative, verify: extra-saving grid size
    affordability_price_reductions: tuple[float, ...] = (0.10, 0.20, 0.30)  # indicative, verify: tested price cuts
    affordability_wait_months: tuple[int, ...] = (3, 6, 9, 12)  # indicative, verify: tested purchase delays
    affordability_discretionary_cut_pct: float = 0.15  # indicative, verify: tested category reduction
    affordability_down_payment_options: tuple[float, ...] = (0.10, 0.20, 0.30, 0.40)  # indicative, verify: tested down-payment shares
    affordability_loan_running_cost_monthly_default: float = 3000.0  # indicative, verify: illustrative maintenance/fuel/insurance reserve in INR

    # ── Goal planning and allocation ────────────────────────────────────────
    goal_min_priority: int = 1  # indicative, verify: priority scale minimum; 1 is highest
    goal_max_priority: int = 3  # indicative, verify: priority scale maximum
    goal_default_min_acceptable_pct: float = 1.00  # indicative, verify: fraction of target required for success
    goal_default_hard: bool = True  # indicative, verify: default hard-goal flag
    goal_default_funding_mode: str = "cash"  # indicative, verify: valid values are cash or loan
    goal_default_minimum_amount: float = 0.0  # indicative, verify: minimum goal target in INR
    goal_retirement_default_age: int = 60  # indicative, verify: default retirement goal age
    goal_fee_fraction_for_loan: float = 0.02  # indicative, verify: illustrative loan/purchase fees fraction
    goal_purchase_post_floor_check_months: int = 3  # indicative, verify: post-purchase emergency-floor check period
    goal_time_to_fund_tolerance_inr: float = 1.0  # indicative, verify: amount tolerance for a funded goal
    allocation_emergency_first: bool = True  # indicative, verify: fund emergency reserve before goal contributions
    allocation_split_by_required_monthly_funding: bool = True  # indicative, verify: distribute surplus by required monthly amount
    compare_plan_default_priority_shift: int = 1  # indicative, verify: default demonstration priority change

    # ── Resilience score ─────────────────────────────────────────────────────
    resilience_hard_goals_weight: float = 0.60  # indicative, verify: share of score from all hard goals met
    resilience_emergency_floor_weight: float = 0.25  # indicative, verify: share of score from floor never breached
    resilience_runway_weight: float = 0.15  # indicative, verify: share of score from liquid runway
    resilience_runway_target_months: float = 6.0  # indicative, verify: runway months giving full runway component
    resilience_strong_min: int = 80  # indicative, verify: grade threshold
    resilience_solid_min: int = 60  # indicative, verify: grade threshold
    resilience_fragile_min: int = 40  # indicative, verify: grade threshold

    # ── Chaos Monkey: reverse stress-test search ─────────────────────────────
    chaos_job_loss_months_max: int = 12  # indicative, verify: bound on job-loss duration
    chaos_income_cut_pct_max: float = 0.40  # indicative, verify: maximum income-cut fraction
    chaos_income_cut_duration_months: int = 12  # indicative, verify: income-cut duration
    chaos_medical_expense_max: float = 1500000.0  # indicative, verify: maximum medical shock in INR
    chaos_market_drop_pct_max: float = 0.50  # indicative, verify: maximum equity market drop
    chaos_parental_support_pct_max: float = 0.30  # indicative, verify: support share of monthly income
    chaos_inflation_spike_points_max: float = 0.05  # indicative, verify: maximum additional annual inflation in decimal form
    chaos_onset_step_months: int = 3  # indicative, verify: grid interval for shock onset
    chaos_max_scenarios: int = 3  # indicative, verify: maximum distinct breaking scenarios displayed
    chaos_optimizer_starts: int = 4  # indicative, verify: starting points for constrained optimisation
    chaos_optimizer_max_iterations: int = 120  # indicative, verify: solver iteration limit
    chaos_job_loss_cost_scale_months: float = 3.0  # indicative, verify: heuristic implausibility scale
    chaos_income_cut_cost_scale_pct: float = 0.20  # indicative, verify: heuristic implausibility scale
    chaos_medical_cost_scale_inr: float = 300000.0  # indicative, verify: heuristic implausibility scale
    chaos_market_drop_cost_scale_pct: float = 0.25  # indicative, verify: heuristic implausibility scale
    chaos_support_cost_scale_pct: float = 0.15  # indicative, verify: heuristic implausibility scale
    chaos_inflation_spike_cost_scale: float = 0.02  # indicative, verify: heuristic implausibility scale
    chaos_likely_cost_max: float = 1.5  # indicative, verify: heuristic plausibility band
    chaos_possible_cost_max: float = 4.0  # indicative, verify: heuristic plausibility band
    chaos_standard_job_loss_months: int = 6  # indicative, verify: standard report-card shock
    chaos_standard_medical_expense: float = 500000.0  # indicative, verify: standard report-card shock in INR
    chaos_standard_income_cut_pct: float = 0.30  # indicative, verify: standard report-card income shock
    chaos_standard_market_drop_pct: float = 0.30  # indicative, verify: standard report-card market shock
    chaos_standard_expense_rise_pct: float = 0.20  # indicative, verify: standard report-card expense shock
    chaos_combined_shock_strength: float = 0.50  # indicative, verify: scale for combined report-card shock

    # ── Repair Lab ───────────────────────────────────────────────────────────
    repair_target_probability: float = 0.85  # indicative, verify: default goal success threshold
    repair_max_steps: int = 8  # indicative, verify: maximum greedy repair iterations
    repair_delay_candidates_months: tuple[int, ...] = (3, 6, 9, 12)  # indicative, verify: candidate deadline changes
    repair_goal_trim_candidates_pct: tuple[float, ...] = (0.05, 0.10, 0.15, 0.20)  # indicative, verify: candidate target reductions
    repair_extra_saving_candidates_inr: tuple[float, ...] = (1000.0, 2500.0, 4000.0, 6000.0, 10000.0)  # indicative, verify: candidate additional savings
    repair_discretionary_cut_candidates_pct: tuple[float, ...] = (0.05, 0.10, 0.15, 0.20)  # indicative, verify: candidate spending cuts
    repair_pause_low_priority_enabled: bool = True  # indicative, verify: allow candidate pause for soft low-priority goal
    repair_penalty_asset_liquidation_enabled: bool = True  # indicative, verify: allow costed penalty-asset candidate
    repair_minimum_probability_gain: float = 0.001  # indicative, verify: discard repairs with negligible gain
    repair_delay_pain_per_month_priority1: float = 1.0  # indicative, verify: pain weight for highest-priority goal delay
    repair_delay_pain_per_month_priority2: float = 0.75  # indicative, verify: pain weight for second-priority goal delay
    repair_delay_pain_per_month_priority3: float = 0.50  # indicative, verify: pain weight for third-priority goal delay
    repair_lifestyle_cut_pain_per_inr: float = 1.0  # indicative, verify: rupee-normalised lifestyle pain weight
    repair_rupee_cost_pain_per_inr: float = 1.0  # indicative, verify: rupee-normalised direct cost weight
    repair_extra_interest_pain_per_inr: float = 1.0  # indicative, verify: rupee-normalised added interest cost weight

    # ── Payday Autopilot and safe-to-spend ────────────────────────────────────
    autopilot_obligation_days_ahead: int = 30  # indicative, verify: obligation lookahead horizon
    autopilot_minimum_guilt_free_spend_pct: float = 0.0  # indicative, verify: lower allowance bound as share of salary
    autopilot_overspend_demo_amount: float = 5000.0  # indicative, verify: demonstration spend shock in INR
    autopilot_pace_on_track_tolerance: float = 0.10  # indicative, verify: spend-pace deviation tolerance

    # ── Cash-Crunch Radar ────────────────────────────────────────────────────
    radar_default_days: int = 90  # indicative, verify: default daily cash-flow projection horizon
    radar_balance_breach_probability_threshold: float = 0.15  # indicative, verify: warning probability threshold
    radar_obligation_cluster_count: int = 3  # indicative, verify: obligations constituting a pile-up
    radar_obligation_cluster_window_days: int = 5  # indicative, verify: pile-up date window
    radar_uncertainty_lower_percentile: float = 10.0  # indicative, verify: P10 lower balance band
    radar_uncertainty_upper_percentile: float = 90.0  # indicative, verify: P90 upper balance band

    # ── Time Machine, leaks and sensitivity ──────────────────────────────────
    leak_discretionary_cut_pct: float = 0.20  # indicative, verify: category cut tested in leak detector
    leak_default_extra_monthly_inr: float = 1000.0  # indicative, verify: rupee-to-days reference increment
    leak_creep_monthly_warning_inr: float = 500.0  # indicative, verify: illustrative monthly creep tax warning
    time_machine_default_month: int = 12  # indicative, verify: initial future-month slider value
    sensitivity_income_pct: float = 0.10  # indicative, verify: income sensitivity step
    sensitivity_expense_pct: float = 0.10  # indicative, verify: expense sensitivity step
    sensitivity_inflation_points: float = 0.02  # indicative, verify: inflation sensitivity step
    sensitivity_equity_return_points: float = 0.03  # indicative, verify: equity return sensitivity step
    sensitivity_job_loss_probability_multiplier_low: float = 0.50  # indicative, verify: lower job-loss probability case
    sensitivity_job_loss_probability_multiplier_high: float = 2.00  # indicative, verify: higher job-loss probability case
    sensitivity_goal_amount_pct: float = 0.10  # indicative, verify: goal-cost sensitivity step
    sensitivity_goal_date_months: int = 6  # indicative, verify: deadline sensitivity step
    sensitivity_fragility_threshold_probability_points: float = 20.0  # indicative, verify: probability swing threshold in percentage points

    # ── Events, guardrails, loan-vs-invest, household, backtest ───────────────
    event_cost_ranges_inr: tuple[tuple[str, float, float], ...] = (
        ("wedding", 300000.0, 2000000.0),  # indicative, verify: illustrative event-cost range
        ("baby", 100000.0, 600000.0),  # indicative, verify: illustrative event-cost range
        ("parents_medical", 50000.0, 1000000.0),  # indicative, verify: illustrative event-cost range
        ("relocation", 50000.0, 300000.0),  # indicative, verify: illustrative event-cost range
        ("home_renovation", 100000.0, 1500000.0),  # indicative, verify: illustrative event-cost range
    )
    event_job_switch_income_gap_months: tuple[int, int] = (1, 4)  # indicative, verify: illustrative income-gap range
    event_layoff_income_gap_months: tuple[int, int] = (3, 9)  # indicative, verify: illustrative income-gap range
    guardrail_emergency_trigger_months: float = 3.0  # indicative, verify: emergency-fund threshold for pausing goals
    guardrail_income_drop_pct: float = 0.20  # indicative, verify: income-drawdown trigger
    guardrail_discretionary_cut_pct: float = 0.15  # indicative, verify: discretionary reduction after income drop
    guardrail_negative_surplus_months: int = 2  # indicative, verify: consecutive negative-surplus trigger
    guardrail_sip_pause_months: int = 3  # indicative, verify: SIP pause duration
    loan_invest_risk_haircut: float = 0.03  # indicative, verify: risk haircut on expected investment return
    household_job_loss_correlation: float = 0.30  # indicative, verify: default Gaussian-copula correlation
    backtest_rolling_origins: int = 6  # indicative, verify: number of monthly rolling-origin checks
    backtest_nominal_coverage: float = 0.80  # indicative, verify: target predictive-interval coverage
    plan_autopsy_history_months: int = 12  # indicative, verify: period replayed in plan autopsy

    # ── Copilot, answer validation and privacy ───────────────────────────────
    llm_mode_enabled_by_default: bool = False  # indicative, verify: offline-first default; never require network
    llm_environment_variable: str = "ASKABHI_LLM_API_KEY"  # indicative, verify: optional environment variable name
    llm_send_raw_transaction_descriptions: bool = False  # indicative, verify: privacy rule; send aggregates only
    llm_number_guard_regenerate_once: bool = True  # indicative, verify: retry unverified numerical response once
    transaction_class_confidence_exact_merchant: float = 0.95  # indicative, verify: confidence prior, not a calibrated probability
    transaction_class_confidence_keyword: float = 0.75  # indicative, verify: confidence prior, not a calibrated probability
    transaction_class_confidence_amount_pattern: float = 0.60  # indicative, verify: confidence prior, not a calibrated probability
    transaction_class_confidence_unknown: float = 0.30  # indicative, verify: confidence prior, not a calibrated probability
    transaction_review_queue_threshold: float = 0.70  # indicative, verify: lower-confidence transactions need review

    # ── Synthetic classification and report defaults ─────────────────────────
    messy_dataset_duplicate_rows: int = 3  # indicative, verify: number of planted duplicate rows
    messy_dataset_invalid_amount_rows: int = 2  # indicative, verify: number of planted zero/negative rows
    messy_dataset_unparseable_date_rows: int = 1  # indicative, verify: number of planted invalid-date rows
    messy_dataset_missing_description_rows: int = 2  # indicative, verify: number of planted missing-description rows
    report_default_title: str = "AskAbhi 360 Financial Resilience Report"  # indicative, verify: report heading

    # ── Tax placeholders: disabled unless independently verified ─────────────
    tax_features_enabled: bool = False  # indicative, verify: disabled; never infer legal tax rules
    tax_placeholder_rate: float = 0.0  # indicative, verify: placeholder only, not a tax estimate

    # ── Product design tokens ────────────────────────────────────────────────
    color_background: str = "#070B09"  # indicative, verify: Neo-Mint Noir app background
    color_background_raised: str = "#0A110D"  # indicative, verify: raised background
    color_card: str = "rgba(16,26,19,.92)"  # indicative, verify: glass-like card surface
    color_teal: str = "#B7FF72"  # indicative, verify: primary light-green accent
    color_cyan: str = "#71F2A2"  # indicative, verify: secondary mint accent
    color_violet: str = "#B7A2FF"  # indicative, verify: optional contrast accent
    color_gold: str = "#F5D66E"  # indicative, verify: warm warning/attention accent
    color_success: str = "#83F0A5"  # indicative, verify: success state
    color_warning: str = "#FFD166"  # indicative, verify: warning state
    color_danger: str = "#FF8585"  # indicative, verify: danger state
    color_text: str = "#F0F7EF"  # indicative, verify: primary text
    color_muted: str = "#A1B4A3"  # indicative, verify: secondary text
    color_terracotta: str = "#B7FF72"  # indicative, verify: retained legacy field mapped to primary accent
    color_sage: str = "#71F2A2"  # indicative, verify: secondary mint accent
    color_peach: str = "rgba(183,255,114,.10)"  # indicative, verify: soft interaction surface
    color_border: str = "#253A2B"  # indicative, verify: card and table border
    card_border_radius_px: int = 16  # indicative, verify: design token
    content_max_width_px: int = 1280  # indicative, verify: design token
    body_font_min_px: float = 15.5  # indicative, verify: accessibility design target
    caption_font_px: int = 13  # indicative, verify: design token
    animation_duration_ms_min: int = 200  # indicative, verify: design motion duration
    animation_duration_ms_max: int = 400  # indicative, verify: design motion duration
    minimum_text_contrast_ratio: float = 4.5  # indicative, verify: accessibility target ratio

    # ── Product and trust labels ─────────────────────────────────────────────
    product_name: str = "AskAbhi 360"  # indicative, verify: product name
    product_tagline: str = "Your money. Smarter decisions. Brighter future."  # indicative, verify: product tagline
    product_disclaimer: str = (
        "AskAbhi 360 is an educational financial-planning tool, not investment, tax, "
        "legal, lending or other regulated financial advice. Projections are uncertain; "
        "verify all rates, prices, account data and assumptions independently."
    )  # indicative, verify: legal/product wording should be reviewed before launch

    def inflation_for(self, category: str | None) -> float:
        """Return configured annual inflation for a goal category; fallback is general inflation."""
        if not category:
            return self.general_inflation_annual
        key = category.strip().lower()
        return dict(self.inflation_by_category).get(key, self.general_inflation_annual)

    def asset_return_volatility(self, asset_class: str | None) -> tuple[float, float]:
        """Return the configured annual expected return and volatility for an asset class."""
        if not asset_class:
            return self.default_liquid_asset_return_annual, 0.01
        key = asset_class.strip().lower()
        mapping = {name: (ret, vol) for name, ret, vol in self.asset_return_volatility_by_class}
        return mapping.get(key, (self.default_liquid_asset_return_annual, 0.01))

    def assumptions_dict(self) -> dict[str, Any]:
        """Return all assumptions in a UI-friendly dictionary, without mutating the config."""
        return {field.name: getattr(self, field.name) for field in fields(self)}


def get_config() -> Config:
    """Return the frozen default configuration used across AskAbhi 360."""
    return Config()

# Frozen module-level alias required by the published interface contract.
CFG = get_config()
