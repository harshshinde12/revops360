# Lessons (self-governing rules)

1. Never depend on login-walled datasets at runtime. Use deterministic seed + manifest; support real drop-in via contract.
2. Never silently drop bad rows. Quarantine with reason + quarantine-rate alert.
3. Never hardcode business logic (stage probs, targets). All in config/config.yaml.
4. ETL must be idempotent: sorted output, fixed float precision, UTC timestamps, content-hash check.
5. Dashboard must handle missing data dir (auto-bootstrap) — Streamlit Cloud starts from fresh clone.
6. Keep Cloud deps light: pandas/numpy/pydantic/yaml/plotly/streamlit only.
7. Generator must guarantee its own contract (engage<=close) — quarantine caught 19/2600 seed rows with close<engage on first run; fixed generator, re-verified 0 quarantined.
8. Never backtest weighted pipeline against past months from a flat export (past deals are closed by construction, forecast=0). Use walk-forward trend predictions vs actuals; document why.
9. Funnel conversion only within open stages — dividing Closed Won by Commit fabricates 42x conversion; set terminal conv to NaN.
10. pytest needs conftest.py sys.path bootstrap (pytest 9 no longer imports rootdir implicitly); numpy must be >=2.0 for Python 3.13 (1.26 has no cp313 wheel).
11. Screenshot loop needs a tall viewport (1600x2400) — 900px hides below-fold regressions.
12. Never combine tickprefix "$" with tickformat "$,.0f" (renders "$$"); money charts opt in via usd_tick() only.
13. Rotated tick labels on bar/value axes overlap — x_angle=-35 only for dense month axes, 0 elsewhere.
14. Outside bar labels clip at the axis edge — extend xaxis_range to ~1.25x max.
15. Never compute conversion from snapshot counts (exceeds 100%, e.g. 129%); removed conv_from_prev, added test guard + doc note.
16. Rename technical columns to boardroom labels before display (ui.pretty) — code names in UI look junior.
17. Never background servers with `&` — use Start-Job + Stop/Remove-Job in the same command, then sweep Get-Process.
18. Prefer font-independent widgets: st.expander's triangle and collapse arrows render raw ligature text when icon fonts fail — pills, static tables and hidden toggles are safer.
19. Layout hygiene: hide stHeader + tighten stMainBlockContainer padding (dead top space); keep tables full-width, never inside narrow columns (cutoff); export buttons side-by-side in columns.
20. No sidebar: top brand bar + 3-column pills filter row carries full Region/Segment/Manager functionality; Streamlit hides the sidebar automatically when nothing renders into it.
