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
