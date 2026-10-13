"""Shared Plotly styling: one formal palette, one layout, every chart.

Industry habit: a `charts` module stops each page inventing its own colors.
All money axes use compact $ formatting; grids are hairlines; hover is unified.
"""
from __future__ import annotations

import plotly.graph_objects as go

NAVY = "#1B2A4A"
TEAL = "#0E7C7B"
SLATE = "#64748B"
LIGHT_SLATE = "#94A3B8"
AMBER = "#D97706"
RED = "#DC2626"
GRID = "#E2E8F0"
BG = "#FFFFFF"

SEQUENTIAL = ["#0F1E3D", "#1B2A4A", "#0E7C7B", "#2AA198", "#7FB8B5", "#CBD5E1"]


def style_fig(fig: go.Figure, title: str = "", height: int = 380,
              x_angle: int = 0) -> go.Figure:
    """Apply the RevOps fintech layout.

    x_angle: x-tick rotation — pass -35 for dense month axes; bar/value axes
    stay horizontal (rotated value labels overlap and look amateur).
    """
    fig.update_layout(
        title={"text": f"<b>{title}</b>" if title else "", "font": {"size": 14, "color": NAVY}},
        font={"family": "Inter, system-ui, sans-serif", "size": 12, "color": NAVY},
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        height=height,
        margin={"l": 60, "r": 20, "t": 50, "b": 60},
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.22, "font": {"size": 11}},
        xaxis={"showgrid": False, "tickangle": x_angle, "tickfont": {"size": 11}},
        # No currency prefix by default: money charts opt in via usd_tick().
        # (Setting both tickprefix "$" and tickformat "$,.0f" renders "$$…".)
        yaxis={"showgrid": True, "gridcolor": GRID, "gridwidth": 1,
               "tickfont": {"size": 11}},
    )
    return fig


def usd_tick(fig: go.Figure) -> go.Figure:
    fig.update_layout(yaxis_tickformat="$,.0f")
    return fig
