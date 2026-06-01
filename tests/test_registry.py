"""Registry tests: parsing, validation, var substitution, and the shipped
``sources.toml`` being internally consistent.
"""

from __future__ import annotations

import pytest

from opendata_fetch.registry import (
    RegistryError,
    get_source,
    list_sources,
    load_registry,
)


def _write(tmp_path, text: str):
    p = tmp_path / "sources.toml"
    p.write_text(text)
    return p


def test_shipped_registry_loads():
    sources = list_sources()
    assert len(sources) == 10
    slugs = {s.slug for s in sources}
    assert "05-cdc-svi" in slugs
    assert "01-nces-schools" in slugs


def test_shipped_registry_has_no_unsubstituted_vars():
    for s in list_sources():
        for f in s.files:
            assert "{" not in f.url, f"{s.slug}: {f.url}"
            assert "{" not in f.dest, f"{s.slug}: {f.dest}"


def test_shipped_registry_min_bytes_present():
    # Every shipped file declares an integrity floor.
    for s in list_sources():
        for f in s.files:
            assert f.min_bytes and f.min_bytes > 0, f"{s.slug}/{f.dest} missing min_bytes"


def test_var_substitution(tmp_path):
    path = _write(
        tmp_path,
        """
        [[source]]
        slug = "x"
        agency = "A"
        dataset = "D"
        vars = { vintage = "2024" }
        [[source.files]]
        url = "https://x.gov/{vintage}/f.csv"
        dest = "f_{vintage}.csv"
        min_bytes = 10
        """,
    )
    src = get_source("x", path)
    assert src.files[0].url == "https://x.gov/2024/f.csv"
    assert src.files[0].dest == "f_2024.csv"


def test_undefined_var_raises(tmp_path):
    path = _write(
        tmp_path,
        """
        [[source]]
        slug = "x"
        agency = "A"
        dataset = "D"
        [[source.files]]
        url = "https://x.gov/{vintage}/f.csv"
        dest = "f.csv"
        """,
    )
    with pytest.raises(RegistryError, match="undefined var"):
        load_registry(path)


def test_missing_required_field_raises(tmp_path):
    path = _write(
        tmp_path,
        """
        [[source]]
        slug = "x"
        dataset = "D"
        [[source.files]]
        url = "https://x.gov/f.csv"
        dest = "f.csv"
        """,
    )
    with pytest.raises(RegistryError, match="missing required field 'agency'"):
        load_registry(path)


def test_handler_and_files_mutually_exclusive(tmp_path):
    path = _write(
        tmp_path,
        """
        [[source]]
        slug = "x"
        agency = "A"
        dataset = "D"
        handler = "mod:fn"
        [[source.files]]
        url = "https://x.gov/f.csv"
        dest = "f.csv"
        """,
    )
    with pytest.raises(RegistryError, match="both 'handler' and 'files'"):
        load_registry(path)


def test_neither_handler_nor_files_raises(tmp_path):
    path = _write(
        tmp_path,
        """
        [[source]]
        slug = "x"
        agency = "A"
        dataset = "D"
        """,
    )
    with pytest.raises(RegistryError, match="neither 'handler' nor 'files'"):
        load_registry(path)


def test_custom_source_flag(tmp_path):
    path = _write(
        tmp_path,
        """
        [[source]]
        slug = "x"
        agency = "A"
        dataset = "D"
        handler = "opendata_fetch.fetchers.example:fetch"
        """,
    )
    src = get_source("x", path)
    assert src.is_custom
    assert src.handler == "opendata_fetch.fetchers.example:fetch"


def test_duplicate_slug_raises(tmp_path):
    path = _write(
        tmp_path,
        """
        [[source]]
        slug = "x"
        agency = "A"
        dataset = "D"
        [[source.files]]
        url = "https://x.gov/a.csv"
        dest = "a.csv"

        [[source]]
        slug = "x"
        agency = "B"
        dataset = "E"
        [[source.files]]
        url = "https://x.gov/b.csv"
        dest = "b.csv"
        """,
    )
    with pytest.raises(RegistryError, match="Duplicate source slug"):
        load_registry(path)


def test_unknown_slug_raises():
    with pytest.raises(RegistryError, match="Unknown source"):
        get_source("99-does-not-exist")
