# EPA NPL Superfund Site Boundaries + Human Exposure (EPA)

EPA's National Priorities List (NPL) is the federal roster of the most contaminated hazardous-waste sites in the US (Superfund sites). Two files describe them together: a GeoJSON of site boundary polygons (with identity attributes such as EPA_ID, site name, state, county, status, last change date) and a JSON list of per-site human-exposure status codes. The two join on the site's EPA ID.

The boundaries file is published on EPA's ArcGIS Hub; the human-exposure file comes from EPA's Superfund Enterprise Management System (SEMS).

**opendata-fetch slug:** `02-epa-npl-superfund`
**Agency:** EPA
**File type:** geojson + json
**Approx. size:** NPL boundaries GeoJSON ~60 MB, Human Exposure JSON ~1.3 MB
**Update cadence:** rolling. The boundaries dataset is refreshed by EPA irregularly; the human-exposure JSON is updated roughly daily.

## Download

opendata-fetch pulls two files at fixed URLs (no templated variable):

```
https://opendata.arcgis.com/api/v3/datasets/d6e1591d9a424f1fa6d95a02095a06d7_0/downloads/data?format=geojson&spatialRefId=4326  -> npl_boundaries.geojson
https://www3.epa.gov/semsjson/Human_Exposure_Site_List.json                                                                      -> human_exposure.json
```

The boundaries URL embeds an ArcGIS dataset id (`d6e1591d9a424f1fa6d95a02095a06d7_0`). If EPA republishes the layer under a new id, edit the URL in `opendata_fetch/sources.toml`. There is no per-year variable for this source.

## Fields and files in this download

Captured from the files as served at audit time. Schemas may drift (EPA refreshes both irregularly).

**`npl_boundaries.geojson`** — MultiPolygon/Polygon features, CRS EPSG:4326, ~2,406 features, 32 attribute fields:

| column | meaning |
|--------|---------|
| `OBJECTID` | Internal feature object ID. |
| `REGION_CODE` | EPA region (1-10). |
| `EPA_PROGRAM` | EPA program associated with the site. |
| `EPA_ID` | Site EPA/SEMS ID (join key; usually 12 characters). |
| `SITE_NAME` | Superfund site name. |
| `SITE_FEATURE_CLASS` | Feature classification grouping. |
| `SITE_FEATURE_TYPE` | Feature type (e.g. `Site Boundary`, `Comprehensive Site Area`); distinguishes multiple polygons per site. |
| `SITE_FEATURE_NAME` | Name of the individual feature. |
| `SITE_FEATURE_DESCRIPTION` | Free-text description of the feature. |
| `NPL_STATUS_CODE` | NPL status (F Final, D Deleted, P Proposed, etc.; see official documentation). |
| `FEDERAL_FACILITY_DETER_CODE` | Federal-facility determination code. |
| `LAST_CHANGE_DATE` | Date the feature record was last changed. |
| `ORIGINAL_CREATION_DATE` | Date the feature record was created. |
| `SITE_FEATURE_SOURCE` | Source of the feature geometry. |
| `STREET_ADDR_TXT` | Site street address. |
| `ADDR_COMMENT` | Address comment/note. |
| `CITY_NAME` | Site city. |
| `COUNTY` | Site county. |
| `STATE_CODE` | 2-letter state code. |
| `ZIP_CODE` | Site ZIP code. |
| `SITE_CONTACT_NAME` | Site contact name. |
| `PRIMARY_TELEPHONE_NUM` | Site contact phone number. |
| `SITE_CONTACT_EMAIL` | Site contact email. |
| `URL_ALIAS_TXT` | Site profile URL alias. |
| `FEATURE_INFO_URL` | URL with more information about the feature. |
| `FEATURE_INFO_URL_DESC` | Description of the info URL. |
| `GIS_AREA` | Feature area as computed in GIS. |
| `GIS_AREA_UNITS` | Units for `GIS_AREA`. |
| `PROJECTION` | Native projection of the source geometry. |
| `SF_GEOSPATIAL_DATA_DISCLAIMER` | Superfund geospatial data disclaimer text. |
| `SHAPE_Length` | Polygon perimeter length (geometry attribute). |
| `SHAPE_Area` | Polygon area (geometry attribute). |

**`human_exposure.json`** — a JSON object with top-level keys `success`, `data`, `meta`. `data` is a list (~1,905 records), one per site, each with 16 fields:

| column | meaning |
|--------|---------|
| `humanexposurepathdesc` | Human-exposure pathway status description (plain-text). |
| `city` | Site city. |
| `nplstatus` | NPL status of the site. |
| `saaflag` | SAA flag (SEMS code; see EPA SEMS documentation). |
| `county` | Site county. |
| `fedfacilityflag` | Federal-facility flag. |
| `zipcode` | Site ZIP code. |
| `epaid` | Site EPA/SEMS ID (lowercase; join key to `EPA_ID`). |
| `regionid` | EPA region. |
| `sitename` | Site name. |
| `eibaselinesiteInd` | Environmental-indicator baseline-site indicator (SEMS code; see EPA SEMS documentation). |
| `siteid` | SEMS internal site ID. |
| `humexposurestscode` | Human-exposure status code (e.g. `HENC`, `HEUC`; see EPA SEMS documentation). |
| `state` | State name. |
| `state_code` | 2-letter state code. |
| `friendlyurl` | Public-facing site profile URL. |

## Provenance & landing pages

- NPL Boundaries dataset (ArcGIS Hub): https://hub.arcgis.com/maps/EPA::npl-superfund-site-boundaries-epa-public-2022/explore
- ArcGIS Hub item page: https://www.arcgis.com/home/item.html?id=d6e1591d9a424f1fa6d95a02095a06d7
- EPA Superfund landing: https://www.epa.gov/superfund/superfund-national-priorities-list-npl
- EPA SEMS overview: https://www.epa.gov/enviro/sems-overview

## Quirks & notes

- **Join keys differ in case:** the boundaries file uses `EPA_ID` (uppercase, with underscore); the human-exposure file uses `epaid` (lowercase). A downstream user joining the two must normalize.
- **The human-exposure JSON drifts on essentially every download.** EPA updates exposure status codes in place; the byte size can stay constant (observed at exactly 1,346,934 bytes across consecutive days) while the content (SHA256) changes. Treat content changes here as expected, not as corruption.
- **Multiple polygons per site:** the boundaries dataset has more features than unique sites. A single EPA_ID can have several feature polygons distinguished by `SITE_FEATURE_TYPE` (e.g., `Comprehensive Site Area`, `Site Boundary`, `Current Ground Boundary`). opendata-fetch ships the raw file with all of them; any dedup is a downstream choice.
- **Dirty `SITE_FEATURE_TYPE` values:** some rows carry a trailing `\r\n`, and some hold the literal string `<Null>` instead of a JSON null. FYI for downstream parsing.
- **Status codes (FYI):** `NPL_STATUS_CODE` includes F (Final), D (Deleted), N, P (Proposed), R, S, A, and null. Human-exposure codes: HENC (not under control, worst), HEPR, HEUC, HHPA, HEID, HEIC, blank (not assigned).
- Geometries are a mix of Polygon and MultiPolygon. At least one site (`RID09321243`) has an 11-character EPA_ID rather than the usual 12.

## Manual fallback

1. **NPL Boundaries:** open the ArcGIS Hub item page above, click Download -> GeoJSON, save as `npl_boundaries.geojson` into the source's download directory.
2. **Human Exposure:** open the JSON URL in a browser and save it as `human_exposure.json`.
3. Re-run `opendata-fetch fetch 02-epa-npl-superfund`; it detects the present files and skips the downloads.
