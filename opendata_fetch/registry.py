"""Source registry: loads and validates ``sources.toml``.

A source is either *declarative* (a fixed list of files to download) or
*custom* (a ``handler`` callable, for irregular sources like FEMA's per-county
flood layer). Most sources are declarative.

``{var}`` placeholders in a file's ``url`` and ``dest`` are substituted from
the source's ``vars`` table. This is how a maintainer bumps a dataset to a new
vintage: change one value in ``vars`` instead of editing every URL. Example::

    [[source]]
    slug = "05-cdc-svi"
    vars = { vintage = "2022" }
    [[source.files]]
    url = "https://svi.cdc.gov/Documents/Data/{vintage}/csv/states/SVI_{vintage}_US.csv"
    dest = "SVI_{vintage}_US.csv"
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

_REGISTRY_PATH = Path(__file__).resolve().parent / "sources.toml"


@dataclass(frozen=True)
class SourceFile:
    """One downloadable file in a declarative source."""

    url: str
    dest: str
    min_bytes: int | None = None


@dataclass(frozen=True)
class Source:
    """A dataset known to opendata-fetch."""

    slug: str
    agency: str
    dataset: str
    doc: str | None = None
    homepage: str | None = None
    update_cadence: str | None = None
    vars: dict[str, str] = field(default_factory=dict)
    files: list[SourceFile] = field(default_factory=list)
    handler: str | None = None

    @property
    def is_custom(self) -> bool:
        """True if this source uses a custom fetcher rather than ``files``."""
        return self.handler is not None


class RegistryError(RuntimeError):
    """Raised when ``sources.toml`` is malformed or a source is invalid."""


def _subst(value: str, variables: dict[str, str], slug: str) -> str:
    try:
        return value.format(**variables)
    except KeyError as e:
        raise RegistryError(
            f"Source '{slug}': '{value}' references undefined var {e}. "
            f"Add it to this source's [source.vars]."
        ) from e


def _parse_source(raw: dict, index: int) -> Source:
    slug = raw.get("slug")
    if not slug:
        raise RegistryError(f"Source #{index} is missing a 'slug'.")

    for required in ("agency", "dataset"):
        if not raw.get(required):
            raise RegistryError(f"Source '{slug}' is missing required field '{required}'.")

    variables = raw.get("vars", {})
    if not isinstance(variables, dict):
        raise RegistryError(f"Source '{slug}': 'vars' must be a table.")

    handler = raw.get("handler")
    raw_files = raw.get("files", [])

    if handler and raw_files:
        raise RegistryError(
            f"Source '{slug}' defines both 'handler' and 'files'; use one."
        )
    if not handler and not raw_files:
        raise RegistryError(
            f"Source '{slug}' defines neither 'handler' nor 'files'."
        )

    files: list[SourceFile] = []
    for fi, f in enumerate(raw_files):
        if "url" not in f or "dest" not in f:
            raise RegistryError(
                f"Source '{slug}' file #{fi} must have both 'url' and 'dest'."
            )
        files.append(
            SourceFile(
                url=_subst(f["url"], variables, slug),
                dest=_subst(f["dest"], variables, slug),
                min_bytes=f.get("min_bytes"),
            )
        )

    return Source(
        slug=slug,
        agency=raw["agency"],
        dataset=raw["dataset"],
        doc=raw.get("doc"),
        homepage=raw.get("homepage"),
        update_cadence=raw.get("update_cadence"),
        vars=variables,
        files=files,
        handler=handler,
    )


def load_registry(path: Path | str | None = None) -> dict[str, Source]:
    """Load and validate the source registry. Returns a ``{slug: Source}`` map."""
    path = Path(path) if path is not None else _REGISTRY_PATH
    with open(path, "rb") as fh:
        data = tomllib.load(fh)

    raw_sources = data.get("source", [])
    if not raw_sources:
        raise RegistryError(f"No [[source]] entries found in {path}.")

    registry: dict[str, Source] = {}
    for i, raw in enumerate(raw_sources):
        source = _parse_source(raw, i)
        if source.slug in registry:
            raise RegistryError(f"Duplicate source slug: '{source.slug}'.")
        registry[source.slug] = source
    return registry


def list_sources(path: Path | str | None = None) -> list[Source]:
    """Return all sources, sorted by slug."""
    return sorted(load_registry(path).values(), key=lambda s: s.slug)


def get_source(slug: str, path: Path | str | None = None) -> Source:
    """Return one source by slug, or raise :class:`RegistryError`."""
    registry = load_registry(path)
    if slug not in registry:
        available = ", ".join(sorted(registry))
        raise RegistryError(f"Unknown source '{slug}'. Available: {available}")
    return registry[slug]
