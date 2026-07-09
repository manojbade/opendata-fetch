# Privacy

opendata-fetch collects, stores, and transmits no personal data. It has no
user accounts, no analytics, and no telemetry. Its only network activity is
outbound requests to public U.S. government open-data endpoints. It processes
only public, non-personal datasets and writes downloaded files to the user's
own local filesystem.

## Do no harm

opendata-fetch handles no personal or sensitive data and redistributes no
data. It fetches public-domain government datasets to the user's machine.
Built-in integrity checks (byte-size floors, rejection of HTML error pages
served with HTTP 200, atomic writes) guard against corrupted or truncated
downloads that could otherwise produce misleading analysis.
