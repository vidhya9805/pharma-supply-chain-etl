import pandas as pd
import numpy as np

np.random.seed(42)
n_rows = 50000

drugs = ['Lantus', 'Toujeo', 'Dupixent', 'Clexane', 'VaxRabeo']
hubs = ['Hyderabad_GCC', 'Frankfurt_Hub', 'Lyon_Plant', 'Boston_Dist']
regions = ['APAC', 'EMEA', 'NA', 'LATAM']

df = pd.DataFrame({
    'shipment_id': [f'SHP-{100000 + i}' for i in range(n_rows)],
    'drug_name': np.random.choice(drugs, n_rows),
    'origin_hub': np.random.choice(hubs, n_rows),
    'destination_region': np.random.choice(regions, n_rows),
    'dispatch_date': pd.date_range('2026-01-01', periods=n_rows, freq='5min'),
    'transit_days': np.random.randint(1, 10, n_rows),
    'storage_temp_c': np.round(np.random.normal(5.0, 2.2, n_rows), 1),
    'units_shipped': np.random.randint(100, 5000, n_rows)
})

# Inject intentional anomalies for quality audit demonstration
df.loc[0:150, 'shipment_id'] = df.loc[151:301, 'shipment_id'].values  # Duplicates
df.loc[500:600, 'units_shipped'] = np.nan  # Missing values

# Automated Data Quality Audit
duplicates = df[df.duplicated(subset=['shipment_id'], keep='first')].copy()
duplicates['audit_issue'] = 'Duplicate Shipment ID'

nulls = df[df.isnull().any(axis=1)].copy()
nulls['audit_issue'] = 'Missing Critical Field'

# Clean dataset
df_clean = df.drop_duplicates(subset=['shipment_id']).dropna().copy()
df_clean['delivery_date'] = df_clean['dispatch_date'] + pd.to_timedelta(df_clean['transit_days'], unit='D')
df_clean['cold_chain_breach'] = np.where((df_clean['storage_temp_c'] < 2.0) | (df_clean['storage_temp_c'] > 8.0), 1, 0)

audit_log = pd.concat([duplicates, nulls])
df_clean.to_csv('clean_shipments.csv', index=False)
audit_log.to_csv('audit_error_log.csv', index=False)

print(f"Processed {n_rows} records | Clean: {len(df_clean)} | Flagged Anomalies: {len(audit_log)}")
print(f"Cold-Chain Breaches Detected: {df_clean['cold_chain_breach'].sum()}")
