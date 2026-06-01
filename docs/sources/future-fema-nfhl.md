# FEMA National Flood Hazard Layer (FEMA)

> Status: planned for a future release (irregular county-by-county source); not yet in the shipped registry.

FEMA's National Flood Hazard Layer (NFHL) is the effective flood-mapping data behind the nation's Flood Insurance Rate Maps. It is published as **per-county shapefiles**, one per DFIRM (Digital Flood Insurance Rate Map), with roughly 2,659 DFIRMs covering US counties, territories, and special districts. Each DFIRM is updated independently on FEMA's own schedule and carries its own publication date. Each county zip contains ~10 shapefile layers; the flood-hazard-area polygons live in `S_FLD_HAZ_AR.shp` (flood zone code, Special Flood Hazard Area flag, base flood elevation).

This source is the reason it is deferred: there is no single national download, the inventory is large (~87 GB of source zips nationally), and acquiring it means discovering a per-county URL list and fetching thousands of files. The documentation below describes how it would be wired into opendata-fetch.

**opendata-fetch slug:** `11-fema-nfhl` (proposed; not in the shipped registry. It would take the next free number after the 10 shipped sources.)
**Agency:** FEMA
**File type:** per-county shapefile zips (each contains ~10 shapefile layers)
**Approx. size:** ~33 MB average per county; ~87 GB total across ~2,659 counties (largest single county ~776 MB)
**Update cadence:** rolling per county. FEMA reissues an individual DFIRM whenever a new Flood Insurance Study completes; the master inventory always reflects current effective maps.

## Download

There is no single national file. Each county zip is at:

```
https://hazards.fema.gov/nfhlv2/output/County/{DFIRMID}_{YYYYMMDD}.zip
```

Example: `https://hazards.fema.gov/nfhlv2/output/County/13007C_20090818.zip` (Baker County, GA). `{DFIRMID}` is a ~6-character FEMA id (usually state FIPS + county FIPS + `C`); `{YYYYMMDD}` is that DFIRM's publication date. Because both the id list and the dates change per county, the URL list must be discovered before fetching (below) rather than templated from a single variable. State-level rollups exist at `https://hazards.fema.gov/nfhlv2/output/State/NFHL_{state-fips}_{YYYYMMDD}.zip` but are not published for every state at predictable dates, so the county path is the reliable one.

### Discovering the county DFIRM list (JS/POST-driven inventory)

The authoritative inventory comes from POSTing to FEMA's NFHL search endpoint and parsing the returned HTML:

- **Endpoint:** `https://hazards.fema.gov/femaportal/NFHL/searchResult.action`
- **Method:** POST, form-encoded. Any valid state works; the endpoint returns ALL county DFIRMs nationally regardless of which state is passed.
- **Body:** `stateFips=11` and `stateName=District of Columbia`

```bash
curl -sL --max-time 60 -A "Mozilla/5.0" -X POST \
  --data-urlencode "stateFips=11" \
  --data-urlencode "stateName=District of Columbia" \
  "https://hazards.fema.gov/femaportal/NFHL/searchResult.action" \
  -o fema_nfhl_inventory.html
```

The response is a single large HTML page. Each county appears as an anchor like:

```html
<a href="Download/ProductsDownLoadServlet?DFIRMID=13007C&state=GEORGIA&county=BAKER COUNTY&fileName=13007C_20090818.zip">
```

Parse the `DFIRMID`, `state`, `county`, and `fileName` out of each `ProductsDownLoadServlet` anchor, derive the date from the filename, and build the `County/{fileName}` download URL. Expect roughly 2,659 anchors; a sharp drop signals FEMA changed the page structure. If the POST stops working, inspect the live form at https://hazards.fema.gov/femaportal/NFHL/searchResult/ for renamed input fields.

## Provenance & landing pages

- FEMA NFHL search-result page (lists all county DFIRMs): https://hazards.fema.gov/femaportal/NFHL/searchResult/
- FEMA Map Service Center: https://msc.fema.gov/
- FEMA National Flood Hazard Layer landing: https://www.fema.gov/flood-maps/national-flood-hazard-layer
- ArcGIS Hub NFHL feature service (live, not bulk): https://hazards.fema.gov/femaportal/wps/portal/NFHLWMS

## Quirks & notes

- **URLs are not directly listed; they are JS/POST-discovered.** You must scrape the inventory page (above) to learn the current DFIRM ids and dates before fetching.
- **Sheer volume:** ~2,659 separate downloads totaling ~87 GB. A fetch implementation needs retry, per-county success/failure tracking, and resume-after-interruption.
- **Multi-layer zips:** each county zip holds ~10 shapefile sets (`S_FLD_HAZ_AR`, `S_FIRM_PAN`, `S_BASE_INDEX`, `S_FLD_HAZ_LN`, etc.). The flood-hazard polygons are in `S_FLD_HAZ_AR.*`. opendata-fetch ships the zip intact; selecting a layer is a downstream choice.
- **DBF encoding:** a small number of county shapefiles have non-UTF-8 (cp1252 / Latin-1) bytes in DBF fields; a downstream reader may need a Latin-1 fallback. FYI.
- **`-9999` is the missing-data sentinel** in numeric columns (`STATIC_BFE`, `DEPTH`, `VELOCITY`, `BFE_REVERT`, `DEP_REVERT`) meaning "not applicable / not measured." FYI for downstream users.
- **CRS is NAD83 (EPSG:4269)**, like the Census tracts; reproject to WGS84 downstream if needed.
- **DFIRMID is opaque.** Most end in `C` (e.g., `13007C`), but territories use other suffixes or numeric-only ids (e.g., `780000` for the Virgin Islands). Treat as strings.
- **Old publication dates are normal.** Some DFIRMs are decades old; that means FEMA hasn't completed a newer study, not that the data is stale. Whatever the inventory lists is the current effective map.
- Flood zone codes (FYI): `X` (minimal hazard, outside SFHA), `A`/`AE`/`AH`/`AO`/`A99`/`AR` (riverine SFHA), `V`/`VE` (coastal SFHA with wave action), `D` (undetermined), `OPEN WATER`. The `SFHA_TF` flag is the headline T/F.

## Manual fallback

For an individual county that fails to download:

1. Open https://hazards.fema.gov/femaportal/NFHL/searchResult/
2. Select the state and county.
3. Click the ZIP icon for that DFIRM.
4. Save it as `{DFIRMID}_{YYYYMMDD}.zip` into the source's download directory.

For a full re-acquisition, the same portal page lets you download each county one at a time; this is slow (thousands of clicks) and a genuine last resort.
