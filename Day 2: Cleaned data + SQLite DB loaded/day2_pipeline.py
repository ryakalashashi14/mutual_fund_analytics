from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DB_PATH = ROOT / "bluestock_mf.db"
SCHEMA_PATH = ROOT / "schema.sql"
QUERIES_PATH = ROOT / "queries.sql"
DATA_DICT_PATH = ROOT / "data_dictionary.md"


def ensure_dirs() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip()


def parse_date(series: pd.Series, dayfirst: bool = True) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", dayfirst=dayfirst)


def parse_month(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series.astype("string").str.strip() + "-01", errors="coerce")


def to_date_key(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.strftime("%Y%m%d").astype("int64")


def save_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, date_format="%Y-%m-%d")


def read_source_csv(path: Path, *, engine: str | None = None) -> pd.DataFrame:
    kwargs = {"engine": engine} if engine else {}
    return pd.read_csv(path, **kwargs)


def clean_fund_master() -> pd.DataFrame:
    raw = read_source_csv(RAW_DIR / "01_fund_master.csv")
    raw.columns = [c.strip() for c in raw.columns]

    df = raw.copy()
    df = df.rename(
        columns={
            "category": "asset_class",
            "sub_category": "scheme_category",
        }
    )
    df["fund_house"] = clean_text(df["fund_house"])
    df["scheme_name"] = clean_text(df["scheme_name"])
    df["asset_class"] = clean_text(df["asset_class"])
    df["scheme_category"] = clean_text(df["scheme_category"])
    df["plan"] = clean_text(df["plan"])
    df["benchmark"] = clean_text(df["benchmark"])
    df["fund_manager"] = clean_text(df["fund_manager"])
    df["risk_category"] = clean_text(df["risk_category"])
    df["sebi_category_code"] = clean_text(df["sebi_category_code"])
    df["launch_date"] = parse_date(df["launch_date"], dayfirst=True)

    numeric_cols = [
        "amfi_code",
        "expense_ratio_pct",
        "exit_load_pct",
        "min_sip_amount",
        "min_lumpsum_amount",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["amfi_code"] = df["amfi_code"].astype("int64")
    df["min_sip_amount"] = df["min_sip_amount"].astype("int64")
    df["min_lumpsum_amount"] = df["min_lumpsum_amount"].astype("int64")
    df["launch_date"] = pd.to_datetime(df["launch_date"])
    df = df.drop_duplicates().sort_values(["fund_house", "amfi_code"]).reset_index(drop=True)

    if df["expense_ratio_pct"].isna().any():
        raise ValueError("fund_master contains non-numeric expense ratios")
    if not df["expense_ratio_pct"].between(0.1, 2.5).all():
        outliers = df.loc[~df["expense_ratio_pct"].between(0.1, 2.5), ["amfi_code", "expense_ratio_pct"]]
        raise ValueError(f"fund_master expense ratio outside expected range:\n{outliers}")

    return df


def clean_nav_history() -> pd.DataFrame:
    raw = read_source_csv(RAW_DIR / "02_nav_history.csv")
    raw.columns = [c.strip() for c in raw.columns]

    df = raw.copy()
    df["amfi_code"] = pd.to_numeric(df["amfi_code"], errors="coerce")
    df["nav_date"] = parse_date(df["date"], dayfirst=True)
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.drop(columns=["date"])
    df = df.dropna(subset=["amfi_code", "nav_date", "nav"])
    df = df[df["nav"] > 0].copy()
    df["amfi_code"] = df["amfi_code"].astype("int64")
    df = df.sort_values(["amfi_code", "nav_date"]).drop_duplicates(["amfi_code", "nav_date"], keep="last")

    expanded_frames: list[pd.DataFrame] = []
    for amfi_code, group in df.groupby("amfi_code", sort=False):
        group = group.sort_values("nav_date").copy()
        original_dates = pd.Index(group["nav_date"])
        full_dates = pd.date_range(group["nav_date"].min(), group["nav_date"].max(), freq="D")
        expanded = (
            group.set_index("nav_date")
            .reindex(full_dates)
            .rename_axis("nav_date")
            .reset_index()
        )
        expanded["amfi_code"] = int(amfi_code)
        expanded["is_imputed"] = (~expanded["nav_date"].isin(original_dates)).astype("int64")
        expanded["nav"] = expanded["nav"].ffill()
        if expanded["nav"].isna().any():
            raise ValueError(f"NAV forward-fill failed for amfi_code {amfi_code}")
        expanded_frames.append(expanded[["amfi_code", "nav_date", "nav", "is_imputed"]])

    result = pd.concat(expanded_frames, ignore_index=True)
    result = result.sort_values(["amfi_code", "nav_date"]).reset_index(drop=True)
    if not (result["nav"] > 0).all():
        raise ValueError("NAV validation failed: found non-positive values")
    return result


def clean_aum() -> pd.DataFrame:
    raw = read_source_csv(RAW_DIR / "03_aum_by_fund_house.csv")
    raw.columns = [c.strip() for c in raw.columns]

    df = raw.rename(columns={"date": "report_date"}).copy()
    df["report_date"] = parse_date(df["report_date"], dayfirst=True)
    df["fund_house"] = clean_text(df["fund_house"])
    for col in ["aum_lakh_crore", "aum_crore", "num_schemes"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["num_schemes"] = df["num_schemes"].astype("int64")
    df = df.drop_duplicates().sort_values(["report_date", "fund_house"]).reset_index(drop=True)
    return df


def clean_monthly_sip_inflows() -> pd.DataFrame:
    raw = read_source_csv(RAW_DIR / "04_monthly_sip_inflows.csv")
    raw.columns = [c.strip() for c in raw.columns]

    df = raw.rename(columns={"month": "report_month"}).copy()
    df["report_month"] = parse_month(df["report_month"])
    numeric_cols = [
        "sip_inflow_crore",
        "active_sip_accounts_crore",
        "new_sip_accounts_lakh",
        "sip_aum_lakh_crore",
        "yoy_growth_pct",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.drop_duplicates().sort_values("report_month").reset_index(drop=True)
    return df


def clean_category_inflows() -> pd.DataFrame:
    raw = read_source_csv(RAW_DIR / "05_category_inflows.csv")
    raw.columns = [c.strip() for c in raw.columns]

    df = raw.rename(columns={"month": "report_month", "category": "scheme_category"}).copy()
    df["report_month"] = parse_month(df["report_month"])
    df["scheme_category"] = clean_text(df["scheme_category"])
    df["net_inflow_crore"] = pd.to_numeric(df["net_inflow_crore"], errors="coerce")
    df = df.drop_duplicates().sort_values(["report_month", "scheme_category"]).reset_index(drop=True)
    return df


def clean_date_dimension() -> pd.DataFrame:
    start = pd.Timestamp("2006-01-01")
    end = pd.Timestamp("2026-05-29")
    dates = pd.date_range(start, end, freq="D")
    df = pd.DataFrame({"calendar_date": dates})
    df["date_key"] = df["calendar_date"].dt.strftime("%Y%m%d").astype("int64")
    df["year"] = df["calendar_date"].dt.year.astype("int64")
    df["quarter"] = df["calendar_date"].dt.quarter.astype("int64")
    df["month"] = df["calendar_date"].dt.month.astype("int64")
    df["month_name"] = df["calendar_date"].dt.strftime("%B")
    df["day"] = df["calendar_date"].dt.day.astype("int64")
    df["day_name"] = df["calendar_date"].dt.day_name()
    df["week_of_year"] = df["calendar_date"].dt.isocalendar().week.astype("int64")
    df["is_weekend"] = df["calendar_date"].dt.dayofweek.isin([5, 6]).astype("int64")
    df["is_month_start"] = df["calendar_date"].dt.is_month_start.astype("int64")
    df["is_month_end"] = df["calendar_date"].dt.is_month_end.astype("int64")
    df["is_quarter_start"] = df["calendar_date"].dt.is_quarter_start.astype("int64")
    df["is_quarter_end"] = df["calendar_date"].dt.is_quarter_end.astype("int64")
    return df


def clean_scheme_performance() -> pd.DataFrame:
    raw = read_source_csv(RAW_DIR / "07_scheme_performance.csv")
    raw.columns = [c.strip() for c in raw.columns]

    df = raw.rename(columns={"category": "scheme_category"}).copy()
    for col in ["scheme_name", "fund_house", "scheme_category", "plan", "risk_grade"]:
        df[col] = clean_text(df[col])

    numeric_cols = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    numeric_ok = df[numeric_cols].notna().all(axis=1)
    expense_ok = df["expense_ratio_pct"].between(0.1, 2.5, inclusive="both")
    df["expense_ratio_in_range"] = expense_ok.astype("int64")
    df["anomaly_flag"] = (~(numeric_ok & expense_ok)).astype("int64")

    if df["anomaly_flag"].any():
        flagged = df.loc[df["anomaly_flag"] == 1, ["amfi_code", "scheme_name"]]
        raise ValueError(f"Unexpected performance anomalies found:\n{flagged}")

    df["amfi_code"] = pd.to_numeric(df["amfi_code"], errors="coerce").astype("int64")
    df["morningstar_rating"] = df["morningstar_rating"].astype("int64")
    df = df.drop_duplicates().sort_values(["fund_house", "amfi_code"]).reset_index(drop=True)
    return df


def clean_transactions() -> pd.DataFrame:
    raw = read_source_csv(RAW_DIR / "08_investors_transactions.csv", engine="python")
    raw.columns = [c.strip() for c in raw.columns]

    df = raw.loc[:, ~raw.columns.str.startswith("Unnamed")].copy()
    df = df.dropna(how="all")
    df = df.rename(columns={})

    string_cols = [
        "investor_id",
        "transaction_type",
        "state",
        "city",
        "city_tier",
        "age_group",
        "gender",
        "payment_mode",
        "kyc_status",
    ]
    for col in string_cols:
        df[col] = clean_text(df[col])

    df["transaction_date"] = parse_date(df["transaction_date"], dayfirst=True)
    df["amfi_code"] = pd.to_numeric(df["amfi_code"], errors="coerce")
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    df["annual_income_lakh"] = pd.to_numeric(df["annual_income_lakh"], errors="coerce")

    transaction_map = {
        "sip": "SIP",
        "lumpsum": "Lumpsum",
        "lump sum": "Lumpsum",
        "lump-sum": "Lumpsum",
        "redemption": "Redemption",
    }
    kyc_map = {
        "verified": "Verified",
        "pending": "Pending",
        "rejected": "Rejected",
        "not verified": "Not Verified",
    }
    df["transaction_type"] = df["transaction_type"].str.lower().map(transaction_map).fillna("Unknown")
    df["kyc_status"] = df["kyc_status"].str.lower().map(kyc_map).fillna("Unknown")

    essential_cols = [
        "investor_id",
        "transaction_date",
        "amfi_code",
        "transaction_type",
        "amount_inr",
        "state",
        "city",
        "city_tier",
        "age_group",
        "gender",
        "annual_income_lakh",
        "payment_mode",
        "kyc_status",
    ]
    df = df.dropna(subset=["investor_id", "transaction_date", "amfi_code", "amount_inr"])
    df = df[df["amount_inr"] > 0].copy()
    df["amfi_code"] = df["amfi_code"].astype("int64")

    unexpected_types = sorted(set(df["transaction_type"]) - {"SIP", "Lumpsum", "Redemption"})
    if unexpected_types:
        raise ValueError(f"Unexpected transaction_type values: {unexpected_types}")
    unexpected_kyc = sorted(set(df["kyc_status"]) - {"Verified", "Pending", "Rejected", "Not Verified"})
    if unexpected_kyc:
        raise ValueError(f"Unexpected kyc_status values: {unexpected_kyc}")

    df = df.drop_duplicates().sort_values(["transaction_date", "investor_id", "amfi_code"]).reset_index(drop=True)
    return df[essential_cols]


def clean_portfolio_holdings() -> pd.DataFrame:
    raw = read_source_csv(RAW_DIR / "09_portfolio_holdings.csv")
    raw.columns = [c.strip() for c in raw.columns]

    df = raw.rename(columns={"portfolio_date": "as_of_date"}).copy()
    df["as_of_date"] = parse_date(df["as_of_date"], dayfirst=True)
    df["stock_symbol"] = clean_text(df["stock_symbol"])
    df["stock_name"] = clean_text(df["stock_name"])
    df["sector"] = clean_text(df["sector"])
    for col in ["amfi_code", "weight_pct", "market_value_cr", "current_price_inr"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["amfi_code"] = df["amfi_code"].astype("int64")
    df = df.drop_duplicates().sort_values(["as_of_date", "amfi_code", "weight_pct"], ascending=[True, True, False]).reset_index(drop=True)
    return df


def clean_benchmark_indices() -> pd.DataFrame:
    raw = read_source_csv(RAW_DIR / "10_benchmark_indeceds.csv")
    raw.columns = [c.strip() for c in raw.columns]

    df = raw.rename(columns={"date": "benchmark_date"}).copy()
    df["benchmark_date"] = parse_date(df["benchmark_date"], dayfirst=True)
    df["index_name"] = clean_text(df["index_name"])
    df["close_value"] = pd.to_numeric(df["close_value"], errors="coerce")
    df = df.drop_duplicates().sort_values(["index_name", "benchmark_date"]).reset_index(drop=True)
    return df


def write_schema_file() -> None:
    schema_sql = """
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
""".strip()
    SCHEMA_PATH.write_text(schema_sql + "\n", encoding="utf-8")


def write_queries_file() -> None:
    queries_sql = """
-- 1. Top 5 fund houses by latest AUM
WITH latest_aum AS (
    SELECT MAX(date_key) AS date_key
    FROM fact_aum
)
SELECT
    a.fund_house,
    date(a.report_date) AS report_date,
    a.aum_crore,
    a.num_schemes
FROM fact_aum a
JOIN latest_aum l
    ON a.date_key = l.date_key
ORDER BY a.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per calendar month across all funds
SELECT
    strftime('%Y-%m', d.calendar_date) AS month,
    ROUND(AVG(n.nav), 4) AS avg_nav
FROM fact_nav n
JOIN dim_date d
    ON n.date_key = d.date_key
GROUP BY strftime('%Y-%m', d.calendar_date)
ORDER BY month;

-- 3. SIP YoY growth from monthly inflows
SELECT
    date(curr.report_month) AS report_month,
    curr.sip_inflow_crore,
    ROUND(
        (curr.sip_inflow_crore - prev.sip_inflow_crore) * 100.0 / prev.sip_inflow_crore,
        2
    ) AS yoy_growth_pct
FROM monthly_sip_inflows_clean curr
LEFT JOIN monthly_sip_inflows_clean prev
    ON date(prev.report_month) = date(curr.report_month, '-1 year')
ORDER BY date(curr.report_month);

-- 4. Transactions by state
SELECT
    state,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- 5. Funds with expense ratio below 1%
SELECT
    amfi_code,
    scheme_name,
    fund_house,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC, scheme_name;

-- 6. Top schemes by 5-year return
SELECT
    f.scheme_name,
    f.fund_house,
    p.return_5yr_pct,
    p.sharpe_ratio,
    p.risk_grade
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
ORDER BY p.return_5yr_pct DESC
LIMIT 10;

-- 7. Transaction mix by type
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM fact_transactions
GROUP BY transaction_type
ORDER BY transaction_count DESC;

-- 8. Category inflow leaders
SELECT
    scheme_category,
    ROUND(SUM(net_inflow_crore), 2) AS total_net_inflow_crore
FROM category_inflows_clean
GROUP BY scheme_category
ORDER BY total_net_inflow_crore DESC
LIMIT 10;

-- 9. Portfolio concentration by sector
SELECT
    sector,
    ROUND(SUM(weight_pct), 2) AS total_weight_pct,
    ROUND(SUM(market_value_cr), 2) AS total_market_value_cr
FROM portfolio_holdings_clean
GROUP BY sector
ORDER BY total_market_value_cr DESC
LIMIT 10;

-- 10. Benchmark index monthly averages
SELECT
    index_name,
    strftime('%Y-%m', benchmark_date) AS month,
    ROUND(AVG(close_value), 2) AS avg_close_value
FROM benchmark_indices_clean
GROUP BY index_name, strftime('%Y-%m', benchmark_date)
ORDER BY index_name, month;
""".strip()
    QUERIES_PATH.write_text(queries_sql + "\n", encoding="utf-8")


def sql_type_for_series(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "DATE"
    if pd.api.types.is_bool_dtype(series):
        return "INTEGER"
    if pd.api.types.is_integer_dtype(series):
        return "INTEGER"
    if pd.api.types.is_float_dtype(series):
        return "REAL"
    return "TEXT"


def describe_column(dataset_key: str, column: str) -> str:
    if column == "amfi_code":
        return "Unique AMFI scheme code used as the scheme identifier."
    if column == "fund_house":
        return "Mutual fund house / asset manager name."
    if column == "scheme_name":
        return "Full scheme name as supplied by the source dataset."
    if column == "asset_class":
        return "Broad asset class from the fund master source (for example Equity or Debt)."
    if column == "scheme_category":
        if dataset_key == "fund_master_clean":
            return "Scheme sub-category or style bucket from the fund master source."
        if dataset_key == "category_inflows_clean":
            return "Category used for monthly inflow aggregation."
        return "Scheme category used in the source dataset."
    if column == "plan":
        return "Scheme plan type, usually Regular or Direct."
    if column == "launch_date":
        return "Scheme launch date normalized to ISO date format."
    if column == "benchmark":
        return "Benchmark index used for scheme comparison."
    if column == "expense_ratio_pct":
        return "Expense ratio expressed in percentage points."
    if column == "exit_load_pct":
        return "Exit load expressed in percentage points."
    if column == "min_sip_amount":
        return "Minimum monthly SIP amount in INR."
    if column == "min_lumpsum_amount":
        return "Minimum lump-sum investment amount in INR."
    if column == "fund_manager":
        return "Named fund manager for the scheme."
    if column == "risk_category":
        return "Risk category classification from the fund master source."
    if column == "sebi_category_code":
        return "SEBI / AMFI category code."
    if column == "nav_date":
        return "Daily NAV observation date in ISO format."
    if column == "nav":
        return "Net asset value per unit, in INR."
    if column == "is_imputed":
        return "Forward-fill indicator: 1 when NAV was imputed for a weekend or holiday, else 0."
    if column == "report_date":
        return "Reporting date for the AUM snapshot."
    if column == "aum_lakh_crore":
        return "Assets under management in lakh crore INR."
    if column == "aum_crore":
        return "Assets under management in crore INR."
    if column == "num_schemes":
        return "Count of schemes in the reporting fund house."
    if column == "report_month":
        return "Monthly reporting date normalized to the first day of the month."
    if column == "sip_inflow_crore":
        return "Monthly SIP inflows in crore INR."
    if column == "active_sip_accounts_crore":
        return "Active SIP accounts measured in crore accounts."
    if column == "new_sip_accounts_lakh":
        return "New SIP accounts opened during the month, measured in lakh."
    if column == "sip_aum_lakh_crore":
        return "SIP assets under management in lakh crore INR."
    if column == "yoy_growth_pct":
        return "Year-over-year growth percentage for the monthly SIP series."
    if column == "calendar_date":
        return "Calendar date in ISO format."
    if column == "date_key":
        return "Surrogate date key in YYYYMMDD format."
    if column == "year":
        return "Calendar year derived from the date."
    if column == "quarter":
        return "Calendar quarter derived from the date."
    if column == "month":
        return "Calendar month number derived from the date."
    if column == "month_name":
        return "Calendar month name derived from the date."
    if column == "day":
        return "Day of month derived from the date."
    if column == "day_name":
        return "Day-of-week name derived from the date."
    if column == "week_of_year":
        return "ISO week number derived from the date."
    if column == "is_weekend":
        return "Weekend flag: 1 for Saturday/Sunday, else 0."
    if column == "is_month_start":
        return "Month-start flag: 1 when the date is the first day of the month."
    if column == "is_month_end":
        return "Month-end flag: 1 when the date is the last day of the month."
    if column == "is_quarter_start":
        return "Quarter-start flag: 1 when the date is the first day of a quarter."
    if column == "is_quarter_end":
        return "Quarter-end flag: 1 when the date is the last day of a quarter."
    if column == "return_1yr_pct":
        return "Trailing 1-year return in percent."
    if column == "return_3yr_pct":
        return "Trailing 3-year return in percent."
    if column == "return_5yr_pct":
        return "Trailing 5-year return in percent."
    if column == "benchmark_3yr_pct":
        return "3-year benchmark return in percent."
    if column == "alpha":
        return "Alpha measure versus the benchmark."
    if column == "beta":
        return "Beta / market sensitivity measure."
    if column == "sharpe_ratio":
        return "Sharpe ratio for risk-adjusted returns."
    if column == "sortino_ratio":
        return "Sortino ratio for downside-risk-adjusted returns."
    if column == "std_dev_ann_pct":
        return "Annualized standard deviation in percent."
    if column == "max_drawdown_pct":
        return "Maximum drawdown in percent."
    if column == "morningstar_rating":
        return "Morningstar rating score on the 1-5 scale."
    if column == "risk_grade":
        return "Risk grade classification standardized during cleanup."
    if column == "expense_ratio_in_range":
        return "Validation flag: 1 when expense ratio falls within 0.1% to 2.5%."
    if column == "anomaly_flag":
        return "Validation flag: 1 when a performance record fails numeric or range checks."
    if column == "investor_id":
        return "Unique investor identifier."
    if column == "transaction_date":
        return "Transaction booking date normalized to ISO format."
    if column == "transaction_type":
        return "Standardized transaction type with allowed values SIP, Lumpsum, and Redemption."
    if column == "amount_inr":
        return "Transaction amount in INR."
    if column == "state":
        return "Investor state."
    if column == "city":
        return "Investor city."
    if column == "city_tier":
        return "City tier classification such as T30 or B30."
    if column == "age_group":
        return "Investor age band."
    if column == "gender":
        return "Investor gender label from the source file."
    if column == "annual_income_lakh":
        return "Declared annual income in lakh INR."
    if column == "payment_mode":
        return "Payment instrument used for the transaction."
    if column == "kyc_status":
        return "KYC status standardized to the source enum values."
    if column == "stock_symbol":
        return "Underlying stock ticker symbol."
    if column == "stock_name":
        return "Underlying company or stock name."
    if column == "sector":
        return "Equity sector bucket for the holding."
    if column == "weight_pct":
        return "Portfolio weight expressed in percentage points."
    if column == "market_value_cr":
        return "Market value of the holding in crore INR."
    if column == "current_price_inr":
        return "Current stock price in INR."
    if column == "as_of_date":
        return "Portfolio snapshot date in ISO format."
    if column == "benchmark_date":
        return "Benchmark index observation date in ISO format."
    if column == "index_name":
        return "Benchmark index name."
    if column == "close_value":
        return "Benchmark closing level."
    return column.replace("_", " ").capitalize()


def write_data_dictionary(cleaned: dict[str, pd.DataFrame]) -> None:
    source_refs = {
        "fund_master_clean": "data/raw/01_fund_master.csv",
        "nav_history_clean": "data/raw/02_nav_history.csv",
        "aum_by_fund_house_clean": "data/raw/03_aum_by_fund_house.csv",
        "monthly_sip_inflows_clean": "data/raw/04_monthly_sip_inflows.csv",
        "category_inflows_clean": "data/raw/05_category_inflows.csv",
        "date_dimension": "Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv",
        "scheme_performance_clean": "data/raw/07_scheme_performance.csv",
        "investor_transactions_clean": "data/raw/08_investors_transactions.csv",
        "portfolio_holdings_clean": "data/raw/09_portfolio_holdings.csv",
        "benchmark_indices_clean": "data/raw/10_benchmark_indeceds.csv",
    }

    display_names = {
        "fund_master_clean": "01_fund_master.csv",
        "nav_history_clean": "02_nav_history.csv",
        "aum_by_fund_house_clean": "03_aum_by_fund_house.csv",
        "monthly_sip_inflows_clean": "04_monthly_sip_inflows.csv",
        "category_inflows_clean": "05_category_inflows.csv",
        "date_dimension": "06_date_dimension.csv",
        "scheme_performance_clean": "07_scheme_performance.csv",
        "investor_transactions_clean": "08_investors_transactions.csv",
        "portfolio_holdings_clean": "09_portfolio_holdings.csv",
        "benchmark_indices_clean": "10_benchmark_indeceds.csv",
    }

    star_schema_notes = [
        "dim_fund mirrors `01_fund_master.csv`.",
        "dim_date is the derived date dimension used by the star schema.",
        "fact_nav mirrors `02_nav_history.csv` and adds `date_key` in SQLite.",
        "fact_transactions mirrors `08_investors_transactions.csv` and adds `transaction_id` and `date_key` in SQLite.",
        "fact_performance mirrors `07_scheme_performance.csv`.",
        "fact_aum mirrors `03_aum_by_fund_house.csv` and adds `aum_id` and `date_key` in SQLite.",
    ]

    lines: list[str] = [
        "# Data Dictionary",
        "",
        "## Standardization Notes",
        "- Date fields are normalized to ISO `YYYY-MM-DD` format.",
        "- Monthly fields are normalized to the first day of the month.",
        "- `scheme_category` is the cleaned name for the source category/sub-category fields.",
        "- `nav_history.csv` is forward-filled across non-trading days and carries an `is_imputed` flag.",
        "- `scheme_performance.csv` includes validation flags for expense-ratio range checks and anomaly detection.",
        "",
        "## Cleaned CSV Dictionary",
        "",
    ]

    for dataset_key, df in cleaned.items():
        if dataset_key not in display_names:
            continue
        lines.extend(
            [
                f"### {display_names[dataset_key]}",
                "",
                f"Source: `{source_refs[dataset_key]}`",
                f"Rows: {len(df):,}",
                "",
                "| Column | Type | Business Definition | Source Reference |",
                "|---|---|---|---|",
            ]
        )
        for column in df.columns:
            lines.append(
                f"| `{column}` | {sql_type_for_series(df[column])} | {describe_column(dataset_key, column)} | `{source_refs[dataset_key]}` |"
            )
        lines.append("")

    lines.extend(
        [
            "## SQLite Star Schema Notes",
            "",
            "| Table | Grain / Purpose | Key Columns | Source Reference |",
            "|---|---|---|---|",
            "| `dim_fund` | One row per scheme / fund | `amfi_code` | Mirrors `01_fund_master.csv` |",
            "| `dim_date` | One row per calendar date | `date_key` | Derived date dimension |",
            "| `fact_nav` | One row per scheme-date NAV observation | `amfi_code`, `date_key` | Mirrors `02_nav_history.csv` |",
            "| `fact_transactions` | One row per transaction | `transaction_id`, `date_key`, `amfi_code` | Mirrors `08_investors_transactions.csv` |",
            "| `fact_performance` | One row per scheme performance snapshot | `amfi_code` | Mirrors `07_scheme_performance.csv` |",
            "| `fact_aum` | One row per fund-house date snapshot | `aum_id`, `date_key` | Mirrors `03_aum_by_fund_house.csv` |",
            "",
            "- `dim_fund` reuses the cleaned fund-master columns without extra database-only fields.",
            "- `dim_date` contains the derived date spine and calendar attributes used across all joins.",
            "- `fact_nav` adds `date_key` to the cleaned NAV history for the foreign key into `dim_date`.",
            "- `fact_transactions` adds an autoincrement `transaction_id` and `date_key` in SQLite.",
            "- `fact_performance` is a direct load of the cleaned performance snapshot.",
            "- `fact_aum` adds an autoincrement `aum_id` and `date_key` in SQLite.",
            "",
            "### Database-Only Columns",
            "",
            "| Column | Type | Business Definition | Source Reference |",
            "|---|---|---|---|",
            "| `date_key` | INTEGER | Surrogate date key in `YYYYMMDD` format used to join facts to `dim_date`. | Derived in SQLite from the cleaned date fields. |",
            "| `transaction_id` | INTEGER | Autoincrement surrogate key for `fact_transactions`. | Generated by SQLite. |",
            "| `aum_id` | INTEGER | Autoincrement surrogate key for `fact_aum`. | Generated by SQLite. |",
            "",
        ]
    )

    DATA_DICT_PATH.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def build_processed_outputs() -> dict[str, pd.DataFrame]:
    fund_master = clean_fund_master()
    nav_history = clean_nav_history()
    aum = clean_aum()
    sip = clean_monthly_sip_inflows()
    category_inflows = clean_category_inflows()
    date_dim = clean_date_dimension()
    performance = clean_scheme_performance()
    transactions = clean_transactions()
    holdings = clean_portfolio_holdings()
    benchmark = clean_benchmark_indices()

    save_csv(fund_master, PROCESSED_DIR / "01_fund_master.csv")
    save_csv(nav_history, PROCESSED_DIR / "02_nav_history.csv")
    save_csv(aum, PROCESSED_DIR / "03_aum_by_fund_house.csv")
    save_csv(sip, PROCESSED_DIR / "04_monthly_sip_inflows.csv")
    save_csv(category_inflows, PROCESSED_DIR / "05_category_inflows.csv")
    save_csv(date_dim, PROCESSED_DIR / "06_date_dimension.csv")
    save_csv(performance, PROCESSED_DIR / "07_scheme_performance.csv")
    save_csv(transactions, PROCESSED_DIR / "08_investors_transactions.csv")
    save_csv(holdings, PROCESSED_DIR / "09_portfolio_holdings.csv")
    save_csv(benchmark, PROCESSED_DIR / "10_benchmark_indeceds.csv")

    return {
        "fund_master_clean": fund_master,
        "nav_history_clean": nav_history,
        "aum_by_fund_house_clean": aum,
        "monthly_sip_inflows_clean": sip,
        "category_inflows_clean": category_inflows,
        "date_dimension": date_dim,
        "scheme_performance_clean": performance,
        "investor_transactions_clean": transactions,
        "portfolio_holdings_clean": holdings,
        "benchmark_indices_clean": benchmark,
    }


def load_sqlite(cleaned: dict[str, pd.DataFrame]) -> dict[str, int]:
    engine = create_engine(f"sqlite:///{DB_PATH}")

    table_counts: dict[str, int] = {}
    with engine.begin() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys = ON;")
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        for statement in schema_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.exec_driver_sql(stmt)

        clean_table_map = {
            "fund_master_clean": "fund_master_clean",
            "nav_history_clean": "nav_history_clean",
            "aum_by_fund_house_clean": "aum_by_fund_house_clean",
            "monthly_sip_inflows_clean": "monthly_sip_inflows_clean",
            "category_inflows_clean": "category_inflows_clean",
            "scheme_performance_clean": "scheme_performance_clean",
            "investor_transactions_clean": "investor_transactions_clean",
            "portfolio_holdings_clean": "portfolio_holdings_clean",
            "benchmark_indices_clean": "benchmark_indices_clean",
        }
        for key, table_name in clean_table_map.items():
            cleaned[key].to_sql(table_name, conn, if_exists="replace", index=False)
            table_counts[table_name] = conn.exec_driver_sql(
                f"SELECT COUNT(*) FROM {table_name}"
            ).scalar_one()

        date_dim = cleaned["date_dimension"].copy()
        date_dim["calendar_date"] = pd.to_datetime(date_dim["calendar_date"])
        date_dim.to_sql("dim_date", conn, if_exists="append", index=False)
        table_counts["dim_date"] = conn.exec_driver_sql("SELECT COUNT(*) FROM dim_date").scalar_one()

        dim_fund = cleaned["fund_master_clean"].copy()
        dim_fund.to_sql("dim_fund", conn, if_exists="append", index=False)
        table_counts["dim_fund"] = conn.exec_driver_sql("SELECT COUNT(*) FROM dim_fund").scalar_one()

        fact_nav = cleaned["nav_history_clean"].copy()
        fact_nav["date_key"] = to_date_key(fact_nav["nav_date"])
        fact_nav.to_sql("fact_nav", conn, if_exists="append", index=False)
        table_counts["fact_nav"] = conn.exec_driver_sql("SELECT COUNT(*) FROM fact_nav").scalar_one()

        fact_transactions = cleaned["investor_transactions_clean"].copy()
        fact_transactions["date_key"] = to_date_key(fact_transactions["transaction_date"])
        fact_transactions.to_sql("fact_transactions", conn, if_exists="append", index=False)
        table_counts["fact_transactions"] = conn.exec_driver_sql("SELECT COUNT(*) FROM fact_transactions").scalar_one()

        fact_performance = cleaned["scheme_performance_clean"].copy()
        fact_performance.to_sql("fact_performance", conn, if_exists="append", index=False)
        table_counts["fact_performance"] = conn.exec_driver_sql("SELECT COUNT(*) FROM fact_performance").scalar_one()

        fact_aum = cleaned["aum_by_fund_house_clean"].copy()
        fact_aum["date_key"] = to_date_key(fact_aum["report_date"])
        fact_aum.to_sql("fact_aum", conn, if_exists="append", index=False)
        table_counts["fact_aum"] = conn.exec_driver_sql("SELECT COUNT(*) FROM fact_aum").scalar_one()

    return table_counts


def verify_counts(cleaned: dict[str, pd.DataFrame], table_counts: dict[str, int]) -> None:
    expected = {
        "fund_master_clean": len(cleaned["fund_master_clean"]),
        "nav_history_clean": len(cleaned["nav_history_clean"]),
        "aum_by_fund_house_clean": len(cleaned["aum_by_fund_house_clean"]),
        "monthly_sip_inflows_clean": len(cleaned["monthly_sip_inflows_clean"]),
        "category_inflows_clean": len(cleaned["category_inflows_clean"]),
        "scheme_performance_clean": len(cleaned["scheme_performance_clean"]),
        "investor_transactions_clean": len(cleaned["investor_transactions_clean"]),
        "portfolio_holdings_clean": len(cleaned["portfolio_holdings_clean"]),
        "benchmark_indices_clean": len(cleaned["benchmark_indices_clean"]),
        "dim_date": len(cleaned["date_dimension"]),
        "dim_fund": len(cleaned["fund_master_clean"]),
        "fact_nav": len(cleaned["nav_history_clean"]),
        "fact_transactions": len(cleaned["investor_transactions_clean"]),
        "fact_performance": len(cleaned["scheme_performance_clean"]),
        "fact_aum": len(cleaned["aum_by_fund_house_clean"]),
    }

    mismatches: list[str] = []
    for table_name, expected_count in expected.items():
        actual = table_counts.get(table_name)
        if actual != expected_count:
            mismatches.append(f"{table_name}: expected {expected_count}, got {actual}")

    if mismatches:
        raise ValueError("SQLite row-count verification failed:\n" + "\n".join(mismatches))


def main() -> None:
    ensure_dirs()
    write_schema_file()
    write_queries_file()

    cleaned = build_processed_outputs()
    write_data_dictionary(cleaned)
    table_counts = load_sqlite(cleaned)
    verify_counts(cleaned, table_counts)

    print("Day 2 pipeline completed successfully.")
    for name, df in cleaned.items():
        if name == "date_dimension":
            continue
        print(f"{name}: {len(df):,} rows")
    print(f"date_dimension: {len(cleaned['date_dimension']):,} rows")
    print(f"SQLite database: {DB_PATH}")
    print(f"Schema file: {SCHEMA_PATH}")
    print(f"Queries file: {QUERIES_PATH}")
    print(f"Data directory: {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
