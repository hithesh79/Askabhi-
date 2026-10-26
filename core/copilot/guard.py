"""Number guard: flag numbers not backed by tool evidence."""
from __future__ import annotations
import re
from core.models import GuardReport

_AMOUNT_WORDS=re.compile(r"(?i)(?:₹\s*)?(-?\d[\d,]*(?:\.\d+)?)\s*(lakh|lakhs|lac|l|crore|crores|cr|k)?")

def _normalise_token(num,unit):
    try: val=float(num.replace(",",""))
    except ValueError: return None
    u=(unit or "").lower()
    if u in ("lakh","lakhs","lac","l"): val*=100000
    elif u in ("crore","crores","cr"): val*=10000000
    elif u=="k": val*=1000
    return round(val,2)

def _numbers(text):
    out=[]
    for m in _AMOUNT_WORDS.finditer(str(text)):
        token=m.group(0).strip()
        num=m.group(1); unit=m.group(2)
        value=_normalise_token(num,unit)
        if value is not None: out.append((token,value))
    # percentages are compared as values in points; date-like numbers can be benign but still flagged
    return out

def verify_numbers(text: str, evidence) -> GuardReport:
    evidence_text=str(evidence)
    evalues={v for _,v in _numbers(evidence_text)}
    verified=[]; unverified=[]
    for token,val in _numbers(text):
        if val in evalues or any(abs(val-x)<=max(.01,abs(x)*.001) for x in evalues): verified.append(token)
        else:
            # Plain numeric list indices and common year-like numbers are not financial outputs.
            if re.fullmatch(r"\d{4}",token) and 1900<=val<=2100: continue
            unverified.append(token)
    return GuardReport(not unverified,unverified,verified)
