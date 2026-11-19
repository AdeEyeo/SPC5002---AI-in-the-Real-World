# Milestone 2, the preprocessing note

## 1. From three files to a feature matrix

### Ingestion
The orders come from three exports, each read by its own function in `src/ingest.py`, which checks the source's row count. The storefront's `web_orders_2025.csv` holds one order per row, 1,900 rows. Its dates are day first and are parsed with an explicit `%d/%m/%Y`, trailing spaces are stripped from the categories, `Returned` Y/N becomes 1/0, and `channel` is added as `web`. The call centre's `phone_orders_2025.json` holds one call per row with one order nested inside, 96 calls. It is flattened with `json_normalize`, `order_date` is the UTC date of `logged_at` without its time, prices and totals are converted from pence to pounds, the 12 quantities stored as text are made integers, the call centre's words are mapped to the storefront's (Home & Garden → home, Health & Beauty → beauty, Sports/Outdoor → sports, GIFT_VOUCHER → voucher, the rest lowercased), and `channel` is added as `phone`. The two are stacked into 1,996 orders. The CRM's `crm_customers.xlsx` is read with `skiprows=2` to skip two title rows, giving 1,088 rows. Its 22 region spellings are collapsed into 7 places, and opt-in Yes/No becomes True/False, with its 32 blanks left blank.

### The join
The CRM holds 1,088 rows for 1,061 customers, because 27 appear twice. I kept neither row for those 27, leaving 1,034 customers, and left-joined the orders to them with `validate="many_to_one"`, giving 1,996 rows, one per order. The 34 orders of the 27 customers have blank region, tenure and opt-in. The result is committed as `data/orders_joined.csv`.

### The cleaning
`src/cleaning.py` repairs or flags the 17 faulty orders found in the audit instead of removing them, so 1,996 orders go in and 1,996 come out. Four zero quantities and four prices of zero or less are set to blank and flagged in `quantity_missing` and `item_price_missing`, with the value each order's total implies written to the ledger, not the column. The four negative order values have their sign corrected, flagged in `order_value_sign_corrected`, and the returned one is also flagged in `order_value_ambiguous`. The five −999 delivery times become blanks, flagged in `delivery_days_missing`. The 77 blank opt-ins are left blank. Each step writes a line to `outputs/cleaning_ledger.csv`, and the script asserts that the orders removed, here none, equal those the ledger names. The result is copied to `data/orders_clean.csv`: 1,996 orders, the original columns plus the five flags.

### The features
`feature_frame` in `src/features.py` hands cross-validation six numeric columns (`item_price`, `discount_pct`, `customer_prior_orders`, `delivery_days`, `order_value`, `quantity`), four categorical ones (`channel`, `category`, `payment_method`, `customer_region`), `customer_id`, and six date features from each order's own date. It leaves out `returned`, `order_id`, the date string, `customer_tenure_days`, `marketing_opt_in` and the five flags. Every step that learns a number sits inside one scikit-learn `Pipeline`, fitted again in every fold: numeric columns are filled with the training folds' median and scaled, and categorical columns are one-hot encoded, ignoring values not seen in training. The model is a logistic regression. By default it uses only the six numeric and four categorical columns, a matrix of 1,996 rows by 26 columns.

## 2. Every decision, and the alternative you rejected

The decisions below follow one rule: a value nobody can trace is not written in, an order is not thrown away for one bad field, and nothing the shop did not know at checkout reaches the model.

### The 27 duplicated customers (Week 2)
I kept neither CRM row for each, rather than keeping the first. Keeping the first lets whichever record sits higher in the spreadsheet win, and the pairs disagree on tenure in all 27 cases and on region in 24. A blank announces itself; a value that may be false looks certain.

### The 46 opt-ins the CRM does not have (Week 2)
I took opt-in from the CRM alone and left the blanks blank, rather than restoring the Week 1 values or filling in the commonest answer. Nothing records who filled the Week 1 values, from what, or when, and a filled value looks exactly like a real one.

### Repair and flag, not drop (Week 4)
I kept the 17 faulty orders rather than dropping them as the slides did, because each has one bad field and several sound ones.

- **Zero quantities and prices, 4 orders each.** I set them to blank and flagged them, rather than writing in the value the order total implies. A value recovered from price × quantity × (1 − discount) = value passes that identity by construction, so no check could catch it if it were wrong.
- **Negative order values, 4 orders.** I corrected the sign rather than dropping them, because each magnitude matches the other three columns to the penny. In Week 4 I left the returned one, ORD-100234, negative, as a possible refund. In Week 5 I corrected it too: with only a returned order negative, a negative value meant "returned", so the cleaning had written the label into a feature. It stays flagged as ambiguous.
- **The five −999 delivery times.** I turned them into flagged blanks rather than dropping or imputing them. −999 is a code, not a duration: with the five in, the mean delivery time is 0.981 days instead of 3.492, and imputing would assert a delivery time nobody measured.

### What the model sees (Week 5)
I assume the prediction is made at checkout and ask of every feature whether its value was known then.

- **The customer's return rate.** Computed on every order before the split, it scores 0.9326, and 0.9335 grouped by customer, against 0.6201 without it, because for a customer with one order the rate is the label. Target encoded inside the pipeline, it adds 0.0024 against an sd of 0.034, since there are only 2.2 orders per customer. So I one-hot encode the four ordinary categoricals, which have 285 to 998 orders per value, and leave `customer_id` out.
- **The six date features.** I left them out: with them the score is 0.6122 (sd 0.0376), without them 0.6201 (sd 0.0347), a difference smaller than the sd. I also rejected a count of each customer's orders in 2025, because it counts later orders; `customer_prior_orders` counts only earlier ones.
- **Columns left out.** `customer_tenure_days` may have been measured after the order, `marketing_opt_in` has 77 blanks I chose not to fill, and the five flags record my cleaning, not the customer.
- **Where each step is fitted.** The median, the scaling and the categories are learned inside the `Pipeline` in every fold, rather than once on every order, so no test fold sees a number learned from its own rows.

One decision breaks the rule. `delivery_days` is not known at checkout. I kept it, rather than removing it or replacing it with the promised delivery time, so that my scores line up with the lab's.

## 3. What is still unexplained

### The 46 opt-in values
The Week 1 file shows an opt-in for 46 orders whose customers have none in the CRM, and nothing records where those values came from. In my table they are 43 orders from 21 customers, plus 3 from duplicated customers. In every customer with more than one order, all their orders carry the same value, so the values behave like a real per-customer record, not a fill. My position is that they are probably real and certainly unverified, and unverified decides it: opt-in is consent, and consent has to be recorded, not assumed. The blanks stay blank. For marketing, unknown means not opted in; for analysis it stays missing. Why the 43 are blank in the CRM is also unexplained: their return rate, 0.116 against 0.192, differs only within chance, and I cannot tell which missingness mechanism produced them.

### The duplicated CRM records
The 27 pairs disagree on tenure in every case and on region in 24, and nothing says which is current. My position is to keep neither until one can be shown to be current.

### Which order fields the system calculates
In all twelve arithmetic faults, exactly one field is wrong and the other three agree, so the data cannot say which fields are stored as entered and which are calculated, or whether ORD-100234 is a sign error or a refund. My position is to correct the four signs, keep ORD-100234 flagged as ambiguous, and keep the implied quantities and prices out of the columns.

### What −999 meant
Nothing says whether −999 means "not recorded", or an order never delivered or cancelled. My position is "not recorded": flagged blanks, with the orders kept.

### When some values were recorded
I cannot tell whether `customer_prior_orders` was counted at the order or at export, what date `customer_tenure_days` is counted to, or whether `Returned` N means "not returned yet" for late orders. My positions are to treat the first as counted at the order, leave tenure out, and read N as "not returned".

### Smaller doubts from ingestion
Phone dates near midnight in British Summer Time, text quantities that may hide typos, whether Sports/Outdoor means the same as sports, and what `customer_region` and `NI` mean all remain open (`docs/sources.md`). My position is to read each value as given, with the assumption written down.

## 4. The imbalance decision

The base rate is 0.1914: 382 of the 1,996 orders were returned.

At the default threshold of 0.5, the logistic regression flags 2 orders and finds none of the 382 returns. Rather than resampling, I lowered the threshold.

My operating point is a threshold of 0.194 on the model's probability of a return. It flags 1,002 of the 1,996 orders in the year, about 19 a week: 259 returns and 743 kept orders, a precision of 0.259. It finds 259 of the 382 returns, a recall of 0.678, and misses 123.

The operations manager would change it, raising the threshold to flag fewer orders a week or lowering it to flag more. Changing it does not require retraining the model.

I did not use `class_weight`. With `class_weight="balanced"`, the model at 0.5 flags 1,009 orders and finds the same 259 returns, so on my data it is equivalent to a threshold of 0.194.

## 5. The method choice

The model is a logistic regression. The question that decided it was whether anyone has to explain a decision. The operations manager looks at about 19 flagged orders a week and can ask why each was flagged. A logistic regression answers with 26 weights that can be read out. Of the alternatives, only a depth-4 decision tree, at 29 nodes, is readable; gradient boosting has 1,412 nodes and a random forest 90,988.

Accuracy points the same way. Over 25 out-of-fold scores, the logistic regression's ROC-AUC is 0.6201 (sd 0.0347), against 0.5789 (sd 0.0274) for the tree, 0.5820 (sd 0.0278) for gradient boosting and 0.5574 (sd 0.0290) for the forest. All three are more than one sd behind, so the only alternative as easy to explain is also clearly less accurate.

## 6. What you would do with another week

With another week, I would do some of the further reading suggested in the lectures, choosing the parts that bear on the decisions in this note: Kaufman et al., "Leakage in data mining" (ACM TKDD, 2012), on leakage; Prokhorenkova et al. (NeurIPS 2018), which calls the encoding problem target leakage, on encoding; Provost and Fawcett's *Data Science for Business* (2013), on the operating point; and the Netflix Technology Blog's "Netflix recommendations: beyond the 5 stars" (2012), on the method choice.