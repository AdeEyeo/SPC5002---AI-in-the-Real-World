## 1. Zero quantities, 4 orders

### What I did
Set the quantity to missing, flagged it in `quantity_missing`, and wrote the quantity the order value implies into the ledger, not into the column. All four orders stay.

### Why
An order for nothing is not an order, so zero is wrong. But a quantity recovered from the identity passes the identity by construction and assumes the price and value are right, so no check could ever catch it if it were wrong. The rest of each order is sound, so dropping it would throw away three good fields to get rid of one bad one.

### The alternative
Drop the four orders (`drop_impossible_quantities`), or write the implied quantity into the column.

### What would change my mind
The order system's owner confirming that `item_price`, `discount_pct` and `order_value` are stored as entered, and only the quantity was lost in export. Then the implied quantity would be a repair rather than a guess, and I would write it in, with the flag kept beside it.

## 2. Zero prices, 4 orders

### What I did
Set the price to missing, flagged it in `item_price_missing`, and wrote the price the order value implies into the ledger, not into the column. All four orders stay.

### Why
The shop does not list stock at a price of nothing, so zero is wrong. But a price recovered from the identity passes the identity by construction and assumes the quantity and value are right, so no check could ever catch it if it were wrong. The rest of each order is sound. The leak lab leaves these four out, because `item_price` is one of its features and a model cannot read a blank.

### The alternative
Drop the four orders (`drop_non_positive_prices`), or write the implied price into the column.

### What would change my mind
The order system's owner confirming that `order_value` is calculated by the system from price, quantity and discount, and the price was lost afterwards. Then the implied price would be a repair rather than a guess, and I would write it in, with the flag kept beside it.

## 3. Negative order values, 4 orders

### What I did
Corrected the sign on the 3 orders that were not returned, flagged in `order_value_sign_corrected`. Flagged ORD-100234, which was returned, in `order_value_ambiguous` and left its value as it was.

### Why
Refunds are recorded by the `returned` flag, not by the value. All four magnitudes match price × quantity × (1 − discount) to the penny, so a sign error fits all four, and the corrected value is checked by three other columns. A refund could explain only the returned one, so that one alone stays undecided.

### The alternative
Drop all four (`drop_negative_order_values`), or correct all four.

### What would change my mind
The order system's owner saying that refunds are sometimes stored as negative values. Then ORD-100234 would be a refund and should be dropped from the orders, and I would ask whether any of the other three were partial refunds too. Learning instead that `order_value` is always calculated would make all four sign errors, and I would correct ORD-100234 as well.

## 4. The −999 delivery times, 5 orders

### What I did
Turned −999 into a genuine blank and flagged it in `delivery_days_missing`, keeping the orders. See `notebooks/week04_sentinel.ipynb`.

### Why
−999 is a placeholder, not a duration. With it in, the mean delivery time is 0.981 days and the sd 50.166; without it, 3.492 and 2.033. Imputing would assert a delivery time nobody measured, and unknown is not average. A blank, unlike −999, cannot be averaged in by accident, and the rest of each order is sound.

### The alternative
Drop the five (`drop_sentinel_delivery_times`), or impute.

### What would change my mind
The delivery system's owner saying what −999 meant. If it means "not recorded", the blanks stand. If it means the order was never delivered or was cancelled, these are a different kind of order, and I would drop them, or model them separately, rather than treat them as ordinary deliveries with a gap.

## 5. The 77 blank opt-ins

### What I did
Nothing, deliberately (`leave_marketing_opt_in_missing`).

### Why
43 are blank in the CRM itself, and 34 come from my join decision to keep neither row for the 27 duplicated customers. Consent has to be recorded, not assumed, so for marketing a blank means not opted in, and for analysis it stays missing and is never filled.

### The alternative
Fill them with the commonest value, or restore the Week 1 values.

### What would change my mind
Two things, one for each group. For the 43: the source of the Week 1 values being found and shown to be a dated consent record, in which case I would restore them with that source named. For the 34: the CRM owner saying which of each duplicated pair is right, in which case those customers' values come back from the CRM itself.

## The imputation I did not do

The column I left alone is `marketing_opt_in`, and what somebody would later measure with it is consent: how many customers agreed to be marketed to. As recorded, 1,083 of the 1,919 orders with a value are opted in, a share of 0.564, with 77 unknown. Filling the 77 blanks with the commonest value, True, raises that to 1,160 of 1,996, a share of 0.581, and turns 48 customers whose answer is unknown into customers who said yes. The share moves by less than two points, which is why the fill looks harmless, but the cost is not in the share. All 48 would be counted as having consented to marketing, and a compliance audit asking for evidence of their consent would find none, because the fill leaves nothing behind to show which values were measured and which were guessed. As with the penguins, no test catches it: the column has no blanks, every value is True or False, and the error is only visible to somebody who knows the 77 were blank.

## Where a fit belongs: the two measurements

The leak lab models 1,992 orders. The 4 with a blank price are left out, counted and printed, rather than adding an imputer that would be a third thing fitted somewhere. Each measurement is paired over 40 seeds: both arms of a seed share one split, so the spread reported is the spread of the *difference*.

### The scaler
Fitting the scaler on every order before the split made no measurable difference at any training size.

| Training rows | Fitted on train | Fitted on all | Mean gap | sd of gap |
|---|---|---|---|---|
| 40 | 0.5454 | 0.5454 | +0.00002 | 0.00219 |
| 80 | 0.5455 | 0.5456 | +0.00006 | 0.00091 |
| 200 | 0.5774 | 0.5775 | +0.00003 | 0.00025 |
| 500 | 0.5994 | 0.5995 | +0.00012 | 0.00021 |
| 1,000 | 0.6106 | 0.6106 | +0.00000 | 0.00026 |
| 1,494 | 0.6191 | 0.6191 | −0.00000 | 0.00018 |

Every mean gap is smaller than its own standard deviation, so none of them can be told apart from zero. The largest, +0.00012 at 500 rows, is about half its sd. The spread is largest at 40 training rows, 0.00219, most likely because the model's default penalty treats a differently scaled input differently when there is little data; from 200 rows up it is a few ten-thousandths. The two middle columns are means over the 40 seeds; their own spreads are not reported, because the quantity being measured is the paired gap, and it has its sd beside it.

### The outliers
Deciding which orders are more than three standard deviations from the mean on every order, and dropping them from both sides of the split, raised the score in all 40 seeds.

| | ROC-AUC | sd | Test orders scored |
|---|---|---|---|
| Honest | 0.6196 | 0.0225 | 498 |
| Flattering | 0.6264 | 0.0239 | 486.8 on average |
| Gap | +0.0068 | 0.0032 | flattering higher in 40 of 40 seeds |
| Honest model, flattering arm's test set | 0.6264 | 0.0238 | 486.8 on average |
| Part of the gap from the test set | +0.0068 | 0.0033 | |

The gap is about twice its sd. It is also far smaller than the sd of either arm on its own, 0.0225 and 0.0239, which is why the comparison had to be paired: two unpaired runs would have buried a gap this size in the noise of the split. Given the cleaned test set, the honest model scores 0.6264, the same as the flattering arm to four decimal places. Of the +0.00684 gap, +0.00679 (sd 0.00331) comes from the test set, which leaves +0.00005 for the model, far inside any spread here.

### Why one gives nothing and the other does not
Fitting the scaler on every order shifts and rescales the inputs, which the logistic regression absorbs into its intercept and coefficients, and ROC-AUC reads only the order of the scores, so the leak barely reaches the number: no gap was larger than its own sd, and the only visible spread, 0.00219 at 40 training rows, most likely comes from the model's default penalty, which treats scale differently when there is little data.

Removing outliers before the split took about 11 orders out of each test set on average (498 against 486.8), and the model was not what improved: given that same cleaned test set, the honest model scores 0.6264 (sd 0.0238), the same as the flattering arm to four decimal places, so +0.00679 of the +0.00684 gap came from leaving out orders the model ranks badly, and the higher score describes an easier population, not a better model.

### Against the lecture's numbers
The shape matches the lecture: a scaler gap near zero and an outlier gap above zero in nearly every seed. The numbers differ a little. For the scaler at 40 training rows, the lecture reported +0.00068 (sd 0.00315) and mine is +0.00002 (sd 0.00219), both well inside their sd. For the outliers, the lecture reported a gap of +0.0063, sd 0.0037, higher in 39 of 40, on 1,484 training rows. Mine is +0.0068, sd 0.0032, higher in 40 of 40, on 1,494. Three reasons might explain it. My cleaning kept the faulty orders, so 13 more reach the model. The returned order with a negative value, ORD-100234, still sits in the mean and sd that the 3-sd rule is measured against. And my `split` and `score` may not match Thursday's notebook line for line. A difference of 0.0005 is well inside one sd of either gap, so I would not claim the two results differ at all.