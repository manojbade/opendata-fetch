"""opendata-fetch: reliably download U.S. government open datasets as the agencies ship them.

opendata-fetch is a thin, dependency-free fetcher. It downloads the raw file an
agency publishes (CSV, GeoJSON, shapefile zip, ...) with retries, atomic
writes, size/integrity checks, and HTML/JSON error-page detection. It does not
transform, reshape, or subset the data: you get the file exactly as the agency
serves it. What you do with it afterwards is up to you.

Library usage::

    import opendata_fetch

    # Download one source into ./data
    paths = opendata_fetch.fetch("05-cdc-svi", dest="data")

    # List everything in the registry
    for src in opendata_fetch.list_sources():
        print(src.slug, src.dataset)
"""

from __future__ import annotations

from opendata_fetch.engine import (
    DownloadError,
    download_file,
    extract_archive,
    sha256_file,
)
from opendata_fetch.registry import Source, get_source, list_sources, load_registry

__version__ = "0.2.0"


def fetch(
    slug: str,
    *,
    dest: str = "data",
    force: bool = False,
    extract: bool = False,
):
    """Download every file for source ``slug`` into ``dest/<slug>/``.

    Args:
        slug: Source identifier, e.g. ``"05-cdc-svi"``. See ``list_sources()``.
        dest: Root directory for downloads. Files land in ``dest/<slug>/``.
        force: Re-download even if the file already exists.
        extract: After download, unzip any ``.zip`` archives in place (the
            whole archive, not selected members).

    Returns:
        List of ``pathlib.Path`` for each downloaded file.
    """
    # Imported lazily so importing the package doesn't pull in the runner.
    from opendata_fetch.runner import fetch_source

    return fetch_source(slug, dest=dest, force=force, extract=extract)


__all__ = [
    "fetch",
    "list_sources",
    "get_source",
    "load_registry",
    "Source",
    "download_file",
    "extract_archive",
    "sha256_file",
    "DownloadError",
    "__version__",
]
