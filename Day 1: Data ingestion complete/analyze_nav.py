import pandas as pd
import os

print("=" * 90)
print("SUMMARY: LIVE NAV DATA FETCHED FROM MFAPI.IN")
print("=" * 90)

schemes = [
    "hdfc_top_100_direct_nav.csv",
    "sbi_bluechip_nav.csv",
    "icici_bluechip_nav.csv",
    "nippon_large_cap_nav.csv",
    "axis_bluechip_nav.csv",
    "kotak_bluechip_nav.csv"
]

for scheme_file in schemes:
    filepath = f"data/api/{scheme_file}"
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        
        print(f"\n{'='*90}")
        print(f"Scheme: {df['scheme_name'].iloc[0]} (Code: {df['scheme_code'].iloc[0]})")
        print(f"Fund House: {df['fund_house'].iloc[0]}")
        print(f"{'='*90}")
        
        # Convert nav to numeric
        df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
        
        print(f"Total Records: {len(df):,}")
        print(f"Date Range: {df['date'].iloc[-1]} to {df['date'].iloc[0]}")
        print(f"\nNAV Statistics:")
        print(f"  Latest NAV: {df['nav'].iloc[0]:.4f}")
        print(f"  Min NAV: {df['nav'].min():.4f}")
        print(f"  Max NAV: {df['nav'].max():.4f}")
        print(f"  Avg NAV: {df['nav'].mean():.4f}")
        print(f"  Std Dev: {df['nav'].std():.4f}")
        
        # Calculate returns
        latest_nav = df['nav'].iloc[0]
        nav_1year_ago = df[df['nav'].notna()].iloc[min(250, len(df)-1)]['nav']  # Approx 1 year ago
        if pd.notna(nav_1year_ago):
            return_1yr = ((latest_nav - nav_1year_ago) / nav_1year_ago) * 100
            print(f"  Approx 1-Yr Return: {return_1yr:.2f}%")
        
        print(f"\nFile: {filepath} ({os.path.getsize(filepath)/1024:.1f} KB)")
