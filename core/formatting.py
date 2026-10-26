"""Indian-number formatting and date helpers."""
from __future__ import annotations
from datetime import date, datetime
import math

def inr(x: float, compact: bool = False) -> str:
    value = float(x or 0)
    sign = "-" if value < 0 else ""
    value = abs(value)
    if compact:
        if value >= 1e7: return f"{sign}₹{value/1e7:.2f} Cr"
        if value >= 1e5: return f"{sign}₹{value/1e5:.2f} L"
        if value >= 1e3: return f"{sign}₹{value/1e3:.1f} K"
    whole = int(round(value))
    s = str(whole)
    if len(s) <= 3: grouped = s
    else:
        last3, head = s[-3:], s[:-3]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:]); head = head[:-2]
        if head: groups.insert(0, head)
        grouped = ",".join(groups + [last3])
    return f"{sign}₹{grouped}"

def pct(p: float, digits: int = 0) -> str:
    return f"{100*float(p):.{digits}f}%"

def months_to_text(m: float) -> str:
    if not math.isfinite(float(m)): return "Not reached within the modelled horizon"
    m = max(0, int(round(m)))
    years, months = divmod(m, 12)
    parts = []
    if years: parts.append(f"{years} year" + ("s" if years != 1 else ""))
    if months or not parts: parts.append(f"{months} month" + ("s" if months != 1 else ""))
    return " ".join(parts)

def date_text(d: date | datetime | str) -> str:
    if isinstance(d, str):
        try: d = date.fromisoformat(d[:10])
        except ValueError: return d
    return d.strftime("%d %b %Y")
