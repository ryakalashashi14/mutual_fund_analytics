"""
Live NAV Fetch Module
=====================
Fetches live NAV data from mfapi.in for Indian mutual fund schemes
Saves data as CSV files in data/api/ folder
Part of Mutual Fund Analytics Day 1 Deliverable

Usage:
    python live_nav_fetch.py
    
    Or import:
    from live_nav_fetch import fetch_nav_for_scheme
    df = fetch_nav_for_scheme(125497, "HDFC Top 100 Direct")
"""

import pandas as pd
import requests
import json
import os
from datetime import datetime
from pathlib import Path


# Define schemes to fetch
SCHEMES = {
    'HDFC Top 100 Direct': 125497,
    'SBI Bluechip': 119551,
    'ICICI Bluechip': 120503,
    'Nippon Large Cap': 118632,
    'Axis Bluechip': 119092,
    'Kotak Bluechip': 120841,
}

API_BASE_URL = "https://api.mfapi.in/mf"
TIMEOUT = 10
OUTPUT_DIR = "data/api"


def fetch_nav_for_scheme(scheme_code, scheme_name):
    """
    Fetch NAV data for a single scheme from mfapi.in
    
    Args:
        scheme_code (int): AMFI scheme code
        scheme_name (str): Human-readable scheme name
        
    Returns:
        pd.DataFrame or None: NAV data with metadata or None on error
    """
    try:
        url = f"{API_BASE_URL}/{scheme_code}"
        print(f"  Fetching {scheme_name} (Code: {scheme_code})...")
        
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        meta = data.get("meta", {})
        nav_data = data.get("data", [])
        
        if not nav_data:
            print(f"    ⚠️  No data found for {scheme_name}")
            return None
        
        # Create DataFrame from NAV data
        df = pd.DataFrame(nav_data)
        
        # Add metadata columns
        df["scheme_code"] = scheme_code
        df["scheme_name"] = scheme_name
        df["fund_house"] = meta.get("fund_house", "")
        df["scheme_type"] = meta.get("scheme_type", "")
        df["scheme_category"] = meta.get("scheme_category", "")
        
        print(f"    ✓ Fetched {len(df):,} records")
        print(f"      Latest NAV: {df['nav'].iloc[0]} on {df['date'].iloc[0]}")
        
        return df
        
    except requests.exceptions.Timeout:
        print(f"    ✗ Timeout: {scheme_name}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"    ✗ Connection error: {scheme_name}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"    ✗ Error: {str(e)[:50]}")
        return None
    except Exception as e:
        print(f"    ✗ Unexpected error: {str(e)[:50]}")
        return None


def save_nav_data(df, scheme_name):
    """
    Save NAV data to CSV file
    
    Args:
        df (pd.DataFrame): NAV data
        scheme_name (str): Scheme name for filename
        
    Returns:
        str: Filepath where data was saved
    """
    if df is None:
        return None
    
    # Create output directory if it doesn't exist
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # Create filename from scheme name
    filename = scheme_name.lower().replace(' ', '_') + '_nav.csv'
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    df.to_csv(filepath, index=False)
    size_kb = os.path.getsize(filepath) / 1024
    print(f"    Saved to: {filepath} ({size_kb:.1f} KB)")
    
    return filepath


def fetch_all_schemes(schemes_dict=None):
    """
    Fetch NAV data for all schemes
    
    Args:
        schemes_dict (dict): Dictionary of scheme_name: scheme_code pairs
                            If None, uses default SCHEMES
        
    Returns:
        dict: Dictionary of scheme_name: dataframe pairs
    """
    if schemes_dict is None:
        schemes_dict = SCHEMES
    
    print("=" * 90)
    print("FETCHING LIVE NAV DATA FROM MFAPI.IN")
    print("=" * 90)
    print()
    
    results = {}
    success_count = 0
    
    for scheme_name, scheme_code in schemes_dict.items():
        df = fetch_nav_for_scheme(scheme_code, scheme_name)
        if df is not None:
            save_nav_data(df, scheme_name)
            results[scheme_name] = df
            success_count += 1
    
    print()
    print("=" * 90)
    print(f"SUMMARY: Successfully fetched {success_count}/{len(schemes_dict)} schemes")
    print("=" * 90)
    
    return results


def print_nav_summary(results):
    """
    Print summary statistics for fetched NAV data
    
    Args:
        results (dict): Dictionary of scheme_name: dataframe pairs
    """
    print()
    print("=" * 90)
    print("NAV DATA SUMMARY")
    print("=" * 90)
    print()
    
    total_records = 0
    
    for scheme_name, df in results.items():
        df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
        records = len(df)
        total_records += records
        
        print(f"Scheme: {scheme_name}")
        print(f"  Records: {records:,}")
        print(f"  Date Range: {df['date'].iloc[-1]} to {df['date'].iloc[0]}")
        print(f"  Latest NAV: {df['nav'].iloc[0]:.4f}")
        print(f"  Min NAV: {df['nav'].min():.4f} | Max NAV: {df['nav'].max():.4f}")
        print()
    
    print(f"Total Records: {total_records:,}")
    print("=" * 90)


if __name__ == "__main__":
    # Fetch all schemes
    results = fetch_all_schemes()
    
    # Print summary if any data fetched
    if results:
        print_nav_summary(results)
    else:
        print("\n⚠️  No NAV data could be fetched. Check internet connection.")
        import sys
        sys.exit(1)
