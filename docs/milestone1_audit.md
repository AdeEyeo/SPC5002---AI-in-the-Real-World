## 1. A profile of both datasets

### Orders

`data/orders_joined.csv` has 1,996 rows and 16 columns. `order_id` takes 1,996 distinct values, so the table holds one row per order, which confirms the Week 2 join did not duplicate anything, unlike the join as operations ran it, which produced 2,030 rows. The categorical columns show that the Week 2 cleaning held: `category` takes 6 values, where uncorrected spaces and capitals would have given 12, and `customer_region` takes 7, from the CRM's 22 strings for the same places.

Three columns have blanks, all from the CRM. `customer_region` and `customer_tenure_days` are blank on the same 34 orders, placed by the 27 customers with two disagreeing CRM rows, because I chose to keep neither row rather than let the order of a spreadsheet decide (`docs/join_decision.md`). `marketing_opt_in` is blank on those 34 and on 43 more, 77 in all. The Week 1 file had no blanks in any of these columns, so its clean null count was hiding both problems (parts 4 and 5).

`delivery_days` has a minimum of −999, which the profile reports without complaint because −999 is a valid integer, even though it cannot be a number of days (part 3).

### Penguins

`data/penguins_raw.csv` has 344 rows and 17 columns. `Region` and `Stage` hold a single value on every row, so they carry no information. Seven columns have blanks, not counting `Comments`: the four body measurements on 2 rows each, `Sex` on 11, `Delta 15 N (o/oo)` on 14 and `Delta 13 C (o/oo)` on 13. `Comments` is blank on 290 rows.

Neither column that looks like an identifier is one on its own. `Individual ID` takes 190 distinct values across 344 rows, but 110, 114 and 120 within the three seasons: it names a nest and one of its parents in one season, not a bird. `Sample Number` repeats within a season on 124 rows, because it restarts for each species. The pair `studyName` and `Individual ID` has no duplicates, and `src/constraints.py` uses it as the key. No column follows a bird from one season to the next.

## 2. Constraints, with reasons

A range rule asks whether one column's value is possible on its own; an identity rule asks whether several columns agree. Every range rule judges only values that are present, because `between` is False for a blank and would otherwise report the two unweighed birds as impossible. Missing and impossible are different findings, and blanks are left to part 4.

### Orders

`quantity` must be at least 1, because an order for nothing is not an order. `item_price` must be above zero, because the shop does not list stock at a price of nothing. `order_value` must not be negative, because refunds are recorded by the `returned` flag, not by the value. `delivery_days` must lie between 0 and 60, because a parcel cannot arrive before it is sent, and two months is beyond any delivery the shop would leave unrecorded as a problem.

The identity rule is that `order_value` equals `item_price × quantity × (1 − discount_pct / 100)`, because the value is derived from the other three. It is compared to within a penny because `order_value` is stored rounded: an exact comparison flags 741 orders, 729 of them only rounding, which would bury the 12 real disagreements. The range rules flag 17 orders and the identity 12, and part 3 shows they are not redundant.

### Penguins

Body mass must lie between 2,500 and 6,500 g and flipper length between 160 and 240 mm, because adults of these three species fall well inside both. `Sex` must be MALE, FEMALE or blank, because the blood test has two possible results. The identity rule is that the egg date falls in the season named by `studyName`, so PAL0708's eggs are dated 2007 or 2008.

All four penguin rules found nothing, which is evidence rather than an absence of it: every recorded measurement is plausible, every recorded sex is one the test can return, and every egg date agrees with its study label, which the row key depends on. The problems in this file are in its blanks and its identifiers, not its measurements.

## 3. Faults

Seventeen orders break at least one rule, and in each exactly one field is wrong. Each range rule catches 4 or 5 of them and misses the rest; the identity catches 12 and misses 5. No order fails the identity alone, so the range rules miss nothing it finds, but it misses what they find, and both kinds are needed. Throughout, `data/` is never edited: corrections belong to the cleaning step in Week 4, where each is counted and flagged.

1. **`delivery_days` is −999 on 5 orders** (ORD-100182, -100250, -100729, -101124, -101568). Found by the delivery range rule. Missed by the identity, because the arithmetic of these rows is right, and by the profile, because −999 is a valid integer. It is a placeholder, not a duration: with these rows the mean delivery time is 0.98 days, and without them 3.49. I propose treating the five as missing, keeping the rows, until whoever owns the delivery system confirms what −999 meant.

2. **`order_value` is negative on 4 orders** (ORD-100234, -100378, -101594, -101872). Found by the value rule and the identity; missed by the other range rules. In all four the magnitude matches price × quantity × (1 − discount) to the penny. Only one, ORD-100234, was returned, so a refund explains at most one and a sign error fits all four. I propose correcting the sign on the other three and flagging ORD-100234 as ambiguous. This is the one correction the data supports independently, because the magnitude was computed from three other columns rather than made to fit.

3. **`quantity` is 0 on 4 orders** (ORD-100443, -101741, -101808, -101913). Found by the quantity rule and the identity; missed by the other range rules. Working back from the value gives 2, 2, 2 and 1, but a quantity recovered from the identity passes it by construction, and assumes the price and value are right, so nothing checks it. I propose setting the quantity to missing, flagged, with the implied value in the cleaning log.

4. **`item_price` is 0 on 4 orders** (ORD-100320, -100438, -100647, -101191). Found by the price rule and the identity; missed by the other range rules. The value implies 39.60, 9.28, 62.26 and 106.12, and for the reason under 3 I propose recording these rather than writing them in.

5. **The Week 1 notebook removed rows without counting them.** Its filters on `quantity > 0` and `delivery_days > 0` took 2,030 rows to 2,021 with no record of why, removing the zero quantities and the −999s and leaving the negative values and zero prices in place. Counting every row a decision removes is the difference between that and the proposals here.

6. **`Individual ID` is reused across seasons**, so 94 IDs appear with two species, on 228 rows. Found by asking whether an ID always has one species, which no rule in `src/constraints.py` does; missed by the profile, where 190 distinct values look ordinary. Grouping or joining on the ID alone silently merges different birds. I propose always keying rows on `studyName` and `Individual ID`, and adding a rule that an ID within one study has one species, so the code catches this next time.

7. **`Sample Number` repeats within a season, on 124 rows.** Found by a uniqueness check; missed by the profile. I propose leaving the column alone and never using it as a key.

8. **`Region` and `Stage` are constant on all 344 rows.** Found by the profile; no constraint notices a constant. I propose keeping them in the raw file, as a record of the study design, and out of any model.

9. **Two comments hold two unrelated reasons** (c07 and c08). Found only by reading them. On c08 a missing sex and missing isotopes have different causes in one field. Nothing can be done to the file, so I record it as a limit on what part 4 can claim.

The 77 blank opt-ins and the 20 penguin rows with missing measurements are blanks, not faulty values, and are dealt with in parts 4 and 5.

## 4. Missingness

Whether a blank is MCAR, MAR or MNAR decides what may be done about it, and none of the three can be tested from the blanks alone, so each column gets the mechanism I think produced it and the evidence for that.

### Penguins

All 20 incomplete rows have a comment, and grouping the blanks by comment accounts for every one. The four body measurements are missing on the same 2 rows, both "Adult not sampled": nothing was attempted, and those rows are blank in every measured column.

The 11 missing values of `Sex` look identical and have four stories: five laboratory failures ("Sexing primers did not amplify"), two birds never sampled, two with no blood sample, and two with none obtained for sexing. Those last two still have isotope values, so blood was taken, but none reached the sexing test. Filling all eleven with the commoner sex would make one silent assumption about four different situations.

The isotopes are missing mostly for want of blood: of the 13 blanks in `Delta 13 C`, 9 say there was not enough, 2 had no sample and 2 are the unsampled adults. `Delta 15 N` has those 13 and one more, "No delta15N data received from lab", the only value in the file that was produced and lost, and the only one an email could recover.

The blanks are not MCAR. Fifteen of the 20 incomplete rows come from PAL0708, against 1 from PAL0809 and 4 from PAL0910, so missingness depends on something recorded, which is consistent with MAR. MNAR cannot be ruled out: if the sexing test failed more often for one sex, nothing in the file could show it. `Comments` is blank on 290 rows, but there a blank means nothing to report, not a missing value.

### Orders

`marketing_opt_in` is blank on 77 orders, through two mechanisms that look the same in the file. Thirty-four are my own doing, from keeping neither CRM row for the 27 duplicated customers; their mechanism is written down, and they become recoverable when the CRM owner says which row is right.

The other 43, from 21 customers, are blank in the CRM itself, with nothing recording why. All are web orders, and their return rate is 0.116 against 0.192 for orders with an opt-in, 5 returns where about 8 would be expected. On 43 orders that is within chance, but if it held, the blanks would be related to the target. They could be MCAR, MAR or MNAR, I cannot tell which, and so they stay blank.

`delivery_days` has no blanks but five missing values: the −999s, which a null count of zero misses.

## 5. The forty-six

The Week 1 file shows an opt-in for 46 orders whose customers have none in the CRM, 34 true and 12 false, with nothing recording where they came from. In my table these are 43 orders from 21 customers, carrying 33 true and 10 false, plus 3 orders from 2 customers whose CRM rows are duplicated.

I no longer think the values were invented. Opt-in belongs to a customer, not an order, and in all 15 of the 21 customers with more than one order, every order carries the same value, which a fill made order by order would almost certainly have broken. The values behave like a per-customer record from an older extract or another system. They also lean towards consent, 77% true against 56% where the CRM has a value, though on 21 customers that may be chance.

My position is that the values are probably real and certainly unverified, and unverified decides it. Opt-in is consent to be marketed to, and consent has to be recorded, not assumed: treating a real "true" as unknown costs one email, while treating an untraceable "true" as consent is a compliance failure. So the blanks stay blank. For marketing use, unknown means not opted in; for analysis it stays missing and is never filled with the commonest value. Opted-in counts come from the CRM's own values with the unknowns beside them, since a count from the Week 1 file is 34 higher than the CRM supports. If the source is found and proves to be a consent record, the values can be restored with that source named.

## 6. Three questions the data cannot answer

**1. To whoever built the Week 1 export: where did the opt-in values for customers with no opt-in in the CRM come from?** Part 5 shows the values behave like a per-customer record, but the file carries no trace of their source, and only the person who wrote the export knows what it joined. If the source is an earlier consent record, they can be restored with that source named. If it is a default, a guess or an unrelated system, they stay blank, and every opted-in count taken from the Week 1 file needs correcting.

**2. To the owner of the storefront's order system: which of `item_price`, `quantity`, `discount_pct` and `order_value` does the system store as entered, and which does it calculate?** In all twelve arithmetic faults exactly one field is wrong and the other three agree, so each could be repaired from the identity, but only if the three that agree are the ones the system trusts. If `order_value` is calculated, a negative value is an export error and correcting its sign is safe. If it is entered by hand, the recovered quantities and prices in part 3 are plausible guesses rather than repairs. The data agrees with itself either way, so it cannot say which.

**3. To the data manager of the Palmer Station LTER programme: was a Delta 15 N value produced for the sample marked "No delta15N data received from lab", and can it be sent?** It is the only blank of the twenty where a value was probably measured and then lost in transfer, so it is the only one asking can recover. Every other penguin blank records a bird not sampled, blood not obtained or a test that failed, and no answer brings those back.

## The annotator exercise

I coded the ten comment strings with `src/agreement.py` as E, B, C, B, B, A, B, C, A, D for c01 to c10. My letters match both prepared readings on the five they agreed on, and one of the two on each of the five where they split. Overall agreement rose from 50% to 67%, but only arithmetically: the disagreement is where it was. Every split is now two to one, so a majority vote would make whichever reader I sided with the ground truth, with nothing in the data recording that it was decided that way.

Two rules came first. The same sentence gets the same letter wherever it appears, so c07 follows c02, and a reason joined to the clutch note is coded by the reason, because only the reason explains a blank. I hesitated on the five the readings split on and on c05. On c02 I chose collection, because the shortfall began with how much blood was drawn. On c04 I chose collection, because the team wrote "Adult not sampled" when nobody tried, and "obtained" implies trying. On c05 I chose collection despite the isotope values, because the team had a phrase for a failed sexing test and did not use it. On c08 I chose processing, because both reasons describe a sample that reached the lab. On c10 I chose a lost result, because "received" names a handover.

Coding all 344 rows by tomorrow means coding ten strings, not 344 rows: 290 rows have no comment and nothing missing, and the 34 with only the clutch note all take E. I would write the two rules into a codebook, have a second person code the strings independently, and send every split to whoever holds the field notes.

What should have been recorded is a reason for each missing measurement, chosen from a fixed list at the time, with fields for whether a sample was attempted, how much blood was taken and which tests it went to. Then none of these ten would need interpreting.