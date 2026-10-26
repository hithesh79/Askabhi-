from datetime import date
import pytest
from core.models import Asset, Liability
from core.networth import net_worth, usable_funds, emi, amortisation


def test_net_worth_sums_assets_and_liabilities(ctx):
    nw=net_worth(ctx.assets,ctx.liabilities)
    assert nw.total_assets==250000
    assert nw.total_liabilities==60000
    assert nw.net_worth==190000


def test_liquidity_breakdown(ctx):
    nw=net_worth(ctx.assets,ctx.liabilities)
    assert nw.by_liquidity["liquid"]==200000
    assert nw.by_liquidity["penalty"]==20000
    assert nw.by_asset_class["equity"]==50000


def test_locked_asset_unavailable_before_unlock(ctx):
    assets=[Asset("Locked","retirement",100000,"retirement","locked",date(2027,1,1))]
    f=usable_funds(assets,date(2026,12,31),0)
    assert f.available==0


def test_locked_asset_available_after_unlock():
    assets=[Asset("Locked","retirement",100000,"retirement","locked",date(2027,1,1))]
    assert usable_funds(assets,date(2027,1,1),0).available==100000


def test_penalty_asset_shown_but_not_available():
    assets=[Asset("FD","deposit",100000,"debt","penalty",penalty_pct=.1)]
    f=usable_funds(assets,date(2026,1,1),0,False)
    assert f.available==0 and f.penalty_available==90000


def test_penalty_asset_available_only_when_allowed():
    assets=[Asset("FD","deposit",100000,"debt","penalty",penalty_pct=.1)]
    assert usable_funds(assets,date(2026,1,1),0,True).available==90000


def test_emergency_floor_is_subtracted():
    assets=[Asset("Cash","bank",100000)]
    assert usable_funds(assets,date(2026,1,1),40000).available==60000


def test_illiquid_asset_excluded():
    assets=[Asset("Gold","gold",100000,"gold","illiquid")]
    f=usable_funds(assets,date(2026,1,1),0,True)
    assert f.available==0 and f.excluded_illiquid==100000


def test_emi_hand_check():
    assert emi(1000000,.09,240)==pytest.approx(8997.0,abs=1)


def test_emi_zero_rate(): assert emi(120000,0,12)==10000

def test_emi_nonpositive_principal(): assert emi(0,.12,12)==0

def test_emi_positive_principal_requires_months():
    with pytest.raises(ValueError): emi(1000,.12,0)

def test_amortisation_closes_balance():
    a=amortisation(100000,.12,12)
    assert len(a)==12 and a.iloc[-1].closing_balance < .01
