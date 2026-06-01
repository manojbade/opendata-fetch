"""Custom fetchers: the escape hatch for sources that can't be expressed as
plain declarative config in ``sources.toml``.

Most datasets are a fixed set of URLs you download and (optionally)
unzip. Those live entirely in ``sources.toml`` with no code. A handful are
irregular: they require discovery calls, pagination, or assembling many files
into one logical dataset (e.g. FEMA's National Flood Hazard Layer, which is
distributed as ~2,600 separate county zips discovered via a search endpoint).

For those, a source entry in ``sources.toml`` sets a ``handler`` pointing at a
callable in this package instead of listing ``files``::

    [[source]]
    slug = "11-fema-nfhl"
    handler = "opendata_fetch.fetchers.fema_nfhl:fetch"

The handler must expose a callable with the signature::

    def fetch(source, dest_dir, *, force=False, extract=False) -> list[Path]:
        ...

where ``source`` is the :class:`opendata_fetch.registry.Source` and ``dest_dir`` is
the resolved ``dest/<slug>/`` directory.

No custom fetchers ship in v1. This package is the documented extension point.
"""
