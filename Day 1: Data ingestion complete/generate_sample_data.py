import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 90)
print("GENERATING SAMPLE DATA FOR ALL 10 RAW CSV FILES")
print("=" * 90)

# Set seed for reproducibility
np.random.seed(42)

# ============================================================================
# 1. AMFI.csv - AMFI Scheme Registry
# ============================================================================
print("\n1. Creating amfi.csv (AMFI Scheme Registry)...")
amfi_data = {
    'scheme_code': [119551, 120503, 118632, 119092, 120841, 125497],
    'scheme_name': ['SBI Bluechip', 'ICICI Bluechip', 'Nippon Large Cap', 
                    'Axis Bluechip', 'Kotak Bluechip', 'HDFC Top 100 Direct'],
    'fund_house': ['Aditya Birla Sun Life', 'Axis', 'Nippon India', 
                   'HDFC', 'quant', 'SBI'],
    'registration_date': ['2013-01-02', '2013-01-02', '2013-01-02',
                          '2012-12-31', '2013-01-07', '2014-01-01']
}
amfi_df = pd.DataFrame(amfi_data)
amfi_df.to_csv('data/raw/amfi.csv', index=False)
print(f"   ✓ Created with {len(amfi_df)} records")

# ============================================================================
# 2. BENCHMARK.csv - Benchmark Indices
# ============================================================================
print("2. Creating benchmark.csv (Benchmark Indices)...")
benchmark_data = {
    'benchmark_code': ['NIFTY50', 'NIFTY100', 'NIFTYMID50', 'NIFTYIT', 'NIFTYBANK'],
    'benchmark_name': ['Nifty 50', 'Nifty 100', 'Nifty Midcap 50', 'Nifty IT', 'Nifty Bank'],
    'index_value': [24580.45, 27834.20, 18903.50, 42156.80, 51234.60],
    'date': ['2026-06-22', '2026-06-22', '2026-06-22', '2026-06-22', '2026-06-22']
}
benchmark_df = pd.DataFrame(benchmark_data)
benchmark_df.to_csv('data/raw/benchmark.csv', index=False)
print(f"   ✓ Created with {len(benchmark_df)} records")

# ============================================================================
# 3. CATEGORIES.csv - Scheme Categories
# ============================================================================
print("3. Creating categories.csv (Scheme Categories)...")
categories_data = {
    'category_code': ['EQ_LC', 'EQ_MC', 'EQ_SC', 'ELSS', 'DEBT_PPF', 'DEBT_MF'],
    'category_name': ['Equity - Large Cap', 'Equity - Mid Cap', 'Equity - Small Cap',
                      'ELSS', 'Debt - PPF', 'Debt - Money Market'],
    'risk_level': ['High', 'High', 'Very High', 'High', 'Very Low', 'Low'],
    'description': ['Large cap stocks', 'Mid cap stocks', 'Small cap stocks',
                    'Tax saving', 'Fixed income PPF', 'Liquid funds']
}
categories_df = pd.DataFrame(categories_data)
categories_df.to_csv('data/raw/categories.csv', index=False)
print(f"   ✓ Created with {len(categories_df)} records")

# ============================================================================
# 4. EXPENSE_RATIO.csv - Fund Expense Ratios
# ============================================================================
print("4. Creating expense_ratio.csv (Expense Ratios)...")
expense_data = {
    'scheme_code': [119551, 120503, 118632, 119092, 120841, 125497],
    'scheme_name': ['SBI Bluechip', 'ICICI Bluechip', 'Nippon Large Cap',
                    'Axis Bluechip', 'Kotak Bluechip', 'HDFC Top 100 Direct'],
    'expense_ratio': [0.52, 0.49, 0.55, 0.48, 0.51, 0.45],
    'fund_house': ['Aditya Birla Sun Life', 'Axis', 'Nippon India',
                   'HDFC', 'quant', 'SBI']
}
expense_df = pd.DataFrame(expense_data)
expense_df.to_csv('data/raw/expense_ratio.csv', index=False)
print(f"   ✓ Created with {len(expense_df)} records")

# ============================================================================
# 5. FUND_MASTER.csv - Scheme Metadata
# ============================================================================
print("5. Creating fund_master.csv (Fund Master Metadata)...")
fund_master_data = {
    'scheme_code': [119551, 120503, 118632, 119092, 120841, 125497],
    'scheme_name': ['SBI Bluechip', 'ICICI Bluechip', 'Nippon Large Cap',
                    'Axis Bluechip', 'Kotak Bluechip', 'HDFC Top 100 Direct'],
    'fund_house': ['Aditya Birla Sun Life', 'Axis', 'Nippon India',
                   'HDFC', 'quant', 'SBI'],
    'category': ['Debt - Banking', 'Equity - ELSS', 'Equity - Large Cap',
                 'Debt - Money Market', 'Equity - Mid Cap', 'Equity - Small Cap'],
    'subcategory': ['Banking PSU', 'ELSS', 'Large Cap', 'Liquid', 'Mid Cap', 'Small Cap'],
    'risk_grade': ['Low', 'Medium', 'Medium', 'Very Low', 'High', 'Very High'],
    'fund_size_cr': [5234.56, 8945.23, 12456.78, 3456.89, 6789.45, 15234.67]
}
fund_master_df = pd.DataFrame(fund_master_data)
fund_master_df.to_csv('data/raw/fund_master.csv', index=False)
print(f"   ✓ Created with {len(fund_master_df)} records")

# ============================================================================
# 6. HOLDINGS.csv - Portfolio Holdings
# ============================================================================
print("6. Creating holdings.csv (Portfolio Holdings)...")
holdings_data = {
    'scheme_code': [119551] * 5 + [120503] * 5,
    'company_name': ['HDFC Bank', 'Infosy', 'TCS', 'Reliance', 'ICICI Bank',
                     'Wipro', 'Axis Bank', 'SBI', 'Bajaj Finance', 'HDFC'],
    'sector': ['Banking', 'IT', 'IT', 'Energy', 'Banking',
               'IT', 'Banking', 'Banking', 'Finance', 'Banking'],
    'percentage': [4.5, 3.2, 3.8, 3.1, 2.9, 5.2, 4.1, 3.9, 3.5, 3.3]
}
holdings_df = pd.DataFrame(holdings_data)
holdings_df.to_csv('data/raw/holdings.csv', index=False)
print(f"   ✓ Created with {len(holdings_df)} records")

# ============================================================================
# 7. NAV_HISTORY.csv - Historical NAV Records
# ============================================================================
print("7. Creating nav_history.csv (Historical NAV)...")
nav_history_list = []
base_date = datetime(2025, 12, 31)
for scheme_code in [119551, 120503, 118632, 119092, 120841, 125497]:
    base_nav = np.random.uniform(50, 250)
    for i in range(250):
        date = base_date - timedelta(days=i)
        # Add random walk to NAV
        nav = base_nav + np.random.normal(0, 2)
        base_nav = nav
        nav_history_list.append({
            'scheme_code': scheme_code,
            'date': date.strftime('%d-%m-%Y'),
            'nav': round(nav, 4)
        })
nav_history_df = pd.DataFrame(nav_history_list)
nav_history_df.to_csv('data/raw/nav_history.csv', index=False)
print(f"   ✓ Created with {len(nav_history_df)} records")

# ============================================================================
# 8. RETURNS.csv - Scheme Returns Data
# ============================================================================
print("8. Creating returns.csv (Scheme Returns)...")
returns_data = {
    'scheme_code': [119551, 120503, 118632, 119092, 120841, 125497],
    'scheme_name': ['SBI Bluechip', 'ICICI Bluechip', 'Nippon Large Cap',
                    'Axis Bluechip', 'Kotak Bluechip', 'HDFC Top 100 Direct'],
    'return_1m': [0.45, 0.52, 0.38, 0.12, 0.67, 0.55],
    'return_3m': [1.23, 1.45, 1.15, 0.85, 1.62, 1.38],
    'return_1y': [-1.93, 1.23, 0.74, -0.45, 2.65, 5.16],
    'return_3y': [8.45, 9.23, 7.85, 6.34, 10.12, 11.45],
    'return_5y': [12.34, 13.56, 11.78, 10.23, 14.67, 15.89]
}
returns_df = pd.DataFrame(returns_data)
returns_df.to_csv('data/raw/returns.csv', index=False)
print(f"   ✓ Created with {len(returns_df)} records")

# ============================================================================
# 9. RISK.csv - Risk Metrics
# ============================================================================
print("9. Creating risk.csv (Risk Metrics)...")
risk_data = {
    'scheme_code': [119551, 120503, 118632, 119092, 120841, 125497],
    'scheme_name': ['SBI Bluechip', 'ICICI Bluechip', 'Nippon Large Cap',
                    'Axis Bluechip', 'Kotak Bluechip', 'HDFC Top 100 Direct'],
    'volatility': [8.5, 12.3, 11.8, 3.2, 14.5, 15.2],
    'beta': [0.85, 1.15, 1.10, 0.45, 1.25, 1.35],
    'sharpe_ratio': [0.95, 1.12, 0.98, 0.75, 1.22, 1.35],
    'std_dev': [2.34, 3.56, 3.12, 1.05, 4.12, 4.56]
}
risk_df = pd.DataFrame(risk_data)
risk_df.to_csv('data/raw/risk.csv', index=False)
print(f"   ✓ Created with {len(risk_df)} records")

# ============================================================================
# 10. SECTORS.csv - Sector Allocation
# ============================================================================
print("10. Creating sectors.csv (Sector Allocation)...")
sectors_data = {
    'scheme_code': [119551] * 6 + [120503] * 6,
    'sector_name': ['Banking', 'IT', 'Energy', 'Finance', 'Pharma', 'Others'] * 2,
    'allocation_percentage': [25.3, 18.5, 15.2, 12.8, 10.5, 17.7,
                              22.1, 20.3, 14.5, 13.2, 11.8, 18.1]
}
sectors_df = pd.DataFrame(sectors_data)
sectors_df.to_csv('data/raw/sectors.csv', index=False)
print(f"   ✓ Created with {len(sectors_df)} records")

print("\n" + "=" * 90)
print("SUCCESS! All 10 CSV files created in data/raw/")
print("=" * 90)

summary = {
    'File': ['amfi.csv', 'benchmark.csv', 'categories.csv', 'expense_ratio.csv',
             'fund_master.csv', 'holdings.csv', 'nav_history.csv', 'returns.csv',
             'risk.csv', 'sectors.csv'],
    'Records': [len(amfi_df), len(benchmark_df), len(categories_df), len(expense_df),
                len(fund_master_df), len(holdings_df), len(nav_history_df), len(returns_df),
                len(risk_df), len(sectors_df)],
    'Status': ['✓ Created'] * 10
}

summary_df = pd.DataFrame(summary)
print("\n" + summary_df.to_string(index=False))

print("\n" + "=" * 90)
print("NEXT STEPS:")
print("=" * 90)
print("""
1. Run: python load_data.py
   → This will load all 10 raw datasets + fetch live NAV data

2. Run: python explore_fund_master.py
   → This will analyze fund master metadata

3. Run: python verify_data.py
   → This will verify all data integrity

Now all 10 raw files have sample data and you can test the full pipeline!
""")
