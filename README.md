# opendata-fetch

**Reliably download U.S. government open datasets as the agencies ship them.**

opendata-fetch is a small, dependency-free tool for fetching public government open data
files (EPA, Census, CDC, NCES, HRSA, ...) into your own pipeline. It handles
the annoying parts of pulling data from government endpoints:

- **rotating / vintage URLs** (NCES school-year stamps, annual Census vintages,
  Socrata dataset IDs) expressed as one-line config knobs
- **integrity checks** that reject truncated downloads and HTML error pages
  served with a `200`
- **retries with backoff**, atomic writes (no half-written files), and
  idempotent skips
- **optional whole-archive extraction** for zipped shapefiles and bundles

What opendata-fetch **does not** do: transform, reshape, filter, or subset the data.
You get the file exactly as the agency publishes it. Slicing columns, joining,
and analysis are your job, with whatever tools you prefer.

## Why

Every team that builds on government open data re-solves the same fetch problems:
the URL changed for the new vintage, the download silently returned an error
page, the 3.8 GB file got truncated, the shapefile zip needs all four sibling
files. opendata-fetch encodes those fixes once, as data, so adding or maintaining a
source is a config edit, not a coding task.

## Install

```bash
pip install opendata-fetch
```

Core has zero runtime dependencies (stdlib only). Requires Python 3.11+ (uses the stdlib `tomllib`).

For development (editable install with tests):

```bash
git clone https://github.com/manojbade/opendata-fetch
cd opendata-fetch
pip install -e ".[dev]"
```

## Usage

```bash
opendata-fetch list                      # show every available source
opendata-fetch fetch 05-cdc-svi          # download one source into ./data/05-cdc-svi/
opendata-fetch fetch 05-cdc-svi 09-census-tracts   # several at once
opendata-fetch fetch --all               # everything (large: hundreds of GB total)
opendata-fetch fetch 09-census-tracts --extract    # unzip archives after download
opendata-fetch fetch 05-cdc-svi --dest /data/raw   # choose the download root
opendata-fetch fetch 04-epa-tri --force  # re-download even if it already exists
opendata-fetch verify 05-cdc-svi         # re-download and byte-compare vs local copy
```

As a library:

```python
import opendata_fetch

paths = opendata_fetch.fetch("05-cdc-svi", dest="data", extract=False)
for src in opendata_fetch.list_sources():
    print(src.slug, "-", src.dataset)
```

## Available sources

Run `opendata-fetch list`. v1 ships 10 sources spanning EPA, Census, CDC, NCES, and
HRSA. Per-source provenance and field notes live in [`docs/sources/`](docs/sources/).

> **Note on size.** Several sources are large (CDC PLACES ~700 MB, EPA SDWA
> ~1 GB across two zips). `fetch --all` downloads everything; fetch individual
> slugs unless you really want the full set.

## Adding your own source

Most sources are pure config. Add a `[[source]]` block to
[`opendata_fetch/sources.toml`](opendata_fetch/sources.toml):

```toml
[[source]]
slug = "12-my-dataset"
agency = "Some Agency"
dataset = "What this dataset is"
update_cadence = "annual; bump `vintage`"
vars = { vintage = "2025" }

  [[source.files]]
  url = "https://example.gov/data/{vintage}/file.csv"
  dest = "file_{vintage}.csv"
  min_bytes = 1_000_000
```

Then `opendata-fetch fetch 12-my-dataset`. No Python required. For irregular sources
that need discovery calls or assembling many files, point the source at a
custom `handler` instead, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Data licensing

opendata-fetch is MIT-licensed. It downloads, but does not redistribute, government
data. The datasets themselves are published by U.S. government agencies and are
generally in the public domain; confirm the terms for any specific dataset on
its agency page (linked in each source's doc) before redistributing.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The most useful contributions are new
sources and keeping existing vintage knobs current.
