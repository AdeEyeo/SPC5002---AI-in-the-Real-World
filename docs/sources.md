## web_orders_2025.csv (storefront)

### 1. Where does it come from, and who owns it?
The online storefront's order export, written as CSV because finance uses it. Owned by whoever runs the storefront; finance consumes it.

### 2. What does one row mean?
One order. 1,900 rows, checked on read.

### 3. What did you have to decide in order to read it? List every decision, not only the ones that would have crashed. The encoding, the date format, the currency unit, the type coercions, the whitespace, the category mapping.
- Encoding: UTF-8 with a byte order mark (the first three bytes are `EF BB BF`). pandas 3 strips it silently; Python's `csv` module keeps it, and a lookup on `Order ID` then raises `KeyError`.
- Dates: `Order Date` is day first (`20/06/2025`) and parsed with an explicit `%d/%m/%Y`. 754 dates would parse either way round, and `format="mixed"` gets 694 of them wrong without raising anything.
- Currency: already pounds, no conversion.
- Whitespace: `Item Category` stripped of trailing spaces; `Payment` stripped as a precaution.
- Coercions: `Returned` `Y`/`N` became `1`/`0`.
- Names: columns renamed to the Week 1 names; `channel` added as `web` because the source does not carry it. The storefront's category and payment words are kept as the standard the other sources are mapped to.

### 4. What are you unsure about?
- Whether `N` means "not returned" or "not returned yet". Orders late in the year may not have had time to come back.
- When `Prior Orders` was counted: at the time of the order, or when the file was exported. If at export, it carries information from after the order, like `export_seq` did.
- Whether `Order Total` always equals price × quantity less discount. I did not check.

## phone_orders_2025.json (call centre)

### 1. Where does it come from, and who owns it?
The call-centre log, written as JSON because that is what its API produces. Owned by the call-centre team.

### 2. What does one row mean?
One call, with one order nested inside it. 96 calls, checked on read.

### 3. What did you have to decide in order to read it? List every decision, not only the ones that would have crashed. The encoding, the date format, the currency unit, the type coercions, the whitespace, the category mapping.
- Structure: read the `calls` list and flattened it with `json_normalize`. `call_ref` and `agent` have no Week 1 column and are dropped.
- Dates: `order_date` is the UTC date of `logged_at`, with the time removed. Left with its time, it would never match the Week 1 file.
- Currency: `unit_price_pence` and `total_pence` divided by 100. Left in pence, phone orders would look 100 times more expensive, and nothing raises.
- Coercions: `order.line.qty` mixes integers and text (12 of 96 are strings), so `int()` was applied to every value. `order.returned` is a real boolean, made `1`/`0`.
- Whitespace: categories stripped before mapping (`'Footwear '` has a trailing space).
- Category mapping, in a dictionary in `src/ingest.py`: Home & Garden → home, Health & Beauty → beauty, Sports/Outdoor → sports; the other three lowercased.
- Payment mapping: `CARD`, `BNPL`, `PAYPAL` lowercased; `GIFT_VOUCHER` → voucher.
- Names: `order.ref` → `order_id`, `customer.crm_id` → `customer_id`; `channel` added as `phone`.

### 4. What are you unsure about?
- Whether the time of the call is the time of the order. A call just after midnight in British Summer Time falls on the previous day in UTC.
- Whether the text quantities were typed by agents and could contain typos that `int()` accepts without complaint.
- Whether a call can ever hold more than one order or line. All 96 hold one, but the `order.line` naming suggests the format allows more.
- Whether Sports/Outdoor and sports mean exactly the same set of products.

## crm_customers.xlsx (customer database)

### 1. Where does it come from, and who owns it?
An extract from the CRM, written as a spreadsheet for the people who open spreadsheets. Owned by the CRM team.

### 2. What does one row mean?
Meant to be one customer. It is not: 1,088 rows for 1,061 customers, 27 of whom appear twice. 154 customers placed no order in 2025 and drop out of a join from the orders, which is correct because the population is orders.

### 3. What did you have to decide in order to read it? List every decision, not only the ones that would have crashed. The encoding, the date format, the currency unit, the type coercions, the whitespace, the category mapping.
- Layout: two title rows above the header, skipped with `skiprows=2`. Without it the read succeeds with 1,090 rows and wrong column names.
- Row count: 1,088 stated and checked, so a longer CRM stops the run.
- Region: 22 strings for 7 places (capitals, trailing spaces, or both), collapsed by stripping, lowercasing and mapping through a dictionary.
- Opt-in: `Yes`/`No` became `True`/`False`; the 32 blanks are left blank.
- Duplicates: both rows dropped for the 27 customers, so their orders have blank CRM fields. See `docs/join_decision.md`.
- Types: tenure becomes a float after the join, because an integer column cannot hold blanks.

### 4. What are you unsure about?
- Which of each duplicated pair is right, and how a customer came to have two records.
- What date tenure is counted to. Every pair differs on it (customer 10024: 909 and 966 days), which might mean two extracts taken at different times.
- What a blank opt-in means: never asked, declined to answer, or a value the system failed to write.
- Whether region is where the customer lives or where orders are delivered, and whether `NI` means Northern Ireland.

## The column that does not reconcile: marketing_opt_in

The CRM leaves opt-in blank for 32 customers. 23 of them ordered in 2025, placing
46 orders. On every one of those orders the Week 1 file shows a value: true on 34
(from 17 customers) and false on 12. None of the three sources contains these
values, and nothing records who filled them, from what, or when.

### What I did.
`orders_joined.csv` takes opt-in only from the CRM, so those 46 orders are blank. I did not copy the Week 1 values back in, and I did not fill the blanks with the most common value. Either would make two systems appear to agree when they do not, and a filled value looks exactly like a real one. Keeping the values because they are already there is not neutral: it is a decision that the unknown filler was right.

### What follows from it.
- Any count of opted-in orders reports three groups: opted in, opted out, and unknown. The unknowns are never folded into either side.
- Any count taken from the Week 1 file is 34 orders too high, and I say so wherever it is used.
- Anything that contacts customers treats unknown as no recorded consent, because contacting someone who never agreed costs more than missing someone who did.

### What would change it.
If the CRM owner, or whoever produced the Week 1 file, can show where the 46 values came from (an older extract, another system, a default), with a date, I would restore them and record that source next to them. Until then, every opt-in number I report can be traced to the CRM, which answers "where did this number come from?"