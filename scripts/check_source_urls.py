#!/usr/bin/env python3
"""Health-check every declarative source URL in the registry.

Government download URLs rot silently: a new vintage ships, the old path 404s,
and nothing in opendata-fetch notices until someone runs `fetch`. This script
probes each URL with a tiny ranged GET (so it doesn't pull whole files) and
reports which ones are broken. It is run weekly by CI (see
`.github/workflows/url-health.yml`) and can be run by hand:

    python scripts/check_source_urls.py

Exit code: 0 if every URL is reachable, 1 if any is broken. Custom-handler
sources are skipped (they have no static URL list).

Not part of the installed package; it only imports the registry.
"""

from __future__ import annotations

import sys
import urllib.error
import urllib.request

from opendata_fetch.engine import USER_AGENT
from opendata_fetch.registry import list_sources

TIMEOUT = 45.0
# HTTP statuses that mean "the server answered and the resource is there".
# 403 is included because several federal endpoints reject bot-ish requests
# yet the URL itself is valid; 416 means the range wasn't satisfiable but the
# file exists. Real rot shows up as 404/410 or a connection failure.
REACHABLE = {200, 206, 403, 416}


def _attempt(url: str, use_range: bool) -> int:
    headers = {"User-Agent": USER_AGENT}
    if use_range:
        headers["Range"] = "bytes=0-0"
    req = urllib.request.Request(url, method="GET", headers=headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        resp.read(1)  # touch the body, then abandon the rest
        return resp.status


def probe(url: str) -> tuple[str, str]:
    """Return (status, detail) for one URL. status is 'ok', 'warn', or 'broken'.

    Tries a 1-byte ranged GET first (cheap); if that fails at the connection
    level, retries once with a plain GET, because some federal endpoints
    (notably ArcGIS) drop ranged requests even though the URL is fine.
    """
    last: tuple[str, str] = ("broken", "no attempt")
    for use_range in (True, False):
        try:
            return "ok", f"HTTP {_attempt(url, use_range)}"
        except urllib.error.HTTPError as e:
            if e.code in REACHABLE:
                return "ok", f"HTTP {e.code}"
            if 500 <= e.code < 600:
                return "warn", f"HTTP {e.code} (server error, may be transient)"
            return "broken", f"HTTP {e.code}"  # 404/410 etc: retrying won't help
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last = ("broken", f"{type(e).__name__}: {e}")  # retry without Range
    return last


def main() -> int:
    broken: list[str] = []
    warned: list[str] = []
    print("Checking source URLs...\n")
    for source in list_sources():
        if source.is_custom:
            print(f"[{source.slug}] custom handler — skipped")
            continue
        for f in source.files:
            status, detail = probe(f.url)
            marker = {"ok": "OK  ", "warn": "WARN", "broken": "FAIL"}[status]
            print(f"[{source.slug}] {marker}  {detail}  {f.url}")
            if status == "broken":
                broken.append(f"{source.slug}: {f.url} ({detail})")
            elif status == "warn":
                warned.append(f"{source.slug}: {f.url} ({detail})")

    print()
    if warned:
        print(f"{len(warned)} warning(s) (transient server errors):")
        for w in warned:
            print(f"  - {w}")
    if broken:
        print(f"\n{len(broken)} BROKEN url(s):")
        for b in broken:
            print(f"  - {b}")
        return 1
    print("All source URLs reachable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
