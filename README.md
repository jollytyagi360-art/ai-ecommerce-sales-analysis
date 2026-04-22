# AI-Assisted E-Commerce Data Analytics Project

## 1) Problem Statement
E-commerce teams need a repeatable analytics workflow to transform raw transactional data into business insights. This project builds a full analytics pipeline that:
- generates realistic e-commerce datasets,
- cleans and analyzes data with Python,
- computes core KPIs,
- segments customers,
- forecasts short-term sales,
- and defines a Power BI dashboard layout for business users.

## 2) Project Structure

```text
ai-ecommerce-sales-analysis/
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── sales.csv
├── outputs/
│   ├── customer_segments.csv
│   ├── kpi_summary.csv
│   ├── monthly_sales.csv
│   ├── revenue_by_category.csv
│   ├── conversion_by_source.csv
│   ├── sales_forecast.csv
│   ├── top_customers.csv
│   └── top_products.csv
├── sql/
│   └── analysis_queries.sql
├── src/
│   ├── generate_dataset.py
│   └── analysis.py
└── README.md
```

## 3) Dataset Design

### customers.csv
- `customer_id`, `customer_name`, `segment_label`, `country`, `signup_date`

### products.csv
- `product_id`, `product_name`, `category`, `unit_cost`, `unit_price`

### sales.csv
- `order_id`, `order_date`, `customer_id`, `product_id`, `quantity`, `unit_price`, `discount_pct`, `gross_sales`, `net_sales`, `order_status`, `completed_order`, `traffic_source`

## 4) Analytics Included

### A) Data Cleaning + EDA (Python: Pandas, NumPy)
- Remove duplicate orders
- Clip impossible negative numeric values
- Create `order_month`
- Build a merged fact table and calculate profit
- Export KPI and trend outputs to `/outputs`

### B) KPI Generation
- **Total Revenue**: Sum of `net_sales` for completed orders
- **Conversion Rate**: Average of `completed_order`
- **Top Products**: Top 10 products by completed-order revenue

### C) SQL Analysis
Ready-to-run SQL queries in `sql/analysis_queries.sql` for:
1. Revenue by category
2. Conversion by traffic source
3. Top products
4. Country sales performance
5. Monthly revenue trend

### D) Customer Segmentation
RFM segmentation (Recency, Frequency, Monetary):
- Quantile-based scoring for each RFM metric
- Combined `rfm_score`
- Segments: `High Value`, `Medium Value`, `Low Value`

### E) Sales Forecasting (Basic Model)
- Aggregate completed-order sales monthly
- Fit a linear trend model using `numpy.polyfit`
- Forecast next 3 months

## 5) Power BI Dashboard Structure

### Page 1: Executive Overview
**Cards / KPIs**
- Total Revenue
- Conversion Rate
- Average Order Value
- Total Completed Orders

**Visuals**
- Line chart: monthly revenue trend + forecast
- Bar chart: revenue by category
- Filled map: revenue by country
- Donut chart: order status split

### Page 2: Product Performance
**Visuals**
- Top 10 products by revenue (horizontal bar)
- Scatter: product revenue vs quantity sold
- Matrix: category > product drilldown with revenue/profit

### Page 3: Customer Insights
**Visuals**
- Stacked column: customer segments counts
- Table: top customers by revenue
- Bar: conversion rate by traffic source
- Slicers: date range, country, category, traffic source

## 6) Key Insights You Can Expect
- Revenue concentration in specific categories/products
- Stronger conversion from high-intent traffic channels
- Clear separation of high/medium/low value customer groups
- Directional month-over-month trend for short-term planning

## 7) Business Impact
- Faster reporting cycle (automated Python + SQL outputs)
- Better budget allocation by channel and product performance
- Improved retention strategy through RFM segmentation
- Better inventory and campaign planning with baseline sales forecast

## 8) How to Run

```bash
python src/generate_dataset.py
python src/analysis.py
```

Generated analytics artifacts will appear in the `outputs/` folder.
