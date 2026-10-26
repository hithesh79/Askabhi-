"""Net-worth, usable liquidity and loan amortisation calculations."""
from __future__ import annotations
from datetime import date
import math
import pandas as pd
from core.models import Asset, Liability, NetWorth, UsableFunds

def _value(row, key, default=0):
    if isinstance(row, dict): return row.get(key, default)
    return getattr(row, key, default)

def net_worth(assets, liabilities) -> NetWorth:
    assets = list(assets or []); liabilities = list(liabilities or [])
    total_assets = sum(max(0.0, float(_value(a, "value", 0))) for a in assets)
    total_liabilities = sum(max(0.0, float(_value(l, "outstanding", 0))) for l in liabilities)
    by_liquidity: dict[str, float] = {}
    by_class: dict[str, float] = {}
    by_kind: dict[str, float] = {}
    for a in assets:
        liq = str(_value(a, "liquidity", "liquid")); cls = str(_value(a, "asset_class", "other"))
        by_liquidity[liq] = by_liquidity.get(liq, 0.0) + max(0.0, float(_value(a, "value", 0)))
        by_class[cls] = by_class.get(cls, 0.0) + max(0.0, float(_value(a, "value", 0)))
    for l in liabilities:
        kind = str(_value(l, "kind", "other")); by_kind[kind] = by_kind.get(kind, 0.0) + max(0.0, float(_value(l, "outstanding", 0)))
    return NetWorth(total_assets, total_liabilities, total_assets-total_liabilities, by_liquidity, by_class, by_kind)

def usable_funds(assets, on_date: date, emergency_floor: float, allow_penalty: bool = False) -> UsableFunds:
    """Available cash excludes locked/unavailable assets and emergency floor."""
    liquid = 0.0; unlocked = 0.0; penalty = 0.0; illiquid = 0.0
    for a in assets or []:
        val = max(0.0, float(_value(a, "value", 0)))
        liquidity = str(_value(a, "liquidity", "liquid"))
        unlock = _value(a, "unlock_date", None)
        if liquidity == "liquid": liquid += val
        elif liquidity == "locked":
            if unlock is not None and unlock <= on_date: unlocked += val
        elif liquidity == "penalty": penalty += val * (1 - min(1.0, max(0.0, float(_value(a, "penalty_pct", 0)))))
        elif liquidity == "illiquid": illiquid += val
    penalty_available = penalty
    total_before_floor = liquid + unlocked + (penalty if allow_penalty else 0.0)
    available = max(0.0, total_before_floor - max(0.0, emergency_floor))
    return UsableFunds(available, penalty_available, max(0.0, emergency_floor), illiquid,
                       {"liquid": liquid, "unlocked": unlocked, "penalty_net": penalty, "illiquid_excluded": illiquid})

def emi(principal: float, annual_rate: float, months: int) -> float:
    """Monthly payment using P*r*(1+r)^n / ((1+r)^n-1); zero-rate handled."""
    p, n = float(principal), int(months)
    if p <= 0: return 0.0
    if n <= 0: raise ValueError("months must be positive for a positive principal")
    r = float(annual_rate) / 12.0
    if r <= 0: return p / n
    q = (1+r) ** n
    return p * r * q / (q - 1)

def amortisation(principal: float, annual_rate: float, months: int) -> pd.DataFrame:
    payment = emi(principal, annual_rate, months); balance = max(0.0, float(principal)); rows=[]
    r = max(0.0, float(annual_rate)) / 12.0
    for i in range(1, int(months)+1):
        interest = balance*r; principal_paid = min(balance, max(0.0, payment-interest)); closing = max(0.0, balance-principal_paid)
        rows.append({"month": i, "opening_balance": balance, "payment": min(payment, balance+interest), "interest": interest, "principal": principal_paid, "closing_balance": closing})
        balance = closing
        if balance < 1e-8: break
    return pd.DataFrame(rows, columns=["month","opening_balance","payment","interest","principal","closing_balance"])

def liquidity_ladder(ctx) -> pd.DataFrame:
    """Return accessible asset amounts at 1m, 6m, 1y, 5y and retirement horizons."""
    from config import CFG
    horizons = list(CFG.liquidity_ladder_months) + [max(0, (ctx.profile.as_of.year + max(0, 60-30) - ctx.profile.as_of.year)*12)]
    horizons = sorted(set(h for h in horizons if h >= 0))
    rows=[]
    for m in horizons:
        year = ctx.profile.as_of.year + (ctx.profile.as_of.month-1+m)//12
        month = (ctx.profile.as_of.month-1+m)%12+1
        import calendar
        d = date(year, month, min(ctx.profile.as_of.day, calendar.monthrange(year,month)[1]))
        funds=usable_funds(ctx.assets,d,0,allow_penalty=True)
        rows.append({"months":m,"date":d,"accessible_including_penalty":funds.available+funds.emergency_floor,"net_usable_after_floor":funds.available})
    return pd.DataFrame(rows)
