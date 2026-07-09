"""Run a source: download its files (or invoke its custom handler).

Sits between the registry (what to fetch) and the engine (how to fetch). The
library entry point ``opendata_fetch.fetch`` and the CLI both call ``fetch_source``.
"""

from __future__ import annotations

import importlib
import json
import logging
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from opendata_fetch.engine import download_file, extract_archive, sha256_file
from opendata_fetch.registry import Source, get_source

log = logging.getLogger(__name__)

MANIFEST_NAME = "manifest.json"


def fetch_source(
    slug: str,
    *,
    dest: str | Path = "data",
    force: bool = False,
    extract: bool = False,
) -> list[Path]:
    """Download every file for ``slug`` into ``dest/<slug>/``.

    Custom sources (those with a ``handler``) delegate to their handler, which
    is responsible for its own download and extraction logic.

    Returns the list of downloaded file paths.
    """
    source = get_source(slug)
    dest_dir = Path(dest) / slug

    if source.is_custom:
        return _run_handler(source, dest_dir, force=force, extract=extract)

    log.info("[%s] %s — %s", source.slug, source.agency, source.dataset)
    dest_dir.mkdir(parents=True, exist_ok=True)

    downloaded: list[Path] = []
    entries: list[dict] = []
    for f in source.files:
        path = download_file(
            f.url,
            dest_dir / f.dest,
            force=force,
            expected_min_bytes=f.min_bytes,
            expected_sha256=f.sha256,
        )
        downloaded.append(path)
        entries.append(
            {
                "dest": f.dest,
                "url": f.url,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    _write_manifest(dest_dir, source, entries)

    if extract:
        _extract_zips(downloaded)

    return downloaded


def _write_manifest(dest_dir: Path, source: Source, entries: list[dict]) -> None:
    """Write a provenance manifest recording what was fetched, when, and its hash.

    The recorded sha256 values are also the numbers you would copy into a
    source's ``sha256`` registry field to pin an immutable file.
    """
    manifest = {
        "slug": source.slug,
        "agency": source.agency,
        "dataset": source.dataset,
        "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "files": entries,
    }
    (dest_dir / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2) + "\n")


def _extract_zips(paths: list[Path]) -> None:
    for path in paths:
        if path.suffix.lower() == ".zip" and zipfile.is_zipfile(path):
            extract_archive(path)


def _run_handler(source: Source, dest_dir: Path, *, force: bool, extract: bool) -> list[Path]:
    """Resolve and call a custom fetcher named as ``module:callable``."""
    spec = source.handler or ""
    if ":" not in spec:
        raise ValueError(
            f"Source '{source.slug}' handler must be 'module:callable', got {spec!r}"
        )
    module_name, func_name = spec.split(":", 1)
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    return func(source, dest_dir, force=force, extract=extract)
