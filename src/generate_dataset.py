"""Generate synthetic e-commerce datasets for analytics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Config:
    seed: int = 42
    n_customers: int = 500
    n_products: int = 60
    n_orders: int = 4000


def build_customers(rng: np.random.Generator, n_customers: int) -> pd.DataFrame:
    customer_ids = np.arange(10001, 10001 + n_customers)
    segments = rng.choice(
        ["New", "Returning", "Loyal"],
        size=n_customers,
        p=[0.35, 0.45, 0.20],
    )
    countries = rng.choice(
        ["USA", "Canada", "UK", "Germany", "India"],
        size=n_customers,
        p=[0.50, 0.10, 0.12, 0.10, 0.18],
    )
    signup_dates = pd.to_datetime("2024-01-01") + pd.to_timedelta(
        rng.integers(0, 730, size=n_customers), unit="D"
    )

    return pd.DataFrame(
        {
            "customer_id": customer_ids,
            "customer_name": [f"Customer_{cid}" for cid in customer_ids],
            "segment_label": segments,
            "country": countries,
            "signup_date": signup_dates,
        }
    )


def build_products(rng: np.random.Generator, n_products: int) -> pd.DataFrame:
    categories = ["Electronics", "Fashion", "Home", "Beauty", "Sports"]
    category_choices = rng.choice(categories, size=n_products, p=[0.30, 0.25, 0.20, 0.12, 0.13])

    base_price = rng.uniform(8, 450, size=n_products).round(2)
    cost = (base_price * rng.uniform(0.45, 0.8, size=n_products)).round(2)

    product_ids = np.arange(2001, 2001 + n_products)
    return pd.DataFrame(
        {
            "product_id": product_ids,
            "product_name": [f"Product_{pid}" for pid in product_ids],
            "category": category_choices,
            "unit_cost": cost,
            "unit_price": base_price,
        }
    )


def build_sales(
    rng: np.random.Generator,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    n_orders: int,
) -> pd.DataFrame:
    order_ids = np.arange(900001, 900001 + n_orders)
    customer_ids = rng.choice(customers["customer_id"], size=n_orders, replace=True)
    product_ids = rng.choice(products["product_id"], size=n_orders, replace=True)

    order_dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(
        rng.integers(0, 450, size=n_orders), unit="D"
    )

    qty = rng.integers(1, 6, size=n_orders)

    price_lookup = products.set_index("product_id")["unit_price"]
    unit_price = product_ids.astype(float)
    for idx, pid in enumerate(product_ids):
        unit_price[idx] = price_lookup.loc[pid]

    discount_pct = rng.choice([0.0, 0.05, 0.1, 0.15, 0.2], size=n_orders, p=[0.45, 0.22, 0.18, 0.10, 0.05])
    gross_sales = unit_price * qty
    net_sales = gross_sales * (1 - discount_pct)

    order_status = rng.choice(
        ["Completed", "Cancelled", "Returned"],
        size=n_orders,
        p=[0.87, 0.08, 0.05],
    )
    completed_flag = (order_status == "Completed").astype(int)

    traffic_source = rng.choice(
        ["Organic", "Paid", "Email", "Direct", "Referral"],
        size=n_orders,
        p=[0.28, 0.24, 0.18, 0.20, 0.10],
    )

    return pd.DataFrame(
        {
            "order_id": order_ids,
            "order_date": order_dates,
            "customer_id": customer_ids,
            "product_id": product_ids,
            "quantity": qty,
            "unit_price": unit_price.round(2),
            "discount_pct": discount_pct,
            "gross_sales": gross_sales.round(2),
            "net_sales": net_sales.round(2),
            "order_status": order_status,
            "completed_order": completed_flag,
            "traffic_source": traffic_source,
        }
    )


def main() -> None:
    cfg = Config()
    rng = np.random.default_rng(cfg.seed)

    customers = build_customers(rng, cfg.n_customers)
    products = build_products(rng, cfg.n_products)
    sales = build_sales(rng, customers, products, cfg.n_orders)

    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)

    customers.to_csv(out_dir / "customers.csv", index=False)
    products.to_csv(out_dir / "products.csv", index=False)
    sales.to_csv(out_dir / "sales.csv", index=False)

    print("Generated data/customers.csv, data/products.csv, data/sales.csv")


if __name__ == "__main__":
    main()
