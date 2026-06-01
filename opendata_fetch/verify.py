"""Verify downloads still match what the agency serves today.

A source's files are skipped on re-fetch when they already exist on disk, so a
normal run never proves the live URL still works or still serves the same
bytes. ``verify`` forces a fresh download into a temporary directory and
compares it, byte-for-byte (SHA-256) and by size, against the copy already in
``dest/<slug>/``.

This is stdlib-only on purpose: it answers "did the bytes change?", not "did
the data semantically change?". A size/hash delta is the signal to go look at
the file with whatever tool fits (pandas, GDAL, jq).

Exit codes (returned to the CLI):
    0  CLEAN  — every file re-downloaded and is byte-identical
    1  DRIFT  — downloads succeeded but some bytes changed since the local copy
    2  ERROR  — a download failed, or there was no local copy to compare against
"""

from __future__ import annotations

import hashlib
import logging
import tempfile
from pathlib import Path
from typing import Any

from opendata_fetch.engine import DownloadError, download_file
from opendata_fetch.registry import get_source

log = logging.getLogger(__name__)

_HASH_BLOCK = 1024 * 1024


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(_HASH_BLOCK)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def _verify_one(slug: str, dest: str | Path) -> dict[str, Any]:
    source = get_source(slug)
    if source.is_custom:
        return {"slug": slug, "skipped": "custom handler — verify not supported"}

    local_dir = Path(dest) / slug
    comparisons: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix=f"opendata-fetch-verify-{slug}-") as tmp:
        tmp_dir = Path(tmp)
        for f in source.files:
            local = local_dir / f.dest
            entry: dict[str, Any] = {"file": f.dest}
            if not local.exists():
                entry["error"] = "no local copy to compare against (fetch it first)"
                comparisons.append(entry)
                continue
            try:
                fresh = download_file(
                    f.url, tmp_dir / f.dest, force=True, expected_min_bytes=f.min_bytes
                )
            except DownloadError as e:
                entry["error"] = f"re-download failed: {e}"
                comparisons.append(entry)
                continue

            old_size, new_size = local.stat().st_size, fresh.stat().st_size
            old_hash, new_hash = _sha256(local), _sha256(fresh)
            entry.update(
                old_size=old_size,
                new_size=new_size,
                size_delta=new_size - old_size,
                identical=old_hash == new_hash,
            )
            comparisons.append(entry)

    return {"slug": slug, "comparisons": comparisons}


def verify_sources(slugs: list[str], dest: str | Path = "data") -> int:
    """Verify each slug; print a summary; return the worst exit code (0/1/2)."""
    results = [_verify_one(slug, dest) for slug in slugs]

    print()
    print("=" * 72)
    print("FEDFETCH DOWNLOAD VERIFICATION")
    print("=" * 72)

    any_error = False
    any_drift = False

    for r in results:
        print(f"\n[{r['slug']}]")
        if "skipped" in r:
            print(f"  skipped: {r['skipped']}")
            continue
        for c in r["comparisons"]:
            if "error" in c:
                print(f"  {c['file']}: ERROR — {c['error']}")
                any_error = True
                continue
            tag = "identical" if c["identical"] else "CHANGED"
            print(
                f"  {c['file']}: [{tag}] size_delta={c['size_delta']:+,} bytes "
                f"({c['old_size']:,} -> {c['new_size']:,})"
            )
            if not c["identical"]:
                any_drift = True

    print()
    print("=" * 72)
    if any_error:
        print("RESULT: ERROR (one or more files could not be verified)")
        return 2
    if any_drift:
        print("RESULT: DRIFT (downloads succeeded; some bytes changed since local copy)")
        return 1
    print("RESULT: CLEAN (every file re-downloaded byte-identical)")
    return 0
