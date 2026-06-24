PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS dim_fund;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    asset_class TEXT NOT NULL,
    scheme_category TEXT NOT NULL,
    plan TEXT NOT NULL,
    launch_date TEXT NOT NULL,
    benchmark TEXT NOT NULL,
    expense_ratio_pct REAL NOT NULL,
    exit_load_pct REAL NOT NULL,
    min_sip_amount INTEGER NOT NULL,
    min_lumpsum_amount INTEGER NOT NULL,
    fund_manager TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    sebi_category_code TEXT NOT NULL
);

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    calendar_date TEXT NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    week_of_year INTEGER NOT NULL,
    is_weekend INTEGER NOT NULL,
    is_month_start INTEGER NOT NULL,
    is_month_end INTEGER NOT NULL,
    is_quarter_start INTEGER NOT NULL,
    is_quarter_end INTEGER NOT NULL
);

CREATE TABLE fact_nav (
    amfi_code INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    nav_date TEXT NOT NULL,
    nav REAL NOT NULL,
    is_imputed INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (amfi_code, date_key),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    date_key INTEGER NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    amount_inr REAL NOT NULL,
    state TEXT NOT NULL,
    city TEXT NOT NULL,
    city_tier TEXT NOT NULL,
    age_group TEXT NOT NULL,
    gender TEXT NOT NULL,
    annual_income_lakh REAL NOT NULL,
    payment_mode TEXT NOT NULL,
    kyc_status TEXT NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE TABLE fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    scheme_category TEXT NOT NULL,
    plan TEXT NOT NULL,
    return_1yr_pct REAL NOT NULL,
    return_3yr_pct REAL NOT NULL,
    return_5yr_pct REAL NOT NULL,
    benchmark_3yr_pct REAL NOT NULL,
    alpha REAL NOT NULL,
    beta REAL NOT NULL,
    sharpe_ratio REAL NOT NULL,
    sortino_ratio REAL NOT NULL,
    std_dev_ann_pct REAL NOT NULL,
    max_drawdown_pct REAL NOT NULL,
    aum_crore REAL NOT NULL,
    expense_ratio_pct REAL NOT NULL,
    morningstar_rating INTEGER NOT NULL,
    risk_grade TEXT NOT NULL,
    expense_ratio_in_range INTEGER NOT NULL,
    anomaly_flag INTEGER NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date TEXT NOT NULL,
    date_key INTEGER NOT NULL,
    fund_house TEXT NOT NULL,
    aum_lakh_crore REAL NOT NULL,
    aum_crore REAL NOT NULL,
    num_schemes INTEGER NOT NULL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);
