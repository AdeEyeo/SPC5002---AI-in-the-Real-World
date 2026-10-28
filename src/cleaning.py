"""
My audit (docs/milestone1_audit.md, part 3) proposed repairing or flagging the 17
faulty orders rather than removing them, so the steps clean() calls keep every
order and record 0 removed. The four drops from the slides are kept below as the
rejected alternative, each with its argument, and are not called.
"""
from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
JOINED = ROOT / "data" / "orders_joined.csv"
OUT = ROOT / "outputs"


class Ledger:
    """One line per cleaning step, so every order that leaves has a reason."""
    def __init__(self):
        self.steps = []
    def record(self, step, before, after, reason):
        self.steps.append({"step": step, "before": before, "after": after,
                           "removed": before - after, "reason": reason})
    def total_removed(self):
        return sum(s["removed"] for s in self.steps)
    def to_frame(self):
        return pd.DataFrame(self.steps,
                            columns=["step", "before", "after", "removed", "reason"])


def drop_impossible_quantities(df, led):
    """Remove orders for fewer than one item.

    An order row exists because something was bought. A quantity of zero is not a
    small order, it is a row that contradicts its own reason for existing, and
    there is no value that would make it right. Four rows.
    
    The rejected alternative to mark_impossible_quantities. Not called.
    """
    out = df[df["quantity"] >= 1]
    led.record("drop_impossible_quantities", len(df), len(out),
               "an order of zero items contradicts the existence of the row")
    return out


def drop_non_positive_prices(df, led):
    """Remove orders whose item price is zero or below.

    This shop records a free item as a 100 per cent discount, not as a zero price,
    so a price of zero or less is a recording error and not a gift. There is no
    source to recover the true price from. Four rows.
    
    The rejected alternative to mark_non_positive_prices. Not called.
    """
    out = df[df["item_price"] > 0]
    led.record("drop_non_positive_prices", len(df), len(out),
               "this shop records a free item as a discount, not a zero price")
    return out


def drop_negative_order_values(df, led):
    """Remove orders whose total order value is negative.

    A refund is kept as a separate record in this business, so an order with a
    negative total is not a refund, it is an error in the order row. Four rows.
    
    The rejected alternative to correct_negative_order_values. Not called.
    """
    out = df[df["order_value"] >= 0]
    led.record("drop_negative_order_values", len(df), len(out),
               "a refund is a separate record, so a negative total is an error")
    return out


def drop_sentinel_delivery_times(df, led):
    """Remove the orders whose delivery_days is -999.

    -999 means not recorded. Keeping these rows and imputing would assert
    a delivery time nobody measured, on orders we already know were
    mishandled by whatever wrote -999. Unknown is not the same as average.
    
    The rejected alternative to mark_sentinel_delivery_times. Not called.
    """
    out = df[df["delivery_days"] != -999]
    led.record("drop_sentinel_delivery_times", len(df), len(out),
               "-999 means not recorded, and unknown is not average")
    return out


def mark_sentinel_delivery_times(df, led):
    """The other defensible choice. Keep the orders, make the absence visible.

    Turns -999 into a genuine blank and keeps a flag, so nothing downstream can
    average it away. It removes nothing, so its ledger line says 0 removed and
    its reason says what changed. Use it in place of the drop in clean if you
    would rather keep the orders than the column. Not both.
    
    Called in clean: my audit proposed treating the five as missing and keeping
    the rows until whoever owns the delivery system confirms what -999 meant, and
    a genuine blank cannot be averaged in by accident the way -999 can.
    """
    out = df.copy()
    sentinel = out["delivery_days"] == -999
    out["delivery_days"] = out["delivery_days"].astype(float).where(~sentinel)
    out["delivery_days_missing"] = out["delivery_days"].isna()
    led.record("mark_sentinel_delivery_times", len(df), len(out),
               f"kept and flagged {int(sentinel.sum())} orders, "
               "where -999 means not recorded")
    return out


def _carry_flag(df, column, new):
    """Keep a flag set by an earlier pass, so cleaning a cleaned table changes nothing."""
    if column in df.columns:
        return df[column].fillna(False).astype(bool) | new
    return new


def mark_impossible_quantities(df, led):
    """Set a quantity of zero to missing, keep the order and flag it. Called in clean.

    An order for nothing is not an order, so zero is wrong, but the true quantity is
    not known. Working back from the order value gives a plausible number, yet a
    quantity recovered from the identity passes the identity by construction and
    assumes the price and value are right, so nothing would check it. The implied
    quantities go into the ledger, not into the column. Chosen over
    drop_impossible_quantities because the rest of each order is sound.
    """
    out = df.copy()
    bad = out["quantity"] == 0
    implied = (out.loc[bad, "order_value"]
               / (out.loc[bad, "item_price"] * (1 - out.loc[bad, "discount_pct"] / 100)))
    out["quantity"] = out["quantity"].astype(float).where(~bad)
    out["quantity_missing"] = _carry_flag(df, "quantity_missing", bad)
    detail = ", ".join(f"{o} implies {q:.0f}"
                       for o, q in zip(out.loc[bad, "order_id"], implied))
    led.record("mark_impossible_quantities", len(df), len(out),
               f"set {int(bad.sum())} zero quantities to missing and flagged them"
               + (f"; {detail}" if detail else ""))
    return out


def mark_non_positive_prices(df, led):
    """Set a price of zero or less to missing, keep the order and flag it. Called in clean.

    The shop does not list stock at a price of nothing, so zero is wrong. The order
    value implies a price, but for the same reason as the quantities that guess
    cannot be checked, so it is recorded in the ledger and not written in. Chosen
    over drop_non_positive_prices because the rest of each order is sound.
    """
    out = df.copy()
    bad = out["item_price"] <= 0
    implied = (out.loc[bad, "order_value"]
               / (out.loc[bad, "quantity"] * (1 - out.loc[bad, "discount_pct"] / 100)))
    out["item_price"] = out["item_price"].where(~bad)
    out["item_price_missing"] = _carry_flag(df, "item_price_missing", bad)
    detail = ", ".join(f"{o} implies {p:.2f}"
                       for o, p in zip(out.loc[bad, "order_id"], implied))
    led.record("mark_non_positive_prices", len(df), len(out),
               f"set {int(bad.sum())} non-positive prices to missing and flagged them"
               + (f"; {detail}" if detail else ""))
    return out


def correct_negative_order_values(df, led):
    """Correct the sign of a negative order value, unless the order was returned. Called in clean.

    Refunds are recorded by the returned flag, not by the value. In all four negative
    orders the magnitude matches price x quantity x (1 - discount) to the penny, so a
    sign error fits all four, and the value is the one field the data supports
    independently. A refund could explain an order that was returned, so that one is
    left as it is and flagged as ambiguous until the order system's owner says which
    fields it calculates. Chosen over drop_negative_order_values because the repair
    is checked by three other columns.
    """
    out = df.copy()
    negative = out["order_value"] < 0
    flip = negative & ~out["returned"].astype(bool)
    ambiguous = negative & out["returned"].astype(bool)
    out["order_value"] = out["order_value"].where(~flip, -out["order_value"])
    out["order_value_sign_corrected"] = _carry_flag(df, "order_value_sign_corrected", flip)
    out["order_value_ambiguous"] = _carry_flag(df, "order_value_ambiguous", ambiguous)
    led.record("correct_negative_order_values", len(df), len(out),
               f"corrected the sign on {int(flip.sum())} orders; flagged "
               f"{int(ambiguous.sum())} returned order(s) as ambiguous and left the value")
    return out


def leave_marketing_opt_in_missing(df):
    """Do nothing to the blank opt-in values, deliberately.

    The CRM never recorded these answers and no source supports any value
    for them, so filling them would invent consent nobody gave. A blank that
    is visible can be handled later, and a filled one cannot be unfilled.
    In this table there are 77: 43 blank in the CRM itself, and 34 from the 27
    duplicated customers whose CRM rows I kept neither of (docs/join_decision.md).
    For marketing, unknown means not opted in. For analysis it stays missing.
    """
    return df


def clean(df):
    """Apply every decision, in order, and return the frame with its ledger.

    The order matters only for the ledger. The four faults are on disjoint sets of
    orders, 4 + 4 + 4 + 5 = 17 in the audit, so the result is the same whichever
    order they run in. Every step repairs or flags, so all 1,996 orders stay and
    each line of the ledger says 0 removed and what it changed. The slides' four
    drops are above, as the rejected alternative.
    """
    led = Ledger()
    out = df
    for step in (mark_impossible_quantities,
                 mark_non_positive_prices,
                 correct_negative_order_values,
                 mark_sentinel_delivery_times):
        out = step(out, led)
    out = leave_marketing_opt_in_missing(out)
    return out.reset_index(drop=True), led


def main():
    df = pd.read_csv(JOINED)
    out, led = clean(df)

    print(led.to_frame()[["step", "before", "after", "removed"]].to_string(index=False))
    assert len(df) - len(out) == led.total_removed(), "a row left without a reason"

    print(f"\n{len(df)} -> {len(out)}   {led.total_removed()} rows removed, all named")
    print(f"base rate {df.returned.mean():.4f} -> {out.returned.mean():.4f}")

    OUT.mkdir(exist_ok=True)
    out.to_csv(OUT / "orders_clean.csv", index=False, lineterminator="\n")
    led.to_frame().to_csv(OUT / "cleaning_ledger.csv", index=False, lineterminator="\n")


if __name__ == "__main__":
    main()