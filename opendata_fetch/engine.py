"""HTTP download engine and archive extraction.

Stdlib only (urllib + ssl + zipfile). Government data files range from a few hundred
KB to ~700 MB; downloads stream in 1 MB blocks to a temporary ``.part`` file
beside the destination, then rename atomically so a half-written file is never
visible. If the destination exists and ``force`` is not set, the network call
is skipped.

Two guardrails catch the most common government-endpoint failure modes:

* ``expected_min_bytes`` rejects truncated downloads.
* a small header sniff rejects HTML error pages and JSON error envelopes that
  some ArcGIS / Akamai-fronted endpoints return with a 200 status.
"""

from __future__ import annotations

import hashlib
import logging
import os
import shutil
import ssl
import subprocess
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

log = logging.getLogger(__name__)

# Identify ourselves to agency server logs. Avoids the default
# "Python-urllib/3.x" User-Agent, which some Akamai-fronted endpoints
# rate-limit aggressively.
USER_AGENT = "opendata-fetch/0.1 (+https://github.com/manojbade/opendata-fetch)"

_BLOCK_SIZE = 1024 * 1024  # 1 MB streaming block


class DownloadError(RuntimeError):
    """Raised when a download cannot be completed or fails a guardrail."""


def sha256_file(path: Path | str) -> str:
    """Return the hex SHA-256 digest of a file, read in bounded blocks."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(_BLOCK_SIZE)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def download_file(
    url: str,
    dest_path: Path | str,
    *,
    force: bool = False,
    expected_min_bytes: int | None = None,
    expected_sha256: str | None = None,
    retries: int = 3,
    backoff_seconds: float = 5.0,
    timeout_seconds: float = 300.0,
) -> Path:
    """Download ``url`` to ``dest_path``. Idempotent: skip if the file exists.

    Args:
        url: HTTP(S) URL to fetch.
        dest_path: Local path to write to. Parent directories are created.
        force: If True, re-download even when the file already exists.
        expected_min_bytes: If set, raise :class:`DownloadError` when the
            downloaded file is smaller than this (catches truncated downloads
            and HTML error pages).
        expected_sha256: If set, the downloaded file must match this digest or
            :class:`DownloadError` is raised. Also upgrades the idempotent skip
            from "a file exists" to "a *valid* file exists": an on-disk file
            whose hash differs is re-downloaded. Only set this for immutable
            files; rolling feeds would fail every time.
        retries: Number of attempts before giving up.
        backoff_seconds: Initial backoff between retries; doubled each retry.
        timeout_seconds: Socket timeout per attempt.

    Returns:
        The destination :class:`~pathlib.Path`.

    Raises:
        DownloadError: if all attempts fail or a guardrail rejects the payload.
    """
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if dest_path.exists() and not force:
        if expected_sha256 is None:
            log.info("  skip (already exists): %s", dest_path.name)
            return dest_path
        if sha256_file(dest_path).lower() == expected_sha256.lower():
            log.info("  skip (cached copy matches sha256): %s", dest_path.name)
            return dest_path
        log.info("  cached copy sha256 mismatch, re-downloading: %s", dest_path.name)

    tmp_path = dest_path.with_suffix(dest_path.suffix + ".part")
    ssl_ctx = ssl.create_default_context()

    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            log.info("  downloading (attempt %d/%d): %s", attempt, retries, url)
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout_seconds, context=ssl_ctx) as resp:
                with open(tmp_path, "wb") as out:
                    while True:
                        block = resp.read(_BLOCK_SIZE)
                        if not block:
                            break
                        out.write(block)

            _check_size(tmp_path, expected_min_bytes, url)
            _sniff_error_payload(tmp_path, url)
            _check_sha256(tmp_path, expected_sha256, url)

            os.replace(tmp_path, dest_path)  # atomic
            size = dest_path.stat().st_size
            log.info("  wrote %s (%.1f MB)", dest_path.name, size / 1024 / 1024)
            return dest_path

        except (urllib.error.URLError, OSError, DownloadError) as e:
            last_err = e
            log.warning("  attempt %d failed: %s", attempt, e)
            if tmp_path.exists():
                tmp_path.unlink()
            if attempt < retries:
                sleep_for = backoff_seconds * (2 ** (attempt - 1))
                log.info("  retrying in %.1fs", sleep_for)
                time.sleep(sleep_for)

    raise DownloadError(
        f"Download failed after {retries} attempts: {url} (last error: {last_err})"
    )


def _check_size(path: Path, expected_min_bytes: int | None, url: str) -> None:
    if expected_min_bytes is None:
        return
    size = path.stat().st_size
    if size < expected_min_bytes:
        raise DownloadError(
            f"Downloaded file is suspiciously small: {size:,} bytes "
            f"(expected at least {expected_min_bytes:,}). URL: {url}"
        )


def _check_sha256(path: Path, expected_sha256: str | None, url: str) -> None:
    if expected_sha256 is None:
        return
    got = sha256_file(path)
    if got.lower() != expected_sha256.lower():
        raise DownloadError(
            f"Downloaded file failed sha256 check: got {got}, "
            f"expected {expected_sha256}. URL: {url}"
        )


def _sniff_error_payload(path: Path, url: str) -> None:
    """Reject HTML error pages and JSON error envelopes served with a 200."""
    with open(path, "rb") as fh:
        head = fh.read(200).lstrip()
    lowered = head[:9].lower()
    if lowered.startswith(b"<html") or lowered.startswith(b"<!doctype"):
        raise DownloadError(
            f"Downloaded payload looks like an HTML page (likely an error or "
            f"rate-limit page) from {url}; first bytes: {head[:80]!r}"
        )
    if head.startswith(b'{"error"'):
        raise DownloadError(
            f"Downloaded payload is a JSON error envelope from {url}; "
            f"first bytes: {head[:200]!r}"
        )


def extract_archive(zip_path: Path | str, dest_dir: Path | str | None = None) -> Path:
    """Extract a whole ``.zip`` archive into a sibling folder.

    Unlike pipeline tools that pick individual members, opendata-fetch extracts the
    entire archive. This is the only correct generic behavior: a shapefile is a
    bundle (``.shp`` + ``.dbf`` + ``.shx`` + ``.prj``) that must stay together,
    and some archives ship several useful files.

    Args:
        zip_path: Path to a ``.zip`` file.
        dest_dir: Directory to extract into. Defaults to a folder named after
            the archive (without the ``.zip`` suffix) beside the archive.

    Returns:
        The extraction directory.
    """
    zip_path = Path(zip_path)
    if not zipfile.is_zipfile(zip_path):
        raise DownloadError(f"Not a valid zip archive: {zip_path}")

    if dest_dir is None:
        dest_dir = zip_path.with_suffix("")
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path) as zf:
            _safe_extractall(zf, dest_dir)
    except NotImplementedError:
        # Stdlib zipfile cannot decompress DEFLATE64 (compression method 9),
        # which some government archives use (e.g. NCES CCD zips). Fall back to
        # the system `unzip`, which handles every method these sources ship.
        _extract_with_unzip(zip_path, dest_dir)

    log.info("  extracted %s -> %s/", zip_path.name, dest_dir.name)
    return dest_dir


def _extract_with_unzip(zip_path: Path, dest_dir: Path) -> None:
    unzip = shutil.which("unzip")
    if unzip is None:
        raise DownloadError(
            f"{zip_path.name} uses a compression method Python's zipfile cannot "
            f"read (likely DEFLATE64), and the 'unzip' command is not installed. "
            f"Install unzip, or extract this archive manually."
        )
    result = subprocess.run(
        [unzip, "-o", "-q", str(zip_path), "-d", str(dest_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise DownloadError(
            f"unzip failed on {zip_path.name} (exit {result.returncode}): "
            f"{result.stderr.strip()}"
        )


def _safe_extractall(zf: zipfile.ZipFile, dest_dir: Path) -> None:
    """Extract all members, refusing any that would escape ``dest_dir``.

    Guards against path-traversal entries (``../`` or absolute paths) in a
    downloaded archive (CVE-2007-4559 class).
    """
    dest_root = dest_dir.resolve()
    for member in zf.namelist():
        target = (dest_dir / member).resolve()
        if not (target == dest_root or dest_root in target.parents):
            raise DownloadError(
                f"Refusing to extract '{member}': path escapes destination dir"
            )
    zf.extractall(dest_dir)
