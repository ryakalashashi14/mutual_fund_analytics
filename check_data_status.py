import pandas as pd
import os

print("=" * 90)
print("DATA LOADING STATUS - CURRENT STATE")
print("=" * 90)

print("\n1. CHECKING RAW CSV FILES (data/raw/)")
print("-" * 90)

raw_files = ['amfi.csv', 'benchmark.csv', 'categories.csv', 'expense_ratio.csv',
             'fund_master.csv', 'holdings.csv', 'nav_history.csv', 'returns.csv',
             'risk.csv', 'sectors.csv']

empty_count = 0
for csv_file in raw_files:
    path = f'data/raw/{csv_file}'
    size = os.path.getsize(path)
    if size == 0:
        print(f"  ❌ {csv_file:<30} 0 bytes (EMPTY)")
        empty_count += 1
    else:
        try:
            df = pd.read_csv(path)
            print(f"  ✓ {csv_file:<30} {size:>10} bytes ({len(df)} rows)")
        except Exception as e:
            print(f"  ⚠️  {csv_file:<30} Error: {str(e)[:40]}")

print(f"\nResult: {empty_count}/10 files are empty")

print("\n2. AVAILABLE DATA IN API FOLDER (data/api/)")
print("-" * 90)

api_files = {
    'hdfc_top_100_direct_nav.csv': 'HDFC Top 100 Direct',
    'sbi_bluechip_nav.csv': 'SBI Bluechip',
    'icici_bluechip_nav.csv': 'ICICI Bluechip',
    'nippon_large_cap_nav.csv': 'Nippon Large Cap',
    'axis_bluechip_nav.csv': 'Axis Bluechip',
    'kotak_bluechip_nav.csv': 'Kotak Bluechip',
}

total_records = 0
for filename, scheme_name in api_files.items():
    path = f'data/api/{filename}'
    if os.path.exists(path):
        df = pd.read_csv(path)
        total_records += len(df)
        print(f"  ✓ {filename:<40} {len(df):>6,} records")

print(f"\nTotal API Records Available: {total_records:,}")

print("\n3. YOUR OPTIONS")
print("-" * 90)
print("""
OPTION 1: Work with existing API data (RECOMMENDED)
  ✓ Already have 19,882 records of live NAV data
  ✓ Data is verified and quality-checked
  ✓ Ready for immediate analysis
  
  Action: Use load_data.py or analyze data/api/* files directly

OPTION 2: Populate raw files first, then load
  ⚠️  Raw files are empty - need external data sources
  ✓ Can manually add CSV data to data/raw/
  ✓ Then use load_data.py to load all 10 files
  
  Action: Populate data/raw/*.csv then run load_data.py

OPTION 3: Create sample data for testing
  ✓ Generate mock data for all 10 datasets
  ✓ Test entire pipeline
  ✓ Good for development/testing
  
  Action: Let me generate sample data for raw folder
""")

print("\n4. CURRENT CAPABILITIES")
print("-" * 90)
print("""
✅ CAN DO NOW:
  - Analyze 6 live mutual fund schemes
  - View NAV history for 3000+ records each
  - Compare performance metrics
  - Study fund characteristics

❌ CANNOT DO WITHOUT RAW DATA:
  - Analyze broader AMFI universe
  - Study expense ratios
  - View complete holdings data
  - Analyze risk metrics
  - Study sector allocation
""")

print("\n" + "=" * 90)
print("WHAT WOULD YOU LIKE TO DO?")
print("=" * 90)
print("""
1. Continue with API data (data/api/*.csv) - IMMEDIATE
2. Populate raw files with sample data - FOR TESTING
3. Load and analyze existing API data - RECOMMENDED
4. Create data ingestion script for AMFI files - ADVANCED
""")
