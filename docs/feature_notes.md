## The moment of prediction

I am assuming the prediction is made at checkout, the moment the order is placed, because that is when the shop could still act on it (a size guide, a confirmation email, a different delivery option). A feature is only honest if its value was known at that moment. Where a feature would be honest under a later moment, I say so.

The table is my own cleaning from Week 4, which repairs or flags the 17 faulty orders instead of removing them, so all 1,996 orders are modelled, not the slides' 1,979. My scores are therefore not the slides' scores, and the shape is what I compare.

## The features, one section each

### item_price, quantity, discount_pct
What it is: the price of one item, how many, and the discount on the order. Why it might predict: expensive items and heavily discounted ones are plausibly bought on impulse or as a gamble on fit, and returned more. Known at checkout: yes. All three are on the basket before payment. My cleaning set 4 zero quantities and 4 non-positive prices to blank and flagged them. The median imputer inside `build_pipeline` fills them from the training folds only, so no fold sees a median learned from its own test rows.

### order_value
What it is: price × quantity × (1 − discount), the total of the order. Why it might predict: a bigger order has more that can go back. Known at checkout: yes. My cleaning corrected the sign on all four negative values, because each magnitude matches the other three columns to the penny. In Week 4 I had left the one returned order, ORD-100234, at −34.97, because a refund could explain it. That made the cleaning read the label: afterwards a negative `order_value` appeared only on a returned order, so the column carried the answer for that row, and the rule could not have been applied to a new order at checkout, which has no `returned` yet. I now correct it too, to +34.97. Even if −34.97 was a refund written after the return, +34.97 is what the order was worth when it was placed, which is the moment this model predicts at. The doubt stays on record in `order_value_ambiguous`, which is not a feature. `docs/cleaning_decisions.md`, section 3, is left as I submitted it in Week 4, as the record of the earlier decision. It still describes ORD-100234 as left negative, and its leak-lab numbers were measured before this change. This section and the docstring of `correct_negative_order_values` describe what the cleaning does now.

### customer_prior_orders
What it is: how many orders the customer had placed before this one. Why it might predict: regular customers know their sizes and the shop. Known at checkout: yes. It counts only earlier orders. It is the honest version of `orders_in_2025`, below.

### delivery_days
What it is: days from dispatch to delivery. Why it might predict: a late delivery is a reason to send something back. Known at checkout: no. The order has not been delivered when it is placed. At most an estimated delivery time is known. The column is honest only if the prediction is made at delivery, which is a different and later question. I keep it in this week's pipeline so my scores line up with the lab's, and I flag it as the first feature to remove or replace with the promised delivery time if the moment stays at checkout. My cleaning turned the five -999 values into genuine blanks with a flag, so the imputer fills them inside each fold and -999 is never averaged in.

### channel, category, payment_method
What they are: where the order was placed, what kind of product, and how it was paid for. Why they might predict: `category` was the strongest honest column in Week 1. Paying later (buy now pay later) plausibly makes returning cheaper. Known at checkout: yes, all three. Payment is chosen before the order is placed. Encoded one-hot, which claims the values are unrelated and puts no order on them. That claim is the right one here. The ordinal codes from Thursday's Task 1 would claim, for example, that beauty lies between apparel and electronics.

### customer_region
What it is: the customer's region, from the CRM. Why it might predict: delivery distance and local habits. Known at checkout: yes, as long as the CRM value is the address at the time of the order and not a later one. The CRM is a snapshot, so I cannot fully check this.

### customer_id (target encoded, Task C only)
What it is: who the customer is. In route 2 it becomes that customer's return rate, learned inside the pipeline. Why it might predict: some customers return more than others. Known at checkout: the identity yes, the rate only in part. In a random split the training folds include the same customer's later orders, so the rate uses returns that had not happened at checkout. Done properly, inside the pipeline, it is worth almost nothing here: 0.6223 against 0.6199 without it, a difference of 0.0024 against an sd of 0.034.

### The six date features
What they are: `day_of_week`, `month`, `day_of_month`, `is_weekend`, `week_of_year` and `days_since_2025`, from `order_date` alone. The day count starts from a fixed 1 January 2025, not the earliest date in the table, so an order's value never depends on which other orders are present. Why they might predict: weekend and seasonal buying, and a trend over the year. Known at checkout: yes, every one comes from the order's own date. Measured: 0.6120 (sd 0.0376) with them, against 0.6199 (sd 0.0347) without. The difference is −0.0079, smaller than the sd, so they add nothing I can measure, and if anything the score went down. Each extra column is another coefficient estimated from the same rows, so a feature worth nothing is not free. `build_pipeline` leaves them out by default.
 
### orders_in_2025 (written, rejected, never called)
What it is: the number of orders the customer placed in 2025. Known at checkout: no. It counts orders placed after this one. It is a leak of time, not of the label, so no test catches it: its correlation with `returned` is small, and it reads like a harmless count. It is kept in `src/features.py` with a docstring saying why, as the record that it was considered and rejected.
 
### Columns in the table that are not features
- `returned` is the answer.
- `order_id` identifies a row and predicts nothing. `export_seq` was the Week 1 leak and stays out (`docs/leakage_note.md`).
- `customer_tenure_days` is a CRM snapshot. If it was measured at the snapshot and not at the order date, it holds time from after the order. Left out until I know when it was taken.
- `marketing_opt_in` has 77 blanks I deliberately did not fill, and it says nothing obvious about returns. Left out.
- The cleaning flags (`quantity_missing`, `item_price_missing`, `order_value_sign_corrected`, `order_value_ambiguous`, `delivery_days_missing`) record what my cleaning did, not what the customer did. They are not features.

## Rows per level
 
From `outputs/encoding_lab.json`, orders divided by distinct values.
 
| Column | Distinct values | Orders per value |
|---|---|---|
| channel | 2 | 998.0 |
| payment_method | 4 | 499.0 |
| category | 6 | 332.7 |
| customer_region | 7 | 285.1 |
| customer_id | 907 | 2.2 |
 
The four ordinary categoricals have hundreds of orders per value, so a rate per value would be estimated well. With so few values, one-hot is cheap and makes the weaker claim, so I would one-hot them anyway. `customer_id` has about 2.2 orders per value, and for a customer with one order the "rate" is that order's label. I would not target encode anything with fewer than roughly 30 to 50 orders per value without cross-fitting and smoothing, and even then I would expect little from it, as route 2 shows. The habit that matters is printing this number before choosing the encoding, not after a suspiciously good score.

## The three routes, on my data
 
ROC-AUC, mean and sd over 5 folds repeated 5 times.
 
| Route | Random split | Grouped by customer |
|---|---|---|
| One-hot only, no customer rate | 0.6199 (sd 0.0347) | 0.6142 (sd 0.0296) |
| Customer target encoded inside the pipeline | 0.6223 (sd 0.0340) | 0.6145 (sd 0.0294) |
| Customer rate on every order, before the split | 0.9326 (sd 0.0102) | 0.9335 (sd 0.0149) |
 
The two honest routes score within one sd of each other under both splits, and grouping lowers each of them slightly (0.6199 to 0.6142, 0.6223 to 0.6145), also well inside the sd. The leaked route is about 0.31 above both, under both splits.
 
How close each version of the customer rate is to the order's own label:
 
| Version | Correlation with own label |
|---|---|
| Group mean on every order | 0.6880 |
| TargetEncoder, fit then transform | 0.6802 |
| TargetEncoder, fit_transform (cross-fitted) | 0.0630 |
 
### Why the grouped split did not rescue the leaked version
 
The leaked column was computed from every order's label before any split existed. So the answer was already written into each row when cross-validation began. For a customer with one order, the rate is that order's label, and for a customer with two it is half of it. Grouping by customer only decides which side of the split a customer's rows land on. Wherever they land, each row still carries its own label inside its feature, and the model reads it straight off the test rows. That is why the grouped score, 0.9335, is no lower than the random one, 0.9326, and both sit far above the honest 0.6199. A validation scheme can only protect against what happens after the split. The fix is to compute the rate where the split can reach it, inside the pipeline. There the score falls back to 0.6223, within one sd of no customer rate at all. The correlations show the same thing. Smoothing alone barely changes the leaked column (0.6880 to 0.6802). Cross-fitting, where no order contributes to its own value, drops it to 0.0630.