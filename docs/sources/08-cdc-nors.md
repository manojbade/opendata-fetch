# CDC National Outbreak Reporting System (CDC)

CDC's National Outbreak Reporting System (NORS) is the national line list of disease outbreaks reported by US states and territories since 1971: foodborne, waterborne, person-to-person, animal-contact, and environmental. Each row is a single outbreak, with date, location, mode of transmission, etiology, setting, and outcome counts (illnesses, hospitalizations, deaths). It is the only national source for state-level waterborne outbreak counts. The file is a single CSV (~19 columns) distributed through the Socrata data portal at data.cdc.gov.

**opendata-fetch slug:** `08-cdc-nors`
**Agency:** CDC
**File type:** csv (Socrata export)
**Approx. size:** ~7.1 MB
**Update cadence:** annual. The Socrata `dataset_id` may change on a new release.

## Download

opendata-fetch pulls one file:

```
https://data.cdc.gov/api/views/{dataset_id}/rows.csv?accessType=DOWNLOAD  -> nors_outbreaks.csv
```

`{dataset_id}` is the Socrata dataset id (currently `5xkq-dg7x`), filled from the source's `vars` table in `opendata_fetch/sources.toml`; updating it is a one-line edit. Unlike PLACES, CDC has historically updated NORS in place under a stable id rather than minting a new id each year, so this id tends to persist; still confirm it on a new release.

## Fields and files in this download

Captured from `nors_outbreaks.csv` (19 columns, one row per reported outbreak). `Water Type` can hold multiple semicolon-separated values; `Animal Type` mixes types.

Columns (19):

| column | meaning |
|--------|---------|
| `Year` | Year the outbreak occurred. |
| `Month` | Month the outbreak occurred. |
| `State` | Reporting state (full name, e.g. `New Jersey`; `Multistate` for multi-state outbreaks). |
| `Primary Mode` | Primary mode of transmission (foodborne, waterborne, person-to-person, animal contact, environmental, etc.). |
| `Etiology` | Causative agent (pathogen, toxin, or chemical). |
| `Serotype or Genotype` | Serotype/genotype subtyping of the etiologic agent, where reported. |
| `Etiology Status` | Confirmed vs suspected status of the etiology. |
| `Setting` | Setting where exposure/transmission occurred (e.g. restaurant, private residence). |
| `Illnesses` | Number of illnesses (cases) in the outbreak. |
| `Hospitalizations` | Number of cases hospitalized. |
| `Info On Hospitalizations` | Whether hospitalization information was collected/known. |
| `Deaths` | Number of deaths. |
| `Info On Deaths` | Whether death information was collected/known. |
| `Food Vehicle` | Implicated food vehicle. |
| `Food Contaminated Ingredient` | Contaminated ingredient within the food vehicle. |
| `IFSAC Category` | IFSAC food-categorization scheme assignment for the food vehicle. |
| `Water Exposure` | Type of water exposure/activity implicated (e.g. recreational, drinking). |
| `Water Type` | Water source/type implicated; may be a semicolon-delimited list of multiple sources. |
| `Animal Type` | Animal type implicated in animal-contact outbreaks; mixes string values and blanks. |

## Provenance & landing pages

- NORS data landing: https://www.cdc.gov/nors/data/index.html
- Socrata dataset page: https://data.cdc.gov/Foodborne-Waterborne-and-Related-Diseases/NORS/5xkq-dg7x
- NORS program landing: https://www.cdc.gov/nors/about/index.html
- BEAM Dashboard (interactive viewer): https://www.cdc.gov/ncezid/dfwed/keyprograms/beam.html

## Quirks & notes

- **HEAD returns Content-Length: 0.** Same Socrata behavior as PLACES: HEAD reports zero length, the bytes arrive on GET. Do not size from HEAD.
- **Socrata `dataset_id` could rotate on a new release.** Re-confirm the id from the dataset page if a fresh release fails to resolve.
- **Encoding:** no BOM observed; standard UTF-8 reads fine, `utf-8-sig` is a harmless defensive choice.
- **Mixed types in `Animal Type`.** That column mixes string values and blanks; a downstream reader should set an explicit dtype or `low_memory=False`.
- **`State` uses full names, not 2-letter codes** ("New Jersey", not "NJ"), and includes a `Multistate` pseudo-state for outbreaks spanning several states. FYI for downstream users joining on state.
- **Some `Water Type` cells are semicolon-delimited lists** (e.g., `Hot Tub/Spa/Whirlpool;Pool - Other Swimming Pool`) when an outbreak hit multiple water sources. FYI for downstream parsing.
- The file goes back to 1971; the `Year` column lets a downstream user window to a recent range.

## Manual fallback

1. Open the Socrata dataset page above.
2. Click "Export" -> "CSV".
3. Save it as `nors_outbreaks.csv` into the source's download directory.
4. Re-run `opendata-fetch fetch 08-cdc-nors`; it detects the present file and skips the download.
