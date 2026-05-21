#!/usr/bin/env python3
"""Write content/robots.txt for TableJourney."""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "content" / "robots.txt"

BODY = """\
# TableJourney
# Policy: open to all well-behaved crawlers, including AI retrieval and
# training bots. Editorial referrals from AI search (ChatGPT, Perplexity,
# Claude, Google AI Overviews, etc.) are an explicit growth channel.
User-agent: *
Allow: /
Disallow: /search?
Disallow: /api/

Sitemap: https://tablejourney.com/sitemap.xml
"""


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(BODY, encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
