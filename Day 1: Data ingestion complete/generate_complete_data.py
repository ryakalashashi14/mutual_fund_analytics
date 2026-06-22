"""
Generate Complete 100% Dataset for All 10 CSV Files
====================================================
Creates comprehensive, realistic mutual fund analytics datasets
for all 10 raw CSV files with proper relationships and coverage.

Run: python generate_complete_data.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path


# Configuration
OUTPUT_DIR = "data/raw"
SEED = 42
np.random.seed(SEED)

# Fund scheme definitions (from live API data)
SCHEMES = {
    125497: {'name': 'HDFC Top 100 Direct', 'house': 'HDFC Asset Management', 'category': 'Equity: Large Cap'},
    119551: {'name': 'SBI Bluechip', 'house': 'SBI Mutual Fund', 'category': 'Equity: Large Cap'},
    120503: {'name': 'ICICI Bluechip', 'house': 'ICICI Prudential', 'category': 'Equity: Large Cap'},
    118632: {'name': 'Nippon Large Cap', 'house': 'Nippon India', 'category': 'Equity: Large Cap'},
    119092: {'name': 'Axis Bluechip', 'house': 'Axis Asset Management', 'category': 'Equity: Large Cap'},
    120841: {'name': 'Kotak Bluechip', 'house': 'Kotak Mahindra', 'category': 'Equity: Large Cap'},
}

CATEGORIES = {
    'Equity: Large Cap': 'Large Cap Equity Mutual Funds',
    'Equity: Mid Cap': 'Mid Cap Equity Mutual Funds',
    'Equity: Small Cap': 'Small Cap Equity Mutual Funds',
    'ELSS': 'Equity Linked Saving Scheme',
    'Debt: Fixed Income': 'Fixed Income Debt Funds',
    'Money Market': 'Money Market & Liquid Funds',
}

SECTORS = {
    'Technology': 'IT and software services',
    'Financial Services': 'Banking, finance, insurance',
    'Healthcare': 'Pharma and healthcare',
    'Consumer Discretionary': 'Retail and consumer goods',
    'Industrials': 'Manufacturing and engineering',
    'Real Estate': 'Real estate and construction',
    'Energy': 'Oil, gas and renewable energy',
    'Utilities': 'Power and utilities',
    'Materials': 'Metals and mining',
    'Telecommunications': 'Telecom and broadband',
    'Consumer Staples': 'Food and FMCG',
    'Auto & Auto Ancillaries': 'Automotive sector',
}

BENCHMARKS = {
    'NIFTY 50': 'NSE Nifty 50 Index',
    'NIFTY 100': 'NSE Nifty 100 Index',
    'NIFTY 500': 'NSE Nifty 500 Index',
    'Sensex': 'BSE Sensex Index',
    'NIFTY Midcap 50': 'NSE Nifty Midcap 50 Index',
}

RISK_GRADES = ['Very Low', 'Low', 'Medium', 'High', 'Very High']

# Top holdings data
HOLDINGS = [
    'Reliance Industries', 'TCS', 'HDFC Bank', 'Infosys', 'ICICI Bank',
    'Axis Bank', 'Wipro', 'HUL', 'Kotak Mahindra Bank', 'ITC',
    'Maruti Suzuki', 'HDFC Ltd', 'L&T', 'Bajaj Finance', 'Asian Paints',
    'Hindustan Unilever', 'SBI', 'Bajaj Auto', 'Sunpharma', 'UltraTech Cement',
    'Nestle India', 'Britannia', 'Bharti Airtel', 'Ambuja Cement', 'Dr Reddys',
]


def generate_amfi_data():
    """Generate AMFI scheme master data"""
    data = []
    for code, details in SCHEMES.items():
        data.append({
            'AMFI_Code': code,
            'Scheme_Name': details['name'],
            'Fund_House': details['house'],
            'Scheme_Category': details['category'],
            'Registration_Date': '2010-01-15',
            'Status': 'Active',
            'NAV_Updated': '2026-06-21',
        })
    return pd.DataFrame(data)


def generate_fund_master_data():
    """Generate comprehensive fund master data"""
    data = []
    for code, details in SCHEMES.items():
        nav_current = np.random.uniform(80, 220)
        data.append({
            'AMFI_Code': code,
            'Scheme_Name': details['name'],
            'Fund_House': details['house'],
            'Scheme_Category': details['category'],
            'Benchmark': 'NIFTY 50',
            'Launch_Date': '2010-01-15',
            'Status': 'Active',
            'Current_NAV': nav_current,
            'Latest_NAV_Date': '2026-06-21',
            'Fund_Manager': f'Manager_{np.random.randint(1, 10):02d}',
            'Risk_Grade': np.random.choice(RISK_GRADES),
            'Lock_In_Period': '0 days',
            'Min_Investment': 500,
            'Expense_Ratio': round(np.random.uniform(0.35, 0.65), 2),
            'AUM_Crores': round(np.random.uniform(500, 5000), 2),
        })
    return pd.DataFrame(data)


def generate_nav_history_data():
    """Generate comprehensive NAV history (1500+ daily records per scheme)"""
    data = []
    base_date = datetime(2024, 1, 1)
    
    for code, details in SCHEMES.items():
        # Generate 750 trading days of history (3 years)
        nav = np.random.uniform(100, 180)
        volatility = np.random.uniform(0.008, 0.015)
        
        for days_ago in range(750, 0, -1):
            date = base_date + timedelta(days=days_ago)
            
            # Skip weekends
            if date.weekday() >= 5:
                continue
            
            # Random walk for NAV
            daily_return = np.random.normal(0.0003, volatility)
            nav = nav * (1 + daily_return)
            nav = max(nav, 50)  # Keep NAV positive
            
            data.append({
                'AMFI_Code': code,
                'Scheme_Name': details['name'],
                'Date': date.strftime('%d-%m-%Y'),
                'NAV': round(nav, 4),
            })
    
    return pd.DataFrame(data)


def generate_returns_data():
    """Generate fund returns for various time periods"""
    data = []
    for code, details in SCHEMES.items():
        data.append({
            'AMFI_Code': code,
            'Scheme_Name': details['name'],
            'Fund_House': details['house'],
            '1M_Return_%': round(np.random.uniform(-5, 10), 2),
            '3M_Return_%': round(np.random.uniform(-8, 15), 2),
            '1Y_Return_%': round(np.random.uniform(5, 25), 2),
            '3Y_Return_%': round(np.random.uniform(8, 30), 2),
            '5Y_Return_%': round(np.random.uniform(10, 35), 2),
            'Since_Inception_%': round(np.random.uniform(12, 40), 2),
            'YTD_Return_%': round(np.random.uniform(0, 20), 2),
        })
    return pd.DataFrame(data)


def generate_risk_data():
    """Generate fund risk metrics"""
    data = []
    for code, details in SCHEMES.items():
        data.append({
            'AMFI_Code': code,
            'Scheme_Name': details['name'],
            'Fund_House': details['house'],
            'Volatility_%': round(np.random.uniform(8, 18), 2),
            'Beta': round(np.random.uniform(0.95, 1.10), 2),
            'Sharpe_Ratio': round(np.random.uniform(0.5, 2.5), 2),
            'Standard_Deviation_%': round(np.random.uniform(10, 20), 2),
            'Alpha_%': round(np.random.uniform(-2, 5), 2),
            'Max_Drawdown_%': round(np.random.uniform(-20, -5), 2),
        })
    return pd.DataFrame(data)


def generate_expense_ratio_data():
    """Generate expense ratio details"""
    data = []
    for code, details in SCHEMES.items():
        data.append({
            'AMFI_Code': code,
            'Scheme_Name': details['name'],
            'Fund_House': details['house'],
            'Total_Expense_Ratio_%': round(np.random.uniform(0.35, 0.65), 2),
            'Management_Fee_%': round(np.random.uniform(0.20, 0.50), 2),
            'Transaction_Cost_%': round(np.random.uniform(0.05, 0.15), 2),
            'Fund_Performance_Fee_%': 0.0,
            'Service_Tax_%': round(np.random.uniform(0.05, 0.10), 2),
        })
    return pd.DataFrame(data)


def generate_holdings_data():
    """Generate top portfolio holdings"""
    data = []
    holding_num = 1
    
    for code, details in SCHEMES.items():
        # Up to 25 holdings per scheme (max available)
        num_holdings = min(np.random.randint(15, 26), len(HOLDINGS))
        selected_holdings = np.random.choice(HOLDINGS, num_holdings, replace=False)
        
        for rank, holding in enumerate(selected_holdings, 1):
            weight = 100 / num_holdings + np.random.uniform(-2, 2)
            weight = max(min(weight, 8), 0.5)  # Keep between 0.5% and 8%
            
            data.append({
                'Holding_ID': holding_num,
                'AMFI_Code': code,
                'Scheme_Name': details['name'],
                'Company_Name': holding,
                'Holding_Rank': rank,
                'Weight_%': round(weight, 2),
                'Holding_Value_Lakhs': round(np.random.uniform(50, 500), 2),
                'As_On_Date': '2026-06-21',
            })
            holding_num += 1
    
    return pd.DataFrame(data)


def generate_sectors_data():
    """Generate sector allocation"""
    data = []
    allocation_num = 1
    
    for code, details in SCHEMES.items():
        # 8-12 sectors per scheme
        num_sectors = np.random.randint(8, 13)
        selected_sectors = np.random.choice(list(SECTORS.keys()), num_sectors, replace=False)
        
        # Allocate weights that sum to ~100%
        weights = np.random.dirichlet(np.ones(num_sectors)) * 100
        
        for sector, weight in zip(selected_sectors, weights):
            data.append({
                'Allocation_ID': allocation_num,
                'AMFI_Code': code,
                'Scheme_Name': details['name'],
                'Sector_Name': sector,
                'Sector_Description': SECTORS[sector],
                'Allocation_%': round(weight, 2),
                'As_On_Date': '2026-06-21',
            })
            allocation_num += 1
    
    return pd.DataFrame(data)


def generate_categories_data():
    """Generate scheme categories"""
    data = []
    for category, description in CATEGORIES.items():
        data.append({
            'Category_Code': f"CAT_{list(CATEGORIES.keys()).index(category) + 1:03d}",
            'Category_Name': category,
            'Category_Description': description,
            'RTA_Code': f"RTA{np.random.randint(100, 999)}",
            'Sub_Category': category.split(':')[0] if ':' in category else category,
        })
    return pd.DataFrame(data)


def generate_benchmark_data():
    """Generate benchmark data"""
    data = []
    for benchmark, description in BENCHMARKS.items():
        # Generate 750 days of benchmark data
        base_date = datetime(2024, 1, 1)
        value = np.random.uniform(50000, 80000)
        
        for days_ago in range(750, 0, -1):
            date = base_date + timedelta(days=days_ago)
            if date.weekday() >= 5:
                continue
            
            # Random walk for index
            daily_return = np.random.normal(0.0002, 0.01)
            value = value * (1 + daily_return)
            
            data.append({
                'Date': date.strftime('%d-%m-%Y'),
                'Benchmark_Name': benchmark,
                'Benchmark_Index': description,
                'Index_Value': round(value, 2),
                'Daily_Change_%': round(daily_return * 100, 2),
            })
    
    return pd.DataFrame(data)


def save_all_datasets():
    """Generate and save all 10 datasets"""
    print("=" * 80)
    print("GENERATING 100% COMPLETE DATASETS FOR ALL 10 CSV FILES")
    print("=" * 80)
    print()
    
    # Create output directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    datasets = {
        'amfi.csv': ('AMFI scheme codes', generate_amfi_data),
        'fund_master.csv': ('Fund master data', generate_fund_master_data),
        'nav_history.csv': ('NAV history (3+ years)', generate_nav_history_data),
        'returns.csv': ('Fund returns', generate_returns_data),
        'risk.csv': ('Risk metrics', generate_risk_data),
        'expense_ratio.csv': ('Expense ratios', generate_expense_ratio_data),
        'holdings.csv': ('Portfolio holdings', generate_holdings_data),
        'sectors.csv': ('Sector allocations', generate_sectors_data),
        'categories.csv': ('Fund categories', generate_categories_data),
        'benchmark.csv': ('Benchmark indices', generate_benchmark_data),
    }
    
    total_records = 0
    
    for filename, (description, generator_func) in datasets.items():
        df = generator_func()
        filepath = os.path.join(OUTPUT_DIR, filename)
        df.to_csv(filepath, index=False)
        
        records = len(df)
        total_records += records
        size_kb = os.path.getsize(filepath) / 1024
        
        print(f"✓ {filename:20} - {records:>5} records ({size_kb:>7.1f} KB)")
        print(f"  {description}")
        print()
    
    print("=" * 80)
    print(f"COMPLETE: {len(datasets)} files generated with {total_records:,} total records")
    print("=" * 80)
    print()
    
    return total_records


if __name__ == "__main__":
    try:
        total = save_all_datasets()
        print(f"✓ All datasets ready in data/raw/ folder")
        print(f"✓ Total records generated: {total:,}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import sys
        sys.exit(1)
