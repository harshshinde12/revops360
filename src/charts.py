"""Shared Plotly styling: executive fintech palette, layout, and polish.

Industry habit: a `charts` module stops each page inventing its own colors.
All money axes use compact $ formatting; grids are hairlines; hover is unified.
"""
from __future__ import annotations

import plotly.graph_objects as go

NAVY = "#0F1E3D"
NAVY_MID = "#1B2A4A"
TEAL = "#0E7C7B"
TEAL_BRIGHT = "#14B8A6"
INDIGO = "#4F46E5"
SLATE = "#64748B"
LIGHT_SLATE = "#94A3B8"
AMBER = "#D97706"
RED = "#DC2626"
EMERALD = "#059669"
GRID = "rgba(148, 163, 184, 0.2)"
BG = "rgba(0,0,0,0)"

# Refined executive sequential palette
SEQUENTIAL = ["#0E7C7B", "#1B2A4A", "#2AA198", "#4F46E5", "#0284C7", "#94A3B8"]


def style_fig(fig: go.Figure, title: str = "", height: int = 380,
              x_angle: int = 0) -> go.Figure:
    """Apply the RevOps executive fintech layout.

    x_angle: x-tick rotation — pass -35 for dense month axes; bar/value axes
    stay horizontal (rotated value labels overlap and look amateur).
    """
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>" if title else "",
            "font": {"size": 14, "color": "#0E7C7B", "family": "Inter, -apple-system, sans-serif"},
            "x": 0.0,
            "xanchor": "left",
        },
        font={"family": "Inter, -apple-system, sans-serif", "size": 12, "color": SLATE},
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        height=height,
        margin={"l": 54, "r": 20, "t": 48 if title else 24, "b": 48},
        hovermode="x unified",
        hoverlabel={
            "bgcolor": NAVY,
            "font_size": 12,
            "font_family": "Inter, -apple-system, sans-serif",
            "font_color": "#FFFFFF",
            "bordercolor": "rgba(255, 255, 255, 0.15)",
        },
        legend={
            "orientation": "h",
            "y": -0.22,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 11, "color": "#475569"},
        },
        xaxis={
            "showgrid": False,
            "tickangle": x_angle,
            "tickfont": {"size": 11, "color": SLATE},
            "linecolor": "#E2E8F0",
        },
        yaxis={
            "showgrid": True,
            "gridcolor": GRID,
            "gridwidth": 1,
            "tickfont": {"size": 11, "color": SLATE},
            "zeroline": False,
        },
    )
    return fig


def usd_tick(fig: go.Figure) -> go.Figure:
    fig.update_layout(yaxis_tickformat="$,.0f")
    return fig

