"""Shared UI primitives: formal fintech theme, KPI cards, number formatting.

Kept separate from app.py so the dashboard layer stays thin and every
visual decision lives in one reviewable place.
"""
from __future__ import annotations

import streamlit as st

NAVY = "#1B2A4A"
NAVY_DEEP = "#0F1E3D"
SLATE = "#64748B"
TEAL = "#0E7C7B"
AMBER = "#B45309"
RED = "#B91C1C"
BG = "#F8FAFC"
BORDER = "#E2E8F0"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="st-"] { font-family: 'Inter', system-ui, -apple-system, sans-serif; }
/* Filter pills: formal single-line chips */
[data-testid="stPills"] [data-baseweb="tag"] { font-weight: 600; }
/* KPI cards */
.revops-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px;
  padding: 14px 16px; box-shadow: 0 1px 2px rgba(15,30,61,0.06); }
.revops-card .lbl { font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; color: #64748B; margin-bottom: 4px; }
.revops-card .val { font-size: 26px; font-weight: 700; color: #0F1E3D; line-height: 1.1; }
.revops-card .sub { font-size: 12px; color: #64748B; margin-top: 4px; }
.pill { display: inline-block; font-size: 11px; font-weight: 600; border-radius: 999px;
  padding: 2px 10px; margin-top: 6px; }
.pill.up { background: #E6F4F1; color: #0E7C7B; }
.pill.warn { background: #FEF3C7; color: #B45309; }
.pill.down { background: #FEE2E2; color: #B91C1C; }
/* Page header */
.revops-head { border-bottom: 2px solid #0F1E3D; padding-bottom: 10px; margin-bottom: 6px; }
.revops-head h1 { font-size: 26px; color: #0F1E3D; margin: 0; }
.revops-head p { color: #64748B; font-size: 13px; margin: 4px 0 0 0; }
/* Tighter tabs */
button[data-baseweb="tab"] { font-weight: 600; color: #475569; }
button[data-baseweb="tab"][aria-selected="true"] { color: #0F1E3D; }
/* Hide Streamlit's sidebar collapse/expand toggle (renders raw
   "keyboard_double_arrow_left" text when the icon font fails to load).
   Selector verified against the installed Streamlit 1.54 frontend bundle. */
[data-testid="stSidebarCollapseButton"] { display: none !important; }
/* Remove dead space above the tabs: hide the top toolbar and tighten padding */
[data-testid="stHeader"] { display: none !important; }
[data-testid="stMainBlockContainer"] { padding-top: 1.2rem !important; }
.block-container { padding-top: 1.2rem !important; }
</style>
"""


def inject_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"<div class='revops-head'><h1>{title}</h1><p>{subtitle}</p></div>",
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, sub: str = "",
             pill: str = "", tone: str = "up") -> None:
    pill_html = f"<span class='pill {tone}'>{pill}</span>" if pill else ""
    st.markdown(
        "<div class='revops-card'>"
        f"<div class='lbl'>{label}</div>"
        f"<div class='val'>{value}</div>"
        + (f"<div class='sub'>{sub}</div>" if sub else "")
        + pill_html
        + "</div>",
        unsafe_allow_html=True,
    )


def fmt_usd(x: float) -> str:
    return f"${x:,.0f}"


def fmt_compact(x: float) -> str:
    ax = abs(x)
    if ax >= 1_000_000:
        return f"${x / 1_000_000:,.2f}M"
    if ax >= 1_000:
        return f"${x / 1_000:,.1f}K"
    return f"${x:,.0f}"


def fmt_pct(x: float) -> str:
    return f"{x:.1%}"


def pretty(df, mapping: dict[str, str]):
    """Rename technical columns to boardroom labels before display."""
    return df.rename(columns=mapping)
