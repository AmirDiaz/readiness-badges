#!/usr/bin/env python3
"""readiness-badges — Agent Readiness badges for your README, from the Sourcey
open registry (https://sourcey.com). Zero dependencies (Python 3 stdlib only).

Generates shields-style SVG badges for companies with a published Sourcey
Agent Readiness grade. Every badge names the product scope and the date the
grade was last tested, and every record carries the release_id — so a badge
in your README is a verifiable citation, not a sticker.

Usage:
    python3 readiness_badge.py --list                        # all graded entities
    python3 readiness_badge.py --entity stripe                # badge(s) to stdout
    python3 readiness_badge.py --entity stripe -o badges/     # write SVG files
    python3 readiness_badge.py --product anthropic-api         # by product key
    python3 readiness_badge.py --all -o badges/               # every badge
    python3 readiness_badge.py --entity stripe --json         # records + provenance

Read-only: fetches the public dataset, never applies for or redeems anything.
"""
from __future__ import annotations

import argparse
import json
import urllib.request

DATASET_URL = "https://sourcey.com/agent-readiness.json"
COMPANIES_URL = "https://sourcey.com/companies.json"
REGISTRY = "https://sourcey.com"

GRADE_COLORS = {
    "A+": "#2ea44f", "A": "#2ea44f",
    "B": "#97ca00", "B+": "#7cbf00",
    "C": "#dfb317", "C+": "#cbbe15",
    "D": "#fe7d37", "D+": "#f39249",
    "F": "#e05d44",
}
UNKNOWN_COLOR = "#9f9f9f"
LABEL = "agent readiness"
DATASET_RELEASE = None


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"user-agent": "readiness-badges/1.0 (+read-only)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_registry():
    readiness = json.loads(fetch(DATASET_URL))
    companies = json.loads(fetch(COMPANIES_URL))
    by_id = {c["entity_id"]: c for c in companies.get("companies", [])}
    global DATASET_RELEASE
    DATASET_RELEASE = readiness.get("release_id")
    return readiness, by_id


def grade_of(profile: dict) -> tuple[str, str]:
    g = (profile.get("grade") or "?").strip().upper()
    if not g or g == "?":
        g = "unrated"
    color = GRADE_COLORS.get(g, UNKNOWN_COLOR)
    return g, color


def date_of(profile: dict) -> str:
    return (profile.get("last_tested_at") or profile.get("effective_from") or "")[:10]


def product_of(profile: dict) -> tuple[str, str]:
    prod = (profile.get("scope") or {}).get("product") or {}
    return prod.get("key") or "", prod.get("name") or ""


def funnel_of(profile: dict) -> str:
    return ((profile.get("scope") or {}).get("funnel") or {}).get("name") or ""


def report_url(profile: dict, company: dict) -> str:
    return (profile.get("canonical_url")
            or (company or {}).get("website")
            or REGISTRY)


def badge_svg(grade: str, color: str, date: str, scope: str = "") -> str:
    """Two-segment shields-style badge: label | grade (+ product scope + date)."""
    right = grade
    if scope:
        right += " \u00b7 " + scope
    if date:
        right += " \u00b7 " + date[:7]
    label_w = 13 + 7.2 * len(LABEL)
    right_w = 13 + 7.2 * len(right) + 6
    total_w = int(label_w + right_w)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="20" role="img" aria-label="{LABEL}: {grade}">
  <title>{LABEL}: {grade} (Sourcey)</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r"><rect width="{total_w}" height="20" rx="3" fill="#fff"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="{int(label_w)}" height="20" fill="#555"/>
    <rect x="{int(label_w)}" width="{int(right_w)}" height="20" fill="{color}"/>
    <rect width="{total_w}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{int(label_w / 2)}" y="15">{LABEL}</text>
    <text x="{int(label_w + right_w / 2)}" y="15">{esc(right)}</text>
  </g>
</svg>
'''


def render_one(profile: dict, company: dict):
    grade, color = grade_of(profile)
    _pk, prod_name = product_of(profile)
    co_name = (company or {}).get("name") or ""
    scope = prod_name
    if scope and co_name and scope.lower().startswith(co_name.lower()):
        scope = ""  # scope repeats the company name - keep the badge tight
    svg = badge_svg(grade, color, date_of(profile), scope)
    record = {
        "entity_id": profile.get("entity_id"),
        "company": co_name or None,
        "product": prod_name or None,
        "funnel": funnel_of(profile) or None,
        "grade": grade,
        "last_tested_at": profile.get("last_tested_at"),
        "report_url": report_url(profile, company or {}),
        "release_id": DATASET_RELEASE,
    }
    return svg, record


def file_stem(profile: dict, company: dict) -> str:
    slug = (company or {}).get("slug") or (profile.get("entity_id") or "unknown")
    pk, _ = product_of(profile)
    return f"{slug}-{pk}-readiness" if pk else f"{slug}-readiness"


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="readiness-badges",
        description="Generate shields-style Agent Readiness badges from the "
                    "Sourcey open registry. Read-only, zero dependencies.",
        epilog="Data: https://sourcey.com — every badge names the product "
               "scope and test date, and every record carries the release_id. "
               "Not an official Sourcey product.")
    ap.add_argument("--entity", help="company slug or entity_id")
    ap.add_argument("--product", help="product key, e.g. anthropic-api")
    ap.add_argument("--list", action="store_true", help="list graded entities")
    ap.add_argument("--all", action="store_true", help="render all badges")
    ap.add_argument("-o", "--out", help="output directory for SVG files")
    ap.add_argument("--json", action="store_true", help="emit records JSON instead of SVG")
    args = ap.parse_args()

    readiness, by_id = load_registry()
    profiles = readiness.get("profiles", [])

    if args.list or not (args.entity or args.product or args.all):
        rows = []
        for p in profiles:
            co = by_id.get(p.get("entity_id"), {})
            rows.append((co.get("slug") or p["entity_id"],
                         product_of(p)[1], grade_of(p)[0], date_of(p)))
        print(f"release: {readiness.get('release_id', '?')[:30]}…  profiles: {len(profiles)}")
        for slug, prod, grade, date in sorted(rows):
            print(f"  {slug:<28} {prod[:34]:<36} {grade:<8} {date}")
        if not (args.entity or args.product or args.all):
            return

    if args.entity or args.product:
        want = (args.entity or args.product).lower()
        matches = []
        for p in profiles:
            co = by_id.get(p.get("entity_id"), {})
            pk, _ = product_of(p)
            if want in ((co.get("slug") or "").lower(),
                        (p.get("entity_id") or "").lower(),
                        pk.lower()):
                matches.append((p, co))
        if not matches:
            raise SystemExit(f"no Agent Readiness profile matched '{want}' "
                             f"(use --list to see graded entities)")
        import os
        records = []
        for p, co in matches:
            svg, record = render_one(p, co)
            records.append(record)
            if args.json:
                continue
            if args.out:
                os.makedirs(args.out, exist_ok=True)
                path = os.path.join(args.out, file_stem(p, co) + ".svg")
                with open(path, "w") as f:
                    f.write(svg)
                print(path)
            else:
                print(svg, end="")
        if args.json:
            print(json.dumps(records if len(records) > 1 else records[0], indent=2))
        return

    if args.all:
        import os
        out = args.out or "badges"
        os.makedirs(out, exist_ok=True)
        made = 0
        for p in profiles:
            co = by_id.get(p.get("entity_id"), {})
            svg, _rec = render_one(p, co)
            with open(os.path.join(out, file_stem(p, co) + ".svg"), "w") as f:
                f.write(svg)
            made += 1
        print(f"rendered {made} badges into {out} "
              f"(release {readiness.get('release_id', '?')[:20]}…)")


if __name__ == "__main__":
    main()
