from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data" / "sources"
WEEK1 = ROOT / "data" / "retail_orders_week1.csv"
OUT = ROOT / "outputs"

ORDER_COLUMNS = [
    "order_id", "order_date", "customer_id", "channel", "category",
    "item_price", "quantity", "discount_pct", "order_value", "payment_method",
    "delivery_days", "customer_prior_orders", "returned",
]

CRM_COLUMNS = ["customer_id", "customer_region", "customer_tenure_days", "marketing_opt_in"]

JOINED_COLUMNS = [
    "order_id", "order_date", "customer_id", "channel", "category",
    "item_price", "quantity", "discount_pct", "order_value", "payment_method",
    "delivery_days", "customer_region", "customer_tenure_days",
    "customer_prior_orders", "marketing_opt_in", "returned",
]

PHONE_CATEGORY = {
    "Apparel": "apparel",
    "Electronics": "electronics",
    "Footwear": "footwear",
    "Health & Beauty": "beauty",
    "Home & Garden": "home",
    "Sports/Outdoor": "sports",
}

PHONE_PAYMENT = {
    "CARD": "card",
    "BNPL": "bnpl",
    "PAYPAL": "paypal",
    "GIFT_VOUCHER": "voucher",
}

REGION = {
    "london": "London",
    "south": "South",
    "midlands": "Midlands",
    "north": "North",
    "scotland": "Scotland",
    "wales": "Wales",
    "ni": "NI",
}

class RowCountError(AssertionError):
    pass
    
def expect(df, n, what):
    if len(df) != n:
        raise RowCountError(f"{what}: expected {n}, got {len(df)}")
    return df

def read_web():
    df = expect(pd.read_csv(SOURCES / "web_orders_2025.csv"), 1_900, "web file")
    out = pd.DataFrame({
        "order_id": df["Order ID"],
        "order_date": pd.to_datetime(df["Order Date"], format="%d/%m/%Y"),
        "customer_id": df["Customer ID"],
        "channel": "web",
        "category": df["Item Category"].str.strip(),
        "item_price": df["Unit Price (GBP)"],
        "quantity": df["Qty"],
        "discount_pct": df["Discount %"],
        "order_value": df["Order Total (GBP)"],
        "payment_method": df["Payment"].str.strip(),
        "delivery_days": df["Delivery (days)"],
        "customer_prior_orders": df["Prior Orders"],
        "returned": (df["Returned"] == "Y").astype(int),
    })
    return expect(out[ORDER_COLUMNS], 1_900, "web read")

def read_phone():
    raw = json.loads((SOURCES / "phone_orders_2025.json").read_text(encoding="utf-8"))
    calls = expect(pd.json_normalize(raw["calls"]), 96, "phone file")
    out = pd.DataFrame({
        "order_id": calls["order.ref"],
        "order_date": (pd.to_datetime(calls["logged_at"], utc=True)
                         .dt.tz_localize(None)
                         .dt.normalize()),
        "customer_id": calls["customer.crm_id"],
        "channel": "phone",
        "category": calls["order.line.category"].str.strip()
                         .map(lambda c: PHONE_CATEGORY[c]),
        "item_price": calls["order.line.unit_price_pence"] / 100,
        "quantity": calls["order.line.qty"].map(int),
        "discount_pct": calls["order.discount_percent"],
        "order_value": calls["order.total_pence"] / 100,
        "payment_method": calls["order.tender"].str.strip()
                         .map(lambda p: PHONE_PAYMENT[p]),
        "delivery_days": calls["order.delivery_days"],
        "customer_prior_orders": calls["customer.prior_orders"],
        "returned": calls["order.returned"].astype(int),
    })
    return expect(out[ORDER_COLUMNS], 96, "phone read")

def read_crm():
    df = expect(pd.read_excel(SOURCES / "crm_customers.xlsx", skiprows=2), 1_088, "crm file")
    opt_in = df["Marketing Opt-In"].str.strip()
    out = pd.DataFrame({
        "customer_id": df["Customer ID"],
        "customer_region": df["Region"].str.strip().str.lower()
                                .map(lambda r: REGION[r]),
        "customer_tenure_days": df["Tenure (days)"],
        "marketing_opt_in": opt_in.map({"Yes": True, "No": False}),
    })
    assert out["marketing_opt_in"].isna().sum() == opt_in.isna().sum(), "unexpected opt-in value"
    return expect(out[CRM_COLUMNS], 1_088, "crm read")

def compare_with_week1(as_run):
    week1 = pd.read_csv(WEEK1, parse_dates=["order_date"])
    a = as_run.sort_values("order_id", kind="stable").reset_index(drop=True)
    b = week1.sort_values("order_id", kind="stable").reset_index(drop=True)
    shared = [c for c in b.columns if c in a.columns]
    differing = {}
    for col in shared:
        x, y = a[col], b[col]
        if pd.api.types.is_float_dtype(x) or pd.api.types.is_float_dtype(y):
            same = np.isclose(x.astype(float), y.astype(float), equal_nan=True)
        else:
            same = (x == y) | (x.isna() & y.isna())
        n = int((~np.asarray(same)).sum())
        if n:
            differing[col] = n
    return {"columns_compared": len(shared),
            "columns_matching": len(shared) - len(differing),
            "differing": differing}

def main():
    web, phone, crm = read_web(), read_phone(), read_crm()
    assert list(web.columns) == list(phone.columns), "web and phone columns differ"
    orders = expect(pd.concat([web, phone], ignore_index=True), 1_996, "web plus phone")

    n_customers = crm["customer_id"].nunique()
    twice = crm.loc[crm["customer_id"].duplicated(), "customer_id"]
    n_affected = int(orders["customer_id"].isin(twice).sum())

    one_each = expect(crm[~crm["customer_id"].isin(twice)],
                      1_034, "crm without the 27 duplicated customers")
    joined = expect(orders.merge(one_each, on="customer_id", how="left",
                                 validate="many_to_one"), 1_996, "join")

    as_run = expect(orders.merge(crm, on="customer_id", how="left"), 2_030,
                    "join as operations ran it")
    comparison = compare_with_week1(as_run)
    
    OUT.mkdir(exist_ok=True)
    joined.to_csv(OUT / "orders_joined.csv", index=False)
    report = {
        "web": {"rows": len(web)},
        "phone": {"rows": len(phone)},
        "orders": {"rows": len(orders)},
        "crm": {"rows": len(crm), "customers": int(n_customers),
                "customers_twice": int(len(twice)),
                "orders_of_customers_twice": n_affected,
                "decision": "kept neither CRM row for customers with two; their orders have blank CRM fields",},
        "join": {"rows": len(joined)},
        "week1_comparison": comparison,
    }
    (OUT / "ingest_report.json").write_text(json.dumps(report, sort_keys=True, indent=2))

    print(f"web {len(web)} phone {len(phone)} orders {len(orders)}")
    print(f"crm {len(crm)} rows, {n_customers} customers, {len(twice)} twice")
    print(f"orders belonging to those {len(twice)}: {n_affected}")
    print(f"join {len(joined)}")
    print(f"join {len(joined)} as operations ran it {len(as_run)}")
    print(f"against Week 1: {comparison['columns_matching']} of "
          f"{comparison['columns_compared']} columns match, "
          f"differing {comparison['differing']}")

if __name__ == "__main__":
    main()