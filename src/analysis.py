"""Run data cleaning, EDA, KPI generation, customer segmentation, and forecasting."""

from __future__ import annotations

from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd


DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    customers = pd.read_csv(DATA_DIR / "customers.csv", parse_dates=["signup_date"])
    products = pd.read_csv(DATA_DIR / "products.csv")
    sales = pd.read_csv(DATA_DIR / "sales.csv", parse_dates=["order_date"])
    return customers, products, sales


def clean_sales_data(sales: pd.DataFrame) -> pd.DataFrame:
    df = sales.copy()
    df = df.drop_duplicates(subset=["order_id"])

    # Handle improbable negative values defensively.
    for col in ["quantity", "unit_price", "discount_pct", "net_sales"]:
        df[col] = df[col].clip(lower=0)

    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    return df


def build_fact_table(
    sales: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    fact = (
        sales.merge(customers[["customer_id", "country", "segment_label"]], on="customer_id", how="left")
        .merge(products[["product_id", "product_name", "category", "unit_cost"]], on="product_id", how="left")
    )
    fact["profit"] = (fact["net_sales"] - (fact["unit_cost"] * fact["quantity"]))
    return fact


def calculate_kpis(fact: pd.DataFrame) -> pd.DataFrame:
    total_revenue = fact.loc[fact["order_status"] == "Completed", "net_sales"].sum()
    conversion_rate = fact["completed_order"].mean()
    aov = fact.loc[fact["order_status"] == "Completed", "net_sales"].mean()

    top_products = (
        fact.loc[fact["order_status"] == "Completed"]
        .groupby("product_name", as_index=False)["net_sales"]
        .sum()
        .sort_values("net_sales", ascending=False)
        .head(10)
    )

    kpi_summary = pd.DataFrame(
        {
            "metric": ["total_revenue", "conversion_rate", "average_order_value"],
            "value": [round(total_revenue, 2), round(conversion_rate, 4), round(aov, 2)],
        }
    )

    OUTPUT_DIR.mkdir(exist_ok=True)
    top_products.to_csv(OUTPUT_DIR / "top_products.csv", index=False)
    kpi_summary.to_csv(OUTPUT_DIR / "kpi_summary.csv", index=False)
    return kpi_summary


def customer_segmentation(fact: pd.DataFrame) -> pd.DataFrame:
    snapshot_date = fact["order_date"].max() + pd.Timedelta(days=1)

    rfm = (
        fact.loc[fact["order_status"] == "Completed"]
        .groupby("customer_id")
        .agg(
            recency=("order_date", lambda d: (snapshot_date - d.max()).days),
            frequency=("order_id", "nunique"),
            monetary=("net_sales", "sum"),
        )
        .reset_index()
    )

    rfm["r_score"] = pd.qcut(rfm["recency"], q=4, labels=[4, 3, 2, 1], duplicates="drop").astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"], q=4, labels=[1, 2, 3, 4], duplicates="drop").astype(int)

    rfm["rfm_score"] = rfm[["r_score", "f_score", "m_score"]].sum(axis=1)

    rfm["segment"] = np.select(
        [
            rfm["rfm_score"] >= 10,
            rfm["rfm_score"].between(7, 9),
            rfm["rfm_score"] <= 6,
        ],
        ["High Value", "Medium Value", "Low Value"],
        default="Low Value",
    )

    rfm.to_csv(OUTPUT_DIR / "customer_segments.csv", index=False)
    return rfm


def sales_forecast(fact: pd.DataFrame, periods: int = 3) -> pd.DataFrame:
    monthly_sales = (
        fact.loc[fact["order_status"] == "Completed"]
        .groupby("order_month", as_index=False)["net_sales"]
        .sum()
        .sort_values("order_month")
    )

    monthly_sales["month_idx"] = np.arange(len(monthly_sales))
    coeffs = np.polyfit(monthly_sales["month_idx"], monthly_sales["net_sales"], deg=1)

    forecast_idx = np.arange(len(monthly_sales), len(monthly_sales) + periods)
    forecast_values = coeffs[0] * forecast_idx + coeffs[1]

    last_month = pd.Period(monthly_sales["order_month"].iloc[-1], freq="M")
    forecast_months = [(last_month + i).strftime("%Y-%m") for i in range(1, periods + 1)]

    forecast_df = pd.DataFrame({"order_month": forecast_months, "forecast_net_sales": forecast_values.round(2)})
    forecast_df.to_csv(OUTPUT_DIR / "sales_forecast.csv", index=False)
    monthly_sales.to_csv(OUTPUT_DIR / "monthly_sales.csv", index=False)
    return forecast_df


def run_sql_analysis(fact: pd.DataFrame) -> dict[str, pd.DataFrame]:
    conn = sqlite3.connect(":memory:")
    fact.to_sql("fact_sales", conn, index=False, if_exists="replace")

    queries = {
        "revenue_by_category": """
            SELECT category, ROUND(SUM(net_sales), 2) AS total_revenue
            FROM fact_sales
            WHERE order_status = 'Completed'
            GROUP BY category
            ORDER BY total_revenue DESC;
        """,
        "conversion_by_source": """
            SELECT traffic_source,
                   ROUND(AVG(completed_order) * 100, 2) AS conversion_rate_pct
            FROM fact_sales
            GROUP BY traffic_source
            ORDER BY conversion_rate_pct DESC;
        """,
        "top_customers": """
            SELECT customer_id, ROUND(SUM(net_sales), 2) AS customer_revenue
            FROM fact_sales
            WHERE order_status = 'Completed'
            GROUP BY customer_id
            ORDER BY customer_revenue DESC
            LIMIT 10;
        """,
    }

    output_tables: dict[str, pd.DataFrame] = {}
    for name, query in queries.items():
        output_tables[name] = pd.read_sql_query(query, conn)
        output_tables[name].to_csv(OUTPUT_DIR / f"{name}.csv", index=False)

    conn.close()
    return output_tables


def main() -> None:
    customers, products, sales = load_data()
    sales_clean = clean_sales_data(sales)
    fact = build_fact_table(sales_clean, customers, products)

    kpis = calculate_kpis(fact)
    segments = customer_segmentation(fact)
    forecast = sales_forecast(fact, periods=3)
    _sql_outputs = run_sql_analysis(fact)

    print("KPI Summary")
    print(kpis)
    print("\nSegment counts")
    print(segments["segment"].value_counts())
    print("\nForecast")
    print(forecast)


if __name__ == "__main__":
    main()
