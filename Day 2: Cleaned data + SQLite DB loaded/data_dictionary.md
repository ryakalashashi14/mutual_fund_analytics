# Data Dictionary

## Standardization Notes
- Date fields are normalized to ISO `YYYY-MM-DD` format.
- Monthly fields are normalized to the first day of the month.
- `scheme_category` is the cleaned name for the source category/sub-category fields.
- `nav_history.csv` is forward-filled across non-trading days and carries an `is_imputed` flag.
- `scheme_performance.csv` includes validation flags for expense-ratio range checks and anomaly detection.

## Cleaned CSV Dictionary

### 01_fund_master.csv

Source: `data/raw/01_fund_master.csv`
Rows: 40

| Column | Type | Business Definition | Source Reference |
|---|---|---|---|
| `amfi_code` | INTEGER | Unique AMFI scheme code used as the scheme identifier. | `data/raw/01_fund_master.csv` |
| `fund_house` | TEXT | Mutual fund house / asset manager name. | `data/raw/01_fund_master.csv` |
| `scheme_name` | TEXT | Full scheme name as supplied by the source dataset. | `data/raw/01_fund_master.csv` |
| `asset_class` | TEXT | Broad asset class from the fund master source (for example Equity or Debt). | `data/raw/01_fund_master.csv` |
| `scheme_category` | TEXT | Scheme sub-category or style bucket from the fund master source. | `data/raw/01_fund_master.csv` |
| `plan` | TEXT | Scheme plan type, usually Regular or Direct. | `data/raw/01_fund_master.csv` |
| `launch_date` | DATE | Scheme launch date normalized to ISO date format. | `data/raw/01_fund_master.csv` |
| `benchmark` | TEXT | Benchmark index used for scheme comparison. | `data/raw/01_fund_master.csv` |
| `expense_ratio_pct` | REAL | Expense ratio expressed in percentage points. | `data/raw/01_fund_master.csv` |
| `exit_load_pct` | REAL | Exit load expressed in percentage points. | `data/raw/01_fund_master.csv` |
| `min_sip_amount` | INTEGER | Minimum monthly SIP amount in INR. | `data/raw/01_fund_master.csv` |
| `min_lumpsum_amount` | INTEGER | Minimum lump-sum investment amount in INR. | `data/raw/01_fund_master.csv` |
| `fund_manager` | TEXT | Named fund manager for the scheme. | `data/raw/01_fund_master.csv` |
| `risk_category` | TEXT | Risk category classification from the fund master source. | `data/raw/01_fund_master.csv` |
| `sebi_category_code` | TEXT | SEBI / AMFI category code. | `data/raw/01_fund_master.csv` |

### 02_nav_history.csv

Source: `data/raw/02_nav_history.csv`
Rows: 64,320

| Column | Type | Business Definition | Source Reference |
|---|---|---|---|
| `amfi_code` | INTEGER | Unique AMFI scheme code used as the scheme identifier. | `data/raw/02_nav_history.csv` |
| `nav_date` | DATE | Daily NAV observation date in ISO format. | `data/raw/02_nav_history.csv` |
| `nav` | REAL | Net asset value per unit, in INR. | `data/raw/02_nav_history.csv` |
| `is_imputed` | INTEGER | Forward-fill indicator: 1 when NAV was imputed for a weekend or holiday, else 0. | `data/raw/02_nav_history.csv` |

### 03_aum_by_fund_house.csv

Source: `data/raw/03_aum_by_fund_house.csv`
Rows: 90

| Column | Type | Business Definition | Source Reference |
|---|---|---|---|
| `report_date` | DATE | Reporting date for the AUM snapshot. | `data/raw/03_aum_by_fund_house.csv` |
| `fund_house` | TEXT | Mutual fund house / asset manager name. | `data/raw/03_aum_by_fund_house.csv` |
| `aum_lakh_crore` | REAL | Assets under management in lakh crore INR. | `data/raw/03_aum_by_fund_house.csv` |
| `aum_crore` | INTEGER | Assets under management in crore INR. | `data/raw/03_aum_by_fund_house.csv` |
| `num_schemes` | INTEGER | Count of schemes in the reporting fund house. | `data/raw/03_aum_by_fund_house.csv` |

### 04_monthly_sip_inflows.csv

Source: `data/raw/04_monthly_sip_inflows.csv`
Rows: 48

| Column | Type | Business Definition | Source Reference |
|---|---|---|---|
| `report_month` | DATE | Monthly reporting date normalized to the first day of the month. | `data/raw/04_monthly_sip_inflows.csv` |
| `sip_inflow_crore` | INTEGER | Monthly SIP inflows in crore INR. | `data/raw/04_monthly_sip_inflows.csv` |
| `active_sip_accounts_crore` | REAL | Active SIP accounts measured in crore accounts. | `data/raw/04_monthly_sip_inflows.csv` |
| `new_sip_accounts_lakh` | REAL | New SIP accounts opened during the month, measured in lakh. | `data/raw/04_monthly_sip_inflows.csv` |
| `sip_aum_lakh_crore` | REAL | SIP assets under management in lakh crore INR. | `data/raw/04_monthly_sip_inflows.csv` |
| `yoy_growth_pct` | REAL | Year-over-year growth percentage for the monthly SIP series. | `data/raw/04_monthly_sip_inflows.csv` |

### 05_category_inflows.csv

Source: `data/raw/05_category_inflows.csv`
Rows: 144

| Column | Type | Business Definition | Source Reference |
|---|---|---|---|
| `report_month` | DATE | Monthly reporting date normalized to the first day of the month. | `data/raw/05_category_inflows.csv` |
| `scheme_category` | TEXT | Category used for monthly inflow aggregation. | `data/raw/05_category_inflows.csv` |
| `net_inflow_crore` | INTEGER | Net inflow crore | `data/raw/05_category_inflows.csv` |

### 06_date_dimension.csv

Source: `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv`
Rows: 7,454

| Column | Type | Business Definition | Source Reference |
|---|---|---|---|
| `calendar_date` | DATE | Calendar date in ISO format. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |
| `date_key` | INTEGER | Surrogate date key in YYYYMMDD format. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |
| `year` | INTEGER | Calendar year derived from the date. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |
| `quarter` | INTEGER | Calendar quarter derived from the date. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |
| `month` | INTEGER | Calendar month number derived from the date. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |
| `month_name` | TEXT | Calendar month name derived from the date. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |
| `day` | INTEGER | Day of month derived from the date. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |
| `day_name` | TEXT | Day-of-week name derived from the date. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |
| `week_of_year` | INTEGER | ISO week number derived from the date. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |
| `is_weekend` | INTEGER | Weekend flag: 1 for Saturday/Sunday, else 0. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |
| `is_month_start` | INTEGER | Month-start flag: 1 when the date is the first day of the month. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |
| `is_month_end` | INTEGER | Month-end flag: 1 when the date is the last day of the month. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |
| `is_quarter_start` | INTEGER | Quarter-start flag: 1 when the date is the first day of a quarter. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |
| `is_quarter_end` | INTEGER | Quarter-end flag: 1 when the date is the last day of a quarter. | `Derived from 01_fund_master.csv, 02_nav_history.csv, 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 07_scheme_performance.csv, 08_investors_transactions.csv, 09_portfolio_holdings.csv, and 10_benchmark_indeceds.csv` |

### 07_scheme_performance.csv

Source: `data/raw/07_scheme_performance.csv`
Rows: 40

| Column | Type | Business Definition | Source Reference |
|---|---|---|---|
| `amfi_code` | INTEGER | Unique AMFI scheme code used as the scheme identifier. | `data/raw/07_scheme_performance.csv` |
| `scheme_name` | TEXT | Full scheme name as supplied by the source dataset. | `data/raw/07_scheme_performance.csv` |
| `fund_house` | TEXT | Mutual fund house / asset manager name. | `data/raw/07_scheme_performance.csv` |
| `scheme_category` | TEXT | Scheme category used in the source dataset. | `data/raw/07_scheme_performance.csv` |
| `plan` | TEXT | Scheme plan type, usually Regular or Direct. | `data/raw/07_scheme_performance.csv` |
| `return_1yr_pct` | REAL | Trailing 1-year return in percent. | `data/raw/07_scheme_performance.csv` |
| `return_3yr_pct` | REAL | Trailing 3-year return in percent. | `data/raw/07_scheme_performance.csv` |
| `return_5yr_pct` | REAL | Trailing 5-year return in percent. | `data/raw/07_scheme_performance.csv` |
| `benchmark_3yr_pct` | REAL | 3-year benchmark return in percent. | `data/raw/07_scheme_performance.csv` |
| `alpha` | REAL | Alpha measure versus the benchmark. | `data/raw/07_scheme_performance.csv` |
| `beta` | REAL | Beta / market sensitivity measure. | `data/raw/07_scheme_performance.csv` |
| `sharpe_ratio` | REAL | Sharpe ratio for risk-adjusted returns. | `data/raw/07_scheme_performance.csv` |
| `sortino_ratio` | REAL | Sortino ratio for downside-risk-adjusted returns. | `data/raw/07_scheme_performance.csv` |
| `std_dev_ann_pct` | REAL | Annualized standard deviation in percent. | `data/raw/07_scheme_performance.csv` |
| `max_drawdown_pct` | REAL | Maximum drawdown in percent. | `data/raw/07_scheme_performance.csv` |
| `aum_crore` | INTEGER | Assets under management in crore INR. | `data/raw/07_scheme_performance.csv` |
| `expense_ratio_pct` | REAL | Expense ratio expressed in percentage points. | `data/raw/07_scheme_performance.csv` |
| `morningstar_rating` | INTEGER | Morningstar rating score on the 1-5 scale. | `data/raw/07_scheme_performance.csv` |
| `risk_grade` | TEXT | Risk grade classification standardized during cleanup. | `data/raw/07_scheme_performance.csv` |
| `expense_ratio_in_range` | INTEGER | Validation flag: 1 when expense ratio falls within 0.1% to 2.5%. | `data/raw/07_scheme_performance.csv` |
| `anomaly_flag` | INTEGER | Validation flag: 1 when a performance record fails numeric or range checks. | `data/raw/07_scheme_performance.csv` |

### 08_investors_transactions.csv

Source: `data/raw/08_investors_transactions.csv`
Rows: 29,099

| Column | Type | Business Definition | Source Reference |
|---|---|---|---|
| `investor_id` | TEXT | Unique investor identifier. | `data/raw/08_investors_transactions.csv` |
| `transaction_date` | DATE | Transaction booking date normalized to ISO format. | `data/raw/08_investors_transactions.csv` |
| `amfi_code` | INTEGER | Unique AMFI scheme code used as the scheme identifier. | `data/raw/08_investors_transactions.csv` |
| `transaction_type` | TEXT | Standardized transaction type with allowed values SIP, Lumpsum, and Redemption. | `data/raw/08_investors_transactions.csv` |
| `amount_inr` | REAL | Transaction amount in INR. | `data/raw/08_investors_transactions.csv` |
| `state` | TEXT | Investor state. | `data/raw/08_investors_transactions.csv` |
| `city` | TEXT | Investor city. | `data/raw/08_investors_transactions.csv` |
| `city_tier` | TEXT | City tier classification such as T30 or B30. | `data/raw/08_investors_transactions.csv` |
| `age_group` | TEXT | Investor age band. | `data/raw/08_investors_transactions.csv` |
| `gender` | TEXT | Investor gender label from the source file. | `data/raw/08_investors_transactions.csv` |
| `annual_income_lakh` | REAL | Declared annual income in lakh INR. | `data/raw/08_investors_transactions.csv` |
| `payment_mode` | TEXT | Payment instrument used for the transaction. | `data/raw/08_investors_transactions.csv` |
| `kyc_status` | TEXT | KYC status standardized to the source enum values. | `data/raw/08_investors_transactions.csv` |

### 09_portfolio_holdings.csv

Source: `data/raw/09_portfolio_holdings.csv`
Rows: 322

| Column | Type | Business Definition | Source Reference |
|---|---|---|---|
| `amfi_code` | INTEGER | Unique AMFI scheme code used as the scheme identifier. | `data/raw/09_portfolio_holdings.csv` |
| `stock_symbol` | TEXT | Underlying stock ticker symbol. | `data/raw/09_portfolio_holdings.csv` |
| `stock_name` | TEXT | Underlying company or stock name. | `data/raw/09_portfolio_holdings.csv` |
| `sector` | TEXT | Equity sector bucket for the holding. | `data/raw/09_portfolio_holdings.csv` |
| `weight_pct` | REAL | Portfolio weight expressed in percentage points. | `data/raw/09_portfolio_holdings.csv` |
| `market_value_cr` | REAL | Market value of the holding in crore INR. | `data/raw/09_portfolio_holdings.csv` |
| `current_price_inr` | REAL | Current stock price in INR. | `data/raw/09_portfolio_holdings.csv` |
| `as_of_date` | DATE | Portfolio snapshot date in ISO format. | `data/raw/09_portfolio_holdings.csv` |

### 10_benchmark_indeceds.csv

Source: `data/raw/10_benchmark_indeceds.csv`
Rows: 8,050

| Column | Type | Business Definition | Source Reference |
|---|---|---|---|
| `benchmark_date` | DATE | Benchmark index observation date in ISO format. | `data/raw/10_benchmark_indeceds.csv` |
| `index_name` | TEXT | Benchmark index name. | `data/raw/10_benchmark_indeceds.csv` |
| `close_value` | REAL | Benchmark closing level. | `data/raw/10_benchmark_indeceds.csv` |

## SQLite Star Schema Notes

| Table | Grain / Purpose | Key Columns | Source Reference |
|---|---|---|---|
| `dim_fund` | One row per scheme / fund | `amfi_code` | Mirrors `01_fund_master.csv` |
| `dim_date` | One row per calendar date | `date_key` | Derived date dimension |
| `fact_nav` | One row per scheme-date NAV observation | `amfi_code`, `date_key` | Mirrors `02_nav_history.csv` |
| `fact_transactions` | One row per transaction | `transaction_id`, `date_key`, `amfi_code` | Mirrors `08_investors_transactions.csv` |
| `fact_performance` | One row per scheme performance snapshot | `amfi_code` | Mirrors `07_scheme_performance.csv` |
| `fact_aum` | One row per fund-house date snapshot | `aum_id`, `date_key` | Mirrors `03_aum_by_fund_house.csv` |

- `dim_fund` reuses the cleaned fund-master columns without extra database-only fields.
- `dim_date` contains the derived date spine and calendar attributes used across all joins.
- `fact_nav` adds `date_key` to the cleaned NAV history for the foreign key into `dim_date`.
- `fact_transactions` adds an autoincrement `transaction_id` and `date_key` in SQLite.
- `fact_performance` is a direct load of the cleaned performance snapshot.
- `fact_aum` adds an autoincrement `aum_id` and `date_key` in SQLite.

### Database-Only Columns

| Column | Type | Business Definition | Source Reference |
|---|---|---|---|
| `date_key` | INTEGER | Surrogate date key in `YYYYMMDD` format used to join facts to `dim_date`. | Derived in SQLite from the cleaned date fields. |
| `transaction_id` | INTEGER | Autoincrement surrogate key for `fact_transactions`. | Generated by SQLite. |
| `aum_id` | INTEGER | Autoincrement surrogate key for `fact_aum`. | Generated by SQLite. |
