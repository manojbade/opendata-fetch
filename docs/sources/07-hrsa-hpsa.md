# HRSA Health Professional Shortage Areas (HRSA)

HRSA designates Health Professional Shortage Areas (HPSAs): geographies, populations, or facilities formally identified as having insufficient access to health-care providers. Designations are published in three disciplines, each as its own national CSV: Primary Care (PC, ~78K records), Mental Health (MH, ~39K records), and Dental Health (DH, ~45K records). Each row is one HPSA designation, with status, designation type (Geographic / Population / Facility), score, designated population, county FIPS, and many descriptive fields.

**opendata-fetch slug:** `07-hrsa-hpsa`
**Agency:** HRSA
**File type:** csv (three files)
**Approx. size:** Primary Care ~45 MB, Mental Health ~23 MB, Dental Health ~26 MB
**Update cadence:** rolling. HRSA refreshes the data-download files continuously (roughly weekly).

## Download

opendata-fetch pulls three files at fixed URLs:

```
https://data.hrsa.gov/DataDownload/DD_Files/BCD_HPSA_FCT_DET_PC.csv  -> hpsa_pc.csv
https://data.hrsa.gov/DataDownload/DD_Files/BCD_HPSA_FCT_DET_MH.csv  -> hpsa_mh.csv
https://data.hrsa.gov/DataDownload/DD_Files/BCD_HPSA_FCT_DET_DH.csv  -> hpsa_dh.csv
```

The general pattern is:

```
https://data.hrsa.gov/DataDownload/DD_Files/BCD_HPSA_FCT_DET_{DISCIPLINE}.csv
```

where `{DISCIPLINE}` is `PC`, `MH`, or `DH`. These are "latest" URLs with no year to bump; if HRSA changes the filenames, edit them in `opendata_fetch/sources.toml`.

HRSA also publishes companion polygon shapefiles for Geographic-type HPSAs (`HPSA_PLYPC_SHP.zip`, `HPSA_PLYMH_SHP.zip`, `HPSA_PLYDH_SHP.zip`) which opendata-fetch does not ship; add them as extra `[[source.files]]` entries if you need geometry.

## Fields and files in this download

Captured at audit time. Three CSVs, one per discipline (`hpsa_pc.csv` = Primary Care, `hpsa_mh.csv` = Mental Health, `hpsa_dh.csv` = Dental Health), one row per HPSA designation component. Each file ends with a trailing comma, which produces one empty unnamed trailing column. `XXXXX` appears as a placeholder in some code fields, and several fields are quoted because they contain commas.

**`hpsa_pc.csv`** (66 columns; Primary Care is the only file with the `PC MCTA Score` column):

`HPSA Name, HPSA ID, Designation Type, HPSA Discipline Class, HPSA Score, PC MCTA Score, Primary State Abbreviation, HPSA Status, HPSA Designation Date, HPSA Designation Last Update Date, Metropolitan Indicator, HPSA Geography Identification Number, HPSA Degree of Shortage, Withdrawn Date, HPSA FTE, HPSA Designation Population, % of Population Below 100% Poverty, HPSA Formal Ratio, HPSA Population Type, Rural Status, Longitude, Latitude, BHCMIS Organization Identification Number, Break in Designation, Common County Name, Common Postal Code, Common Region Name, Common State Abbreviation, Common State County FIPS Code, Common State FIPS Code, Common State Name, County Equivalent Name, County or County Equivalent Federal Information Processing Standard Code, Discipline Class Number, HPSA Address, HPSA City, HPSA Component Name, HPSA Component Source Identification Number, HPSA Component State Abbreviation, HPSA Component Type Code, HPSA Component Type Description, HPSA Designation Population Type Description, HPSA Estimated Served Population, HPSA Estimated Underserved Population, HPSA Metropolitan Indicator Code, HPSA Population Type Code, HPSA Postal Code, HPSA Provider Ratio Goal, HPSA Resident Civilian Population, HPSA Shortage, HPSA Status Code, HPSA Type Code, HPSA Withdrawn Date String, Primary State FIPS Code, Primary State Name, Provider Type, Rural Status Code, State Abbreviation, State and County Federal Information Processing Standard Code, State FIPS Code, State Name, U.S. - Mexico Border 100 Kilometer Indicator, U.S. - Mexico Border County Indicator, Data Warehouse Record Create Date, Data Warehouse Record Create Date Text`

**`hpsa_mh.csv`** and **`hpsa_dh.csv`** (65 columns each): identical to the Primary Care column set above **minus** `PC MCTA Score`.

**Column meanings.** Most column names are already full English (e.g. `HPSA Designation Last Update Date`, `% of Population Below 100% Poverty`) and are left as-is. One-liners for the non-obvious ones:

- `HPSA ID` — the designation's unique HRSA identifier.
- `Designation Type` / `HPSA Type Code` — what the designation covers: Geographic, Population, or Facility (the `*Code` is the coded form).
- `HPSA Score` — priority/severity score: 0-25 for Primary Care and Mental Health, 0-26 for Dental Health; higher = greater shortage. Used to rank designations for placement of providers.
- `PC MCTA Score` — Primary Care Medically-Underserved-related scoring component (Primary Care file only).
- `HPSA Degree of Shortage` — categorical severity of the shortage.
- `HPSA FTE` — full-time-equivalent providers needed to remove the designation.
- `HPSA Formal Ratio` — the population-to-provider ratio underlying the designation.
- `HPSA Provider Ratio Goal` — the target population-to-provider ratio that would resolve the shortage.
- `Metropolitan Indicator` / `HPSA Metropolitan Indicator Code` — metro vs non-metro classification (text and coded form).
- **`*Code` columns** (e.g. `HPSA Status Code`, `HPSA Type Code`, `HPSA Component Type Code`, `Rural Status Code`, `HPSA Population Type Code`) — coded versions of the corresponding text columns.
- `XXXXX` — placeholder value (not a real code) appearing in some code fields, notably `Common State County FIPS Code` for non-county (state-wide/national) designations.

For exact field definitions, see the HRSA Find Shortage Areas / data-download documentation (https://data.hrsa.gov/data/dictionary; the data-download index and HPSA Find tool are linked under Provenance below).

## Provenance & landing pages

- HRSA Data Downloads index: https://data.hrsa.gov/data/download
- HPSA program landing: https://data.hrsa.gov/topics/health-workforce/shortage-areas
- HPSA Find interactive tool: https://data.hrsa.gov/tools/shortage-area/hpsa-find

## Quirks & notes

- **Encoding:** no BOM observed; a standard UTF-8 read works, and `utf-8-sig` is a harmless defensive choice.
- **Quoted strings with embedded commas.** Several fields (e.g., `Common County Name`, address-like fields) contain commas. Use a real CSV parser; do not split on commas with a shell tool.
- **The three discipline files have slightly different schemas** (PC has ~66 columns including a `PC MCTA Score`; MH and DH have ~65). FYI for downstream users joining across disciplines.
- **County FIPS leading zeros.** `Common State County FIPS Code` is a 5-character string (2-digit state + 3-digit county); read as a string so states 01-09 keep the leading zero.
- **`XXXXX` placeholder county FIPS.** A handful of rows per discipline carry `Common State County FIPS Code = "XXXXX"` for non-county (state-wide / national) designations. FYI for downstream users.
- **Score scale (FYI):** the HPSA Score runs 0-25 for PC and MH and 0-26 for DH; higher means a more severe shortage.
- **Status / type values (FYI):** `HPSA Status` is `Designated`, `Withdrawn`, or `Proposed For Withdrawal` (note the capital F). `HPSA Population Type` is `Geographic`, `Population`, or `Facility`.

## Manual fallback

1. Open the HRSA Data Downloads index above.
2. Choose "Health Workforce" -> "Shortage Areas".
3. Click the CSV link for each discipline (PC, MH, DH).
4. Save them as `hpsa_pc.csv`, `hpsa_mh.csv`, `hpsa_dh.csv` into the source's download directory.
5. Re-run `opendata-fetch fetch 07-hrsa-hpsa`; it detects the present files and skips the downloads.
