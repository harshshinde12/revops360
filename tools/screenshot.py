"""Dev-only screenshot harness for the UI introspection loop.

Usage (app must already be running):
    python tools/screenshot.py --port 8510 --label iter0
Saves screenshots/iter0_overview.png, ..._pipeline.png, ..._forecast.png,
..._teams.png, ..._dataquality.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

TABS = ["Overview", "Pipeline", "Forecast", "Teams", "Data Quality"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8510)
    ap.add_argument("--label", type=str, default="iter0")
    ap.add_argument("--outdir", type=str, default="screenshots")
    ap.add_argument("--height", type=int, default=900)
    args = ap.parse_args();

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    url = f"http://localhost:{args.port}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": args.height})
        page.goto(url, wait_until="networkidle", timeout=120000)
        # Wait for app content: sidebar title renders once session connects
        page.get_by_text("RevOps360").first.wait_for(timeout=120000)
        page.wait_for_timeout(4000)  # let Plotly canvases paint
        for tab in TABS:
            try:
                page.get_by_role("tab", name=tab).click(timeout=10000)
            except Exception:
                print(f"WARN: could not click tab {tab!r}")
            page.wait_for_timeout(3500)
            fname = out / f"{args.label}_{tab.lower().replace(' ', '')}.png"
            page.screenshot(path=str(fname), full_page=True)
            print(f"saved {fname}")
        browser.close()


if __name__ == "__main__":
    main()
