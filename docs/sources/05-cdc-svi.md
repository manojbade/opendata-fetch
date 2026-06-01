# CDC/ATSDR Social Vulnerability Index (CDC / ATSDR)

The Social Vulnerability Index (SVI), from CDC's Agency for Toxic Substances and Disease Registry (ATSDR), scores how socially vulnerable each US census tract is to external stressors such as disasters and environmental hazards. It rolls 16 census-tract variables (poverty, unemployment, housing burden, education, age, disability, single-parent households, minority status, language, housing type, crowding, vehicle access, group quarters) into four theme percentile ranks plus one overall rank (`RPL_THEMES`). All ranks run 0 to 1; higher means more vulnerable.

The national tract-level CSV is one row per census tract (~84,000 rows). SVI is keyed by the 11-character tract FIPS code.

**opendata-fetch slug:** `05-cdc-svi`
**Agency:** CDC / ATSDR
**File type:** csv
**Approx. size:** ~58 MB
**Update cadence:** biennial. Bump `vintage` to the latest release year.

## Download

opendata-fetch pulls one file:

```
https://svi.cdc.gov/Documents/Data/{vintage}/csv/states/SVI_{vintage}_US.csv  -> SVI_{vintage}_US.csv
```

The general pattern is:

```
https://svi.cdc.gov/Documents/Data/{year}/{format}/states/SVI_{year}_US.csv
```

`{vintage}` is the release year (2014, 2016, 2018, 2020, 2022, ...), filled from the source's `vars` table in `opendata_fetch/sources.toml`; bumping it is a one-line edit. Released roughly every two years.

## Fields and files in this download

Captured from `SVI_2022_US.csv` (158 columns, one row per census tract). The 2022 file opens with a UTF-8 BOM before the first column name; `-999` is CDC's missing-data sentinel. Column naming convention: `E_` = estimate, `M_` = margin of error, `EP_`/`MP_` = percentage + its margin, `EPL_` = per-variable percentile rank, `SPL_`/`RPL_` = summed/overall theme percentile, `F_` = top-quartile flag.

Columns (158):

`ST, STATE, ST_ABBR, STCNTY, COUNTY, FIPS, LOCATION, AREA_SQMI, E_TOTPOP, M_TOTPOP, E_HU, M_HU, E_HH, M_HH, E_POV150, M_POV150, E_UNEMP, M_UNEMP, E_HBURD, M_HBURD, E_NOHSDP, M_NOHSDP, E_UNINSUR, M_UNINSUR, E_AGE65, M_AGE65, E_AGE17, M_AGE17, E_DISABL, M_DISABL, E_SNGPNT, M_SNGPNT, E_LIMENG, M_LIMENG, E_MINRTY, M_MINRTY, E_MUNIT, M_MUNIT, E_MOBILE, M_MOBILE, E_CROWD, M_CROWD, E_NOVEH, M_NOVEH, E_GROUPQ, M_GROUPQ, EP_POV150, MP_POV150, EP_UNEMP, MP_UNEMP, EP_HBURD, MP_HBURD, EP_NOHSDP, MP_NOHSDP, EP_UNINSUR, MP_UNINSUR, EP_AGE65, MP_AGE65, EP_AGE17, MP_AGE17, EP_DISABL, MP_DISABL, EP_SNGPNT, MP_SNGPNT, EP_LIMENG, MP_LIMENG, EP_MINRTY, MP_MINRTY, EP_MUNIT, MP_MUNIT, EP_MOBILE, MP_MOBILE, EP_CROWD, MP_CROWD, EP_NOVEH, MP_NOVEH, EP_GROUPQ, MP_GROUPQ, EPL_POV150, EPL_UNEMP, EPL_HBURD, EPL_NOHSDP, EPL_UNINSUR, SPL_THEME1, RPL_THEME1, EPL_AGE65, EPL_AGE17, EPL_DISABL, EPL_SNGPNT, EPL_LIMENG, SPL_THEME2, RPL_THEME2, EPL_MINRTY, SPL_THEME3, RPL_THEME3, EPL_MUNIT, EPL_MOBILE, EPL_CROWD, EPL_NOVEH, EPL_GROUPQ, SPL_THEME4, RPL_THEME4, SPL_THEMES, RPL_THEMES, F_POV150, F_UNEMP, F_HBURD, F_NOHSDP, F_UNINSUR, F_THEME1, F_AGE65, F_AGE17, F_DISABL, F_SNGPNT, F_LIMENG, F_THEME2, F_MINRTY, F_THEME3, F_MUNIT, F_MOBILE, F_CROWD, F_NOVEH, F_GROUPQ, F_THEME4, F_TOTAL, E_DAYPOP, E_NOINT, M_NOINT, E_AFAM, M_AFAM, E_HISP, M_HISP, E_ASIAN, M_ASIAN, E_AIAN, M_AIAN, E_NHPI, M_NHPI, E_TWOMORE, M_TWOMORE, E_OTHERRACE, M_OTHERRACE, EP_NOINT, MP_NOINT, EP_AFAM, MP_AFAM, EP_HISP, MP_HISP, EP_ASIAN, MP_ASIAN, EP_AIAN, MP_AIAN, EP_NHPI, MP_NHPI, EP_TWOMORE, MP_TWOMORE, EP_OTHERRACE, MP_OTHERRACE`

### Column families

Rather than 158 individual definitions, the columns follow a small set of naming patterns. The same set of thematic variables repeats across each prefix family:

- **Geographic identity:** `ST`, `STATE`, `ST_ABBR`, `STCNTY`, `COUNTY`, `FIPS` (11-char tract FIPS), `LOCATION`, `AREA_SQMI`.
- **Base counts:** `E_TOTPOP`/`M_TOTPOP` (total population), `E_HU`/`M_HU` (housing units), `E_HH`/`M_HH` (households), plus `E_DAYPOP` (estimated daytime population).
- **`E_` = estimate** and **`M_` = margin of error** for each thematic variable (raw counts).
- **`EP_` = estimated percentage** and **`MP_` = its margin of error** for each thematic variable.
- **`EPL_` = per-variable percentile rank** (0-1, higher = more vulnerable).
- **`SPL_THEMEn` = summed theme percentile**, **`RPL_THEMEn` = overall theme percentile rank**; `SPL_THEMES`/`RPL_THEMES` are the across-all-themes summary.
- **`F_` = top-quartile flag** (1 if the variable/theme ranks in the most-vulnerable quartile); `F_TOTAL` sums the flags.

The thematic variables (the suffix shared across families) are: `POV150` (below 150% poverty), `UNEMP` (unemployed), `HBURD` (housing-cost burden), `NOHSDP` (no high-school diploma), `UNINSUR` (uninsured), `AGE65` (aged 65+), `AGE17` (aged 17 and under), `DISABL` (with a disability), `SNGPNT` (single-parent households), `LIMENG` (limited English), `MINRTY` (racial/ethnic minority), `MUNIT` (multi-unit housing), `MOBILE` (mobile homes), `CROWD` (crowded housing), `NOVEH` (no vehicle), `GROUPQ` (group quarters). The race/ethnicity detail variables (`AFAM`, `HISP`, `ASIAN`, `AIAN`, `NHPI`, `TWOMORE`, `OTHERRACE`) and `NOINT` (no internet) appear only in `E_`/`M_`/`EP_`/`MP_` form (no percentile/flag).

The four themes are: Theme 1 = Socioeconomic, Theme 2 = Household Characteristics, Theme 3 = Racial & Ethnic Minority Status, Theme 4 = Housing Type & Transportation.

For exact per-column definitions, see the official SVI 2022 documentation PDF (linked under Provenance below, and at https://www.atsdr.cdc.gov/place-health/media/pdfs/2024/SVI2022Documentation_08.pdf).

## Provenance & landing pages

- CDC SVI interactive data-download page: https://svi.cdc.gov/dataDownloads/data-download.html
- ATSDR SVI Data & Documentation: https://www.atsdr.cdc.gov/place-health/php/svi/svi-data-documentation-download.html
- ATSDR SVI program landing: https://www.atsdr.cdc.gov/place-health/php/svi/index.html
- SVI 2022 documentation (full methodology): https://www.atsdr.cdc.gov/place-health/media/pdfs/2024/10/SVI2022Documentation.pdf

## Quirks & notes

- **Download URL is hidden behind JavaScript.** The CDC SVI download page builds the URL from form selections via `/js/loadXML.js`; there is no direct download link in the page HTML. The direct URL above was reverse-engineered from that JS, which is how you find a new year's URL if the format changes.
- **BOM in the first column header.** The file begins with a UTF-8 byte-order mark before the first column name (`ST`). Read as `utf-8-sig`. FYI for downstream parsing.
- **`-999` is the missing-data sentinel.** CDC uses `-999` (and variants like `-999.0`) across numeric columns to mean "data unavailable / insufficient data," typically in very small or suppressed tracts. Treat `-999` as missing, not as a real value. This is an FYI for downstream users; opendata-fetch ships the file as-is.
- **FIPS leading zeros.** The 11-character tract `FIPS` (2-digit state + 3-digit county + 6-digit tract) must be read as a string; integer parsing drops the leading zero for states 01-09.
- Theme composition (FYI): Theme 1 = Socioeconomic, Theme 2 = Household Characteristics, Theme 3 = Racial & Ethnic Minority Status, Theme 4 = Housing Type & Transportation.

## Manual fallback

1. Open the CDC SVI data-download page above.
2. Select: Year = latest available; Geography = United States; Geography Type = Census Tracts; File Type = CSV.
3. Click "Go" to trigger the download.
4. Save the resulting `SVI_{vintage}_US.csv` into the source's download directory.
5. Re-run `opendata-fetch fetch 05-cdc-svi`; it detects the present file and skips the download.
