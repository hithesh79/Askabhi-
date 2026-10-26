"""Generate a self-contained, print-friendly AskAbhi 360 financial report.

The downloadable report uses the same Neo-Mint Noir black-and-lime visual identity
as the app. It has no remote assets or runtime network requirements; browser font
imports are intentionally omitted from reports so the document remains portable.
"""
from __future__ import annotations

from datetime import datetime
import html

from core.formatting import date_text, inr, pct
from core.models import ScenarioParams
from core.resilience import resilience_score
from core.simulate import simulate


_REPORT_BG = "#070B09"
_REPORT_PANEL = "#101A13"
_REPORT_BORDER = "#253A2B"
_REPORT_TEXT = "#F0F7EF"
_REPORT_MUTED = "#A1B4A3"
_REPORT_LIME = "#B7FF72"
_REPORT_MINT = "#71F2A2"
_REPORT_GOLD = "#F5D66E"


def build_report_html(session) -> str:
    """Return a complete HTML report using the provided context and shared draws."""
    ctx = session["ctx"] if isinstance(session, dict) else session.ctx
    draws = session["draws"] if isinstance(session, dict) else session.draws
    result = simulate(ctx, ScenarioParams(), draws)
    score = resilience_score(ctx, result)

    rows = "".join(
        "<tr>"
        f"<td>{html.escape(g.name)}</td>"
        f"<td>{inr(g.target_amount_today)}</td>"
        f"<td>{date_text(g.target_date)}</td>"
        f"<td>{pct(result.goal_probabilities.get(g.goal_id, 0))} "
        f"± {pct(result.goal_standard_errors.get(g.goal_id, 0), 1)} pp</td>"
        f"<td>{'Hard' if g.hard else 'Soft'}</td>"
        "</tr>"
        for g in ctx.goals
    )

    values = [float(value) for value in result.net_worth_p50]
    minimum = min(values, default=0.0)
    maximum = max(values, default=1.0)
    span = max(1.0, maximum - minimum)
    points = []
    for index, value in enumerate(values):
        x = 30 + index * 900 / max(1, len(values) - 1)
        y = 190 - 145 * (value - minimum) / span
        points.append(f"{x:.1f},{y:.1f}")

    chart = (
        "<svg viewBox='0 0 960 220' role='img' "
        "aria-label='Median simulated net-worth projection' "
        "xmlns='http://www.w3.org/2000/svg'>"
        f"<line x1='30' y1='190' x2='930' y2='190' stroke='{_REPORT_BORDER}'/>"
        f"<polyline points='{' '.join(points)}' fill='none' stroke='{_REPORT_LIME}' "
        "stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/>"
        f"<text x='30' y='18' fill='{_REPORT_MUTED}' font-size='12'>"
        "P50 net-worth path · modelled, not guaranteed</text></svg>"
    )

    disclaimer = (
        "AskAbhi 360 is an educational planning tool, not investment, tax, legal, "
        "lending or other regulated financial advice. Synthetic data validates "
        "mechanics only. Verify account data, rates, costs, assumptions and all "
        "recommendations independently."
    )
    generated_at = datetime.now().strftime("%d %b %Y %H:%M")
    title = html.escape("AskAbhi 360 Financial Resilience Report")
    persona = html.escape(str(ctx.persona_name))
    grade = html.escape(str(score.grade))
    verdict = html.escape(f"Your modelled resilience is {score.score}/100 ({score.grade}).")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root{{--bg:{_REPORT_BG};--panel:{_REPORT_PANEL};--border:{_REPORT_BORDER};--text:{_REPORT_TEXT};--muted:{_REPORT_MUTED};--lime:{_REPORT_LIME};--mint:{_REPORT_MINT};--gold:{_REPORT_GOLD}}}
*{{box-sizing:border-box}}
body{{margin:0;background:radial-gradient(ellipse at 8% 0%,rgba(91,255,135,.08),transparent 34%),var(--bg);color:var(--text);font:15px/1.6 'DM Sans',Inter,system-ui,-apple-system,sans-serif}}
main{{max-width:1080px;margin:auto;padding:34px 22px 60px}}
h1,h2,h3{{font-family:'Space Grotesk','DM Sans',Inter,system-ui,sans-serif;line-height:1.18;letter-spacing:-.025em}}
h1{{font-size:clamp(28px,4vw,42px);margin:.35rem 0}}
h2{{font-size:22px;margin:.2rem 0 .7rem}}
p{{margin:.6rem 0}}
.muted{{color:var(--muted)}}
.kicker{{font-size:11px;text-transform:uppercase;letter-spacing:.16em;font-weight:800;color:var(--lime)}}
.card{{border:1px solid var(--border);background:linear-gradient(145deg,rgba(16,26,19,.97),rgba(10,17,12,.97));border-radius:18px;padding:22px;margin:16px 0;box-shadow:0 10px 30px rgba(0,0,0,.18)}}
.hero{{border-color:#36553E;background:radial-gradient(ellipse at 95% 0%,rgba(183,255,114,.10),transparent 38%),linear-gradient(125deg,#101A13,#0A110D)}}
.score{{font-size:clamp(42px,7vw,60px);font-weight:800;letter-spacing:-.055em;color:var(--lime);font-family:'Space Grotesk','DM Sans',sans-serif}}
.pill{{display:inline-block;margin:4px 6px 4px 0;padding:5px 10px;border:1px solid #31573A;border-radius:999px;background:#162D20;color:var(--lime);font-size:12px;font-weight:700}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}
.metric{{border:1px solid var(--border);background:#0C150F;border-radius:14px;padding:15px;min-width:0}}
.metric-label{{color:var(--muted);font-size:12px}}
.metric-value{{font-weight:800;font-size:20px;overflow-wrap:anywhere;font-variant-numeric:tabular-nums}}
table{{width:100%;border-collapse:collapse;overflow-wrap:anywhere}}
th,td{{padding:12px 10px;border-bottom:1px solid var(--border);text-align:left}}
th{{color:var(--muted);font-size:12px;font-weight:700}}
th:first-child,td:first-child{{padding-left:0}}
.disclaimer{{border-left:3px solid var(--lime);padding:12px 15px;background:rgba(183,255,114,.055);border-radius:0 10px 10px 0;color:#D4E1D5}}
@media(max-width:650px){{main{{padding:18px 12px 36px}}.card{{padding:16px;border-radius:14px}}.grid{{grid-template-columns:1fr}}table{{font-size:12px}}th,td{{padding:8px 5px}}}}
@media print{{body{{background:white;color:#111}}.card,.metric{{background:white;border-color:#bbb;box-shadow:none}}.muted,th{{color:#444}}.score,.kicker{{color:#225D37}}.disclaimer{{background:#f4f8f4;color:#222}}svg text{{fill:#444}}}}
</style>
</head>
<body><main>
<section class="card hero">
  <div class="kicker">AskAbhi 360 · Financial intelligence</div>
  <h1>A financial plan that survives real life.</h1>
  <p class="muted">Persona: <strong>{persona}</strong> · As of {date_text(ctx.profile.as_of)} · Generated {generated_at}</p>
  <h2>{verdict}</h2>
  <p class="muted">This report uses financial assumptions and seeded simulation draws. Probabilities are estimates, not promises.</p>
  <span class="pill">● Evidence-led</span><span class="pill">● Reproducible</span><span class="pill">● Educational planning</span>
</section>
<section class="card">
  <h2>Financial verdict</h2>
  <div class="grid">
    <div class="metric"><div class="metric-label">Resilience score</div><div class="score">{score.score}<span style="font-size:18px;color:var(--muted)"> / 100</span></div><div class="muted">{grade} · Explainable heuristic</div></div>
    <div class="metric"><div class="metric-label">Hard-goal success</div><div class="metric-value">{pct(score.hard_goals_probability)}</div><div class="muted">Modelled across seeded scenarios</div></div>
    <div class="metric"><div class="metric-label">Emergency floor maintained</div><div class="metric-value">{pct(score.emergency_floor_never_breached_probability)}</div><div class="muted">Estimated probability</div></div>
  </div>
  <p>Liquid runway: <strong>{score.runway_months:.1f} months</strong>.</p>
  <p class="muted">Random seed: <code>{draws.seed}</code> · Draw fingerprint: <code>{draws.fingerprint()}</code></p>
</section>
<section class="card">
  <h2>Goal feasibility</h2>
  <div style="overflow-x:auto"><table><thead><tr><th>Goal</th><th>Amount today</th><th>Target date</th><th>Estimated feasibility</th><th>Type</th></tr></thead><tbody>{rows}</tbody></table></div>
</section>
<section class="card"><h2>Projected net worth</h2>{chart}<p class="muted">The line shows the median simulated path. Results depend on income, spending, inflation, returns, liquidity, and user assumptions.</p></section>
<section class="card"><h2>Assumptions and limitations</h2><p>Income, spending, inflation, market returns, job-loss probability, unexpected expenses and asset liquidity are modelled using configurable assumptions. Synthetic data validates mechanics only, not real-world forecast accuracy.</p><p class="disclaimer">{html.escape(disclaimer)}</p></section>
</main></body></html>"""
