"""Shared UI primitives: executive revenue intelligence design system.

Features:
- Enterprise light theme design system with standardized 12px tokens.
- Standardized 12px border-radius and backdrop-filter blur on header.
- Clean typography scale with bold figures and muted labels.
- Zero decorative emojis or raw glyphs on metric cards and headers.
- Hoverable tooltips for technical metric details.
- Zebra-striped telemetry tables with status pill badges.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

NAVY = "#0F1E3D"
NAVY_DEEP = "#09122C"
SLATE = "#64748B"
LIGHT_SLATE = "#94A3B8"
TEAL = "#0E7C7B"
TEAL_ACCENT = "#2DD4BF"
INDIGO = "#4F46E5"
AMBER = "#D97706"
RED = "#DC2626"
EMERALD = "#059669"

# Minimalist corporate SVG icon library
SVG_ICONS = {
    "info": """<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>""",
    "globe": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>""",
    "building": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"/><line x1="9" y1="22" x2="9" y2="22.01"/><line x1="15" y1="22" x2="15" y2="22.01"/><line x1="9" y1="6" x2="9" y2="6.01"/><line x1="15" y1="6" x2="15" y2="6.01"/><line x1="9" y1="10" x2="9" y2="10.01"/><line x1="15" y1="10" x2="15" y2="10.01"/><line x1="9" y1="14" x2="9" y2="14.01"/><line x1="15" y1="14" x2="15" y2="14.01"/></svg>""",
    "user": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>""",
    "briefcase": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>""",
    "calendar": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>""",
    "dollar": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>""",
    "target": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>""",
    "chart": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>""",
    "trending": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>""",
    "activity": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>""",
    "scale": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 16l3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1z"/><path d="M2 16l3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>""",
    "refresh": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>""",
    "clock": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>""",
    "shield": """<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>""",
    "check": """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>""",
    "alert": """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>""",
    "download": """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>""",
    "file": """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>""",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

/* ----------------- CSS Theme Tokens ----------------- */
:root {
    --bg-app: #F8FAFC;
    --bg-primary: #FFFFFF;
    --bg-card: #FFFFFF;
    --bg-subtle: #F1F5F9;
    --border-color: #E2E8F0;
    --border-subtle: #CBD5E1;
    --text-primary: #0F172A;
    --text-secondary: #475569;
    --text-muted: #64748B;
    --accent-color: #0E7C7B;
    --accent-hover: #0A6160;
    --accent-subtle: #E6F4F1;
    --card-shadow: 0 1px 3px rgba(15, 23, 42, 0.05), 0 1px 2px rgba(15, 23, 42, 0.03);
    --card-hover-shadow: 0 10px 25px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04);
}

html, body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    letter-spacing: -0.01em;
}

/* Explicitly preserve Material Symbols and Streamlit internal icons from font override */
[data-testid*="Icon"], 
[class*="material-symbols"], 
[class*="material-icons"], 
.material-symbols-rounded, 
.material-symbols-outlined,
[data-testid="stIcon"],
span[class*="Icon"] {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
}

/* App container - Locked permanently to clean light theme */
.stApp, [data-testid="stAppViewContainer"], .main, [data-testid="stMainBlockContainer"] {
    background-color: var(--bg-app) !important;
    color: var(--text-primary) !important;
}

.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1440px !important;
}

/* Streamlit header hygiene */
[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
footer { display: none !important; }

/* ----------------- Top Command Bar with Blur ----------------- */
.revops-brand-bar {
    background: linear-gradient(135deg, rgba(9, 18, 44, 0.94) 0%, rgba(15, 30, 61, 0.92) 55%, rgba(24, 44, 77, 0.90) 100%);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 8px 24px -4px rgba(10, 17, 40, 0.2), 0 2px 6px -1px rgba(10, 17, 40, 0.12);
    position: relative;
    overflow: hidden;
}

.brand-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-emblem {
    font-size: 19px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 0.04em;
    display: flex;
    align-items: center;
    gap: 6px;
}

.brand-emblem .brand-icon {
    color: #2DD4BF;
    font-size: 18px;
}

.brand-emblem .brand-hl {
    color: #2DD4BF;
}

.brand-tag {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #94A3B8;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 6px;
    padding: 3px 8px;
}

.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 600;
    color: #A7F3D0;
    background: rgba(16, 185, 129, 0.14);
    border: 1px solid rgba(16, 185, 129, 0.28);
    border-radius: 999px;
    padding: 3px 9px;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.45; transform: scale(0.85); }
}

.live-dot {
    width: 6.5px;
    height: 6.5px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 6px #10B981;
    display: inline-block;
    animation: pulse-dot 2.2s infinite ease-in-out;
}

.brand-right {
    display: flex;
    align-items: center;
    gap: 8px;
    z-index: 1;
}

.scope-pill {
    font-size: 11.5px;
    font-weight: 500;
    color: #E2E8F0;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 5px 11px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.scope-pill b {
    color: #FFFFFF;
    font-weight: 700;
}

/* ----------------- High-Contrast Enterprise Notification Banners ----------------- */
.revops-banner {
    border-radius: 8px;
    padding: 14px 18px;
    margin: 12px 0 16px 0;
    border-left: 4px solid var(--accent-color);
    background: #FFFFFF;
    border-top: 1px solid #E2E8F0;
    border-right: 1px solid #E2E8F0;
    border-bottom: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
}

.revops-banner.tone-warning {
    border-left-color: #D97706;
    background: #FFFDF5;
}

.revops-banner.tone-error {
    border-left-color: #DC2626;
    background: #FEF7F7;
}

.revops-banner.tone-success {
    border-left-color: #059669;
    background: #F6FEF9;
}

.revops-banner.tone-info {
    border-left-color: #0E7C7B;
    background: #F7FBFC;
}

.revops-banner .banner-head {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}

.revops-banner .banner-tag {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 2px 6px;
    border-radius: 4px;
    background: rgba(15, 23, 42, 0.06);
    color: #0F172A;
}

.revops-banner.tone-warning .banner-tag {
    background: #FEF3C7;
    color: #92400E;
}

.revops-banner.tone-error .banner-tag {
    background: #FEE2E2;
    color: #991B1B;
}

.revops-banner.tone-success .banner-tag {
    background: #DCFCE7;
    color: #166534;
}

.revops-banner .banner-title {
    font-weight: 700;
    font-size: 13.5px;
    color: #0F172A;
}

.revops-banner .banner-body {
    font-size: 13px;
    color: #334155;
    line-height: 1.5;
}

.revops-banner .banner-meta {
    margin-top: 8px;
    padding-top: 6px;
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    font-size: 11.5px;
    font-weight: 600;
    color: #64748B;
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
}

/* Streamlit multiselect styling */
[data-baseweb="select"] {
    border-radius: 8px !important;
}

[data-baseweb="select"] > div {
    background-color: var(--bg-card) !important;
    border-color: var(--border-color) !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
    min-height: 38px !important;
}

[data-baseweb="select"] > div:hover {
    border-color: var(--border-subtle) !important;
}

[data-baseweb="tag"] {
    background-color: var(--bg-subtle) !important;
    color: var(--text-primary) !important;
    border-radius: 6px !important;
    border: 1px solid var(--border-color) !important;
    font-weight: 600 !important;
    font-size: 11.5px !important;
}

/* ----------------- Tabs ----------------- */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 6px;
    background: var(--bg-subtle);
    padding: 5px;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    margin-bottom: 18px;
}

[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-size: 13.5px;
    font-weight: 600;
    color: var(--text-secondary);
    padding: 7px 18px;
    border-radius: 8px;
    border: 1px solid transparent !important;
    background: transparent;
    transition: all 0.18s ease-in-out;
}

[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    color: var(--text-primary);
    background: var(--bg-card);
}

[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--text-primary) !important;
    background: var(--bg-card) !important;
    box-shadow: var(--card-shadow) !important;
    font-weight: 700;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none !important;
}

/* ----------------- Metric KPI Cards ----------------- */
.revops-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: var(--card-shadow);
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease;
    position: relative;
    overflow: visible;
}

.revops-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--card-hover-shadow);
    border-color: var(--border-subtle);
}

.revops-card.tone-up { border-top: 3.5px solid #0E7C7B; }
.revops-card.tone-teal { border-top: 3.5px solid #0E7C7B; }
.revops-card.tone-navy { border-top: 3.5px solid #0F1E3D; }
.revops-card.tone-indigo { border-top: 3.5px solid #4F46E5; }
.revops-card.tone-warn { border-top: 3.5px solid #D97706; }
.revops-card.tone-down { border-top: 3.5px solid #DC2626; }
.revops-card.tone-neutral { border-top: 3.5px solid #64748B; }

.revops-card .top-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2px;
}

.revops-card .lbl-group {
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.revops-card .lbl {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.revops-card .val {
    font-size: 28px;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.15;
    letter-spacing: -0.025em;
    font-feature-settings: 'tnum' 1;
    margin: 4px 0 2px 0;
}

.revops-card .sub {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-secondary);
    margin-top: 4px;
    line-height: 1.35;
}

/* ----------------- Tooltips ----------------- */
.info-tooltip-wrap {
    position: relative;
    display: inline-flex;
    align-items: center;
    cursor: help;
    color: var(--text-muted);
    transition: color 0.15s ease;
}

.info-tooltip-wrap:hover {
    color: var(--accent-color);
}

.info-tooltip-bubble {
    visibility: hidden;
    opacity: 0;
    position: absolute;
    bottom: calc(100% + 7px);
    left: 50%;
    transform: translateX(-50%) translateY(4px);
    background: #0F172A;
    color: #F8FAFC;
    padding: 6px 10px;
    border-radius: 7px;
    font-size: 11px;
    font-weight: 500;
    white-space: nowrap;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.12);
    transition: opacity 0.15s ease, transform 0.15s ease;
    z-index: 99999;
    pointer-events: none;
}

.info-tooltip-wrap:hover .info-tooltip-bubble {
    visibility: visible;
    opacity: 1;
    transform: translateX(-50%) translateY(0);
}

/* ----------------- Pill Badges ----------------- */
.pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    font-weight: 600;
    border-radius: 999px;
    padding: 2px 9px;
    margin-top: 6px;
}

.pill.up {
    background: var(--accent-subtle);
    color: var(--accent-color);
    border: 1px solid rgba(14, 124, 123, 0.25);
}

.pill.warn {
    background: #FEF3C7;
    color: #B45309;
    border: 1px solid rgba(180, 83, 9, 0.22);
}

.pill.down {
    background: #FEE2E2;
    color: #B91C1C;
    border: 1px solid rgba(185, 28, 28, 0.22);
}

.pill.neutral {
    background: var(--bg-subtle);
    color: var(--text-secondary);
    border: 1px solid var(--border-color);
}

/* ----------------- Page & Section Headers ----------------- */
.revops-head {
    border-bottom: 1.5px solid var(--border-color);
    padding-bottom: 10px;
    margin-bottom: 16px;
    margin-top: 4px;
}

.revops-head .kicker {
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent-color);
    margin-bottom: 2px;
}

.revops-head h2 {
    font-size: 22px;
    font-weight: 750;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin: 0;
    line-height: 1.25;
}

.revops-head p {
    color: var(--text-secondary);
    font-size: 12.5px;
    font-weight: 500;
    margin: 5px 0 0 0;
}

.section-kicker {
    font-size: 11px;
    font-weight: 750;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: var(--accent-color);
    margin-top: 16px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.section-kicker::before {
    content: '';
    width: 3px;
    height: 12px;
    background: var(--accent-color);
    border-radius: 2px;
}

/* ----------------- Callouts ----------------- */
.revops-callout {
    border-radius: 10px;
    padding: 12px 16px;
    margin: 10px 0;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    font-size: 13px;
    line-height: 1.45;
    border: 1px solid transparent;
}

.revops-callout .callout-icon {
    line-height: 1.2;
    flex-shrink: 0;
    margin-top: 2px;
}

.revops-callout.success {
    background: #F0FDF4;
    border-color: #BBF7D0;
    color: #166534;
}

.revops-callout.warning {
    background: #FFFBEB;
    border-color: #FDE68A;
    color: #92400E;
}

.revops-callout.error {
    background: #FEF2F2;
    border-color: #FECACA;
    color: #991B1B;
}

.revops-callout.info {
    background: #F0F9FF;
    border-color: #BAE6FD;
    color: #075985;
}

/* ----------------- Telemetry Table with Zebra Striping ----------------- */
.telemetry-table-container {
    border: 1px solid var(--border-color);
    border-radius: 10px;
    overflow: hidden;
    background: var(--bg-card);
    box-shadow: var(--card-shadow);
    margin: 8px 0 16px 0;
}

.telemetry-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
    text-align: left;
}

.telemetry-table th {
    background: var(--bg-subtle);
    color: var(--text-muted);
    font-weight: 700;
    text-transform: uppercase;
    font-size: 10.5px;
    letter-spacing: 0.06em;
    padding: 10px 14px;
    border-bottom: 1px solid var(--border-color);
}

.telemetry-table td {
    padding: 10px 14px;
    color: var(--text-primary);
    border-bottom: 1px solid var(--border-color);
}

.telemetry-table tbody tr:nth-child(even) {
    background-color: var(--bg-subtle);
}

.telemetry-table tbody tr:nth-child(odd) {
    background-color: var(--bg-card);
}

.telemetry-table tbody tr:hover {
    background-color: rgba(14, 124, 123, 0.08);
}

.status-badge {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 2px 9px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

.status-badge.success {
    background: #DCFCE7;
    color: #166534;
    border: 1px solid #BBF7D0;
}

.status-badge.skipped {
    background: #E0F2FE;
    color: #0369A1;
    border: 1px solid #BAE6FD;
}

.status-badge.failed {
    background: #FEE2E2;
    color: #991B1B;
    border: 1px solid #FECACA;
}

/* ----------------- Dataframe & Buttons ----------------- */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-color) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    box-shadow: var(--card-shadow) !important;
    background: var(--bg-card) !important;
}

[data-testid="stDownloadButton"] button, [data-testid="stBaseButton-secondary"] {
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: 8px !important;
    border: 1px solid var(--border-subtle) !important;
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05) !important;
    transition: all 0.15s ease-in-out !important;
    padding: 8px 16px !important;
}

[data-testid="stDownloadButton"] button:hover {
    border-color: var(--accent-color) !important;
    color: var(--accent-color) !important;
    background: var(--bg-subtle) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 10px -2px rgba(14, 124, 123, 0.15) !important;
}
</style>
"""


def inject_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def brand_header(title: str = "REVOPS360",
                 tag: str = "REVENUE INTELLIGENCE",
                 opp_count: int = 0,
                 date_range: str = "",
                 currency: str = "USD ($)") -> None:
    """Render the executive top command banner with clean enterprise typography."""
    opp_fmt = f"{opp_count:,}" if opp_count else "—"

    html = f"""
    <div class='revops-brand-bar'>
        <div class='brand-left'>
            <div class='brand-emblem'>
                <span>{title[:6]}<span class='brand-hl'>{title[6:]}</span></span>
            </div>
            <span class='brand-tag'>{tag}</span>
            <span class='live-badge'>
                <span class='live-dot'></span> PIPELINE CACHED
            </span>
        </div>
        <div class='brand-right'>
            <span class='scope-pill'>Deals: <b>{opp_fmt}</b></span>
            <span class='scope-pill'>Horizon: <b>{date_range}</b></span>
            <span class='scope-pill'>Base: <b>{currency}</b></span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", kicker: str = "") -> None:
    kicker_html = f"<div class='kicker'>{kicker}</div>" if kicker else ""
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"<div class='revops-head'>{kicker_html}<h2>{title}</h2>{sub_html}</div>",
        unsafe_allow_html=True,
    )


def section_kicker(title: str) -> None:
    st.markdown(f"<div class='section-kicker'>{title}</div>", unsafe_allow_html=True)


def kpi_card(label: str, value: str, sub: str = "",
             pill: str = "", tone: str = "up", icon: str = "",
             tooltip: str = "") -> None:
    """Render a metric card with bold figures, muted label, and optional hover tooltip."""
    pill_html = f"<span class='pill {tone}'>{pill}</span>" if pill else ""

    tooltip_html = ""
    if tooltip:
        tooltip_html = f"""
        <span class='info-tooltip-wrap'>
            {SVG_ICONS['info']}
            <span class='info-tooltip-bubble'>{tooltip}</span>
        </span>
        """

    st.markdown(
        f"<div class='revops-card tone-{tone}'>"
        f"<div class='top-row'>"
        f"  <div class='lbl-group'><span class='lbl'>{label}</span>{tooltip_html}</div>"
        f"</div>"
        f"<div class='val'>{value}</div>"
        + (f"<div class='sub'>{sub}</div>" if sub else "")
        + pill_html
        + "</div>",
        unsafe_allow_html=True,
    )


def notification_banner(title: str, text: str, tone: str = "warning", meta: str = "") -> None:
    """Render a streamlined, high-contrast enterprise notification banner with clean typography and zero decorative warning icons."""
    meta_html = f"<div class='banner-meta'>{meta}</div>" if meta else ""
    st.markdown(
        f"<div class='revops-banner tone-{tone}'>"
        f"  <div class='banner-head'>"
        f"    <span class='banner-tag'>{tone.upper()}</span>"
        f"    <span class='banner-title'>{title}</span>"
        f"  </div>"
        f"  <div class='banner-body'>{text}</div>"
        f"  {meta_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def telemetry_table(df: pd.DataFrame) -> None:
    """Render an executive ETL telemetry table with zebra-striping and status badges."""
    rows = []
    for _, row in df.iterrows():
        status = str(row.get("status", "")).lower()
        badge_class = "success" if status == "success" else "skipped" if status == "skipped" else "failed"
        q_rate = f"{float(row.get('quarantine_rate', 0)):.2%}"
        duration = f"{float(row.get('duration_s', 0)):.2f}s"
        rows.append(
            f"<tr>"
            f"<td><code>{row.get('run_id', '')}</code></td>"
            f"<td>{str(row.get('utc_time', ''))[:19]}</td>"
            f"<td><span class='status-badge {badge_class}'>{status}</span></td>"
            f"<td>{int(row.get('rows_in', 0)):,}</td>"
            f"<td>{int(row.get('rows_out', 0)):,}</td>"
            f"<td>{q_rate}</td>"
            f"<td>{duration}</td>"
            f"</tr>"
        )

    table_html = (
        "<div class='telemetry-table-container'>"
        "<table class='telemetry-table'>"
        "<thead><tr>"
        "<th>Run ID</th><th>UTC Timestamp</th><th>Status</th>"
        "<th>Rows In</th><th>Rows Out</th><th>Quarantine</th><th>Duration</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )
    st.html(table_html)


def callout(text: str, tone: str = "info", title: str = "", icon: str = "") -> None:
    """Render an executive alert box with clean typography and zero decorative icons."""
    title_html = f"<div class='callout-title'><b>{title}</b></div>" if title else ""
    st.markdown(
        f"<div class='revops-callout {tone}'>"
        f"<div class='callout-body'>{title_html}<div class='callout-text'>{text}</div></div>"
        "</div>",
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
