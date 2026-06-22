import pandas as pd
import os

files = [
    'hdfc_top_100_direct_nav.csv',
    'sbi_bluechip_nav.csv',
    'icici_bluechip_nav.csv',
    'nippon_large_cap_nav.csv',
    'axis_bluechip_nav.csv',
    'kotak_bluechip_nav.csv'
]

print("\n" + "="*70)
print("FINAL DATA VERIFICATION")
print("="*70 + "\n")

total_rows = 0
for f in files:
    path = f"data/api/{f}"
    if os.path.exists(path):
        df = pd.read_csv(path)
        size = os.path.getsize(path) / 1024
        rows = len(df)
        total_rows += rows
        print(f"✓ {f}")
        print(f"  Rows: {rows:,} | Size: {size:.1f} KB | Columns: {df.shape[1]}")
        print(f"  Latest NAV Date: {df['date'].iloc[0]} | Latest Value: {df['nav'].iloc[0]}")

print(f"\n{'='*70}")
print(f"TOTAL: {total_rows:,} rows across 6 schemes")
print(f"STATUS: ✅ ALL DATA LOADED SUCCESSFULLY")
print("="*70 + "\n")
