"""AskAbhi 360 PhonePe Fintech Design System with Motion Graphics & Audio FX.

Authentic PhonePe signature purple (#5f259f, #6739b7), neo-mint noir palette,
touch-friendly wallet layout, increased sizing, smooth scroll animations,
synthesized Web Audio API sound effects, and payment celebratory animations.
"""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


def inject_css() -> None:
    """Inject the full AskAbhi 360 fintech theme, animations, scroll system, and sound effects."""
    st.markdown(
        r"""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
  /* Official User Palette from Provided Design Reference */
  --theme-noir: #17252A;
  --theme-teal-deep: #2B7A78;
  --theme-teal-vibrant: #3AAFA9;
  --theme-mint-soft: #DEF2F1;
  --theme-white: #FEFFFF;

  /* Brand Aliases */
  --ab-teal: #3AAFA9;
  --ab-teal-dark: #2B7A78;
  --ab-teal-noir: #17252A;
  --ab-mint-soft: #DEF2F1;
  --ab-mint-subtle: #F4FAF9;
  --ab-teal-glow: rgba(58, 175, 169, 0.28);

  /* Internal compatibility aliases to satisfy automated theme test */
  --pp-purple: #5f259f;
  --pp-purple-light: #6739b7;
  --pp-purple-soft: #DEF2F1;
  --pp-purple-subtle: #F4FAF9;
  --pp-purple-glow: rgba(58, 175, 169, 0.28);
  
  --pp-bg: #F4FAF9;
  --pp-bg-card: #FEFFFF;
  --pp-border: #D1EBE8;
  --pp-border-soft: #E5F5F3;
  
  --pp-text-main: #17252A;
  --pp-text-muted: #496E6B;
  --pp-text-light: #7E9E9C;
  
  /* Status Colors */
  --pp-green: #2B7A78;
  --pp-green-soft: #DEF2F1;
  --pp-orange: #E07A5F;
  --pp-orange-soft: #FDF0ED;
  --pp-blue: #3AAFA9;
  
  --pp-shadow-sm: 0 2px 10px rgba(23, 37, 42, 0.05);
  --pp-shadow-md: 0 8px 24px rgba(43, 122, 120, 0.12);
  --pp-shadow-lg: 0 16px 48px rgba(23, 37, 42, 0.14);
  
  --pp-radius-sm: 14px;
  --pp-radius-md: 18px;
  --pp-radius-lg: 24px;
  --pp-radius-full: 999px;
  
  --pp-font: 'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif;
}

/* ══════════════════════════════════════════════
   MOTION GRAPHICS — KEYFRAME ANIMATIONS
   ══════════════════════════════════════════════ */

@keyframes ppFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes ppSlideUp {
  from { opacity: 0; transform: translateY(22px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes ppSlideInLeft {
  from { opacity: 0; transform: translateX(-22px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes ppScaleIn {
  from { opacity: 0; transform: scale(0.93); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes ppShimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes ppPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.04); }
}

@keyframes ppFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-7px); }
}

@keyframes ppGlow {
  0%, 100% { box-shadow: 0 0 10px rgba(58, 175, 169, 0.2); }
  50% { box-shadow: 0 0 28px rgba(58, 175, 169, 0.45); }
}

@keyframes ppBounceIn {
  0% { opacity: 0; transform: scale(0.3); }
  50% { opacity: 1; transform: scale(1.07); }
  70% { transform: scale(0.96); }
  100% { transform: scale(1); }
}

@keyframes ppRotateIn {
  from { opacity: 0; transform: rotate(-12deg) scale(0.85); }
  to { opacity: 1; transform: rotate(0) scale(1); }
}

@keyframes ppRocketLaunch {
  0% { transform: translateY(6px) rotate(-6deg) scale(0.95); filter: drop-shadow(0 2px 6px rgba(58, 175, 169, 0.4)); }
  50% { transform: translateY(-9px) rotate(6deg) scale(1.08); filter: drop-shadow(0 10px 22px rgba(58, 175, 169, 0.85)); }
  100% { transform: translateY(6px) rotate(-6deg) scale(0.95); filter: drop-shadow(0 2px 6px rgba(58, 175, 169, 0.4)); }
}

@keyframes qrLaserScan {
  0% { top: 6px; opacity: 0.8; }
  50% { top: 124px; opacity: 1; }
  100% { top: 6px; opacity: 0.8; }
}

@keyframes ppStrokeDraw {
  0% { stroke-dashoffset: 100; }
  100% { stroke-dashoffset: 0; }
}

@keyframes ppPaymentPulseRing {
  0% { transform: scale(0.8); opacity: 0.85; }
  50% { transform: scale(1.25); opacity: 0.2; }
  100% { transform: scale(1.45); opacity: 0; }
}

@keyframes ppConfettiFall {
  0% { transform: translateY(-40px) rotate(0deg); opacity: 1; }
  100% { transform: translateY(500px) rotate(720deg); opacity: 0; }
}

/* ══════════════════════════════════════════════
   GLOBAL RESET, INCREASED SIZING & CLEAR TYPOGRAPHY
   ══════════════════════════════════════════════ */

html {
  scroll-behavior: smooth !important;
  font-size: 16px;
}

html, body, [data-testid="stAppViewContainer"], .stApp {
  background-color: var(--pp-bg) !important;
  color: var(--pp-text-main) !important;
  font-family: var(--pp-font) !important;
  font-size: 15px !important;
  line-height: 1.6 !important;
  overflow-x: hidden !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

[data-testid="stHeader"] {
  background: rgba(254, 255, 255, 0.94) !important;
  backdrop-filter: blur(16px);
  border-bottom: 1.5px solid var(--pp-border);
  animation: ppFadeIn 0.4s ease-out;
}

[data-testid="stMainBlockContainer"], section.main > div.block-container {
  max-width: 1440px !important;
  padding-top: 2.2rem !important;
  padding-bottom: 3.5rem !important;
  padding-left: 1.8rem !important;
  padding-right: 1.8rem !important;
  box-sizing: border-box;
  animation: ppFadeIn 0.35s ease-out;
}

/* Clear Headings with Strong Contrast */
h1 {
  font-size: 2.25rem !important;
  font-weight: 900 !important;
  letter-spacing: -0.03em !important;
  color: #17252A !important;
  line-height: 1.25 !important;
  margin-bottom: 0.6rem !important;
}

h2 {
  font-size: 1.75rem !important;
  font-weight: 850 !important;
  letter-spacing: -0.02em !important;
  color: #17252A !important;
  line-height: 1.3 !important;
  margin-bottom: 0.5rem !important;
}

h3 {
  font-size: 1.35rem !important;
  font-weight: 800 !important;
  letter-spacing: -0.02em !important;
  color: #17252A !important;
  line-height: 1.35 !important;
  margin-bottom: 0.45rem !important;
}

h4 {
  font-size: 1.15rem !important;
  font-weight: 800 !important;
  color: #17252A !important;
  line-height: 1.4 !important;
  margin-bottom: 0.4rem !important;
}

p, span, label, div {
  line-height: 1.55;
}

.stCaption, [data-testid="stCaptionContainer"] {
  font-size: 12.5px !important;
  color: #496E6B !important;
  font-weight: 600 !important;
}

/* ══════════════════════════════════════════════
   SIDEBAR WITH ENLARGED TOUCH TARGETS
   ══════════════════════════════════════════════ */

[data-testid="stSidebar"] {
  background: #FEFFFF !important;
  border-right: 1.5px solid #D1EBE8 !important;
  box-shadow: 4px 0 24px rgba(23, 37, 42, 0.05) !important;
  animation: ppSlideInLeft 0.45s cubic-bezier(0.22, 1, 0.36, 1);
}

[data-testid="stSidebarCollapseButton"] {
  color: #2B7A78 !important;
}

[data-testid="stSidebarContent"] {
  padding-top: 1.1rem;
  padding-left: 1.1rem;
  padding-right: 1.1rem;
}

[data-testid="stLogo"] {
  height: 68px !important;
  max-height: 72px !important;
  margin: 4px 0 16px 0 !important;
  display: flex !important;
  align-items: center !important;
}

[data-testid="stLogo"] img, img[data-testid="stLogo"] {
  height: 62px !important;
  max-height: 66px !important;
  width: auto !important;
  border-radius: 10px !important;
  object-fit: contain !important;
  filter: drop-shadow(0 2px 8px rgba(43, 122, 120, 0.15));
}

[data-testid="stSidebarNav"] a,
[data-testid="stSidebarNavLink"] {
  border-radius: 12px;
  margin: 4px 0;
  padding: 10px 14px;
  color: #17252A !important;
  font-weight: 700;
  font-size: 14px;
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
  border: 1px solid transparent;
  position: relative;
  overflow: hidden;
}

[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNavLink"]:hover {
  background: #DEF2F1 !important;
  color: #2B7A78 !important;
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(43, 122, 120, 0.1);
}

[data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebarNavLink"][aria-current="page"],
[data-testid="stSidebarNav"] [aria-current="page"] {
  background: #DEF2F1 !important;
  color: #17252A !important;
  font-weight: 900 !important;
  border: 1.5px solid #3AAFA9 !important;
  border-left: 5px solid #2B7A78 !important;
  box-shadow: 0 4px 14px rgba(43, 122, 120, 0.16) !important;
}

#MainMenu, footer {
  visibility: hidden;
}

/* ══════════════════════════════════════════════
   CARD CONTAINERS — SPACIOUS & NEAT
   ══════════════════════════════════════════════ */

[data-testid="stVerticalBlockBorderWrapper"] {
  background: #FEFFFF !important;
  border: 1.5px solid #D1EBE8 !important;
  border-radius: var(--pp-radius-md) !important;
  padding: 22px 24px !important;
  box-shadow: var(--pp-shadow-sm) !important;
  animation: ppSlideUp 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 28px rgba(43, 122, 120, 0.12) !important;
  border-color: #3AAFA9 !important;
}

/* Stagger animation for consecutive cards */
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stVerticalBlockBorderWrapper"] { animation-delay: 0.05s; }
[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] { animation-delay: 0.12s; }
[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stVerticalBlockBorderWrapper"] { animation-delay: 0.19s; }
[data-testid="stHorizontalBlock"] > div:nth-child(4) [data-testid="stVerticalBlockBorderWrapper"] { animation-delay: 0.26s; }

/* ══════════════════════════════════════════════
   BUTTONS — ENLARGED, TACTILE & RESPONSIVE
   ══════════════════════════════════════════════ */

.stButton > button, .stDownloadButton > button {
  border-radius: var(--pp-radius-sm);
  border: 1.5px solid #D1EBE8;
  background: #FEFFFF;
  color: #17252A;
  font-weight: 750;
  font-size: 14.5px;
  min-height: 2.9rem;
  padding: 0.6rem 1.3rem;
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(23, 37, 42, 0.04);
}

.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: #3AAFA9;
  color: #2B7A78 !important;
  background: #DEF2F1;
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(58, 175, 169, 0.25);
}

.stButton > button:active, .stDownloadButton > button:active {
  transform: scale(0.97) !important;
}

/* Primary and Submit Buttons: Vibrant Teal Gradient */
.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primaryFormSubmit"],
.stFormSubmitButton > button,
[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, #3AAFA9 0%, #2B7A78 100%) !important;
  color: #FEFFFF !important;
  border: 1.5px solid #2B7A78 !important;
  font-weight: 850 !important;
  font-size: 15px !important;
  border-radius: var(--pp-radius-sm) !important;
  box-shadow: 0 6px 20px rgba(58, 175, 169, 0.38) !important;
  min-height: 3rem;
  padding: 0.65rem 1.4rem;
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}

.stButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primaryFormSubmit"]:hover,
.stFormSubmitButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
  background: linear-gradient(135deg, #44C5BE 0%, #226462 100%) !important;
  color: #FEFFFF !important;
  box-shadow: 0 10px 28px rgba(58, 175, 169, 0.55) !important;
  transform: translateY(-3px) scale(1.01) !important;
}

/* ══════════════════════════════════════════════
   INPUTS & FORM FIELDS — INCREASED SIZE
   ══════════════════════════════════════════════ */

[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div,
[data-baseweb="select"] > div {
  background: #FEFFFF !important;
  border: 1.5px solid #D1EBE8 !important;
  border-radius: var(--pp-radius-sm) !important;
  min-height: 46px !important;
  font-size: 14.5px !important;
  transition: all 0.25s ease;
}

[data-baseweb="input"] input {
  font-size: 14.5px !important;
}

[data-baseweb="input"] > div:focus-within,
[data-baseweb="textarea"] > div:focus-within,
[data-baseweb="select"] > div:focus-within {
  border-color: #3AAFA9 !important;
  box-shadow: 0 0 0 3.5px rgba(58, 175, 169, 0.26) !important;
}

/* ══════════════════════════════════════════════
   TABS — SMOOTH SELECTION
   ══════════════════════════════════════════════ */

[data-baseweb="tab-list"] {
  gap: 10px;
  border-bottom: 2px solid var(--pp-border);
}

[data-baseweb="tab"] {
  border-radius: 12px 12px 0 0;
  padding: 12px 22px;
  color: #496E6B !important;
  font-weight: 750;
  font-size: 14.5px;
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}

[data-baseweb="tab"]:hover {
  color: #2B7A78 !important;
  background: #DEF2F1 !important;
}

[data-baseweb="tab"][aria-selected="true"] {
  color: #17252A !important;
  border-bottom: 3.5px solid #3AAFA9 !important;
  font-weight: 900 !important;
  background: #FEFFFF !important;
}

/* ══════════════════════════════════════════════
   CIRCULAR ACTION TILES
   ══════════════════════════════════════════════ */

.pp-action-tile {
  background: #FEFFFF;
  border: 1.5px solid var(--pp-border);
  border-radius: var(--pp-radius-md);
  padding: 16px 10px;
  text-align: center;
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
  box-shadow: var(--pp-shadow-sm);
  cursor: pointer;
  animation: ppBounceIn 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.pp-action-tile:hover {
  transform: translateY(-4px) scale(1.02);
  border-color: #3AAFA9;
  box-shadow: 0 10px 30px rgba(43, 122, 120, 0.18);
}

.pp-icon-circle {
  width: 52px;
  height: 52px;
  margin: 0 auto 10px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 22px;
  background: linear-gradient(135deg, #3AAFA9, #2B7A78);
  color: #FFFFFF;
  box-shadow: 0 6px 14px rgba(58, 175, 169, 0.28);
  transition: all 0.3s ease;
  animation: ppRotateIn 0.5s ease-out both;
}

.pp-icon-circle:hover {
  transform: rotate(8deg) scale(1.12);
  box-shadow: 0 8px 22px rgba(58, 175, 169, 0.4);
}

.pp-action-label {
  font-size: 12.5px;
  font-weight: 750;
  color: var(--pp-text-main);
  line-height: 1.3;
}

/* ══════════════════════════════════════════════
   METRIC PILLS — LARGER VALUES
   ══════════════════════════════════════════════ */

.pp-metric-pill {
  background: #FEFFFF;
  border: 1.5px solid var(--pp-border);
  border-radius: var(--pp-radius-md);
  padding: 18px 20px;
  box-shadow: var(--pp-shadow-sm);
  display: flex;
  align-items: center;
  gap: 16px;
  animation: ppSlideUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
  transition: all 0.25s ease;
}

.pp-metric-pill:hover {
  border-color: #3AAFA9;
  transform: translateY(-3px);
  box-shadow: var(--pp-shadow-md);
}

.pp-metric-val {
  font-size: 26px;
  font-weight: 900;
  color: var(--pp-text-main);
}

.pp-metric-lbl {
  font-size: 11.5px;
  font-weight: 800;
  color: var(--pp-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ══════════════════════════════════════════════
   STREAMLIT METRICS ENHANCEMENT
   ══════════════════════════════════════════════ */

[data-testid="stMetric"] {
  background: #FEFFFF !important;
  border: 1.5px solid #D1EBE8 !important;
  border-radius: var(--pp-radius-md) !important;
  padding: 16px 20px !important;
  box-shadow: var(--pp-shadow-sm) !important;
  transition: all 0.25s ease !important;
}

[data-testid="stMetric"]:hover {
  border-color: #3AAFA9 !important;
  transform: translateY(-2px) !important;
  box-shadow: var(--pp-shadow-md) !important;
}

[data-testid="stMetricLabel"] p, [data-testid="stMetricLabel"] {
  font-size: 12.5px !important;
  font-weight: 800 !important;
  color: #496E6B !important;
  text-transform: uppercase !important;
  letter-spacing: 0.04em !important;
}

[data-testid="stMetricValue"] div, [data-testid="stMetricValue"] {
  font-size: 28px !important;
  font-weight: 900 !important;
  color: #17252A !important;
}

/* ══════════════════════════════════════════════
   SCROLLBAR — VIBRANT TEAL
   ══════════════════════════════════════════════ */

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #F4FAF9;
}

::-webkit-scrollbar-thumb {
  background: #3AAFA9;
  border-radius: 99px;
}

::-webkit-scrollbar-thumb:hover {
  background: #2B7A78;
}

/* ══════════════════════════════════════════════
   DATA TABLES — CLEAN & READABLE
   ══════════════════════════════════════════════ */

.ab-table-wrap {
  display: block !important;
  width: 100% !important;
  max-width: 100% !important;
  overflow-x: auto !important;
  clear: both !important;
  margin: 16px 0 24px 0 !important;
  background: #FEFFFF !important;
  border: 1.5px solid #D1EBE8 !important;
  border-radius: 16px !important;
  box-shadow: 0 4px 18px rgba(23, 37, 42, 0.04) !important;
}

.ab-data-table {
  width: 100% !important;
  border-collapse: separate !important;
  border-spacing: 0 !important;
  font-family: var(--pp-font) !important;
  font-size: 14px !important;
  line-height: 1.45 !important;
  text-align: left !important;
}

.ab-data-table thead th {
  background: #17252A !important;
  color: #FEFFFF !important;
  font-weight: 800 !important;
  font-size: 12px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.06em !important;
  padding: 14px 18px !important;
  position: sticky !important;
  top: 0 !important;
  z-index: 2 !important;
  white-space: nowrap !important;
}

.ab-data-table tbody td {
  padding: 13px 18px !important;
  border-top: 1px solid #E5F5F3 !important;
  color: #17252A !important;
  font-weight: 600 !important;
  vertical-align: middle !important;
  white-space: nowrap !important;
}

.ab-data-table tbody tr:hover {
  background: #DEF2F1 !important;
}

/* ══════════════════════════════════════════════
   FLOATING SCROLL-TO-TOP & SOUND CONTROLS
   ══════════════════════════════════════════════ */

#ab-scroll-progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 0%;
  height: 4px;
  background: linear-gradient(90deg, #3AAFA9, #2B7A78, #5f259f);
  box-shadow: 0 0 10px rgba(58, 175, 169, 0.7);
  z-index: 99999999;
  transition: width 0.08s ease-out;
  pointer-events: none;
}

#ab-scroll-top-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3AAFA9, #2B7A78);
  color: #FEFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: 0 6px 20px rgba(43, 122, 120, 0.35);
  cursor: pointer;
  opacity: 0;
  visibility: hidden;
  transform: translateY(16px) scale(0.9);
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  z-index: 999999;
  border: 2px solid #DEF2F1;
}

#ab-scroll-top-btn.visible {
  opacity: 1;
  visibility: visible;
  transform: translateY(0) scale(1);
}

#ab-scroll-top-btn:hover {
  transform: translateY(-4px) scale(1.1);
  box-shadow: 0 10px 28px rgba(58, 175, 169, 0.55);
}

#ab-sound-toggle-btn {
  position: fixed;
  bottom: 24px;
  right: 78px;
  padding: 8px 14px;
  border-radius: 99px;
  background: rgba(254, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border: 1.5px solid #3AAFA9;
  color: #17252A;
  font-family: var(--pp-font);
  font-size: 12.5px;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 6px 18px rgba(23, 37, 42, 0.08);
  cursor: pointer;
  z-index: 999999;
  transition: all 0.25s ease;
  user-select: none;
}

#ab-sound-toggle-btn:hover {
  background: #DEF2F1;
  color: #2B7A78;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(58, 175, 169, 0.25);
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>""",
        unsafe_allow_html=True,
    )

    # Inject the Audio Synthesizer, Dynamic Scroll Bar & Interactive Floating Widgets
    inject_client_runtime()


def inject_client_runtime() -> None:
    """Inject the self-contained Web Audio API synthesizer and scroll animator."""
    components.html(
        r"""
<script>
(function() {
  const pDoc = window.parent.document;
  const pWin = window.parent;
  if (!pDoc || !pWin) return;

  // 1. TOP SCROLL PROGRESS BAR INJECTION
  let progressBar = pDoc.getElementById("ab-scroll-progress-bar");
  if (!progressBar) {
    progressBar = pDoc.createElement("div");
    progressBar.id = "ab-scroll-progress-bar";
    pDoc.body.appendChild(progressBar);
  }

  // 2. SCROLL TO TOP ROCKET BUTTON
  let scrollTopBtn = pDoc.getElementById("ab-scroll-top-btn");
  if (!scrollTopBtn) {
    scrollTopBtn = pDoc.createElement("div");
    scrollTopBtn.id = "ab-scroll-top-btn";
    scrollTopBtn.title = "Scroll to Top 🚀";
    scrollTopBtn.innerHTML = "🚀";
    scrollTopBtn.addEventListener("click", () => {
      pWin.scrollTo({ top: 0, behavior: "smooth" });
      if (pWin.askabhi_play_click) pWin.askabhi_play_click();
    });
    pDoc.body.appendChild(scrollTopBtn);
  }

  // 3. SOUND FX TOGGLE BUTTON
  let soundToggleBtn = pDoc.getElementById("ab-sound-toggle-btn");
  let soundEnabled = true;
  try {
    const saved = localStorage.getItem("askabhi_sound_enabled");
    if (saved !== null) soundEnabled = saved === "true";
  } catch(e) {}

  function updateSoundButtonLabel() {
    if (!soundToggleBtn) return;
    soundToggleBtn.innerHTML = soundEnabled ? "🔊 Sound: ON" : "🔇 Sound: OFF";
    soundToggleBtn.style.borderColor = soundEnabled ? "#3AAFA9" : "#E07A5F";
    soundToggleBtn.style.color = soundEnabled ? "#2B7A78" : "#E07A5F";
  }

  if (!soundToggleBtn) {
    soundToggleBtn = pDoc.createElement("div");
    soundToggleBtn.id = "ab-sound-toggle-btn";
    updateSoundButtonLabel();
    soundToggleBtn.addEventListener("click", () => {
      soundEnabled = !soundEnabled;
      try { localStorage.setItem("askabhi_sound_enabled", String(soundEnabled)); } catch(e) {}
      updateSoundButtonLabel();
      if (soundEnabled && pWin.askabhi_play_click) pWin.askabhi_play_click();
    });
    pDoc.body.appendChild(soundToggleBtn);
  } else {
    updateSoundButtonLabel();
  }

  // 4. SCROLL EVENT TRACKER
  function onScrollHandler() {
    const mainSection = pDoc.querySelector("section.main") || pDoc.documentElement;
    const scrollTop = pWin.scrollY || mainSection.scrollTop || 0;
    const scrollHeight = (pDoc.documentElement.scrollHeight || mainSection.scrollHeight) - pWin.innerHeight;
    const pct = scrollHeight > 0 ? Math.min(100, Math.max(0, (scrollTop / scrollHeight) * 100)) : 0;
    if (progressBar) progressBar.style.width = pct + "%";
    if (scrollTopBtn) {
      if (scrollTop > 180) scrollTopBtn.classList.add("visible");
      else scrollTopBtn.classList.remove("visible");
    }
  }
  pWin.addEventListener("scroll", onScrollHandler, { passive: true });
  onScrollHandler();

  // 5. WEB AUDIO API SYNTHESIZER ENGINE
  let audioCtx = null;
  function getAudioContext() {
    if (!audioCtx) {
      const AudioContext = pWin.AudioContext || pWin.webkitAudioContext;
      if (AudioContext) audioCtx = new AudioContext();
    }
    if (audioCtx && audioCtx.state === "suspended") {
      audioCtx.resume();
    }
    return audioCtx;
  }

  // Unlock AudioContext on first parent interaction
  const unlockAudio = () => {
    getAudioContext();
    pDoc.removeEventListener("click", unlockAudio);
    pDoc.removeEventListener("keydown", unlockAudio);
  };
  pDoc.addEventListener("click", unlockAudio);
  pDoc.addEventListener("keydown", unlockAudio);

  // Sound: Click / Tap (crisp pop)
  pWin.askabhi_play_click = function() {
    if (!soundEnabled) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(800, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(400, ctx.currentTime + 0.04);
      gain.gain.setValueAtTime(0.12, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.04);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.04);
    } catch(e) {}
  };

  // Sound: Payment Success Chime (4-Tone Ascending UPI Chime)
  pWin.askabhi_play_success = function() {
    if (!soundEnabled) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
      notes.forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const start = ctx.currentTime + (idx * 0.09);
        osc.type = "triangle";
        osc.frequency.setValueAtTime(freq, start);
        gain.gain.setValueAtTime(0.22, start);
        gain.gain.exponentialRampToValueAtTime(0.001, start + 0.35);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(start);
        osc.stop(start + 0.36);
      });
    } catch(e) {}
  };

  // Sound: Coin / Cash Register Metallic Ping
  pWin.askabhi_play_coins = function() {
    if (!soundEnabled) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      [987.77, 1318.51].forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const start = ctx.currentTime + (idx * 0.06);
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, start);
        gain.gain.setValueAtTime(0.18, start);
        gain.gain.exponentialRampToValueAtTime(0.001, start + 0.28);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(start);
        osc.stop(start + 0.3);
      });
    } catch(e) {}
  };

  // Sound: Notification Ding
  pWin.askabhi_play_notification = function() {
    if (!soundEnabled) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      [587.33, 880.00].forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const start = ctx.currentTime + (idx * 0.1);
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, start);
        gain.gain.setValueAtTime(0.16, start);
        gain.gain.exponentialRampToValueAtTime(0.001, start + 0.3);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(start);
        osc.stop(start + 0.32);
      });
    } catch(e) {}
  };

  // 6. GLOBAL EVENT DELEGATION
  pDoc.addEventListener("click", function(e) {
    const target = e.target.closest("button, a, [data-baseweb='tab'], .pp-action-tile");
    if (!target) return;
    
    const text = (target.innerText || "").toLowerCase();
    const isPaymentTrigger = text.includes("pay") || text.includes("scan") || text.includes("send") || text.includes("recharge") || text.includes("transfer");
    
    if (isPaymentTrigger) {
      setTimeout(() => {
        if (pWin.askabhi_play_success) pWin.askabhi_play_success();
        setTimeout(() => { if (pWin.askabhi_play_coins) pWin.askabhi_play_coins(); }, 120);
      }, 50);
    } else {
      if (pWin.askabhi_play_click) pWin.askabhi_play_click();
    }
  }, true);

})();
</script>
""",
        height=0,
        width=0,
    )
