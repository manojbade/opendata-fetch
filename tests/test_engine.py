"""Engine tests. HTTP is mocked at the urlopen boundary so nothing hits the
network. Covers the success path plus every guardrail and the extractor.
"""

from __future__ import annotations

import hashlib
import io
import zipfile
from contextlib import contextmanager

import pytest

from opendata_fetch import engine
from opendata_fetch.engine import (
    DownloadError,
    download_file,
    extract_archive,
    sha256_file,
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class _FakeResponse:
    """Minimal stand-in for the urlopen context manager."""

    def __init__(self, payload: bytes):
        self._buf = io.BytesIO(payload)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self, n: int = -1) -> bytes:
        return self._buf.read(n)


@contextmanager
def _patch_urlopen(monkeypatch, payload: bytes):
    def fake_urlopen(req, timeout=None, context=None):
        return _FakeResponse(payload)

    monkeypatch.setattr(engine.urllib.request, "urlopen", fake_urlopen)
    yield


def test_download_success(tmp_path, monkeypatch):
    dest = tmp_path / "out.csv"
    with _patch_urlopen(monkeypatch, b"col1,col2\n1,2\n"):
        result = download_file("https://x.gov/f.csv", dest)
    assert result == dest
    assert dest.read_bytes() == b"col1,col2\n1,2\n"
    assert not dest.with_suffix(".csv.part").exists()  # temp cleaned up


def test_idempotent_skip(tmp_path, monkeypatch):
    dest = tmp_path / "out.csv"
    dest.write_bytes(b"existing")

    def explode(*a, **k):
        raise AssertionError("network should not be hit when file exists")

    monkeypatch.setattr(engine.urllib.request, "urlopen", explode)
    assert download_file("https://x.gov/f.csv", dest) == dest
    assert dest.read_bytes() == b"existing"


def test_force_redownloads(tmp_path, monkeypatch):
    dest = tmp_path / "out.csv"
    dest.write_bytes(b"old")
    with _patch_urlopen(monkeypatch, b"new-bytes-here"):
        download_file("https://x.gov/f.csv", dest, force=True)
    assert dest.read_bytes() == b"new-bytes-here"


def test_min_bytes_rejects_truncated(tmp_path, monkeypatch):
    dest = tmp_path / "out.csv"
    with _patch_urlopen(monkeypatch, b"tiny"):
        with pytest.raises(DownloadError, match="suspiciously small"):
            download_file("https://x.gov/f.csv", dest, expected_min_bytes=1000, retries=1)
    assert not dest.exists()  # nothing left behind on failure


def test_html_error_page_rejected(tmp_path, monkeypatch):
    dest = tmp_path / "out.csv"
    with _patch_urlopen(monkeypatch, b"<!DOCTYPE html><html>rate limited</html>"):
        with pytest.raises(DownloadError, match="HTML page"):
            download_file("https://x.gov/f.csv", dest, retries=1)


def test_json_error_envelope_rejected(tmp_path, monkeypatch):
    dest = tmp_path / "out.json"
    with _patch_urlopen(monkeypatch, b'{"error":{"code":429}}'):
        with pytest.raises(DownloadError, match="JSON error envelope"):
            download_file("https://x.gov/f.json", dest, retries=1)


def test_retry_then_success(tmp_path, monkeypatch):
    dest = tmp_path / "out.csv"
    calls = {"n": 0}

    def flaky_urlopen(req, timeout=None, context=None):
        calls["n"] += 1
        if calls["n"] == 1:
            raise OSError("transient connection reset")
        return _FakeResponse(b"recovered-payload")

    monkeypatch.setattr(engine.urllib.request, "urlopen", flaky_urlopen)
    monkeypatch.setattr(engine.time, "sleep", lambda *_: None)  # no real backoff
    download_file("https://x.gov/f.csv", dest, retries=3)
    assert calls["n"] == 2
    assert dest.read_bytes() == b"recovered-payload"


def test_all_retries_fail(tmp_path, monkeypatch):
    dest = tmp_path / "out.csv"

    def always_fail(req, timeout=None, context=None):
        raise OSError("down")

    monkeypatch.setattr(engine.urllib.request, "urlopen", always_fail)
    monkeypatch.setattr(engine.time, "sleep", lambda *_: None)
    with pytest.raises(DownloadError, match="failed after 3 attempts"):
        download_file("https://x.gov/f.csv", dest, retries=3)


def test_extract_archive_whole_bundle(tmp_path):
    zip_path = tmp_path / "bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("shape.shp", b"shp")
        zf.writestr("shape.dbf", b"dbf")
        zf.writestr("shape.prj", b"prj")
    out = extract_archive(zip_path)
    assert (out / "shape.shp").exists()
    assert (out / "shape.dbf").exists()
    assert (out / "shape.prj").exists()


def test_extract_rejects_path_traversal(tmp_path):
    zip_path = tmp_path / "evil.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("../escape.txt", b"pwned")
    with pytest.raises(DownloadError, match="escapes destination"):
        extract_archive(zip_path)


def test_extract_non_zip_raises(tmp_path):
    f = tmp_path / "not.zip"
    f.write_bytes(b"plain text")
    with pytest.raises(DownloadError, match="Not a valid zip"):
        extract_archive(f)


def test_extract_falls_back_to_unzip_on_deflate64(tmp_path, monkeypatch):
    # A normal zip; we force the stdlib path to raise NotImplementedError to
    # simulate DEFLATE64, then assert the unzip fallback is used.
    zip_path = tmp_path / "d64.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("inner.txt", b"data")

    def boom(zf, dest):
        raise NotImplementedError("compression type 9 (deflate64)")

    monkeypatch.setattr(engine, "_safe_extractall", boom)

    called = {}

    def fake_unzip(zp, dest):
        called["args"] = (zp, dest)

    monkeypatch.setattr(engine, "_extract_with_unzip", fake_unzip)
    out = extract_archive(zip_path)
    assert called["args"] == (zip_path, out)


def test_unzip_fallback_errors_without_unzip(tmp_path, monkeypatch):
    monkeypatch.setattr(engine.shutil, "which", lambda name: None)
    with pytest.raises(DownloadError, match="unzip' command is not installed"):
        engine._extract_with_unzip(tmp_path / "x.zip", tmp_path)


def test_sha256_file(tmp_path):
    f = tmp_path / "x.bin"
    f.write_bytes(b"hello world")
    assert sha256_file(f) == _sha(b"hello world")


def test_sha256_match_passes(tmp_path, monkeypatch):
    payload = b"pinned-immutable-bytes"
    dest = tmp_path / "out.bin"
    with _patch_urlopen(monkeypatch, payload):
        download_file("https://x.gov/f", dest, expected_sha256=_sha(payload))
    assert dest.read_bytes() == payload


def test_sha256_mismatch_rejected(tmp_path, monkeypatch):
    dest = tmp_path / "out.bin"
    with _patch_urlopen(monkeypatch, b"actual-bytes"):
        with pytest.raises(DownloadError, match="failed sha256 check"):
            download_file("https://x.gov/f", dest, expected_sha256=_sha(b"wrong"), retries=1)
    assert not dest.exists()  # bad payload never lands at dest


def test_sha256_uppercase_pin_accepted(tmp_path, monkeypatch):
    payload = b"case-insensitive"
    dest = tmp_path / "out.bin"
    with _patch_urlopen(monkeypatch, payload):
        download_file("https://x.gov/f", dest, expected_sha256=_sha(payload).upper())
    assert dest.exists()


def test_skip_if_cached_hash_matches(tmp_path, monkeypatch):
    payload = b"already-here-and-valid"
    dest = tmp_path / "out.bin"
    dest.write_bytes(payload)

    def explode(*a, **k):
        raise AssertionError("must not hit network when cached hash matches")

    monkeypatch.setattr(engine.urllib.request, "urlopen", explode)
    download_file("https://x.gov/f", dest, expected_sha256=_sha(payload))
    assert dest.read_bytes() == payload


def test_redownload_if_cached_hash_differs(tmp_path, monkeypatch):
    dest = tmp_path / "out.bin"
    dest.write_bytes(b"stale-bytes")  # on disk but wrong hash
    fresh = b"fresh-correct-bytes"
    with _patch_urlopen(monkeypatch, fresh):
        download_file("https://x.gov/f", dest, expected_sha256=_sha(fresh))
    assert dest.read_bytes() == fresh  # replaced, not skipped
