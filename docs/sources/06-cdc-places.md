# CDC PLACES: Local Data for Better Health, Census Tract (CDC)

CDC PLACES (a CDC / Robert Wood Johnson Foundation collaboration) publishes model-based small-area estimates of health outcomes, preventive-service use, health behaviors, disabilities, and social determinants. It combines BRFSS survey data with American Community Survey demographics using multilevel modeling. The census-tract file is a long-format CSV: one row per tract x measure, covering 40 distinct measures, distributed through the Socrata data portal at data.cdc.gov.

**opendata-fetch slug:** `06-cdc-places`
**Agency:** CDC
**File type:** csv (Socrata export)
**Approx. size:** ~695 MB (long format, ~3.05 million rows)
**Update cadence:** annual. The Socrata `dataset_id` changes on each release, so it must be re-discovered on data.cdc.gov.

## Download

opendata-fetch pulls one file:

```
https://data.cdc.gov/api/views/{dataset_id}/rows.csv?accessType=DOWNLOAD  -> PLACES_CensusTract.csv
```

`{dataset_id}` is the Socrata dataset id for the current release (e.g., `cwsq-ngmh`), filled from the source's `vars` table in `opendata_fetch/sources.toml`; updating it is a one-line edit. **Socrata assigns a new id per annual release,** so unlike year-templated sources you cannot just bump a number, you must look up the new id.

### Finding the current dataset_id

**Programmatic (Socrata catalog API):**

```bash
curl -sL "https://api.us.socrata.com/api/catalog/v1?domains=data.cdc.gov&q=PLACES+census+tract&limit=20"
```

In the JSON results, keep entries whose name contains "Local Data for Better Health, Census Tract Data" (NOT the "GIS Friendly Format" wide variant, and not the county-level series), pick the most recent by `updatedAt`, and read `resource.id`. That id goes into `dataset_id`.

**Manual:** browse https://data.cdc.gov/browse?q=PLACES+census+tract, sort by most recent, open "PLACES: Local Data for Better Health, Census Tract Data, {year} release"; the dataset id is the slug at the end of the URL.

## Fields and files in this download

Captured from the 2025 release (`PLACES_CensusTract.csv`, 24 columns; ~3.05M rows, ~83,500 tracts, 40 measures). This is a **long-format** file: one row per census tract x health measure, so a single tract appears on up to 40 rows. `MeasureId` / `Short_Question_Text` identify the measure; `Data_Value` holds the estimate.

Columns (24):

| column | meaning |
|--------|---------|
| `Year` | Data year of the estimate. |
| `StateAbbr` | 2-letter state postal abbreviation. |
| `StateDesc` | Full state name. |
| `CountyName` | County name containing the tract. |
| `CountyFIPS` | 5-character county FIPS (state + county). |
| `LocationName` | Tract identifier (11-character tract GEOID). |
| `DataSource` | Underlying source of the estimate (e.g. BRFSS). |
| `Category` | Broad measure category (e.g. Health Outcomes, Prevention). |
| `Measure` | Full label of the health measure. |
| `Data_Value_Unit` | Unit of the value (typically `%`). |
| `Data_Value_Type` | Estimate type (e.g. age-adjusted vs crude prevalence). |
| `Data_Value` | The model-based estimate. |
| `Data_Value_Footnote_Symbol` | Footnote symbol flagging suppressed/missing values. |
| `Data_Value_Footnote` | Footnote text explaining the symbol. |
| `Low_Confidence_Limit` | Lower bound of the 95% confidence interval. |
| `High_Confidence_Limit` | Upper bound of the 95% confidence interval. |
| `TotalPopulation` | Total tract population. |
| `TotalPop18plus` | Tract population aged 18 and over. |
| `Geolocation` | Tract centroid as a point (lon/lat). |
| `LocationID` | Tract identifier (11-character tract FIPS). |
| `CategoryID` | Short code for `Category`. |
| `MeasureId` | Short code for the measure (e.g. `CASTHMA`). |
| `DataValueTypeID` | Short code for `Data_Value_Type` (`CrdPrv` crude, `AgeAdjPrv` age-adjusted). |
| `Short_Question_Text` | Short plain-text label for the measure. |

## Provenance & landing pages

- PLACES data portal: https://www.cdc.gov/places/tools/data-portal.html
- Current census-tract release on data.cdc.gov: https://data.cdc.gov/500-Cities-Places/PLACES-Local-Data-for-Better-Health-Census-Tract-D/cwsq-ngmh
- PLACES program landing: https://www.cdc.gov/places/index.html
- PLACES methodology: https://www.cdc.gov/places/methodology/index.html

## Quirks & notes

- **Socrata `dataset_id` rotates every release.** Re-discover it (above) rather than assuming the prior id still resolves.
- **HEAD returns Content-Length: 0.** Socrata generates the CSV on demand, so a HEAD request reports zero length; the bytes arrive during the GET. Do not rely on HEAD for size estimation. (The registry sets `min_bytes` at 600 MB as the integrity floor for this file.)
- **Two parallel series exist:** "Local Data for Better Health, Census Tract Data" (long format, the one opendata-fetch ships) and "Census Tract Data (GIS Friendly Format)" (wide). Make sure the id you set points at the one you want.
- **Long format (FYI):** each row is a single measure for a single tract; a tract has up to 40 rows (one per measure). `MeasureId` is the short code (e.g., `CASTHMA`), `Measure` the full label. Each measure carries a single `DataValueTypeID`, either `CrdPrv` (crude prevalence) or `AgeAdjPrv` (age-adjusted), not both. Some `Data_Value` cells are blank where the BRFSS sample was too small; the `Data_Value_Footnote_Symbol` flags those.
- `LocationID` is the 11-character tract FIPS; read as a string to preserve leading zeros.

## Manual fallback

1. Open the PLACES data portal above and find the latest census-tract release.
2. Click "Export" -> "CSV".
3. Save it as `PLACES_CensusTract.csv` into the source's download directory.
4. Re-run `opendata-fetch fetch 06-cdc-places`; it detects the present file and skips the download.
