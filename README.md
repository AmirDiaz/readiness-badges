# readiness-badges

**Shields-style Agent Readiness badges from the [Sourcey](https://sourcey.com) open registry — zero dependencies (Python 3 stdlib only).**

[Sourcey](https://sourcey.com) publishes Agent Readiness report cards for vendor APIs and SaaS services — A+ through F grades with five-stage outcomes, evidence coverage, and a canonical report URL. As of October 2, 2026, 25 profiles are published, covering products like the Anthropic API (B), Cloudflare Public DNS (A+), the Cloudflare Developer Platform (C+), the Stripe API (C+), GitHub (B+/D across products), and the Frantic bounty board (B).

`readiness-badges` turns any published profile into a badge you can drop in a README:

```text
[ agent readiness | B+ · Anthropic API · 2026-09 ]
```

Each badge names the **product scope** and the **month last tested**, and each JSON record carries the **exact `release_id`** and canonical report URL — so a badge is a verifiable citation, not a sticker.

## Install

```bash
git clone https://github.com/AmirDiaz/readiness-badges.git
cd readiness-badges
python3 readiness_badge.py --list
```

No `pip install`. No API key. Python 3.10+.

## Usage

### List everything graded

```bash
$ python3 readiness_badge.py --list
release: sha256:8094c042ec143bbd5d47c59…  profiles: 25
  algolia                     Algolia DocSearch MCP            A     2026-09-21
  anthropic                   Anthropic API                   B     2026-09-06
  cloudflare                  Cloudflare Developer Platform   C+    2026-09-06
  cloudflare                  Cloudflare 1.1.1.1 Public DNS   A+    2026-09-06
  frantic                     Frantic bounty board            B     2026-09-18
  stripe                      Stripe API                      C+    2026-09-06
  …
```

### One badge (SVG to stdout)

```bash
python3 readiness_badge.py --entity anthropic > anthropic-readiness.svg
python3 readiness_badge.py --product anthropic-api            # by product key
```

Multi-scope companies render every published profile — Cloudflare gives both its Developer Platform (C+) and Public DNS (A+) badges, each labeled with its product.

### Write badge files

```bash
python3 readiness_badge.py --entity cloudflare -o badges/
python3 readiness_badge.py --all -o badges/      # all 25
```

### Machine-readable record (with provenance)

```bash
$ python3 readiness_badge.py --entity frantic --json
{
  "entity_id": "ent_01kypvhevf4pe9r00p3zbpkkqt",
  "company": "Frantic",
  "product": "Frantic bounty board",
  "funnel": "Agent work lifecycle",
  "grade": "B",
  "last_tested_at": "2026-09-18T01:16:32.648Z",
  "report_url": "https://sourcey.com/c/frantic/agent-readiness/frantic-bounty-board/agent-work-lifecycle",
  "release_id": "sha256:8094c042ec143bbd5d47c59219c4f4abb189db6368c4a51f37a862963f9a4580"
}
```

### Embed in a README

Commit the SVG next to your README and link the canonical report:

```markdown
[![agent readiness](badges/anthropic-readiness.svg)](https://sourcey.com/c/anthropic/agent-readiness/anthropic-api/api-service-lifecycle)
```

## Design rules

- **Read-only.** The tool fetches two public JSON datasets and renders. It never applies for, redeems, ranks, or purchases anything, and never posts anywhere.
- **Grades are scoped facts, not company-wide verdicts.** The same company can hold an A+ on one product and a C+ on another; the badge always names the product.
- **Citations carry provenance.** Records include `last_tested_at`, the canonical `report_url`, and the dataset `release_id`, per Sourcey's guidance to cite an exact release rather than timeless truth.
- **Unrated means unrated.** Missing grades render gray `unrated` — never guessed.

## Data sources

- [agent-readiness.json](https://sourcey.com/agent-readiness.json) · [companies.json](https://sourcey.com/companies.json)
- Registry: [sourcey.com](https://sourcey.com) · repository: [github.com/sourcey/startup-credits](https://github.com/sourcey/startup-credits)

## License

MIT. Data belongs to Sourcey and its publishers; this tool only reads their public endpoints and labels every badge with its release.
