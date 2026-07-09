# Contributing to opendata-fetch

Thanks for helping. The two most valuable contributions are **adding a new
source** and **keeping existing sources current** when an agency publishes a
new vintage. Both are usually one-file edits.

opendata-fetch has a hard scope rule that keeps it small and trustworthy:

> **opendata-fetch downloads files. It does not transform them.**

No column subsetting, no reshaping, no joins, no derived fields, no format
conversion. Users get the file exactly as the agency ships it. PRs that add
transform logic will be declined, not because they're bad, but because they
belong downstream of opendata-fetch, not inside it.

## Add a source (the common case)

Most datasets are a fixed set of URLs. Add a `[[source]]` block to
[`opendata_fetch/sources.toml`](opendata_fetch/sources.toml):

```toml
[[source]]
slug = "12-my-dataset"                 # NN-kebab-case, unique
agency = "Some Agency"
dataset = "One line describing what this dataset is"
doc = "docs/sources/12-my-dataset.md"  # optional but encouraged
homepage = "https://agency.gov/dataset"
update_cadence = "annual; bump `vintage`"
vars = { vintage = "2025" }            # optional; see below

  [[source.files]]
  url = "https://agency.gov/data/{vintage}/file.csv"
  dest = "file_{vintage}.csv"          # filename saved on disk
  min_bytes = 1_000_000                # integrity floor (see below)
```

Then:

```bash
opendata-fetch fetch 12-my-dataset           # confirm it downloads
opendata-fetch verify 12-my-dataset          # confirm the live URL is byte-stable
```

Add a matching doc under `docs/sources/` (copy an existing one for the shape).
That's it. No Python.

### Fields

| Field | Required | Notes |
|-------|----------|-------|
| `slug` | yes | `NN-kebab-case`, unique across the registry |
| `agency` | yes | publishing agency |
| `dataset` | yes | one-line description |
| `doc` | no | path to the source's doc |
| `homepage` | no | agency landing page |
| `update_cadence` | no | how often it changes / how to bump it |
| `vars` | no | substitution variables (see below) |
| `files` | one of | list of `{url, dest, min_bytes, sha256?}` |
| `handler` | one of | custom fetcher, for irregular sources (see below) |

A source must have **either** `files` **or** `handler`, never both.

### `vars` and the `{placeholder}` convention

Many dataset URLs embed a year or version. Put that value in `vars` and
reference it as `{name}` in `url` and `dest`. Bumping a dataset to a new
release then means changing **one line**:

```toml
vars = { vintage = "2024" }    # change to "2026" when the new file lands
```

Common variables already in use: `vintage` (year/school-year) and `dataset_id`
(Socrata four-by-four IDs that rotate each release). Use whatever name reads
clearly; it just has to match the `{...}` in the URLs.

### `min_bytes`

Set it comfortably **below** the real file size (roughly half is a good rule).
It is an integrity floor: a download smaller than this is rejected as a
truncated file or an HTML error page. Too high and normal files fail; too low
and a truncated download slips through. Note the observed size in the source's
doc.

### `sha256` (optional pin — stable files only)

Add `sha256 = "<hex digest>"` to a file entry **only** when that exact file is
immutable once published (a fixed-vintage Census/NCES file, for example). When
set, `fetch` fails on any hash mismatch and skips re-download only if the cached
copy still matches.

**Do not pin rolling files** (daily feeds, "latest" URLs, Socrata exports that
change in place) — a pin would fail on every legitimate update and train users
to ignore the check. When in doubt, leave it unset.

To get the digest, fetch the file once and copy the `sha256` from the generated
`manifest.json` (or run `shasum -a 256 <file>`). Because the hash is
vintage-specific, **re-pin (or drop the line) whenever you bump `vintage`** —
the new file has a different hash.

## Bump a vintage (keeping a source current)

When an agency publishes a new year/version:

1. Find the new value (year, or the new Socrata `dataset_id`, etc.).
2. Update the source's `vars` in `sources.toml`. If the filename pattern also
   changed (e.g. NCES embeds a release-date stamp that isn't the vintage),
   update the `url`/`dest` templates too.
3. Update `min_bytes` if the size shifted materially.
4. If the file had a `sha256` pin, re-pin it to the new file's digest (or drop
   the line) — the old hash will not match the new vintage.
5. `opendata-fetch fetch <slug> --force` to confirm.
6. Note the change in the source's doc.

## Add an irregular source (custom fetcher)

A few sources can't be expressed as a fixed URL list, e.g. they require a
discovery call or assemble many files into one dataset (FEMA's National Flood
Hazard Layer is ~2,600 county zips found via a search endpoint). For those,
point the source at a `handler` instead of `files`:

```toml
[[source]]
slug = "11-fema-nfhl"
agency = "FEMA"
dataset = "National Flood Hazard Layer (per-county)"
handler = "opendata_fetch.fetchers.fema_nfhl:fetch"
```

Implement the handler in `opendata_fetch/fetchers/` with this signature:

```python
def fetch(source, dest_dir, *, force=False, extract=False) -> list[Path]:
    """Download source.files-equivalent into dest_dir, return written paths."""
```

Keep custom fetchers stdlib-only where possible. If a fetcher genuinely needs
a third-party library, add it as an **optional extra** in `pyproject.toml`, not
to the core dependencies; the base install stays dependency-free.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest          # run the test suite (mocked HTTP, no network)
ruff check .    # lint
```

Tests must not hit the network. Mock at the `urlopen` boundary (see
`tests/test_engine.py`) or patch `download_file` (see `tests/test_runner.py`).

## What to expect from review

- New sources: welcome. Include a doc and confirm `fetch` + `verify` work.
- Vintage bumps: welcome, the most useful routine contribution.
- Transform/analysis features: out of scope (see the scope rule above).
- Bug fixes to the engine/registry: welcome, with a test.
