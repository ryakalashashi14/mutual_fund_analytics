import pandas as pd
import requests
import json
from datetime import datetime
import os

print("=" * 80)
print("LOADING 10 RAW DATASETS")
print("=" * 80)

# List of datasets to load
dataset_files = {
    "amfi": "data/raw/amfi.csv",
    "benchmark": "data/raw/benchmark.csv",
    "categories": "data/raw/categories.csv",
    "expense_ratio": "data/raw/expense_ratio.csv",
    "fund_master": "data/raw/fund_master.csv",
    "holdings": "data/raw/holdings.csv",
    "nav_history": "data/raw/nav_history.csv",
    "returns": "data/raw/returns.csv",
    "risk": "data/raw/risk.csv",
    "sectors": "data/raw/sectors.csv",
}

datasets = {}

# Load and analyze each dataset
for name, filepath in dataset_files.items():
    print(f"\n{'='*80}")
    print(f"Dataset: {name}")
    print(f"{'='*80}")
    
    if os.path.exists(filepath):
        file_size = os.path.getsize(filepath)
        print(f"File: {filepath}")
        print(f"File Size: {file_size} bytes")
        
        if file_size == 0:
            print("⚠️  File is empty - skipping")
            continue
        
        try:
            df = pd.read_csv(filepath)
            datasets[name] = df
            
            print(f"Shape: {df.shape}")
            print(f"\nData Types:\n{df.dtypes}")
            print(f"\nFirst 5 Rows:\n{df.head()}")
            print(f"\nMissing Values:\n{df.isnull().sum()}")
            print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        except Exception as e:
            print(f"✗ Error loading {name}: {str(e)}")
    else:
        print(f"⚠️  File not found: {filepath}")

# Assign to variables for backward compatibility
amfi = datasets.get("amfi")
benchmark = datasets.get("benchmark")
categories = datasets.get("categories")
expense_ratio = datasets.get("expense_ratio")
fund_master = datasets.get("fund_master")
holdings = datasets.get("holdings")
nav_history = datasets.get("nav_history")
returns = datasets.get("returns")
risk = datasets.get("risk")
sectors = datasets.get("sectors")

print("\n\n" + "=" * 80)
print("FETCHING LIVE NAV DATA FROM MFAPI.IN")
print("=" * 80)

# Define schemes to fetch
schemes = {
    "HDFC Top 100 Direct": 125497,
    "SBI Bluechip": 119551,
    "ICICI Bluechip": 120503,
    "Nippon Large Cap": 118632,
    "Axis Bluechip": 119092,
    "Kotak Bluechip": 120841,
}

def fetch_nav_from_mfapi(scheme_code, scheme_name):
    """
    Fetch NAV data from mfapi.in for a given scheme code
    """
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        print(f"\nFetching {scheme_name} (Code: {scheme_code})...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse meta and nav data
        meta = data.get("meta", {})
        nav_data = data.get("data", [])
        
        # Create DataFrame from nav data
        if nav_data:
            df = pd.DataFrame(nav_data)
            
            # Add meta information
            df["scheme_code"] = scheme_code
            df["scheme_name"] = scheme_name
            df["fund_house"] = meta.get("fund_house", "")
            df["scheme_type"] = meta.get("scheme_type", "")
            df["scheme_category"] = meta.get("scheme_category", "")
            
            # Save to CSV in data/api/
            filename = f"data/api/{scheme_name.lower().replace(' ', '_')}_nav.csv"
            df.to_csv(filename, index=False)
            
            print(f"✓ Fetched {len(df)} records")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Latest NAV: {df.iloc[0]['nav']} on {df.iloc[0]['date']}")
            print(f"  Saved to: {filename}")
            
            return df
        else:
            print(f"✗ No data found for {scheme_name}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching {scheme_name}: {str(e)}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return None

# Fetch NAV data for all schemes
nav_results = {}
for scheme_name, scheme_code in schemes.items():
    nav_results[scheme_name] = fetch_nav_from_mfapi(scheme_code, scheme_name)

print("\n\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Raw datasets with data: {len([df for df in datasets.values() if df is not None])}/10")
print(f"Empty raw datasets: {len(dataset_files) - len([df for df in datasets.values() if df is not None])}/10")
print(f"Successfully fetched NAV: {len([df for df in nav_results.values() if df is not None])}/6")