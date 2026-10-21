from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"

rules = []  # (dataset, ids, name, rows that break it, reason)


def rule(dataset, ids, name, broken, reason):
    rules.append((dataset, ids, name, broken.fillna(False), reason))


def order_rules(o):
    ids = o["order_id"]
    rule("orders", ids, "quantity >= 1", o.quantity < 1,
         "An order for nothing is not an order.")
    rule("orders", ids, "item_price > 0", o.item_price <= 0,
         "The shop does not give stock away at a listed price of zero.")
    rule("orders", ids, "delivery 0 to 60 days",
         o.delivery_days.notna() & ~o.delivery_days.between(0, 60),
         "A delivery cannot arrive before it is sent or take two months.")
    rule("orders", ids, "order_value >= 0", o.order_value < 0,
         "A sale cannot have negative value; refunds are the returned flag.")
    expected = o.item_price * o.quantity * (1 - o.discount_pct / 100)
    rule("orders", ids, "value = price x qty x (1 - discount)",
         (o.order_value - expected).abs() >= 0.01,
         "order_value is derived from the other three, rounded to the penny.")


def penguin_rules(p):
    ids = p["studyName"] + "/" + p["Individual ID"]
    mass = p["Body Mass (g)"]
    rule("penguins", ids, "body mass 2500 to 6500 g",
         mass.notna() & ~mass.between(2500, 6500),
         "No adult of these three species weighs outside this range.")
    flip = p["Flipper Length (mm)"]
    rule("penguins", ids, "flipper 160 to 240 mm",
         flip.notna() & ~flip.between(160, 240),
         "Outside this an adult flipper is a measuring or typing error.")
    sex = p["Sex"]
    rule("penguins", ids, "sex is MALE, FEMALE or blank",
         sex.notna() & ~sex.isin(["MALE", "FEMALE"]),
         "Sex came from a blood test with two possible results.")
    year = pd.to_datetime(p["Date Egg"]).dt.year
    first = 2000 + p["studyName"].str[3:5].astype(int)
    in_season = (year == first) | (year == first + 1)
    rule("penguins", ids, "egg date inside the study season",
         year.notna() & ~in_season,
         "PAL0708 is the 2007-08 season, so its eggs are dated 2007 or 2008.")


def main():
    order_rules(pd.read_csv(DATA / "orders_joined.csv"))
    penguin_rules(pd.read_csv(DATA / "penguins_raw.csv"))
    rows = [pd.DataFrame({"dataset": d, "row_id": ids[broken].values,
                          "rule": name, "reason": reason})
            for d, ids, name, broken, reason in rules]
    violations = (pd.concat(rows, ignore_index=True)
                  .sort_values(["dataset", "rule", "row_id"], kind="stable"))
    OUT.mkdir(exist_ok=True)
    violations.to_csv(OUT / "violations.csv", index=False)
    for d, ids, name, broken, reason in rules:
        print(f"{d:9} {name:40} {int(broken.sum())}")


if __name__ == "__main__":
    main()