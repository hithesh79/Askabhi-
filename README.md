# AskAbhi 360 — Financial Intelligence & Multi-Goal Planning

**A financial plan that survives real life.**

AskAbhi 360 is an offline-first personal-finance planning prototype for India's salaried and irregular-income users. It joins transaction intelligence, behavioural analysis, assets and liabilities, multi-goal planning, uncertainty-aware simulation, reverse stress testing, plan repair and an explainable financial copilot in one workflow.

> **Important:** AskAbhi is an educational planning tool, not investment, tax, legal, lending or other regulated financial advice. All forecasts depend on assumptions and data quality. Results are not guarantees. Verify financial data, rates, prices, fees and assumptions independently.

---

### 📑 Hackathon Deliverables & Quick Links
- 📘 **[Comprehensive Project Report (PROJECT_REPORT.md)](PROJECT_REPORT.md)** — Detailed 13-section technical report, problem understanding, mathematical modeling, test suite results, and architectural specifications.
- 🎨 **[Visual Guide & Design Tokens (VISUAL_GUIDE.md)](VISUAL_GUIDE.md)** — Design tokens, color palette, typography, and UI specs.
- 📊 **[Build & QA Status (BUILD_STATUS.md)](BUILD_STATUS.md)** — Verification results (161 passed, 1 skipped, 1 xfailed).
- 🖥️ **[Interactive Pitch Slides](AskAbhi360_Presentation.html)** & **[PowerPoint Deck](AskAbhi360_F02_Presentation.pptx)**.

---

## 📸 Visual Showcase

| Command Centre Dashboard | UPI Payments & Bills |
| :---: | :---: |
| ![Command Centre Dashboard](docs/screenshots/01_dashboard_command_center.png) | ![UPI Payments Interface](docs/screenshots/02_upi_payments_interface.png) |
| **Multi-Goal Stochastic Planning** | **"Can I Afford It?" Arbiter** |
| ![Multi-Goal Planning](docs/screenshots/03_goals_multi_planning.png) | ![Can I Afford It](docs/screenshots/04_can_i_afford_it_decision.png) |
| **Glass-Box Financial Copilot** | **Clean Financial Analytics** |
| ![AskAbhi AI Copilot](docs/screenshots/05_askabhi_ai_copilot.png) | ![Clean Financial Analytics](docs/screenshots/06_dashboard_clean_overview.png) |

---

## Visual identity: AskAbhi 360

The app uses **Neo-Mint Noir + UPI-first navigation**: near-black surfaces, light-green/lime accents, controlled glow, a familiar payment-app structure (transfer money, recharge and bills, people, recent activity, financial shortcuts), readable dark-mode charts, responsive layouts, and the original locally bundled owl mascot, **Abhi**. Typography uses DM Sans for the interface, Space Grotesk for display headings and key figures, and JetBrains Mono for technical values, with system-font fallbacks. Google Fonts are an optional enhancement; the core UI does not depend on them. The green-accent owl and wordmark are stored in `assets/` and require no network connection. See `VISUAL_GUIDE.md` for colour and typography tokens.

The **Home** page now opens directly into the app instead of a blocking onboarding/marketing screen. It presents transfer shortcuts, bill categories, recent people, a financial overview, recent transactions and goal cards. **Pay & UPI** provides UPI ID, bank-transfer, self-transfer, QR-preview, bill-preview, request and history journeys; it stores only local demo previews. It does not send money, generate a live UPI collect request, or claim a payment succeeded. Production payments need an authorised payment integration and a reliable status verification mechanism. Live account connectivity remains a roadmap item; imported and synthetic records are labelled clearly.

## What is built into this project

### Mandatory F-02 capabilities

- Income, spending, savings/assets, outstanding liabilities, inflation and goal time horizons.
- Add/edit/remove goals, rank priorities, select target dates and amounts, model cash or loan funding, and specify minimum acceptable funding.
- Change income, expenses, inflation, market assumptions, target dates and unexpected expenses; compare alternatives using common random draws.
- Calculate goal-feasibility probabilities, Monte Carlo standard errors, funding shortfalls, projected net worth, liquidity and target timing.
- Explain trade-offs when goals compete for finite cash flow.

### Faculty requirements

1. **Behaviour analysis:** merchant/category classification, recurring items, subscriptions, payday burst, weekend ratio, month-end squeeze, lifestyle trend and stated-versus-observed savings gap.
2. **Irregular analysis:** income coefficient of variation, lean months, P20 planning income for irregular earners, and estimated monthly reserve for lumpy expenses.
3. **Assets and liabilities:** editable financial records, net worth, liquidity classes, locked assets, penalty assets, loans, EMIs and credit-card debt.
4. **Goal setting and prioritisation:** create/edit goals and compare goal priorities/deadlines.
5. **Planned vs unplanned spending:** recurring/fixed versus variable one-off estimates with a compound-Poisson shock model.
6. **Discuss analysis:** deterministic, offline rule-based copilot with evidence-backed calculation tools. An optional OpenAI-compatible phrasing adapter can be enabled separately.

### Differentiating decision features

- **Can I Afford It?** Compare purchase cash funding, loans, EMI burden and the effect on other goals.
- **Rupee-to-Days Leak Detector:** re-simulate selected discretionary cuts on identical random draws.
- **Money Time Machine:** compare stated, behaviour-based and improved-savings projections.
- **Payday Autopilot / Safe-to-Spend:** allocate available income to obligations, essentials, reserve and goal contributions.
- **Cash-Crunch Radar:** estimate the daily balance path, first configured danger date and obligation clusters.
- **What Matters:** sensitivity comparison for the goal's assumptions.
- **Chaos Monkey:** a bounded, heuristic reverse stress search and standard stress report card.
- **Repair Lab:** candidate repairs evaluated on common random numbers. The engine never claims a target is reached unless its calculated result reaches it.
- **Conflict map, life events, guardrails, debt/invest/buffer arbiter, household approximation and backtesting.**
- **Glass-box Copilot:** local intent handling, evidence trails and a numerical guard for optional LLM phrasing.
- **HTML report and Presenter Mode / Judge Challenge.**

AskAbhi is not claiming that spend trackers or Monte Carlo financial planners are new. Its intended differentiation is the *combination* of transaction reconciliation, a behaviour twin, competing-goal simulation, reverse stress testing, same-random-draw repair verification, and an evidence-backed copilot.

## Maturity labels — be truthful in the demo

- **BUILT:** local CSV ingestion, classification/reconciliation, behavioural model, assets/liabilities, financial calculation engine, synthetic personas, simulations, decision tools and offline copilot.
- **SIMULATED:** Arjun and Meera transaction histories stand in for bank/UPI records. They are synthetic and must never be presented as live accounts.
- **ROADMAP:** real bank/UPI integrations through supported consent-based financial-data partners; production LLM service at scale; regional languages, hardened multi-user infrastructure and partner integrations.

To support managed Windows environments where the Arrow/PyArrow DLL can be blocked by Application Control, tabular views and edit forms use escaped HTML tables and native Streamlit controls rather than `st.dataframe`/`st.data_editor`. This avoids the Arrow renderer path that triggered the reported crash.

This ZIP does **not** contain a live bank or UPI connection. The UI should not imply that it does. Direct account connections depend on partner participation, consent, security reviews and provider-specific APIs. Uploads/templates are the reliable offline fallback.

## Architecture

```text
Bank / UPI data exports / statements / demo personas
                       |
                       v
          Validation + reconciliation
     duplicate removal / own-transfer handling
      card payment and SIP double-count prevention
                       |
                       v
         Transaction intelligence + review queue
                       |
                       v
             Shared financial profile
    behaviour / irregular income / assets / liabilities
                       |
                       v
          Multi-goal F-02 decision engine
     inflation / cash flow / priorities / liabilities
                       |
                       v
       Simulation + affordability + stress test
                       |
                       v
       Repair + sensitivity + resilience assessment
                       |
             +---------+---------+
             |                   |
             v                   v
   Streamlit interface      Offline Copilot
   charts / proof drawers   optional LLM phrasing
             |                   |
             +---------+---------+
                       v
             Evidence-backed decisions
```

Financial calculations live in `core/` and do not import Streamlit. UI/session state lives in `ui/`. `config.py` centralises numerical assumptions. NumPy's seeded `default_rng` creates a `Draws` object; paired simulations reuse it and show its fingerprint.

## Quick start

Python 3.10–3.12 is the target runtime.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

### macOS / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. Select **Use sample person** to work offline with Arjun, or choose Meera for irregular income. `?skip=1` can bypass onboarding for a demo run.

## Test and smoke check

```bash
python -m compileall -q .
python -m pytest -q
python scripts/smoke.py
```

The full suite tests pure financial logic without requiring Streamlit. A UI smoke test is attempted only when the installed Streamlit testing API is available. Network integration is not required for the test suite.

## 90-second demo script

1. **0–10 seconds — Problem:** “AskAbhi plans on what the user actually does with money, not only what they intend to do.” Show the BUILT / SIMULATED / ROADMAP labels.
2. **10–25 seconds — Understand:** select Arjun and show transaction review, behaviour insights, assets/liabilities, reconciled card payments and SIP contributions.
3. **25–40 seconds — Pay and decide:** preview a clearly labelled demo payment in Pay & UPI, then open Can I Afford It? and model a ₹4.5 lakh BMW-class bike. No real payment is sent.
4. **40–55 seconds — F-02:** change a goal deadline or priority, then compare Plan A and B on the same random draws. Show required savings, feasibility and trade-offs.
5. **55–70 seconds — Break it:** introduce a medical expense or income loss. Run Chaos Monkey or the stress report and show the goal-risk change.
6. **70–82 seconds — Fix it:** open Repair Lab, show repair candidates, the before/after probabilities and identical fingerprint.
7. **82–90 seconds — Trust:** ask the offline Copilot “Why am I unable to save enough for my BMW bike even though my salary is good?” Show its evidence and explain that outputs are estimates, not promises.

## Assumptions that matter most

1. Transaction descriptions and imported records are complete enough to estimate behaviour; missing history weakens the result.
2. Inflation, income growth, asset returns, volatility, job-loss probability and shock severities are illustrative assumptions, not predictions.
3. Category classification and recurring-payment detection require review; a payment to a jeweller does not automatically prove the user acquired an asset.
4. Vehicle on-road cost, lender rates, fees, prepayment charges, card interest and tax treatment must be verified. Tax fields are disabled placeholders; no Indian tax rule is inferred.
5. Simulation output depends on its model structure. A probability is conditional on the stated assumptions and is not a guarantee or a regulated rating.

The application does not adjust dates for weekends or holidays. Long-horizon forecasts (especially beyond 15 years) are highly sensitive to assumptions and should be treated cautiously. Fewer than 12 months of transactions weakens seasonal and unplanned-event estimates; under three months is especially insufficient. AskAbhi cannot infer a structural job/business change that has not appeared in historical data.

## Privacy and AI

The default copilot works offline with a rule-based intent router and the deterministic engine. The optional adapter uses `ASKABHI_LLM_API_KEY` (the previous `KAVACH_LLM_API_KEY` is accepted for compatibility) and may send aggregate result evidence to an OpenAI-compatible endpoint; it is off unless configured. API billing is separate from ChatGPT subscriptions. Review deployment data handling, logging, retention, access controls and consent before any real-user rollout. Never upload raw personal transaction descriptions to an LLM by default.

## Startup roadmap

1. **Core pilot:** validate data quality, financial calculations, model explanations and user comprehension with consenting test users.
2. **Account connections:** integrate supported consent-based financial-data partners; implement revocation, least privilege, audit and secure storage.
3. **Personalisation:** improve classification review, irregular-income models, local-language support and transparent goal recommendations.
4. **Distribution:** explore a free tier, employer financial-wellness benefits, white-label resilience reports for financial institutions and an advisor-support workspace.
5. **Governance:** security/privacy review, independent model validation, monitoring, user recourse and legally reviewed product claims.

Investment advice in India may require appropriate registration and compliance. AskAbhi is positioned here as educational financial planning and decision support; the team must obtain legal/regulatory advice before selling any regulated advice, recommendations or intermediary service.

## AI-assistance disclosure

AI tools assisted with drafting and generating code and tests. The team must review, run and understand the implementation before presenting or deploying it, and must be able to explain the financial formulas, model assumptions, limitations and test results to the jury.

## Six-slide pitch outline

1. **The problem:** People have competing financial goals, irregular cash flow and unexpected commitments; a static budget does not show whether a plan survives real life.
2. **AskAbhi 360:** A financial decision system that connects transaction understanding, assets/liabilities, goal planning and uncertainty-aware simulations.
3. **What makes it different:** The behaviour twin and reconciliation layer feed one shared planning engine; Chaos Monkey finds weaknesses, and Repair Lab re-tests candidate fixes using identical random draws.
4. **Live demonstration:** Start with Arjun's synthetic data, ask whether the ₹4.5 lakh BMW-class bike is affordable, and show its effect on education and home goals.
5. **Proof and trust:** Show a stress scenario, a repair comparison, the draw fingerprint, formula/assumption evidence and honest limitations.
6. **Business and roadmap:** Begin as educational financial planning; later evaluate supported consent-based account connections, privacy/security assurance, employer wellness and institution-facing reports. Do not claim live integrations in the demo.

## Questions judges are likely to ask

**Is this just another expense tracker?** No. Transaction categorisation is an input. The core workflow connects actual behaviour to competing goals, simulates uncertainty, searches for plan-breaking shocks and tests repairs on the same random draws.

**What exactly is AI doing?** The offline copilot routes questions to deterministic financial tools and explains their results. Optional OpenAI API integration only phrases supplied evidence; it is disabled by default and numerical claims are checked against that evidence.

**Are Google Pay, PhonePe and bank accounts connected live?** No. Demo transactions are synthetic and CSV import is supported. Live financial connections are roadmap work dependent on suitable consent-based partners and security reviews.

**How do you prevent double-counting?** Reconciliation identifies own-account transfers, card settlements and SIP contributions so transfers are not treated as new consumption and SIPs are treated as savings. Classification remains reviewable.

**Are the probabilities predictions or guarantees?** Neither. They are model-based estimates conditional on supplied data and assumptions. The app reports uncertainty and highlights weak history and sensitivity to assumptions.

**How are repairs proven?** Candidate plans are re-simulated using the same random draws, so before-and-after differences are not caused by a new set of random numbers. Results remain model-dependent, not guarantees.

**Can this provide regulated investment advice?** This prototype is positioned as educational planning and decision support. Legal and regulatory review is required before offering any regulated advice or financial service.

**What is the biggest limitation?** Synthetic data validates mechanics, not real-world accuracy. Short histories, unobserved obligations, structural income changes and long-range return/inflation assumptions can materially affect results.
