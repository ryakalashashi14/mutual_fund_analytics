"""
Data Ingestion Module
=====================
Loads all 10 CSV datasets from data/raw/ folder
Handles empty files gracefully with error checking
Part of Mutual Fund Analytics Day 1 Deliverable

Usage:
    python data_ingestion.py
    
    Or import:
    from data_ingestion import load_all_datasets
    datasets = load_all_datasets()
"""

import pandas as pd
import os
import sys
from pathlib import Path

def load_dataset(filepath, name):
    """
    Load a single CSV dataset with error handling
    
    Args:
        filepath (str): Path to CSV file
        name (str): Human-readable dataset name
        
    Returns:
        pd.DataFrame or None: Loaded dataframe or None if error
    """
    try:
        if not os.path.exists(filepath):
            print(f"  ⚠️  {name}: File not found - {filepath}")
            return None
        
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            print(f"  ⚠️  {name}: File is empty (0 bytes)")
            return None
        
        df = pd.read_csv(filepath)
        print(f"  ✓ {name:<30} Shape: {df.shape} | Size: {file_size/1024:.1f} KB")
        return df
        
    except Exception as e:
        print(f"  ✗ {name}: Error - {str(e)[:50]}")
        return None


def load_all_datasets():
    """
    Load all 10 raw CSV datasets
    
    Returns:
        dict: Dictionary with dataset names as keys and dataframes as values
    """
    print("=" * 90)
    print("LOADING ALL 10 RAW DATASETS")
    print("=" * 90)
    print()
    
    datasets = {
        'amfi': ('data/raw/amfi.csv', 'AMFI Scheme Registry'),
        'benchmark': ('data/raw/benchmark.csv', 'Benchmark Indices'),
        'categories': ('data/raw/categories.csv', 'Scheme Categories'),
        'expense_ratio': ('data/raw/expense_ratio.csv', 'Expense Ratios'),
        'fund_master': ('data/raw/fund_master.csv', 'Fund Master Metadata'),
        'holdings': ('data/raw/holdings.csv', 'Portfolio Holdings'),
        'nav_history': ('data/raw/nav_history.csv', 'Historical NAV'),
        'returns': ('data/raw/returns.csv', 'Scheme Returns'),
        'risk': ('data/raw/risk.csv', 'Risk Metrics'),
        'sectors': ('data/raw/sectors.csv', 'Sector Allocation'),
    }
    
    loaded_data = {}
    loaded_count = 0
    
    for key, (filepath, name) in datasets.items():
        df = load_dataset(filepath, name)
        if df is not None:
            loaded_data[key] = df
            loaded_count += 1
    
    print()
    print("=" * 90)
    print(f"SUMMARY: {loaded_count}/10 datasets loaded successfully")
    print("=" * 90)
    
    return loaded_data


def print_dataset_info(datasets):
    """
    Print detailed information for each loaded dataset
    
    Args:
        datasets (dict): Dictionary of loaded dataframes
    """
    print()
    print("=" * 90)
    print("DATASET INFORMATION")
    print("=" * 90)
    
    for name, df in datasets.items():
        print(f"\n{'='*90}")
        print(f"Dataset: {name}")
        print(f"{'='*90}")
        print(f"Shape: {df.shape}")
        print(f"\nData Types:\n{df.dtypes}")
        print(f"\nFirst 5 Rows:\n{df.head()}")
        print(f"\nMissing Values:\n{df.isnull().sum()}")


if __name__ == "__main__":
    # Load all datasets
    datasets = load_all_datasets()
    
    # Print info if datasets loaded
    if datasets:
        print_dataset_info(datasets)
        print()
        print("=" * 90)
        print(f"Total Records Loaded: {sum(len(df) for df in datasets.values()):,}")
        print("=" * 90)
    else:
        print("\n⚠️  No datasets could be loaded. Check data/raw/ folder.")
        sys.exit(1)
