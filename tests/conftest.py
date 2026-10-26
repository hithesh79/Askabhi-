from __future__ import annotations
from datetime import date
import pandas as pd
import pytest
from config import CFG
from core.behaviour import analyse
from core.classify import classify
from core.data_gen import generate_persona
from core.models import Asset, BehaviourProfile, Goal, Liability, PlanContext, Profile
from core.reconcile import reconcile
from core.rng import make_draws

AS_OF = date(2026, 1, 31)


def make_small_context(*, income=95000.0, assets=True, goals=True, locked=False):
    profile = Profile(AS_OF, income, "salaried", .04, .01, 60000, 25000, 2, 20000,
                      [income] * 12)
    asset_rows = []
    if assets:
        asset_rows = [
            Asset("Savings", "bank", 100000, "cash", "liquid", exp_return=.03, vol=.01),
            Asset("Liquid fund", "mutual_fund", 50000, "debt", "liquid", exp_return=.05, vol=.03),
            Asset("Equity fund", "investment", 50000, "equity", "liquid", exp_return=.08, vol=.16),
            Asset("FD", "deposit", 20000, "debt", "penalty", penalty_pct=.01, exp_return=.05, vol=.01),
            Asset("Gold", "gold", 30000, "gold", "illiquid", exp_return=.04, vol=.10),
        ]
    if locked:
        asset_rows.append(Asset("Locked PPF", "retirement", 100000, "retirement", "locked",
                                date(2026, 4, 30), exp_return=.06, vol=.04))
    liabilities = [Liability("Personal loan", "personal_loan", 60000, .10, 5000, 12)] if assets else []
    goal_rows = []
    if goals:
        goal_rows = [
            Goal("bike", "Bike", "vehicle", 100000, date(2026, 7, 31), 1, True, .9,
                 .06, "cash", .2, .12, 36, 1500, 1.10),
            Goal("education", "Education", "education", 200000, date(2027, 1, 31), 2, False, .6),
            Goal("emergency", "Emergency reserve", "emergency", 40000, date(2026, 7, 31), 1, True, .8),
        ]
    bp = BehaviourProfile(as_of=AS_OF,
        category_monthly_mean={"Essentials": 20000.0, "Food delivery": 4000.0, "Fixed": 3000.0},
        category_monthly_std={"Essentials": 1200.0, "Food delivery": 1500.0, "Fixed": 100.0},
        category_nature={"Essentials": "essential", "Food delivery": "discretionary", "Fixed": "fixed"},
        monthly_spend_history=[27000.0] * 12, monthly_income_history=[income] * 12,
        seasonal_index={m: 1.0 for m in range(1, 13)}, safe_income=income,
        months_of_data=12, confidence="High", unplanned_lambda_annual=1.0,
        unplanned_lognormal_mu=9.0, unplanned_lognormal_sigma=.6,
        actual_median_saving=income-27000, transaction_categories=pd.DataFrame(columns=["kind", "amount"]))
    tx = pd.DataFrame([
        {"date":"2025-11-01", "description":"Salary credit", "amount":income, "type":"credit", "account":"SAVINGS"},
        {"date":"2025-11-03", "description":"Swiggy order", "amount":650, "type":"debit", "account":"SAVINGS"},
    ])
    return PlanContext(profile, asset_rows, liabilities, goal_rows, bp, CFG, tx, "Test persona")


@pytest.fixture
def ctx():
    return make_small_context()


@pytest.fixture

def draws():
    return make_draws(42, 40, 60)


@pytest.fixture

def arjun_bundle():
    return generate_persona("Arjun", AS_OF, 42)


@pytest.fixture

def meera_bundle():
    return generate_persona("Meera", AS_OF, 42)


@pytest.fixture

def analysed_arjun(arjun_bundle):
    tx = classify(arjun_bundle.transactions)
    tx, _ = reconcile(tx)
    bp = analyse(tx, AS_OF, arjun_bundle.profile)
    return tx, bp, arjun_bundle
