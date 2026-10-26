"""Standalone presentation generator for AskAbhi 360 Problem Statement F-02.
Does NOT touch or affect any application code.
Run: python create_pptx.py
Generates: AskAbhi360_F02_Presentation.pptx
"""
import sys

def main():
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.enum.text import PP_ALIGN
        from pptx.dml.color import RGBColor
    except ImportError:
        import subprocess
        print("Installing python-pptx library to build .pptx file...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx"])
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.enum.text import PP_ALIGN
        from pptx.dml.color import RGBColor

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5) # 16:9 Widescreen

    COLOR_BG = RGBColor(11, 22, 25)       # #0B1619
    COLOR_TEAL = RGBColor(58, 175, 169)   # #3AAFA9
    COLOR_DARK_TEAL = RGBColor(43, 122, 120) # #2B7A78
    COLOR_WHITE = RGBColor(254, 255, 255) # #FEFFFF
    COLOR_MUTED = RGBColor(142, 174, 171) # #8EAEAB
    COLOR_CARD = RGBColor(23, 37, 42)     # #17252A

    blank_layout = prs.slide_layouts[6]

    slides_data = [
        {
            "badge": "✦ HACKATHON PITCH DECK · PROBLEM STATEMENT F-02",
            "title": "AskAbhi 360: Multi-Goal Financial Planning Under Uncertainty",
            "sub": "A deterministic decision-support copilot navigating competing life priorities, stochastic market volatility, and life shocks.",
            "points": [
                ("🎯 Multi-Goal Priority Engine", "Sequential waterfall allocation: Living Obligations → Emergency Floor → Hard Goals → Flexible Milestones."),
                ("🎲 Stochastic Monte Carlo Core", "2,000 correlated simulations under Common Random Numbers (CRN) with category-specific stochastic inflation."),
                ("🛡️ Grounded AI Copilot (Abhi 🚀)", "Zero hallucinated balances. Verifiable proofs and mathematical audit trails for every recommendation.")
            ]
        },
        {
            "badge": "PROBLEM DECONSTRUCTION",
            "title": "The Real-World Reality of Problem Statement F-02",
            "sub": "Why traditional financial planning spreadsheets and generic AI chatbots fail.",
            "points": [
                ("❌ Why Spreadsheets Fail", "Spreadsheets assume flat 8% returns and flat 6% inflation, ignoring market downturns and higher education (9%) or medical (11%) inflation drift."),
                ("❌ Why LLMs & Chatbots Fail", "Generic LLMs invent savings totals and lack stochastic mathematical cores, producing unverifiable advice with zero banking interactivity."),
                ("💡 The F-02 Core Requirement", "Users must be able to evaluate competing goals, modify assumptions, simulate life shocks, and understand consequences over time.")
            ]
        },
        {
            "badge": "SYSTEM ARCHITECTURE",
            "title": "AskAbhi 360: Three-Tier Grounded Architecture",
            "sub": "Clean separation between mathematical deterministic computation and conversational guidance.",
            "points": [
                ("🖥️ Tier 1: Interactive UI Shell", "Fintech Command Center with 90-day cash radar, Value/Turbo Mode toggle, touch-friendly wallet, and sound effects."),
                ("🚀 Tier 2: AskAbhi AI Copilot", "Empathetic companion powered by offline deterministic tool routing, displaying verifiable proofs and mathematical evidence trails."),
                ("⚙️ Tier 3: Deterministic Math Core", "2,000-draw correlated Monte Carlo, Priority Arbiter, Goal Conflict Matrix, Chaos Stress Testing, and Behaviour Twin.")
            ]
        },
        {
            "badge": "MULTI-GOAL OPTIMIZATION",
            "title": "Priority Arbiter & Goal Conflict Sensitivity Matrix",
            "sub": "Resolving simultaneous competing demands on finite monthly income.",
            "points": [
                ("🌊 Capital Allocation Waterfall", "1. Contractual EMIs → 2. Essential Living Spend → 3. Emergency Reserve Floor → 4. Hard Goals (P1) → 5. Flexible Goals (P2/P3)."),
                ("⚖️ Goal Conflict Sensitivity Matrix", "Calculates exact cross-elasticities: funding Goal A with an extra ₹5,000/mo reduces Goal B feasibility by 14 pp and delays it by 3.2 months."),
                ("🔍 Visible Trade-Offs", "Eliminates surprise shortfalls by demonstrating mathematical sacrifices before any major spending commitment.")
            ]
        },
        {
            "badge": "PLANNING UNDER UNCERTAINTY",
            "title": "2,000-Draw Stochastic Monte Carlo Simulation Core",
            "sub": "Simulating correlated asset returns and divergent category inflation under Common Random Numbers.",
            "points": [
                ("📈 Correlated Asset Paths", "Cash, Debt, Equity, Gold, and Real Estate modeled via Geometric Brownian Motion with correlated covariance matrices."),
                ("🏷️ Category-Specific Inflation", "Higher Education (8.5%-10%) and Healthcare (9%-11.5%) modeled with accelerated stochastic drift versus CPI (5.5%)."),
                ("🎯 Common Random Numbers (CRN)", "Plan comparisons run on identical random seed draws, guaranteeing differences reflect pure decision quality rather than sampling noise.")
            ]
        },
        {
            "badge": "DECISION SUPPORT ENGINE",
            "title": "\"Can I Afford It?\" Purchase Decision Support",
            "sub": "Evaluating major purchases (e.g. ₹4.5 Lakh BMW Motorcycle) against active long-term life plans.",
            "points": [
                ("🛵 Real Scenario Testing", "Simulates cash vs 3-year loan EMI (₹11,215/month) on identical reproducible random draws."),
                ("🔍 The 3 Golden Criteria", "1. Liquid emergency floor remains intact; 2. Debt-to-income remains under safe 40% threshold; 3. Core life goals stay feasible."),
                ("🛠️ Actionable Levers", "Recommends exact adjustments (e.g. extend tenure by 12 months or trim weekend leaks by ₹3,500) to keep long-term home goals on track.")
            ]
        },
        {
            "badge": "STRESS TESTING & RECOVERY",
            "title": "Chaos Money & Algorithmic Non-Worsening Plan Repair",
            "sub": "Testing plausible life shocks and generating automated recovery plans without human trial-and-error.",
            "points": [
                ("⚡ Plausible Life Shocks", "Simulates 3–6 month job loss, 20% annual salary cuts, and sudden ₹5,00,000 medical emergency outflows."),
                ("🛠️ Non-Worsening Plan Repair", "Algorithmic optimizer rebalances high-interest debt and temporarily pauses soft goals while protecting core retirement and education."),
                ("📈 Restored Feasibility", "Recovers plan probability from 42% back to 85%+ on identical random draws without manual trial-and-error.")
            ]
        },
        {
            "badge": "BEHAVIOURAL ECONOMICS",
            "title": "Behaviour Twin & Rupee-to-Days Leak Analytics",
            "sub": "Mining real banking and UPI statements to reconcile stated budgets with actual debit habits.",
            "points": [
                ("🧠 Behavioural Diagnostics", "Extracts Weekend Spending Multiplier (1.85x), Payday Burst Splurge (38% in first 5 days), and Month-End Cash Squeeze."),
                ("📈 Lifestyle Creep Slope", "Calculates upward drift rate (+₹1,240/month) and identifies unviewed recurring subscriptions."),
                ("⏱️ Rupee-to-Days Leak Detector", "Translates discretionary spending directly into timeline gains: trimming ₹3,200/mo on food delivery recovers 54 days on home goal!")
            ]
        },
        {
            "badge": "OPERATING STRATEGY",
            "title": "Strategy Modes: 🛡️ Value Mode vs 🚀 Turbo Mode",
            "sub": "Empowering users to toggle between defensive resilience and aggressive milestone acceleration.",
            "points": [
                ("🛡️ Value Mode (Prudent / Defensive)", "Strict 6-month liquid cushion, +25% monthly savings rate, relaxed daily spend, and guaranteed debt safety under severe volatility."),
                ("🚀 Turbo Mode (Goal Accelerator)", "3-month cushion, +40% savings velocity, 20% trim on non-priority leaks redirected to goals, achieving milestones 6–9 months sooner!"),
                ("⚡ Real-Time Recalculation", "One-click toggle instantly shifts all dashboard recommendations, advice feeds, and goal timelines.")
            ]
        },
        {
            "badge": "CONCLUSION & HACKATHON IMPACT",
            "title": "How AskAbhi 360 Delivers the F-02 Mandate",
            "sub": "A production-grade, interactive, decision-support solution for multi-goal financial life.",
            "points": [
                ("🏆 Complete Problem Coverage", "Handles competing goals, stochastic uncertainty, life shocks, trade-off communication, and behavioural spending reality."),
                ("🚀 Zero Hallucinations Guarantee", "Deterministic Python math engine guarantees 100% auditability and verifiable proofs."),
                ("🎯 Production-Ready FinTech UX", "PhonePe-style UPI rails, vector QR scanner, Web Audio API sound effects, celebratory payment animations, and responsive layout.")
            ]
        }
    ]

    for data in slides_data:
        slide = prs.slides.add_slide(blank_layout)

        # Background shape
        bg = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height) # msoShapeRectangle
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.color.rgb = COLOR_BG

        # Badge
        badge_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.4))
        tf_b = badge_box.text_frame
        tf_b.word_wrap = True
        p_b = tf_b.paragraphs[0]
        p_b.text = data["badge"]
        p_b.font.size = Pt(11)
        p_b.font.bold = True
        p_b.font.color.rgb = COLOR_TEAL

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.9), Inches(11.7), Inches(0.8))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = data["title"]
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_WHITE

        # Subtitle
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.7), Inches(0.5))
        tf_s = sub_box.text_frame
        tf_s.word_wrap = True
        p_s = tf_s.paragraphs[0]
        p_s.text = data["sub"]
        p_s.font.size = Pt(13)
        p_s.font.color.rgb = COLOR_MUTED

        # 3 Content Cards
        card_w = Inches(3.7)
        card_h = Inches(4.3)
        gap = Inches(0.3)
        start_x = Inches(0.8)
        start_y = Inches(2.3)

        for i, (head, body) in enumerate(data["points"]):
            x = start_x + i * (card_w + gap)
            c_shape = slide.shapes.add_shape(1, x, start_y, card_w, card_h)
            c_shape.fill.solid()
            c_shape.fill.fore_color.rgb = COLOR_CARD
            c_shape.line.color.rgb = COLOR_DARK_TEAL
            c_shape.line.width = Pt(1.5)

            tb = slide.shapes.add_textbox(x + Inches(0.2), start_y + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            
            p_h = tf.paragraphs[0]
            p_h.text = head
            p_h.font.size = Pt(15)
            p_h.font.bold = True
            p_h.font.color.rgb = COLOR_TEAL
            p_h.space_after = Pt(12)

            p_body = tf.add_paragraph()
            p_body.text = body
            p_body.font.size = Pt(12)
            p_body.font.color.rgb = COLOR_WHITE
            p_body.line_spacing = 1.3

        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.8), Inches(11.7), Inches(0.4))
        tf_f = footer_box.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = "AskAbhi 360 · Grounded Multi-Goal Decision Support Engine · Live at http://localhost:8508"
        p_f.font.size = Pt(10)
        p_f.font.color.rgb = COLOR_MUTED

    output_file = "AskAbhi360_F02_Presentation.pptx"
    prs.save(output_file)
    print(f"Presentation saved successfully as '{output_file}'!")

if __name__ == "__main__":
    main()
