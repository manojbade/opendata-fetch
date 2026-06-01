# NCES EDGE School District Composite Boundaries (NCES, U.S. Dept. of Education)

NCES EDGE repackages the U.S. Census Bureau's TIGER/Line school-district boundary polygons into a single "composite" file that combines all district types (Elementary, Secondary, Unified, Administrative) into one dataset with wall-to-wall US coverage, one polygon per district (~13,400 districts). Each district is keyed by a 7-character `GEOID`, which matches the `LEAID` format used in the NCES CCD school data. The file is a standard Esri shapefile bundle delivered as a single zip.

**opendata-fetch slug:** `10-nces-edge-districts`
**Agency:** NCES (U.S. Dept. of Education)
**File type:** shapefile zip
**Approx. size:** ~202 MB zip (~300 MB uncompressed shapefile)
**Update cadence:** annual (school year). Bump `vintage`.

## Download

opendata-fetch pulls one file:

```
https://nces.ed.gov/programs/edge/data/EDGE_SCHOOLDISTRICT_TL25_SY{vintage}.zip  -> EDGE_SCHOOLDISTRICT_TL25_SY{vintage}.zip
```

The general pattern is:

```
https://nces.ed.gov/programs/edge/data/EDGE_SCHOOLDISTRICT_TL{YY}_SY{YYYY}.zip
```

where `TL{YY}` is the TIGER/Line year (e.g., `TL25` = 2025) and `SY{YYYY}` is the school year (e.g., `SY2425` = 2024-25). `{vintage}` is the school-year code, filled from the source's `vars` table in `opendata_fetch/sources.toml`; bumping it is a one-line edit. Note the `TL{YY}` portion is a separate literal in the registry filename and changes on its own cadence, so when moving to a new release, update both the variable and the `TL` stamp. NCES typically publishes the composite file about 6 months after the school year ends.

## Fields and files in this download

Captured from the `SY2425` (2024-25) release. Schema may shift between vintages.

**You get:** one zip containing a single Esri shapefile bundle (`.shp`, `.shx`, `.dbf`, `.prj`, `.cpg`, plus `.shp.xml` metadata sidecars) inside the `EDGE_SCHOOLDISTRICT_TL25_SY2425 (1)/` subfolder. One polygon per district.

**Geometry:** Polygon, CRS EPSG:4269 (NAD83), ~13,368 features.

**Attribute fields (19):**

| column | meaning |
|--------|---------|
| `STATEFP` | 2-digit state FIPS code. |
| `ELSDLEA` | Elementary school district LEA code (populated only for elementary districts). |
| `SCSDLEA` | Secondary school district LEA code (populated only for secondary districts). |
| `UNSDLEA` | Unified school district LEA code (populated only for unified districts). |
| `SDADMLEA` | Administrative school district LEA code (populated only for administrative districts). |
| `GEOID` | 7-character district ID (state FIPS + district code); matches CCD `LEAID`. |
| `NAME` | District name. |
| `LSAD` | Legal/statistical area description code (constant `"00"` for this file). |
| `LOGRADE` | Lowest grade offered (NCES grade code, e.g. `PK`, `KG`, `01`-`13`). |
| `HIGRADE` | Highest grade offered (NCES grade code). |
| `MTFCC` | MAF/TIGER feature class code. |
| `SDTYP` | School district type code. |
| `FUNCSTAT` | Functional status code. |
| `ALAND` | Land area in square meters. |
| `AWATER` | Water area in square meters. |
| `INTPTLAT` | Internal-point latitude (computed point within the polygon). |
| `INTPTLON` | Internal-point longitude (computed point within the polygon). |
| `GEO_YEAR` | Geography vintage year. |
| `SCHOOLYEAR` | School year the boundaries represent. |

The four LEA columns (`ELSDLEA`/`SCSDLEA`/`UNSDLEA`/`SDADMLEA`) indicate district type; exactly one is populated per district. See the Quirks section below for details.

## Provenance & landing pages

- EDGE School District Boundaries page (lists all available years): https://nces.ed.gov/programs/edge/Geographic/DistrictBoundaries
- Composite file documentation (PDF): https://nces.ed.gov/programs/edge/docs/EDGE_SDBOUNDARIES_COMPOSITE_FILEDOC.pdf
- EDGE Geographic landing: https://nces.ed.gov/programs/edge/Geographic
- ArcGIS Hub alternative access: https://data-nces.opendata.arcgis.com/datasets/school-district-boundaries-current/explore

## Quirks & notes

- **Zip subfolder naming quirk.** The unzipped contents sit inside a folder named like `EDGE_SCHOOLDISTRICT_TL25_SY2425 (1)/` (trailing space + parenthesized `(1)`). A downstream reader opening the shapefile must handle the space and parentheses (GDAL's `/vsizip/` virtual filesystem, or a glob, both work). FYI.
- **Multi-file shapefile bundle.** Standard Esri set (.shp, .shx, .dbf, .prj, plus sidecars); all are needed to read geometry. opendata-fetch ships the zip intact.
- **CRS is NAD83 (EPSG:4269)**, like Census tracts; reproject to WGS84 downstream if needed. FYI.
- **GEOID format (FYI):** 7 characters = 2-digit state FIPS + 5-digit district code (e.g., `0407530`); read as a string to preserve leading zeros. Matches CCD `LEAID`.
- **District type lives in four columns.** `ELSDLEA`, `SCSDLEA`, `UNSDLEA`, `SDADMLEA`: exactly one is populated per district, indicating Elementary / Secondary / Unified / Administrative. In areas with separate elementary and secondary districts sharing the same geography, both appear as overlapping polygons. FYI for downstream users.
- **Geometry validity (FYI):** Census/NCES polygons commonly include tiny self-intersections that strict validators flag (often several percent of rows), usually repairable downstream with a zero-width buffer. `LSAD` is a constant `"00"` for this file.
- Grade-range fields `LOGRADE`/`HIGRADE` use NCES grade codes (`PK`, `KG`, `01`-`13`, `UG`, `AE`). `INTPTLAT`/`INTPTLON` are computed internal points per polygon.

## Manual fallback

1. Open the EDGE School District Boundaries page above.
2. Find the most recent year in the "Composite Boundary Files" section.
3. Right-click the "ZIP" link -> "Save Link As".
4. Save it as `EDGE_SCHOOLDISTRICT_TL25_SY{vintage}.zip` into the source's download directory.
5. Re-run `opendata-fetch fetch 10-nces-edge-districts`; it detects the present file and skips the download.
