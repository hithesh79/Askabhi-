import pytest
from datetime import date
from core.formatting import inr, pct, months_to_text, date_text

@pytest.mark.parametrize("value,expected", [
    (12345678,"₹1,23,45,678"), (1234,"₹1,234"), (0,"₹0"), (-123456,"-₹1,23,456"),
    (999,"₹999"), (100000,"₹1,00,000"), (123456789,"₹12,34,56,789"),
])
def test_indian_grouping(value, expected): assert inr(value) == expected

@pytest.mark.parametrize("value,expected", [(0,"0%"),(.5,"50%"),(1,"100%"),(.123,"12%")])
def test_percent_format(value, expected): assert pct(value) == expected

def test_percent_digits(): assert pct(.1234,1)=="12.3%"

def test_compact_lakh(): assert inr(250000,compact=True)=="₹2.50 L"

def test_compact_crore(): assert inr(25000000,compact=True)=="₹2.50 Cr"

def test_compact_thousands(): assert inr(1500,compact=True)=="₹1.5 K"

@pytest.mark.parametrize("months,expected", [(0,"0 months"),(1,"1 month"),(12,"1 year"),(14,"1 year 2 months"),(24,"2 years")])
def test_months_to_text(months,expected): assert months_to_text(months)==expected

def test_infinite_months(): assert "Not reached" in months_to_text(float("inf"))

def test_date_text_iso(): assert date_text("2026-10-25")=="25 Oct 2026"

def test_date_text_bad_string_is_preserved(): assert date_text("bad-date")=="bad-date"
