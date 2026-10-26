"""Deterministic synthetic personas and realistic transaction histories.

Arjun is seeded with recurring subscriptions, weekend dining, payday bursts,
month-end squeeze, festival-season spending, lifestyle creep and one-off shocks.
Meera has highly variable freelance credits and several lean months. All values
are synthetic and demonstrate mechanics, not predictions about real customers.
"""
from __future__ import annotations
from datetime import date, timedelta
import calendar
import numpy as np
import pandas as pd
from config import CFG
from core.models import Asset, Liability, Goal, Profile, PersonaBundle

def add_months(d: date, months: int) -> date:
    idx = d.year*12 + d.month-1 + int(months)
    y, m0 = divmod(idx, 12); m=m0+1
    return date(y,m,min(d.day,calendar.monthrange(y,m)[1]))

def _monthly_date(as_of: date, months_ago: int, day: int) -> date:
    d=add_months(as_of,-months_ago)
    return date(d.year,d.month,min(day,calendar.monthrange(d.year,d.month)[1]))

def _generate_transactions(name: str, as_of: date, seed: int, months: int = 12) -> pd.DataFrame:
    rng=np.random.default_rng(seed + (0 if name.lower()=="arjun" else 303))
    rows=[]; salary=CFG.arjun_monthly_net_income if name.lower()=="arjun" else CFG.meera_monthly_mean_income
    descriptions=[("Rent", "Housing", 18000, "essential"), ("BigBasket groceries", "Groceries", 4200, "essential"),
        ("Electricity bill", "Utilities", 1400, "essential"), ("Airtel broadband", "Telecom", 999, "fixed"),
        ("Jio mobile", "Telecom", 599, "fixed"), ("Netflix subscription", "Subscriptions", 649, "fixed"),
        ("Hotstar subscription", "Subscriptions", 299, "fixed"), ("Gym membership", "Subscriptions", 1200, "fixed"),
        ("LIC premium", "Insurance", 2500, "fixed"), ("Petrol pump", "Transport", 2800, "essential"),
        ("Swiggy order", "Food delivery", 750, "discretionary"), ("Zomato order", "Food delivery", 650, "discretionary"),
        ("Zepto delivery", "Groceries", 850, "essential"), ("Uber ride", "Transport", 450, "discretionary"),
        ("Amazon shopping", "Shopping", 1700, "discretionary"), ("UPI transfer to family", "Family support", 4000, "essential"),
        ("Medical pharmacy", "Medical", 1000, "essential"), ("Coffee shop", "Dining", 350, "discretionary"),
        ("Restaurant dinner", "Dining", 1600, "discretionary"), ("Personal loan EMI", "Loan EMI", 8500, "fixed")]
    for m in range(months,0,-1):
        first=_monthly_date(as_of,m,1)
        month_income = salary if name.lower()=="arjun" else max(18000, salary*rng.lognormal(-0.5*0.40**2,0.40))
        # Salary/income credit near the beginning of the month. Irregular persona has multiple client credits.
        if name.lower()=="arjun":
            rows.append({"date":first.isoformat(),"description":"Salary credit - employer","amount":round(month_income,2),"type":"credit","account":"SAVINGS"})
        else:
            n_clients=int(rng.integers(1,4)); amounts=rng.dirichlet(np.ones(n_clients))*month_income
            for j,amt in enumerate(amounts):
                day=int(rng.integers(2,24)); d=date(first.year,first.month,min(day,calendar.monthrange(first.year,first.month)[1]))
                rows.append({"date":d.isoformat(),"description":f"Freelance client payment {j+1}","amount":round(float(amt),2),"type":"credit","account":"SAVINGS"})
        # Repeat fixed and varied spends throughout the month
        for desc,cat,base,nature in descriptions:
            if name.lower()=="meera" and cat=="Loan EMI": continue
            # lifestyle creep applies gradually to nonessential merchants
            creep=1+(0.008*(months-m)) if nature=="discretionary" else 1.0
            if desc=="LIC premium":
                # One annual premium is intentionally planted in April.
                if first.month != 4: continue
                amt=base*12
                day=10
            elif desc in ("Rent","Airtel broadband","Jio mobile","Netflix subscription","Hotstar subscription","Gym membership","Personal loan EMI"):
                amt=base
                # Plant repeatable due dates so monthly recurring detection can discover
                # these examples from transaction history instead of relying on labels.
                fixed_days={"Rent":5,"Personal loan EMI":5,"Airtel broadband":12,
                            "Jio mobile":19,"Netflix subscription":15,
                            "Hotstar subscription":17,"Gym membership":10}
                day=fixed_days[desc]
            else:
                # More dining on weekends and shortly after salary; use 2-4 transactions per month.
                count=int(rng.integers(2,5)) if cat in ("Food delivery","Dining","Shopping","Transport") else int(rng.integers(1,3))
                for j in range(count):
                    if cat in ("Food delivery","Dining"):
                        day=int(rng.choice([3,5,8,12,16,19,21,24,26,28], p=np.array([.18,.15,.12,.08,.08,.08,.07,.08,.08,.08])))
                    else: day=int(rng.integers(2,29))
                    dd=date(first.year,first.month,min(day,calendar.monthrange(first.year,first.month)[1]))
                    amount=max(50,base*creep*rng.lognormal(-0.5*0.28**2,0.28))
                    if first.month in (10,11) and nature=="discretionary": amount*=1.35
                    rows.append({"date":dd.isoformat(),"description":desc,"amount":round(amount,2),"type":"debit","account":"SAVINGS"})
                continue
            day=min(day,calendar.monthrange(first.year,first.month)[1]); dd=date(first.year,first.month,day)
            rows.append({"date":dd.isoformat(),"description":desc,"amount":round(amt,2),"type":"debit","account":"SAVINGS"})
        # card purchases, card settlement and a SIP transfer (not consumption)
        card_total=0.0
        for desc,amt in [("Amazon card purchase",rng.uniform(500,2500)),("Fuel card purchase",rng.uniform(500,1200))]:
            card_total += amt
            rows.append({"date":_monthly_date(as_of,m,18).isoformat(),"description":desc,"amount":round(float(amt),2),"type":"debit","account":"CREDIT_CARD"})
        rows.append({"date":_monthly_date(as_of,m,25).isoformat(),"description":"Credit card bill payment","amount":round(card_total,2),"type":"debit","account":"SAVINGS"})
        rows.append({"date":_monthly_date(as_of,m,10).isoformat(),"description":"SIP mutual fund transfer","amount":5000.0 if name.lower()=="arjun" else 2000.0,"type":"debit","account":"SAVINGS"})
        # Intentional one-off shocks
        if m in (9,5,2):
            shock_desc={9:"Bike repair - unexpected",5:"Medical emergency expense",2:"Gadget replacement"}[m]
            shock_amt={9:8500,5:12500,2:18000}[m]
            rows.append({"date":_monthly_date(as_of,m,24).isoformat(),"description":shock_desc,"amount":float(shock_amt),"type":"debit","account":"SAVINGS"})
    df=pd.DataFrame(rows)
    if not df.empty:
        # Tune synthetic discretionary/variable purchases to leave a realistic savings margin
        # for the F-02 demo. Fixed contractual commitments remain at their stated value.
        fixed_tokens=("rent","personal loan emi","airtel broadband","jio mobile","netflix subscription","hotstar subscription","gym membership","lic premium","sip mutual fund transfer","credit card bill payment")
        for idx,row in df.iterrows():
            desc=str(row["description"]).lower()
            if str(row["type"]).lower()=="debit" and not any(token in desc for token in fixed_tokens):
                df.at[idx,"amount"]=round(float(row["amount"])*0.72,2)
        df["date"]=pd.to_datetime(df["date"]).dt.date.astype(str)
        df=df.sort_values(["date","description"],kind="stable").reset_index(drop=True)
    return df

def generate_persona(name: str, as_of: date, seed: int = 42) -> PersonaBundle:
    key=name.strip().lower()
    if key not in {"arjun","meera"}: raise ValueError("name must be Arjun or Meera")
    transactions=_generate_transactions(key,as_of,seed,CFG.demo_history_months)
    if key=="arjun":
        profile=Profile(as_of,CFG.arjun_monthly_net_income,"salaried",CFG.arjun_income_growth_annual,CFG.arjun_job_loss_probability_annual,stated_monthly_budget=60000.0,stated_monthly_saving=25000.0,emergency_months=6,essential_monthly_spend=35000.0)
        assets=[Asset("Savings account","bank",CFG.demo_starting_cash,"cash","liquid",exp_return=.03,vol=.01),Asset("Liquid mutual fund","mutual_fund",CFG.demo_starting_liquid_fund,"debt","liquid",exp_return=.06,vol=.06),Asset("Equity mutual funds / SIP","investment",CFG.demo_starting_equity,"equity","liquid",exp_return=.10,vol=.20),Asset("EPF","retirement",CFG.demo_starting_epf,"retirement","locked",date(as_of.year+32,as_of.month,min(as_of.day,calendar.monthrange(as_of.year+32,as_of.month)[1])),exp_return=.08,vol=.12),Asset("PPF","retirement",CFG.demo_starting_ppf,"retirement","locked",date(as_of.year+5,as_of.month,min(as_of.day,calendar.monthrange(as_of.year+5,as_of.month)[1])),exp_return=.07,vol=.04),Asset("Fixed deposit","deposit",CFG.demo_starting_fd,"debt","penalty",penalty_pct=.01,exp_return=.06,vol=.01),Asset("Gold","gold",CFG.demo_starting_gold,"gold","illiquid",exp_return=.06,vol=.15)]
        liabilities=[Liability("Education/personal loan","personal_loan",CFG.demo_personal_loan_outstanding,CFG.demo_personal_loan_annual_rate,CFG.demo_personal_loan_emi,CFG.demo_personal_loan_months_left),Liability("Credit-card balance","credit_card",CFG.demo_credit_card_outstanding,CFG.credit_card_default_interest_annual,3000.0,6)]
        goals=[Goal("bike","BMW-class bike","vehicle",CFG.demo_bike_goal_amount,add_months(as_of,CFG.demo_bike_goal_months),1,True,.95,None,"cash",.25,.12,36,3500,1.15),Goal("mba","MBA / higher education","education",CFG.demo_mba_goal_amount_today,add_months(as_of,CFG.demo_mba_goal_months),2,False,.40,None,"cash"),Goal("home","Home down payment","home",CFG.demo_home_down_payment_today,add_months(as_of,CFG.demo_home_goal_months),2,False,.75,None,"cash"),Goal("retirement","Retirement corpus","retirement",25000000.0,date(as_of.year+(CFG.demo_retirement_age-CFG.arjun_age),as_of.month,min(as_of.day,calendar.monthrange(as_of.year+(CFG.demo_retirement_age-CFG.arjun_age),as_of.month)[1])),3,False,.75,None,"cash"),Goal("emergency","Emergency fund top-up","emergency",35000.0*6,add_months(as_of,18),1,True,.9,None,"cash")]
        desc="Arjun: salaried Bengaluru professional; synthetic 12-month transaction history with spending patterns and competing goals."
    else:
        profile=Profile(as_of,CFG.meera_monthly_mean_income,"irregular",.03,.08,stated_monthly_budget=55000.0,stated_monthly_saving=15000.0,emergency_months=8,essential_monthly_spend=30000.0)
        assets=[Asset("Savings account","bank",110000,"cash","liquid",exp_return=.03,vol=.01),Asset("Liquid fund","investment",90000,"debt","liquid",exp_return=.06,vol=.06),Asset("Equity investments","investment",80000,"equity","liquid",exp_return=.10,vol=.20),Asset("Gold jewellery","gold",60000,"gold","illiquid",exp_return=.06,vol=.15)]
        liabilities=[Liability("Credit-card balance","credit_card",12000,.36,2500,5)]
        goals=[Goal("emergency","Emergency fund","emergency",240000,add_months(as_of,12),1,True,.9),Goal("studio","Home studio upgrade","other",350000,add_months(as_of,24),2,False,.8),Goal("home","Home down payment","home",1500000,add_months(as_of,72),2,True,.8)]
        desc="Meera: freelance designer with variable synthetic income and lean months."
    return PersonaBundle(name.strip().title(),profile,transactions,assets,liabilities,goals,desc)

def generate_all(as_of: date, seed: int = 42) -> dict[str, PersonaBundle]:
    """Generate deterministic demo personas and a deliberately messy CSV dataset."""
    result={"Arjun":generate_persona("Arjun",as_of,seed),"Meera":generate_persona("Meera",as_of,seed)}
    # Keep synthetic messy examples as a separate CSV written by generate_csvs().
    # Do not store a DataFrame inside transactions.attrs: pandas propagates attrs
    # through Series operations and newer pandas versions try to compare nested
    # DataFrames as booleans, breaking normal groupby/indexing operations.
    return result

def generate_csvs(directory, as_of: date | None = None, seed: int = 42) -> dict[str, str]:
    """Write demo CSV files to a chosen directory and return their paths."""
    from pathlib import Path
    out=Path(directory); out.mkdir(parents=True,exist_ok=True); as_of=as_of or date.today()
    personas=generate_all(as_of,seed); paths={}
    for name,key in [("Arjun","transactions.csv"),("Meera","transactions_meera.csv")]:
        p=out/key; personas[name].transactions.to_csv(p,index=False,encoding="utf-8"); paths[name]=str(p)
    template=pd.DataFrame(columns=["date","description","amount","type","account"])
    tp=out/"transactions_template.csv"; template.to_csv(tp,index=False,encoding="utf-8"); paths["template"]=str(tp)
    arjun=personas["Arjun"].transactions
    messy=pd.concat([arjun,arjun.iloc[:2],pd.DataFrame([
        {"date":"invalid","description":"Unparseable date","amount":100,"type":"debit","account":"SAVINGS"},
        {"date":as_of.isoformat(),"description":"Zero amount","amount":0,"type":"debit","account":"SAVINGS"},
        {"date":as_of.isoformat(),"description":"Negative amount","amount":-10,"type":"debit","account":"SAVINGS"},
        {"date":as_of.isoformat(),"description":"","amount":250,"type":"debit","account":"SAVINGS"}])],ignore_index=True)
    mp=out/"transactions_messy.csv"; messy.to_csv(mp,index=False,encoding="utf-8"); paths["messy"]=str(mp)
    return paths
