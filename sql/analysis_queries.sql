-- 1) Revenue by product category
SELECT category,
       ROUND(SUM(net_sales), 2) AS total_revenue
FROM fact_sales
WHERE order_status = 'Completed'
GROUP BY category
ORDER BY total_revenue DESC;

-- 2) Conversion rate by traffic source
SELECT traffic_source,
       ROUND(AVG(completed_order) * 100, 2) AS conversion_rate_pct
FROM fact_sales
GROUP BY traffic_source
ORDER BY conversion_rate_pct DESC;

-- 3) Top 10 products by revenue
SELECT product_name,
       ROUND(SUM(net_sales), 2) AS product_revenue
FROM fact_sales
WHERE order_status = 'Completed'
GROUP BY product_name
ORDER BY product_revenue DESC
LIMIT 10;

-- 4) Country-level sales performance
SELECT country,
       COUNT(DISTINCT order_id) AS total_orders,
       ROUND(SUM(net_sales), 2) AS revenue,
       ROUND(AVG(net_sales), 2) AS avg_order_value
FROM fact_sales
WHERE order_status = 'Completed'
GROUP BY country
ORDER BY revenue DESC;

-- 5) Monthly sales trend
SELECT strftime('%Y-%m', order_date) AS order_month,
       ROUND(SUM(net_sales), 2) AS monthly_revenue
FROM fact_sales
WHERE order_status = 'Completed'
GROUP BY strftime('%Y-%m', order_date)
ORDER BY order_month;
