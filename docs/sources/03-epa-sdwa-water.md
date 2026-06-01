# EPA SDWA Water: Service-Area Boundaries + Violations (EPA)

Two EPA drinking-water datasets shipped together. The first is the Community Water System service-area boundaries from EPA's Office of Research and Development (ORD) SAB Model (a national set of polygons for public water systems, distributed as a zip containing a GeoPackage plus census crosswalk tables). The second is the bulk Safe Drinking Water Act (SDWA) table dump from EPA ECHO: water-system identity, the full violations/enforcement history, Lead and Copper Rule samples, and code-value lookups.

Both are large, frequently-refreshed national files. Records key on PWSID (the public water system identifier).

**opendata-fetch slug:** `03-epa-sdwa-water`
**Agency:** EPA
**File type:** two zip archives (one contains a GeoPackage + CSVs; the other contains ~11 CSVs)
**Approx. size:** SAB boundaries zip ~544 MB, SDWA tables zip ~523 MB (the largest CSV inside, `SDWA_VIOLATIONS_ENFORCEMENT.csv`, is ~3.8 GB uncompressed)
**Update cadence:** rolling. The SAB zip always points to the latest version; ECHO refreshes the SDWA tables roughly quarterly.

## Download

opendata-fetch pulls two files at fixed "latest" URLs (no templated variable):

```
https://github.com/USEPA/ORD_SAB_Model/raw/refs/heads/main/Version_History/PWS_Boundaries_Latest.zip  -> PWS_Boundaries_Latest.zip
https://echo.epa.gov/files/echodownloads/SDWA_latest_downloads.zip                                     -> SDWA_latest_downloads.zip
```

Both URLs track the current release automatically; there is no year to bump. If EPA changes the SAB repo path or the ECHO filename, edit the URL in `opendata_fetch/sources.toml`.

### What's inside each zip

**SAB boundaries zip:** `3_0/Service_Areas_V_3_0.gpkg` (~655 MB uncompressed, the polygons), plus census crosswalk CSVs (`Tracts_V_3_0.csv`, `Block_Groups_V_3_0.csv`, `Blocks_V_3_0.csv`), `Missing_CWS_V_3_0.csv`, and `Documentation.pdf`.

**SDWA tables zip:** 11 CSVs, including `SDWA_PUB_WATER_SYSTEMS.csv` (~123 MB), `SDWA_VIOLATIONS_ENFORCEMENT.csv` (~3.8 GB), `SDWA_LCR_SAMPLES.csv` (~118 MB), `SDWA_REF_CODE_VALUES.csv` (lookup table), `SDWA_SERVICE_AREAS.csv`, `SDWA_FACILITIES.csv`, `SDWA_SITE_VISITS.csv`, and others.

## Fields and files in this download

Captured from the files as served at audit time. EPA refreshes these (the ECHO tables roughly quarterly), so column sets can change between releases; resolve coded values against `SDWA_REF_CODE_VALUES.csv` rather than hardcoding.

### SDWA tables zip (`SDWA_latest_downloads.zip`) — 11 CSVs

These tables are not annotated column-by-column (~190 columns total); below is a one-line description of what each table holds. **Shared keys:** `PWSID` (the public water system ID) appears in every system-keyed table and is the primary join key. Most tables also carry `SUBMISSIONYEARQUARTER` (the ECHO data refresh quarter) and `FIRST_REPORTED_DATE`/`LAST_REPORTED_DATE` (when the record was first/last reported to SDWIS). For exact per-column definitions and code meanings, see the SDWIS/ECHO data element dictionary (the ECHO downloads page is linked under Provenance below); resolve coded values against `SDWA_REF_CODE_VALUES.csv`.

**SDWA_PUB_WATER_SYSTEMS.csv** (51) — water-system identity: name, type, owner, source water, population served, service connections, contact/address, and primacy agency. `SUBMISSIONYEARQUARTER, PWSID, PWS_NAME, PRIMACY_AGENCY_CODE, EPA_REGION, SEASON_BEGIN_DATE, SEASON_END_DATE, PWS_ACTIVITY_CODE, PWS_DEACTIVATION_DATE, PWS_TYPE_CODE, DBPR_SCHEDULE_CAT_CODE, CDS_ID, GW_SW_CODE, LT2_SCHEDULE_CAT_CODE, OWNER_TYPE_CODE, POPULATION_SERVED_COUNT, POP_CAT_2_CODE, POP_CAT_3_CODE, POP_CAT_4_CODE, POP_CAT_5_CODE, POP_CAT_11_CODE, PRIMACY_TYPE, PRIMARY_SOURCE_CODE, IS_GRANT_ELIGIBLE_IND, IS_WHOLESALER_IND, IS_SCHOOL_OR_DAYCARE_IND, SERVICE_CONNECTIONS_COUNT, SUBMISSION_STATUS_CODE, ORG_NAME, ADMIN_NAME, EMAIL_ADDR, PHONE_NUMBER, PHONE_EXT_NUMBER, FAX_NUMBER, ALT_PHONE_NUMBER, ADDRESS_LINE1, ADDRESS_LINE2, CITY_NAME, ZIP_CODE, COUNTRY_CODE, FIRST_REPORTED_DATE, LAST_REPORTED_DATE, STATE_CODE, SOURCE_WATER_PROTECTION_CODE, SOURCE_PROTECTION_BEGIN_DATE, OUTSTANDING_PERFORMER, OUTSTANDING_PERFORM_BEGIN_DATE, REDUCED_RTCR_MONITORING, REDUCED_MONITORING_BEGIN_DATE, REDUCED_MONITORING_END_DATE, SEASONAL_STARTUP_SYSTEM`

**SDWA_VIOLATIONS_ENFORCEMENT.csv** (38, ~3.8 GB uncompressed) — the full violation and enforcement history: one row per violation (with its rule, contaminant, health-based flag, compliance period) joined to any enforcement action taken. `SUBMISSIONYEARQUARTER, PWSID, VIOLATION_ID, FACILITY_ID, COMPL_PER_BEGIN_DATE, COMPL_PER_END_DATE, NON_COMPL_PER_BEGIN_DATE, NON_COMPL_PER_END_DATE, PWS_DEACTIVATION_DATE, VIOLATION_CODE, VIOLATION_CATEGORY_CODE, IS_HEALTH_BASED_IND, CONTAMINANT_CODE, VIOL_MEASURE, UNIT_OF_MEASURE, FEDERAL_MCL, STATE_MCL, IS_MAJOR_VIOL_IND, SEVERITY_IND_CNT, CALCULATED_RTC_DATE, VIOLATION_STATUS, PUBLIC_NOTIFICATION_TIER, CALCULATED_PUB_NOTIF_TIER, VIOL_ORIGINATOR_CODE, SAMPLE_RESULT_ID, CORRECTIVE_ACTION_ID, RULE_CODE, RULE_GROUP_CODE, RULE_FAMILY_CODE, VIOL_FIRST_REPORTED_DATE, VIOL_LAST_REPORTED_DATE, ENFORCEMENT_ID, ENFORCEMENT_DATE, ENFORCEMENT_ACTION_TYPE_CODE, ENF_ACTION_CATEGORY, ENF_ORIGINATOR_CODE, ENF_FIRST_REPORTED_DATE, ENF_LAST_REPORTED_DATE`

**SDWA_LCR_SAMPLES.csv** (15) — Lead and Copper Rule sample results: per-sample measured values (with contaminant, unit, result sign) and sampling dates. `SUBMISSIONYEARQUARTER, PWSID, SAMPLE_ID, SAMPLING_END_DATE, SAMPLING_START_DATE, RECONCILIATION_ID, SAMPLE_FIRST_REPORTED_DATE, SAMPLE_LAST_REPORTED_DATE, SAR_ID, CONTAMINANT_CODE, RESULT_SIGN_CODE, SAMPLE_MEASURE, UNIT_OF_MEASURE, SAR_FIRST_REPORTED_DATE, SAR_LAST_REPORTED_DATE`

**SDWA_FACILITIES.csv** (19) — facilities that make up each water system (intakes, wells, treatment, storage, etc.) with type, activity status, water type, and any seller linkage. `SUBMISSIONYEARQUARTER, PWSID, FACILITY_ID, FACILITY_NAME, STATE_FACILITY_ID, FACILITY_ACTIVITY_CODE, FACILITY_DEACTIVATION_DATE, FACILITY_TYPE_CODE, SUBMISSION_STATUS_CODE, IS_SOURCE_IND, WATER_TYPE_CODE, AVAILABILITY_CODE, SELLER_TREATMENT_CODE, SELLER_PWSID, SELLER_PWS_NAME, FILTRATION_STATUS_CODE, IS_SOURCE_TREATED_IND, FIRST_REPORTED_DATE, LAST_REPORTED_DATE`

**SDWA_GEOGRAPHIC_AREAS.csv** (11) — geographic areas served by each system: area type plus the state, county, city, ZIP, and tribal/ANSI codes covered. `SUBMISSIONYEARQUARTER, PWSID, GEO_ID, AREA_TYPE_CODE, TRIBAL_CODE, STATE_SERVED, ANSI_ENTITY_CODE, ZIP_CODE_SERVED, CITY_SERVED, COUNTY_SERVED, LAST_REPORTED_DATE`

**SDWA_EVENTS_MILESTONES.csv** (10) — scheduled compliance events/milestones for each system, with milestone/reason codes, target and actual dates, and comments. `SUBMISSIONYEARQUARTER, PWSID, EVENT_SCHEDULE_ID, EVENT_END_DATE, EVENT_ACTUAL_DATE, EVENT_COMMENTS_TEXT, EVENT_MILESTONE_CODE, EVENT_REASON_CODE, FIRST_REPORTED_DATE, LAST_REPORTED_DATE`

**SDWA_PN_VIOLATION_ASSOC.csv** (12) — public-notification associations: links a public-notice violation to the related underlying violation(s) it covers. `SUBMISSIONYEARQUARTER, PWSID, PN_VIOLATION_ID, RELATED_VIOLATION_ID, COMPL_PER_BEGIN_DATE, COMPL_PER_END_DATE, NON_COMPL_PER_BEGIN_DATE, NON_COMPL_PER_END_DATE, VIOLATION_CODE, CONTAMINANT_CODE, FIRST_REPORTED_DATE, LAST_REPORTED_DATE`

**SDWA_SERVICE_AREAS.csv** (6) — service-area type classification(s) for each system, with a primary-service-area flag. `SUBMISSIONYEARQUARTER, PWSID, SERVICE_AREA_TYPE_CODE, IS_PRIMARY_SERVICE_AREA_CODE, FIRST_REPORTED_DATE, LAST_REPORTED_DATE`

**SDWA_SITE_VISITS.csv** (20) — sanitary-survey / site-visit records: visit date, reason, and per-area evaluation codes (source water, treatment, distribution, security, management, financial, etc.). `SUBMISSIONYEARQUARTER, PWSID, VISIT_ID, VISIT_DATE, AGENCY_TYPE_CODE, VISIT_REASON_CODE, MANAGEMENT_OPS_EVAL_CODE, SOURCE_WATER_EVAL_CODE, SECURITY_EVAL_CODE, PUMPS_EVAL_CODE, OTHER_EVAL_CODE, COMPLIANCE_EVAL_CODE, DATA_VERIFICATION_EVAL_CODE, TREATMENT_EVAL_CODE, FINISHED_WATER_STOR_EVAL_CODE, DISTRIBUTION_EVAL_CODE, FINANCIAL_EVAL_CODE, VISIT_COMMENTS, FIRST_REPORTED_DATE, LAST_REPORTED_DATE`

**SDWA_REF_ANSI_AREAS.csv** (4) — ANSI/FIPS area lookup: maps ANSI state + entity codes to area names (used by `GEOGRAPHIC_AREAS`). `ANSI_STATE_CODE, ANSI_ENTITY_CODE, ANSI_NAME, STATE_CODE`

**SDWA_REF_CODE_VALUES.csv** (3, the lookup table) — the code-to-description dictionary: each row maps a coded value (by `VALUE_TYPE`) to its plain-text meaning; resolve all `*_CODE` columns in the other tables against this. `VALUE_TYPE, VALUE_CODE, VALUE_DESCRIPTION`

### SAB boundaries zip (`PWS_Boundaries_Latest.zip`)

**`3_0/Service_Areas_V_3_0.gpkg`** — a GeoPackage with two layers (both CRS EPSG:4269, NAD83):

- Layer **`CWS`** (Community Water Systems, MultiPolygon, ~44,656 features, 22 fields) — estimated service-area boundary polygons for community water systems, one or more per system. Key columns: `PWSID` (join key), `PWS_Name`, `Population_Served_Count`, `Service_Connections_Count`, `Service_Area_Type`, plus modeling/provenance columns (`Model_Method`, `Data_Source`, `Verification_Status`) and the polygon geometry (`Shape_Length`/`Shape_Area`). Full field list: `Original_Data_Provider, Data_Provider_Type, Data_Source, PWSID, PWS_Name, Primacy_Agency, Pop_Cat_5, Population_Served_Count, Service_Connections_Count, Model_Method, Service_Area_Type, Symbology_Field, Modification_Method, Feature_Type, Method_Details, Verification_Status, Detailed_Facility_Report, Confirmed, PWSID_1, Shape_Length, Shape_Area, Date_Create`
- Layer **`T_NTNC`** (transient + non-transient non-community systems, MultiPolygon, ~77,469 features, 15 fields) — service-area polygons for non-community systems (schools, workplaces, campgrounds, etc.). Key columns: `PWSID` (join key), `PWS_Name`, `PWS_TYPE_CODE`, `POPULATION_SERVED_COUNT`, `SERVICE_AREA_TYPE`, plus location/source attributes. Full field list: `PWSID, PWS_Name, LOCATION_CONFIDENCE, PRIMACY_AGENCY_CODE, PWS_TYPE_CODE, POPULATION_SERVED_COUNT, PRIMARY_SOURCE_CODE, IS_WHOLESALER_IND, IS_SCHOOL_OR_DAYCARE_IND, SERVICE_CONNECTIONS_COUNT, parcelnumb, AREAKM, SERVICE_AREA_TYPE, Detailed_Facility_Report, Data_Source`

**Census crosswalk CSVs** (PWSID-to-census-geography weights, 10 columns each):
- `3_0/Census_Tables/Tracts_V_3_0.csv`: `GEOID20, PWSID, Tract_Km, Tract_I_Km, Area_Weight, Pop20_AW, Tract_Buildings, Tract_O_Buildings, Bldg_Weight, Pop20_BW`
- `3_0/Census_Tables/Block_Groups_V_3_0.csv`: `GEOID20, PWSID, BG_Km, BG_I_Km, Area_Weight, Pop20_AW, BG_Buildings, BG_O_Buildings, Bldg_Weight, Pop20_BW`
- `3_0/Census_Tables/Blocks_V_3_0.csv`: `GEOID20, PWSID, Block_Km, Block_I_Km, Area_Weight, Pop20_AW, Block_Buildings, Block_O_Buildings, Bldg_Weight, Pop20_BW`

**`3_0/Missing_CWS_V_3_0.csv`** (6, systems with no boundary): an unnamed index column, then `PWS ID, PWS Name, Primacy Agency, Population Served Count, Service Connections Count`. The zip also includes `Documentation.pdf`, `README.md`, `Copy_Features.R`, and `Crosswalk.png`.

## Provenance & landing pages

- EPA Community Water System Service Area Boundaries: https://www.epa.gov/ground-water-and-drinking-water/community-water-system-service-area-boundaries
- EPA ORD SAB Model GitHub repo: https://github.com/USEPA/ORD_SAB_Model
- EPA ECHO downloads index: https://echo.epa.gov/files/echodownloads/
- EPA SDWIS Federal Reports / data downloads: https://echo.epa.gov/tools/data-downloads

## Quirks & notes

- **The SDWA zip is ~523 MB and one CSV inside it is ~3.8 GB uncompressed.** A downstream reader must chunk `SDWA_VIOLATIONS_ENFORCEMENT.csv`; it does not fit comfortably in memory.
- **ECHO CSV dates are `MM/DD/YYYY`, not ISO.** A naive string MAX produces wrong results; parse to a date type before comparing. FYI for downstream users.
- **ECHO CSVs use double-quoted strings.** Use a real CSV parser with quote handling.
- **Code meanings can change between releases.** Violation/rule/contaminant codes are described in `SDWA_REF_CODE_VALUES.csv`; do not hardcode a specific numeric code (e.g., the Lead Consumer Notice violation code has shifted across releases). Resolve codes against the reference table at read time.
- **PWSID format (FYI):** usually a 2-letter state code + 7 digits (9 chars total), but tribal/territory systems use non-standard formats (e.g., 9 digits with no letter prefix). Read PWSID as a string.
- **SAB GeoPackage holds duplicate PWSIDs** for utilities with split/discontiguous service areas (multiple polygons per system). The raw file keeps them all; dedup is a downstream choice.
- `min_bytes` for both files is set at 400 MB in the registry as an integrity floor; a truncated download or HTML error page falls below it and is rejected.

## Manual fallback

1. **SAB boundaries:** open the EPA SABs landing page, click "Download Map Data", save the zip as `PWS_Boundaries_Latest.zip` into the source's download directory.
2. **SDWA tables:** open the ECHO downloads index, download `SDWA_latest_downloads.zip` into the same directory.
3. Re-run `opendata-fetch fetch 03-epa-sdwa-water`; it detects the present files and skips the downloads.
