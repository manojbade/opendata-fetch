"""Runner tests: download dispatch, extract toggle, and custom-handler routing.
``download_file`` is patched so no network or real files are needed.
"""

from __future__ import annotations

import zipfile

import pytest

from opendata_fetch import runner
from opendata_fetch.registry import RegistryError


def _toml(tmp_path, text):
    p = tmp_path / "sources.toml"
    p.write_text(text)
    return p


def test_fetch_source_downloads_all_files(tmp_path, monkeypatch):
    path = _toml(
        tmp_path,
        """
        [[source]]
        slug = "x"
        agency = "A"
        dataset = "D"
        [[source.files]]
        url = "https://x.gov/a.csv"
        dest = "a.csv"
        min_bytes = 5
        [[source.files]]
        url = "https://x.gov/b.csv"
        dest = "b.csv"
        min_bytes = 5
        """,
    )
    monkeypatch.setattr(runner, "get_source", lambda slug: __import__(
        "opendata_fetch.registry", fromlist=["get_source"]
    ).get_source(slug, path))

    seen = []

    def fake_download(url, dest, *, force, expected_min_bytes):
        seen.append((url, str(dest), force, expected_min_bytes))
        return dest

    monkeypatch.setattr(runner, "download_file", fake_download)

    paths = runner.fetch_source("x", dest=tmp_path / "out", force=True)
    assert len(paths) == 2
    assert seen[0][0] == "https://x.gov/a.csv"
    assert seen[0][2] is True  # force threaded through
    assert seen[0][3] == 5  # min_bytes threaded through
    assert str(paths[0]).endswith("out/x/a.csv")


def test_extract_only_touches_zips(tmp_path, monkeypatch):
    path = _toml(
        tmp_path,
        """
        [[source]]
        slug = "x"
        agency = "A"
        dataset = "D"
        [[source.files]]
        url = "https://x.gov/a.csv"
        dest = "a.csv"
        [[source.files]]
        url = "https://x.gov/b.zip"
        dest = "b.zip"
        """,
    )
    monkeypatch.setattr(runner, "get_source", lambda slug: __import__(
        "opendata_fetch.registry", fromlist=["get_source"]
    ).get_source(slug, path))

    out_dir = tmp_path / "out" / "x"
    out_dir.mkdir(parents=True)
    csv_file = out_dir / "a.csv"
    csv_file.write_text("col\n1\n")
    zip_file = out_dir / "b.zip"
    with zipfile.ZipFile(zip_file, "w") as zf:
        zf.writestr("inner.txt", b"hi")

    monkeypatch.setattr(runner, "download_file", lambda url, dest, **k: dest)

    extracted = []
    monkeypatch.setattr(runner, "extract_archive", lambda p: extracted.append(p))

    runner.fetch_source("x", dest=tmp_path / "out", extract=True)
    assert extracted == [zip_file]  # only the zip, not the csv


def test_custom_handler_invoked(tmp_path, monkeypatch):
    path = _toml(
        tmp_path,
        """
        [[source]]
        slug = "x"
        agency = "A"
        dataset = "D"
        handler = "tests.test_runner:_demo_handler"
        """,
    )
    monkeypatch.setattr(runner, "get_source", lambda slug: __import__(
        "opendata_fetch.registry", fromlist=["get_source"]
    ).get_source(slug, path))

    result = runner.fetch_source("x", dest=tmp_path / "out", force=True, extract=True)
    assert result == ["handled:x:force=True:extract=True"]


def _demo_handler(source, dest_dir, *, force, extract):
    return [f"handled:{source.slug}:force={force}:extract={extract}"]


def test_bad_handler_spec_raises(tmp_path, monkeypatch):
    path = _toml(
        tmp_path,
        """
        [[source]]
        slug = "x"
        agency = "A"
        dataset = "D"
        handler = "no_colon_here"
        """,
    )
    monkeypatch.setattr(runner, "get_source", lambda slug: __import__(
        "opendata_fetch.registry", fromlist=["get_source"]
    ).get_source(slug, path))
    with pytest.raises(ValueError, match="module:callable"):
        runner.fetch_source("x", dest=tmp_path / "out")


def test_unknown_slug_propagates():
    with pytest.raises(RegistryError):
        runner.fetch_source("99-nope")
