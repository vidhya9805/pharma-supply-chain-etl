\# Pharmaceutical Supply Chain \& Cold-Chain Quality Audit Pipeline



An end-to-end \*\*Python and SQL data engineering pipeline\*\* designed to ingest, validate, and analyze \*\*50,000+ global pharmaceutical logistics records\*\*, tracking temperature excursions (`2°C–8°C` cold-chain compliance) and On-Time In-Full (OTIF) delivery KPIs.



\## Architecture \& Workflow

1\. \*\*Automated Data Ingestion \& Quality Audit (`etl\_pipeline.py`):\*\*

&#x20;  - Simulates 50,000 multi-hub pharmaceutical shipments (\*Lantus, Toujeo, Dupixent, Clexane, VaxRabeo\*) across APAC, EMEA, NA, and LATAM.

&#x20;  - Identifies and quarantines duplicate shipment IDs and missing critical fields into `audit\_error\_log.csv` (252 anomalies isolated), outputting 49,748 validated records to `clean\_shipments.csv`.

&#x20;  - Flags cold-chain temperature breaches (`< 2.0°C` or `> 8.0°C`), detecting 8,191 excursions.

2\. \*\*Relational Storage \& Analytical SQL (`load\_and\_query.py`):\*\*

&#x20;  - Loads validated records into a local relational database (`pharma\_supply.db`) with composite indexing on `(origin\_hub, drug\_name)` for fast aggregation.

&#x20;  - Executes analytical SQL queries utilizing \*\*Common Table Expressions (CTEs)\*\*, \*\*Window Functions (`DENSE\_RANK`)\*\*, and conditional `CASE` aggregations to compute hub-level breach rates and OTIF delivery percentages.

3\. \*\*Automated Executive Reporting:\*\*

&#x20;  - Exports summary metrics to `hub\_kpi\_summary.csv` and generates a visual KPI comparison chart (`hub\_kpi\_chart.png`).



\## Visual KPI Output

!\[Hub Performance Chart](hub\_kpi\_chart.png)



\## Tech Stack

\- \*\*Languages:\*\* Python 3.11, SQL

\- \*\*Libraries:\*\* Pandas, NumPy, SQLite3, Matplotlib



