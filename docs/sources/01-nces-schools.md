# NCES Schools: CCD + EDGE Geocode (NCES, U.S. Dept. of Education)

The National Center for Education Statistics (NCES) Common Core of Data (CCD) is the federal census of US public schools and school districts. Four files together define the universe of public schools for a given school year: the Directory (identity, address, district, charter, grade range, operational status), Characteristics (NSLP designation, virtual flag, shared time), Membership (enrollment counts by grade/race/sex), and the EDGE Geocode file (latitude/longitude, locale code, county FIPS, CBSA, congressional district).

Schools are keyed by the 12-character NCESSCH identifier; districts by the 7-character LEAID. The EDGE Geocode file comes from the companion Education Demographic and Geographic Estimates program and supplies the geographic attributes the CCD tables lack.

**opendata-fetch slug:** `01-nces-schools`
**Agency:** NCES (U.S. Dept. of Education)
**File type:** zip archives (each contains CSV / SAS7BDAT; EDGE zip also contains pipe-delimited TXT, xlsx, and a nested shapefile zip)
**Approx. size:** Directory ~13 MB, Characteristics ~5.4 MB, Membership ~203 MB (2.3 GB uncompressed), EDGE Geocode ~29 MB
**Update cadence:** annual (school year). Bump `vintage` and the 6-digit release stamp in the filenames.

## Download

opendata-fetch pulls four files:

```
https://nces.ed.gov/ccd/Data/zip/ccd_sch_029_{vintage}_w_1a_073025.zip   (Directory)
https://nces.ed.gov/ccd/Data/zip/ccd_sch_129_{vintage}_w_1a_073025.zip   (Characteristics)
https://nces.ed.gov/ccd/Data/zip/ccd_sch_052_{vintage}_l_1a_073025.zip   (Membership)
https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_{vintage}.zip (EDGE Geocode)
```

The general patterns are:
- CCD school-level files: `https://nces.ed.gov/ccd/Data/zip/ccd_sch_{filetype}_{SY}_{stage}_1a_{releaseDate}.zip`
- EDGE Geocode: `https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_{SY}.zip`

`{vintage}` is the school-year code (`2425` = 2024-25, `2526` = 2025-26). It is filled from the source's `vars` table in `opendata_fetch/sources.toml`, so moving to a new year is a one-line edit. Note two things change per release: `{vintage}` and the embedded 6-digit release-date stamp (`073025`), so the filename literals in the registry must be updated alongside the variable.

**Stage suffix is inconsistent across files for the same year.** As of 2024-25: Directory (`029`) and Characteristics (`129`) use `w` (working/preliminary), Membership (`052`) uses `l` (locked/final). When probing for a new release, try both `w` and `l` since the stage depends on file type and timing.

The same school-level page also lists Staff (`ccd_sch_033`) and Lunch Program Eligibility (`ccd_sch_059`) files that opendata-fetch does not ship; add them as extra `[[source.files]]` entries if you need them.

## Fields and files in this download

Captured from the `2425` (2024-25) release. Column sets are stable year to year but can shift; treat this as a snapshot.

**Directory** (`ccd_sch_029_2425_w_1a_073025.csv`, 65 columns). Annotated by group rather than per-column:

`SCHOOL_YEAR, FIPST, STATENAME, ST, SCH_NAME, LEA_NAME, STATE_AGENCY_NO, UNION, ST_LEAID, LEAID, ST_SCHID, NCESSCH, SCHID, MSTREET1, MSTREET2, MSTREET3, MCITY, MSTATE, MZIP, MZIP4, LSTREET1, LSTREET2, LSTREET3, LCITY, LSTATE, LZIP, LZIP4, PHONE, WEBSITE, SY_STATUS, SY_STATUS_TEXT, UPDATED_STATUS, UPDATED_STATUS_TEXT, EFFECTIVE_DATE, SCH_TYPE_TEXT, SCH_TYPE, RECON_STATUS, OUT_OF_STATE_FLAG, CHARTER_TEXT, CHARTAUTH1, CHARTAUTHN1, CHARTAUTH2, CHARTAUTHN2, NOGRADES, G_PK_OFFERED, G_KG_OFFERED, G_1_OFFERED, G_2_OFFERED, G_3_OFFERED, G_4_OFFERED, G_5_OFFERED, G_6_OFFERED, G_7_OFFERED, G_8_OFFERED, G_9_OFFERED, G_10_OFFERED, G_11_OFFERED, G_12_OFFERED, G_13_OFFERED, G_UG_OFFERED, G_AE_OFFERED, GSLO, GSHI, LEVEL, IGOFFERED`

- **Identifiers:** `SCHOOL_YEAR`, `FIPST` (state FIPS), `STATE_AGENCY_NO`, `UNION`, `ST_LEAID`/`LEAID` (state and NCES district IDs), `ST_SCHID`/`NCESSCH`/`SCHID` (state and NCES school IDs).
- **Names:** `SCH_NAME` (school), `LEA_NAME` (district), `STATENAME`, `ST`.
- **Mailing address (`M*`):** `MSTREET1-3`, `MCITY`, `MSTATE`, `MZIP`, `MZIP4`.
- **Location/physical address (`L*`):** `LSTREET1-3`, `LCITY`, `LSTATE`, `LZIP`, `LZIP4`.
- **Contact:** `PHONE`, `WEBSITE`.
- **Operational status:** `SY_STATUS`/`SY_STATUS_TEXT` (school-year status, see Quirks for codes), `UPDATED_STATUS`/`UPDATED_STATUS_TEXT`, `EFFECTIVE_DATE`, `RECON_STATUS`, `OUT_OF_STATE_FLAG`.
- **Type & charter:** `SCH_TYPE`/`SCH_TYPE_TEXT` (school type), `CHARTER_TEXT` (charter status), `CHARTAUTH1/CHARTAUTHN1/CHARTAUTH2/CHARTAUTHN2` (charter authorizer IDs/names).
- **Grades offered:** `NOGRADES` flag, the `G_*_OFFERED` per-grade flags (`PK`, `KG`, `1`-`13`, `UG`, `AE`), and the summaries `GSLO`/`GSHI` (lowest/highest grade), `LEVEL` (school level), `IGOFFERED`.

**Characteristics** (`ccd_sch_129_2425_w_1a_073025.csv`, 17 columns):

`SCHOOL_YEAR, FIPST, STATENAME, ST, SCH_NAME, STATE_AGENCY_NO, UNION, ST_LEAID, LEAID, ST_SCHID, NCESSCH, SCHID, SHARED_TIME, NSLP_STATUS, NSLP_STATUS_TEXT, VIRTUAL, VIRTUAL_TEXT`

- **Identity (12):** same identifier/name/state columns as the Directory (`SCHOOL_YEAR` … `SCHID`).
- `SHARED_TIME` — whether the school is a shared-time facility (students attend part-time from other schools).
- `NSLP_STATUS`/`NSLP_STATUS_TEXT` — National School Lunch Program participation designation (free/reduced-price lunch program status).
- `VIRTUAL`/`VIRTUAL_TEXT` — virtual-school status code and its text label.

**Membership** (`ccd_sch_052_2425_l_1a_073025.csv`, 18 columns; one row per school x grade x race/ethnicity x sex):

`SCHOOL_YEAR, FIPST, STATENAME, ST, SCH_NAME, STATE_AGENCY_NO, UNION, ST_LEAID, LEAID, ST_SCHID, NCESSCH, SCHID, GRADE, RACE_ETHNICITY, SEX, STUDENT_COUNT, TOTAL_INDICATOR, DMS_FLAG`

- **Identity (12):** same identifier/name/state columns as the Directory.
- `GRADE` — grade level for the row.
- `RACE_ETHNICITY` — race/ethnicity category for the row.
- `SEX` — sex category for the row.
- `STUDENT_COUNT` — enrollment count for that grade x race x sex cell.
- `TOTAL_INDICATOR` — flags whether the row is a subtotal/total (vs a single grade x race x sex cell).
- `DMS_FLAG` — data-management-system reporting/quality flag.

**EDGE Geocode** (`EDGE_GEOCODE_PUBLICSCH_2425.TXT`, pipe-delimited, **no header row**, 23 positional fields). In file order: NCES school ID, LEAID, school name, operating-state FIPS, street, city, state, ZIP, state FIPS, county FIPS, county name, locale code, latitude, longitude, CBSA code, CBSA name, CBSA type, CSA code, CSA name, congressional district code, state-legislature lower district, state-legislature upper district, school year. The key columns to note: `NCESSCH` and `LEAID` (join keys back to the CCD tables), latitude/longitude (address-geocoded point), the NCES locale code (urban/rural classification), county FIPS, the CBSA code (metro/micro area), and the congressional district code. The same EDGE zip also contains the identical data as an `.xlsx` (with labeled headers), a `.sas7bdat`, and a nested `Shapefile_SCH.zip`; field meanings are documented in `EDGE_GEOCODE_PUBLIC_FILEDOC.pdf` inside the zip.

## Provenance & landing pages

- CCD data index: https://nces.ed.gov/ccd/files.asp
- EDGE geocode: https://nces.ed.gov/programs/edge/geographic/schoollocations
- EDGE locale framework: https://nces.ed.gov/programs/edge/Geographic/LocaleBoundaries
- Release calendar: https://ies.ed.gov/nces-statistical-products-release-calendar
- EDGE geocode field documentation: `EDGE_GEOCODE_PUBLIC_FILEDOC.pdf` (inside the EDGE zip)

## Quirks & notes

- **Membership zip uses DEFLATE64 compression** (zip compression method 9). Python's stdlib `zipfile` cannot decode it, and `zipfile-deflate64` does not currently build on Python 3.13. Use the `unzip` binary (`unzip -p`) to extract it; `unzip` handles DEFLATE64 and is available on macOS and standard Linux runners.
- **EDGE Geocode zip contains multiple formats:** pipe-delimited TXT (no header), xlsx (with headers), SAS7BDAT, and a nested `Shapefile_SCH.zip`. The TXT column meanings are documented in `EDGE_GEOCODE_PUBLIC_FILEDOC.pdf`.
- The Directory and Characteristics zips contain both CSV and SAS7BDAT.
- NCESSCH (12-char) and LEAID (7-char) are string IDs with leading zeros for some states. Read them as strings; integer parsing drops leading zeros.
- Membership is large (203 MB compressed, ~2.3 GB uncompressed) because rows are at the school x grade x race x sex level. A downstream reader should stream/chunk it rather than load it whole.
- Latitude/longitude in EDGE Geocode are address-geocoding estimates, not GPS readings (documented in the EDGE file doc).
- FYI for downstream users: `SY_STATUS` codes are 1=Open, 2=Closed, 3=New, 4=Added, 5=Changed Boundary/Agency, 6=Inactive, 7=Future, 8=Reopened. Grade codes (`GSLO`/`GSHI`) are 2-char strings including reserved codes `M` (Missing) and `N` (Not applicable), not integers.

## Manual fallback

1. Download each file from the corresponding landing page above using a browser (CCD index for the `ccd_sch_*` zips; EDGE geocode page for the geocode zip).
2. Place the file in the source's download directory with the exact filename opendata-fetch expects.
3. Re-run `opendata-fetch fetch 01-nces-schools`; it detects the present file and skips the download.
