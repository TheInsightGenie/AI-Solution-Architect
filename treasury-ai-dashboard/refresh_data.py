#!/usr/bin/env python3
"""Refresh the rate series in index.html from official FRED data.

The dashboard ships with month-end values for the 10-year Treasury constant
maturity yield (DGS10) and the federal funds target upper bound (DFEDTARU).
The 2026 readings were taken from published snapshots; the earlier ones were
reconstructed from period reporting. This script replaces the whole window
with the authoritative series.

FRED's CSV endpoint needs no API key. Run it anywhere with outbound HTTPS:

    python3 refresh_data.py                  # trailing 24 months, ending today
    python3 refresh_data.py --end 2026-09-04 # pin the as-of date
    python3 refresh_data.py --check          # report drift, write nothing

Only the TSY and FFR arrays and the as-of stamp are touched. Everything the
script cannot source from FRED -- the capex series, the earnings scorecard --
is left alone, because those come from company filings rather than a feed.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import re
import sys
import urllib.request
from pathlib import Path

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={start}&coed={end}"
HERE = Path(__file__).resolve().parent
TARGET = HERE / "index.html"

MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fetch(series_id: str, start: dt.date, end: dt.date) -> dict[dt.date, float]:
    """Pull one FRED series as {date: value}, skipping the '.' no-data rows."""
    url = FRED.format(sid=series_id, start=start.isoformat(), end=end.isoformat())
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            body = resp.read().decode("utf-8")
    except Exception as exc:  # network, TLS, 403 from a proxy -- all fatal here
        sys.exit(f"could not fetch {series_id} from FRED: {exc}")

    rows: dict[dt.date, float] = {}
    reader = csv.reader(io.StringIO(body))
    header = next(reader, None)
    if not header:
        sys.exit(f"empty response for {series_id}")
    for row in reader:
        if len(row) < 2 or row[1].strip() in (".", ""):
            continue
        rows[dt.date.fromisoformat(row[0].strip())] = float(row[1])
    if not rows:
        sys.exit(f"no observations returned for {series_id}")
    return rows


def month_ends(daily: dict[dt.date, float], months: list[tuple[int, int]]) -> list[float]:
    """Last observation on or before the end of each (year, month)."""
    out = []
    for year, month in months:
        nxt = dt.date(year + (month == 12), (month % 12) + 1, 1)
        candidates = [d for d in daily if d < nxt]
        if not candidates:
            sys.exit(f"no observation on or before {year}-{month:02d} month-end")
        out.append(daily[max(candidates)])
    return out


def window(end: dt.date) -> list[tuple[int, int]]:
    """The 25 month-buckets ending in `end`'s month (24 months trailing)."""
    months = []
    year, month = end.year, end.month
    for _ in range(25):
        months.append((year, month))
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return list(reversed(months))


def as_js_array(values: list[float], places: int, per_line: int = 12) -> str:
    cells = [f"{v:.{places}f}" for v in values]
    lines = [",".join(cells[i:i + per_line]) for i in range(0, len(cells), per_line)]
    pad = "\n" + " " * 13
    return pad.join(lines)


def replace_array(html: str, name: str, body: str) -> str:
    pattern = re.compile(r"(var " + name + r" = \[)(.*?)(\];)", re.S)
    if not pattern.search(html):
        sys.exit(f"could not find the {name} array in index.html")
    return pattern.sub(lambda m: m.group(1) + body + m.group(3), html, count=1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--end", help="as-of date, YYYY-MM-DD (default: today)")
    ap.add_argument("--check", action="store_true",
                    help="print the drift against the shipped values and exit")
    args = ap.parse_args()

    end = dt.date.fromisoformat(args.end) if args.end else dt.date.today()
    months = window(end)
    start = dt.date(months[0][0], months[0][1], 1) - dt.timedelta(days=40)

    print(f"window: {months[0][0]}-{months[0][1]:02d} .. {months[-1][0]}-{months[-1][1]:02d}")
    tsy = month_ends(fetch("DGS10", start, end), months)
    ffr = month_ends(fetch("DFEDTARU", start, end), months)

    html = TARGET.read_text(encoding="utf-8")

    if args.check:
        shipped = re.search(r"var TSY = \[(.*?)\];", html, re.S)
        old = [float(x) for x in shipped.group(1).replace("\n", "").split(",") if x.strip()]
        print(f"\n{'month':>8}  {'shipped':>8}  {'FRED':>8}  {'drift':>8}")
        for (y, m), fresh in zip(months, tsy):
            label = f"{MONTH_ABBR[m - 1]} {str(y)[2:]}"
            if len(old) == len(tsy):
                prev = old[months.index((y, m))]
                print(f"{label:>8}  {prev:8.2f}  {fresh:8.2f}  {(fresh - prev) * 100:+7.0f}bp")
            else:
                print(f"{label:>8}  {'--':>8}  {fresh:8.2f}  {'--':>8}")
        print("\nnothing written (--check)")
        return

    labels = ",".join(f'"{MONTH_ABBR[m - 1]} {str(y)[2:]}"' for y, m in months)
    html = re.sub(r"(var MONTHS = \[)(.*?)(\];)",
                  lambda m: m.group(1) + labels + m.group(3), html, count=1, flags=re.S)
    html = replace_array(html, "TSY", as_js_array(tsy, 2))
    html = replace_array(html, "FFR", as_js_array(ffr, 2))

    stamp = f"{end.day} {MONTH_ABBR[end.month - 1]} {end.year}"
    html = re.sub(r"(<span class=\"dot\"></span>As of )[^<]*(</span>)",
                  lambda m: m.group(1) + stamp + m.group(2), html, count=1)

    TARGET.write_text(html, encoding="utf-8")
    print(f"\nwrote {TARGET.name}: 10Y {tsy[-1]:.2f}%, fed funds upper {ffr[-1]:.2f}%, as of {stamp}")
    print("note: the capex bars and the earnings table come from filings and were not touched.")


if __name__ == "__main__":
    main()
