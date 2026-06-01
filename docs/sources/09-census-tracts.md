# Census Tract Cartographic Boundaries (U.S. Census Bureau)

The U.S. Census Bureau's Cartographic Boundary (CB) files provide simplified polygon geometry for US census tracts, the small statistical subdivisions of counties (~4,000 people each) that serve as the geographic unit for most CDC and ACS small-area data. opendata-fetch ships the national tract file at 1:500,000 scale (`500k`), a good tradeoff of size and precision. The file is a standard Esri shapefile bundle delivered as a single zip (~85,000 tract polygons, each with an 11-character GEOID, state/county codes and names, and land/water areas).

The Census Bureau also publishes `5m` (1:5,000,000) and `20m` (1:20,000,000) generalizations of the same tracts, and full-resolution TIGER/Line files; opendata-fetch ships only the `500k` CB file.

**opendata-fetch slug:** `09-census-tracts`
**Agency:** U.S. Census Bureau
**File type:** shapefile zip (contains .shp, .shx, .dbf, .prj, .cpg, plus XML metadata)
**Approx. size:** ~55 MB zip (~80 MB+ uncompressed)
**Update cadence:** annual (typically March/April). Bump `vintage`.

## Download

opendata-fetch pulls one file:

```
https://www2.census.gov/geo/tiger/GENZ{vintage}/shp/cb_{vintage}_us_tract_500k.zip  -> cb_{vintage}_us_tract_500k.zip
```

`{vintage}` is the reference year (e.g., `2024`), filled from the source's `vars` table in `opendata_fetch/sources.toml`; bumping it is a one-line edit. Note the year appears twice in the URL (the `GENZ{vintage}` folder and the `cb_{vintage}` filename) and is templated consistently from the single variable.

To pull a different scale, change `500k` to `5m` or `20m` in the URL.

## Fields and files in this download

Captured from the `2024` release (`cb_2024_us_tract_500k.zip`). One zip containing a single Esri shapefile bundle: `.shp`, `.shx`, `.dbf`, `.prj`, `.cpg`, plus `.shp.ea.iso.xml` and `.shp.iso.xml` metadata sidecars. One polygon per census tract.

**Geometry:** Polygon, CRS EPSG:4269 (NAD83), ~85,184 features.

**Attribute fields (13):**

| column | meaning |
|--------|---------|
| `STATEFP` | 2-digit state FIPS code. |
| `COUNTYFP` | 3-digit county FIPS code (within state). |
| `TRACTCE` | 6-digit census tract code (within county). |
| `GEOIDFQ` | Fully-qualified GEOID (`1400000US...` form). |
| `GEOID` | 11-character tract ID (2-digit state + 3-digit county + 6-digit tract); read as string. |
| `NAME` | Tract name/number (short form). |
| `NAMELSAD` | Tract name with legal/statistical descriptor (e.g. `Census Tract 51.27`). |
| `STUSPS` | 2-letter state postal abbreviation. |
| `NAMELSADCO` | County name with legal/statistical descriptor. |
| `STATE_NAME` | Full state name. |
| `LSAD` | Legal/statistical area description code. |
| `ALAND` | Land area in square meters. |
| `AWATER` | Water area in square meters. |

`GEOID` is the 11-character tract ID (2-digit state + 3-digit county + 6-digit tract); read as a string to keep leading zeros. `ALAND`/`AWATER` are land/water area in square meters. Official field definitions: the Census TIGER/Line technical documentation (https://www.census.gov/programs-surveys/geography/technical-documentation/complete-technical-documentation/tiger-geo-line.html).

## Provenance & landing pages

- Cartographic Boundary Files (current year): https://www.census.gov/geographies/mapping-files/2024/geo/carto-boundary-file.html
- All years archive: https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
- Mapping files index: https://www.census.gov/geographies/mapping-files.html

## Quirks & notes

- **Multi-file shapefile bundle in one zip.** The zip contains the full Esri shapefile set (.shp, .shx, .dbf, .prj, .cpg) plus XML metadata; all the sidecar files are required to read the geometry. opendata-fetch ships the zip intact.
- **CRS is NAD83 (EPSG:4269), not WGS84.** Most web-mapping tooling expects WGS84 (EPSG:4326). The two differ by under a meter for most US locations; a downstream consumer reprojects if needed. FYI.
- **GEOID composition (FYI):** 11 characters = 2-digit STATEFP + 3-digit COUNTYFP + 6-digit TRACTCE (e.g., `06077005127`). Read as a string to preserve leading zeros. A separate `GEOIDFQ` column carries the fully-qualified form (`1400000US...`).
- **Tract count varies year to year** as tracts are split or renumbered, so counts differ across vintages (and across other tract-keyed sources like SVI). FYI for downstream joins.
- A few "tracts" cover open water only (ALAND = 0, high AWATER); they are valid tract FIPS and are included as shipped.

## Manual fallback

1. Open the Cartographic Boundary Files page for the year above.
2. Scroll to the Census Tracts section.
3. Click "Census Tracts: {year}" -> "shp" -> select "1:500,000 (national)" and download.
4. Save the zip as `cb_{vintage}_us_tract_500k.zip` into the source's download directory.
5. Re-run `opendata-fetch fetch 09-census-tracts`; it detects the present file and skips the download.
