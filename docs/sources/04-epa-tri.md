# EPA TRI Basic Data File (EPA)

EPA's Toxics Release Inventory (TRI) tracks toxic-chemical releases self-reported by industrial and federal facilities. The Basic Data File is a national CSV for a single reporting year, with one row per facility x chemical x reporting form. Each row carries the facility location, chemical identity, carcinogen/PBT/PFAS flags, and quantitative release amounts across many pathways. Roughly 21,000 facilities report each year, yielding ~77,000 rows nationally.

**opendata-fetch slug:** `04-epa-tri`
**Agency:** EPA
**File type:** csv
**Approx. size:** ~58 MB for one year's national file
**Update cadence:** annual. Bump `vintage` to the latest reporting year.

## Download

opendata-fetch pulls one file:

```
https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/{vintage}_us/csv  -> {vintage}_us.csv
```

The general pattern is:

```
https://data.epa.gov/efservice/downloads/tri/mv_tri_basic_download/{YEAR}_{GEOGRAPHY}/csv
```

`{vintage}` is the calendar reporting year (e.g., `2024`), filled from the source's `vars` table in `opendata_fetch/sources.toml`; bumping it is a one-line edit. `{GEOGRAPHY}` is `us` for the national file or a two-letter state code; opendata-fetch ships the national file.

### TRI release timing

The preliminary dataset for a reporting year appears around July-September of the following year; EPA finalizes it (the "National Analysis" dataset) in October. The URL does not change between preliminary and final, so the same templated URL serves whichever EPA has currently published.

## Fields and files in this download

Captured from the `2024` reporting-year national file (`2024_us.csv`), 122 columns, one row per facility x chemical x form. Columns keep EPA's ordinal-number prefixes verbatim. Schema is stable across recent years.

> Note: this raw file **includes facility names, street addresses, and parent-company names** (columns 4-6, 15-20). They are public EPA data, but if you republish a derivative, consider whether you want to carry those identifying fields.

Columns (122):

`1. YEAR, 2. TRIFD, 3. FRS ID, 4. FACILITY NAME, 5. STREET ADDRESS, 6. CITY, 7. COUNTY, 8. ST, 9. ZIP, 10. BIA, 11. TRIBE, 12. LATITUDE, 13. LONGITUDE, 14. HORIZONTAL DATUM, 15. PARENT CO NAME, 16. PARENT CO DB NUM, 17. STANDARD PARENT CO NAME, 18. FOREIGN PARENT CO NAME, 19. FOREIGN PARENT CO DB NUM, 20. STANDARD FOREIGN PARENT CO NAME, 21. FEDERAL FACILITY, 22. INDUSTRY SECTOR CODE, 23. INDUSTRY SECTOR, 24. PRIMARY SIC, 25. SIC 2, 26. SIC 3, 27. SIC 4, 28. SIC 5, 29. SIC 6, 30. PRIMARY NAICS, 31. NAICS 2, 32. NAICS 3, 33. NAICS 4, 34. NAICS 5, 35. NAICS 6, 36. DOC_CTRL_NUM, 37. CHEMICAL, 38. ELEMENTAL METAL INCLUDED, 39. TRI CHEMICAL/COMPOUND ID, 40. CAS#, 41. SRS ID, 42. CLEAN AIR ACT CHEMICAL, 43. CLASSIFICATION, 44. METAL, 45. METAL CATEGORY, 46. CARCINOGEN, 47. PBT, 48. PFAS, 49. FORM TYPE, 50. UNIT OF MEASURE, 51. 5.1 - FUGITIVE AIR, 52. 5.2 - STACK AIR, 53. 5.3 - WATER, 54. 5.4 - UNDERGROUND, 55. 5.4.1 - UNDERGROUND CL I, 56. 5.4.2 - UNDERGROUND C II-V, 57. 5.5.1 - LANDFILLS, 58. 5.5.1A - RCRA C LANDFILL, 59. 5.5.1B - OTHER LANDFILLS, 60. 5.5.2 - LAND TREATMENT, 61. 5.5.3 - SURFACE IMPNDMNT, 62. 5.5.3A - RCRA SURFACE IM, 63. 5.5.3B - OTHER SURFACE I, 64. 5.5.4 - OTHER DISPOSAL, 65. ON-SITE RELEASE TOTAL, 66. 6.1 - POTW - TRNS RLSE, 67. 6.1 - POTW - TRNS TRT, 68. POTW - TOTAL TRANSFERS, 69. 6.2 - M10, 70. 6.2 - M41, 71. 6.2 - M62, 72. 6.2 - M40 METAL, 73. 6.2 - M61 METAL, 74. 6.2 - M71, 75. 6.2 - M81, 76. 6.2 - M82, 77. 6.2 - M72, 78. 6.2 - M63, 79. 6.2 - M66, 80. 6.2 - M67, 81. 6.2 - M64, 82. 6.2 - M65, 83. 6.2 - M73, 84. 6.2 - M79, 85. 6.2 - M90, 86. 6.2 - M94, 87. 6.2 - M99, 88. OFF-SITE RELEASE TOTAL, 89. 6.2 - M20, 90. 6.2 - M24, 91. 6.2 - M26, 92. 6.2 - M28, 93. 6.2 - M93, 94. OFF-SITE RECYCLED TOTAL, 95. 6.2 - M56, 96. 6.2 - M92, 97. OFF-SITE ENERGY RECOVERY T, 98. 6.2 - M40 NON-METAL, 99. 6.2 - M50, 100. 6.2 - M54, 101. 6.2 - M61 NON-METAL, 102. 6.2 - M69, 103. 6.2 - M95, 104. OFF-SITE TREATED TOTAL, 105. 6.2 - UNCLASSIFIED, 106. 6.2 - TOTAL TRANSFER, 107. TOTAL RELEASES, 108. 8.1 - RELEASES, 109. 8.1A - ON-SITE CONTAINED, 110. 8.1B - ON-SITE OTHER, 111. 8.1C - OFF-SITE CONTAIN, 112. 8.1D - OFF-SITE OTHER R, 113. 8.2 - ENERGY RECOVER ON, 114. 8.3 - ENERGY RECOVER OF, 115. 8.4 - RECYCLING ON SITE, 116. 8.5 - RECYCLING OFF SIT, 117. 8.6 - TREATMENT ON SITE, 118. 8.7 - TREATMENT OFF SITE, 119. PRODUCTION WSTE (8.1-8.7), 120. 8.8 - ONE-TIME RELEASE, 121. PROD_RATIO_OR_ ACTIVITY, 122. 8.9 - PRODUCTION RATIO`

### Column families

Rather than 122 individual definitions, the columns fall into a few blocks. The `5.x`, `6.x`, and `8.x` prefixes mirror the sections of EPA's TRI Form R reporting form, and the `M__` codes are EPA waste-transfer method codes (resolve exact code meanings against the documentation PDF below):

- **Identity & location (1-20):** reporting year, facility identifiers (`TRIFD`, `FRS ID`), facility name/address, county/state/ZIP, tribal land (`BIA`, `TRIBE`), lat/lon + datum, and parent-company names/identifiers.
- **Federal-facility & industry classification (21-35):** `FEDERAL FACILITY` flag, EPA industry sector, and the SIC (`24-29`) and NAICS (`30-35`) codes for the facility.
- **Chemical identity & flags (36-50):** form control number, chemical name and IDs (`CAS#`, `SRS ID`, TRI compound ID), and classification flags (`CLEAN AIR ACT CHEMICAL`, `METAL`, `CARCINOGEN`, `PBT`, `PFAS`), plus form type and unit of measure.
- **On-site releases, Form R Section 5 (51-65):** quantities released on-site by pathway: fugitive/stack air (`5.1`/`5.2`), water (`5.3`), underground injection (`5.4.x`), landfills/land treatment/surface impoundments/other disposal (`5.5.x`), and the `ON-SITE RELEASE TOTAL`.
- **Off-site transfers, Form R Section 6 (66-106):** POTW transfers (`6.1`), then off-site transfers by waste-management method code (`6.2 - M__`), grouped into release/recycling/energy-recovery/treatment subtotals (`OFF-SITE … TOTAL`) and `6.2 - TOTAL TRANSFER`.
- **Total (107):** `TOTAL RELEASES` across all pathways.
- **Waste management, Form R Section 8 (108-122):** source-reduction and waste-management quantities: total releases (`8.1`), on/off-site disposal detail (`8.1A-D`), energy recovery (`8.2`/`8.3`), recycling (`8.4`/`8.5`), treatment (`8.6`/`8.7`), total production-related waste (`8.1-8.7`), one-time releases (`8.8`), and the production ratio / activity index (`8.9`).

For exact per-column definitions and the full `M__` method-code list, see the TRI Basic Data Files documentation PDF (linked under Provenance below).

## Provenance & landing pages

- TRI Basic Data Files index (1987-present): https://www.epa.gov/toxics-release-inventory-tri-program/tri-basic-data-files-calendar-years-1987-present
- TRI Program landing: https://www.epa.gov/toxics-release-inventory-tri-program
- Documentation PDF: https://www.epa.gov/system/files/documents/2025-09/basic_data_files_documentation_august_2024.pdf

## Quirks & notes

- **HTTP HEAD returns 500.** The URL responds with HTTP 500 to a HEAD request but downloads correctly on GET. Do not rely on HEAD to test availability; do a small ranged GET or just download and validate.
- **Numeric column-name prefixes.** Raw columns are prefixed with ordinals: `1. YEAR`, `2. TRIFD`, `3. FRS ID`, `12. LATITUDE`, etc. FYI for downstream parsing.
- **Encoding:** no BOM observed, so a standard UTF-8 read works; reading as `utf-8-sig` is harmless and defends against EPA adding a BOM later.
- **Yes/No fields are strings.** `CARCINOGEN`, `PBT`, `PFAS`, `FEDERAL FACILITY` are stored as `"YES"`/`"NO"` text, not booleans.
- **Multiple rows per facility.** One facility reports one row per chemical, so a facility appears many times. The file also carries three identifiers: `TRIFD` (TRI facility id), `FRS ID` (EPA-wide facility id), `DOC_CTRL_NUM` (per-form id). Some facilities have slightly different lat/lon across their rows (geocoding revisions). All of this is preserved as shipped; any dedup is a downstream choice.

## Manual fallback

1. Open the TRI Basic Data Files index above.
2. Use the "Choose a year" and "Choose a state or geographic region" controls; select the latest year and "United States".
3. Click "Download Basic Data" to get the CSV.
4. Save it as `{vintage}_us.csv` into the source's download directory.
5. Re-run `opendata-fetch fetch 04-epa-tri`; it detects the present file and skips the download.
