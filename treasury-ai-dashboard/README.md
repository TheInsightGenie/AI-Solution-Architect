# Yields and the AI Buildout

A single-page dashboard mapping the relationship between the **US 10-year Treasury yield**,
the **federal funds rate**, and **big tech AI earnings and capital spending** over the
trailing 24 months (September 2024 – September 2026).

## The question it answers

The Fed cut 125bp between September 2024 and December 2025 and has held at 3.50–3.75%
through all of 2026. Over that same window the 10-year Treasury yield *rose* roughly 95bp,
to its highest level since November 2023. Meanwhile the four largest hyperscalers took
combined quarterly capex from ~$72B to $166B, funded increasingly with debt.

The dashboard lays those three series side by side and argues the mechanism connecting
them: AI capex now outruns operating cash flow, the gap is funded in the bond market, that
supply widens term premium at the long end, and the higher discount rate compresses the
multiple on exactly the long-duration earnings the capex is meant to produce.

## Files

| File | What it is |
|---|---|
| `index.html` | The dashboard. Self-contained — no build step, no runtime data fetch. |
| `refresh_data.py` | Repulls the two rate series from FRED and rewrites them in place. |

## Viewing it

Open `index.html` in a browser, or publish it. It is a body fragment (no `<!doctype>` /
`<html>` / `<head>` wrapper) so it can be published directly as a Claude Artifact; to open
it standalone, wrap it in a minimal HTML skeleton first.

The page renders in light and dark themes, is keyboard navigable (the rates chart takes
focus and steps month-by-month with arrow keys), and every chart has a table view.

## Refreshing the data

```bash
python3 refresh_data.py                   # trailing 24 months ending today
python3 refresh_data.py --end 2026-09-04  # pin the as-of date
python3 refresh_data.py --check           # show drift vs. shipped values, write nothing
```

Standard library only — no dependencies, no API key. It pulls FRED's public CSV endpoint
for `DGS10` (10-year constant maturity) and `DFEDTARU` (fed funds target upper bound),
takes the last observation in each month, and rewrites the `MONTHS`, `TSY` and `FFR`
arrays plus the as-of stamp in `index.html`.

Run `--check` first if you want to see how far the shipped values have drifted before
overwriting them.

## Data provenance

This matters, so the dashboard states it on the page as well as here.

**Sourced from published reports** — all 2026 month-end 10Y readings and October 2025; the
full Fed funds path including all eight 2026 FOMC meetings; combined Q2 2026 capex of
$166.0B (+87% YoY, +27% QoQ); every figure in the mechanism and earnings sections.

**Reconstructed** — month-end 10Y for September 2024 through January 2026, assembled from
period reporting and anchored to the verified readings either side. Treat as approximate to
about ±5bp. Quarterly capex before Q1 2026 is apportioned from reported annual totals.
Running `refresh_data.py` replaces the entire rate series with official FRED data and
resolves this; the capex bars come from company filings and are left untouched.

The environment this was built in had no direct network access to FRED, Treasury or market
data hosts, so the seed series was assembled from published reporting rather than pulled
from a feed. That is the reason `refresh_data.py` exists.

## Caveats

Correlation across 24 monthly observations does not establish causation. The
capex-to-yields channel is one mechanism among several carrying term premium — fiscal
deficits and inflation expectations are at least as important. The charts show two series
moving apart; the mechanism section is the argued explanation for it, not a fitted result.

Not investment advice.
