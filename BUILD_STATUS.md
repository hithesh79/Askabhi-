# AskAbhi 360 — UPI-First UI Update & QA Status

## Shipped in this update
- Home opens straight into the app's working command centre rather than a blocking intro screen.
- UPI-app-inspired layout: AskAbhi brand bar, Transfer Money shortcuts, Recharge & Bills, sample people, recent transactions, money overview, Abhi's insight and goal cards.
- Black / forest-black surfaces, light-green and mint accents, restrained glow, DM Sans / Space Grotesk / JetBrains Mono with fallbacks, and the bundled Abhi owl.
- Pay & UPI now includes Pay, Recharge & Bills, Request and Activity journeys, with UPI ID / bank / self-transfer / QR-preview paths and locally recorded demo previews. Home shortcuts select the relevant payment journey.
- All `st.dataframe` and `st.data_editor` calls were replaced with escaped HTML tables and native-widget editors to avoid the reported Windows Application Control block on `pyarrow.lib`.
- Existing financial engines and page routes retained.

## Automated verification
- `python -m compileall -q .`: passed.
- `python -m pytest -q`: **161 passed, 1 skipped, 1 xfailed**.
- `python scripts/smoke.py`: passed for Arjun and Meera; deterministic local pipeline completed in approximately 0.26 seconds in this environment.
- Static search: no remaining `st.dataframe` or `st.data_editor` calls.
- The conditional UI AppTest remains skipped because Streamlit is not installed in the build environment. Live browser rendering therefore still needs confirmation on the user's computer.
- The expected failure documents a real model limitation: two months of history cannot reveal an unseen structural income break.

## Payment and data status
Synthetic personas and imported CSV files are supported. The payment interface creates local demo previews only; no real UPI transfer, live bank feed, QR decoding, or live payment confirmation is active. Production UPI requires the appropriate authorised provider integration and trusted payment-status verification.
