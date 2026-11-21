import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# 1. Connect to local SQLite database (auto-creates pharma_supply.db, no password needed)
conn = sqlite3.connect("pharma_supply.db")

# 2. Load cleaned CSV into SQL database and create a composite index for query speed
df = pd.read_csv("clean_shipments.csv")
df.to_sql("shipments_fact", con=conn, if_exists="replace", index=False)
conn.execute("CREATE INDEX IF NOT EXISTS idx_hub_drug ON shipments_fact (origin_hub, drug_name);")
conn.commit()
print("Successfully loaded 49,748 rows into SQL table 'shipments_fact' with composite index.")

# 3. Analytical SQL Query: CTE + Window Function (DENSE_RANK) + On-Time In-Full (OTIF)
analytical_query = """
WITH HubDrugMetrics AS (
    SELECT 
        origin_hub,
        drug_name,
        COUNT(*) AS total_shipments,
        ROUND(AVG(transit_days), 2) AS avg_transit_days,
        SUM(cold_chain_breach) AS breach_count,
        ROUND(100.0 * SUM(cold_chain_breach) / COUNT(*), 2) AS breach_rate_pct,
        ROUND(100.0 * SUM(CASE WHEN transit_days <= 5 AND cold_chain_breach = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS otif_pct
    FROM shipments_fact
    GROUP BY origin_hub, drug_name
)
SELECT 
    origin_hub,
    drug_name,
    total_shipments,
    avg_transit_days,
    breach_rate_pct,
    otif_pct,
    DENSE_RANK() OVER (PARTITION BY origin_hub ORDER BY breach_rate_pct DESC) AS risk_rank
FROM HubDrugMetrics
ORDER BY origin_hub, risk_rank;
"""

kpi_df = pd.read_sql(analytical_query, con=conn)
conn.close()

kpi_df.to_csv("hub_kpi_summary.csv", index=False)
print("\n--- Top Cold-Chain Risk Summary ---")
print(kpi_df.head(8).to_string(index=False))

# 4. Generate Executive KPI Chart for GitHub README
hub_summary = kpi_df.groupby("origin_hub")[["breach_rate_pct", "otif_pct"]].mean().reset_index()

fig, ax = plt.subplots(figsize=(8, 4.5))
x = range(len(hub_summary))
ax.bar([i - 0.18 for i in x], hub_summary["otif_pct"], width=0.35, label="OTIF Delivery (%)", color="#2E7D32")
ax.bar([i + 0.18 for i in x], hub_summary["breach_rate_pct"], width=0.35, label="Cold-Chain Breach (%)", color="#C62828")

ax.set_xticks(x)
ax.set_xticklabels(hub_summary["origin_hub"])
ax.set_ylabel("Percentage (%)")
ax.set_title("Pharmaceutical Hub Performance: OTIF vs. Cold-Chain Breaches")
ax.legend()
plt.tight_layout()
plt.savefig("hub_kpi_chart.png", dpi=150)
print("\nSaved executive chart: hub_kpi_chart.png")
