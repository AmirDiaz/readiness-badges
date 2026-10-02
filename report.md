# readiness-badges — delivery report

## What was built

`readiness-badges` generates shields-style SVG badges from Sourcey's Agent Readiness report cards (25 published profiles as of 2026-10-02, release sha256:8094c042…). Badges name the product scope and month last tested; JSON records carry the canonical report URL and exact release_id, so every badge is a verifiable citation rather than a static sticker.

## Why it exists

Sourcey's readiness grades are scoped, dated, evidence-bound facts — but there was no way to display one in a README. Vendors, integrators, and agents comparing services benefit from a standard visual that links back to the canonical report. The tool follows Sourcey's own trust-boundary guidance: cite the release, keep unknowns explicit, never present a stale grade as timeless.

## Verified behavior (live tests, 2026-10-02)

- `--list` enumerates all 25 profiles with product scopes and dates.
- `--entity cloudflare` renders BOTH published profiles (Developer Platform C+, Public DNS A+) — scope-aware, not company-flattened.
- `--product anthropic-api` selects by product key (B badge, "Anthropic API" scope shown).
- `--entity frantic --json` returns the canonical report URL (sourcey.com/c/frantic/agent-readiness/…) plus the dataset release_id.
- `--all -o badges/` rendered all 25 SVGs to disk.
- Unmatched entities exit non-zero with guidance — no fabricated grades.
- Zero third-party dependencies (argparse/json/urllib/os).

## Trust boundary

Read-only consumer of the two public JSON datasets. Never applies for, redeems, ranks, or purchases anything. Unrated renders gray "unrated". Not an official Sourcey product.

## Files

- `readiness_badge.py` — the tool (single file, stdlib only)
- `README.md` — usage + design rules + data sources
- `evidence.json` — machine-readable evidence packet
- `badges/` — all 25 rendered example badges
