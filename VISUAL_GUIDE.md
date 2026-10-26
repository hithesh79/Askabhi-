# AskAbhi 360 — Neo-Mint UPI-First UI Guide

## Design direction
A familiar, UPI-first payment-app workflow with original AskAbhi branding: a top app bar, transfer-money shortcuts, recharge and bill categories, people/contact shortcuts, recent activity, a financial overview, goal cards, and Abhi's contextual insight panel. The layout follows established payment-app interaction patterns without using PhonePe's logo, copy, or proprietary assets.

## Palette
- App background: `#070B09`
- Raised background: `#0A110D`
- Card: `#101A13`
- Border: `#253A2B`
- Primary light-green accent: `#B7FF72`
- Secondary mint: `#71F2A2`
- Main text: `#F0F7EF`
- Muted text: `#A1B4A3`
- Warm amber: `#F5D66E`
- Success: `#83F0A5`
- Warning: `#FFD166`
- Danger: `#FF8585`

## Typography
- DM Sans for interface text.
- Space Grotesk for headings and key financial figures.
- JetBrains Mono for formulas and technical fingerprints.
- System-font fallback keeps the interface readable if network fonts are unavailable.

## Main app layout
1. App bar with AskAbhi 360 brand, profile and local/demo status.
2. Transfer money: Scan QR preview, UPI ID, bank transfer, self transfer.
3. Recharge and bill-payment categories.
4. Money overview with net worth, liquid funds, income and estimated commitments.
5. Recent transaction list with search.
6. Abhi's insight and financial shortcuts.
7. Financial goal cards with modelled feasibility and target dates.

## Interaction and safety
- Home shortcuts navigate to the relevant Pay & UPI workflow.
- UPI, bank, self-transfer and bill screens create clearly labelled local previews only. They do not move money or claim a payment succeeded.
- No UPI PIN, OTP or bank password is collected. Live payments require an authorised integration and trusted status verification.
- Abhi is the original owl mascot; use it for welcome/insight/Copilot moments rather than decorating every data table.
- Animations are restrained and disabled for `prefers-reduced-motion`.

## Windows compatibility
Tabular results are rendered as escaped HTML and editable financial records use native widgets, avoiding `st.dataframe` and `st.data_editor`, which triggered an Arrow/PyArrow DLL policy error in the reported Windows environment. The actual live launch should still be retested on the user's computer.
