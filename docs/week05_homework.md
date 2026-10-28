# Week 5 homework

Due Thursday 29 October at 11:00, before the Week 6 lecture.
Until the GitHub setup is fixed, hand in one zip of your repository on QMplus,
made as `docs/week05_brief.md` says. Once GitHub works, push to the same
repository on github.qmul.ac.uk instead.

About eight hours, Friday's lab included.

## 1. Finish the features and the encoding lab

`make features` and `make encoding-lab` run from a clean clone. With Weeks 1 to
4 finished, `make test` shows 38 passed, and this week's eight pass on their own
with `python -m pytest -q tests/test_week5_contract.py`. `make verify`, or
`python src/verify.py`, prints four hashes and `the two runs match`.

Add both targets to the Running this section of your `README.md`.

## 2. `docs/feature_notes.md`

One short section per feature or group of features.

- what it is
- why you think it predicts anything
- was its value known at the moment of the prediction

The third takes one line each and is the one that gets read. Answer it for the
boring features too, `delivery_days` among them, because the boring ones are
where the surprises are. Say what moment of prediction you are assuming.

## 3. Rows per level

In `docs/feature_notes.md`, under its own heading. A table of every categorical
column you have, with the number of orders divided by the number of distinct
values. Then a sentence on which you would target encode and which you would
not, and roughly where you would draw the line.

There is no correct threshold. There is a correct habit, which is computing the
number before choosing the encoding rather than after seeing the score.

## 4. The three routes, on your data

In `docs/feature_notes.md` too. The three scores from
`outputs/encoding_lab.json`, random and grouped, each with its spread. Then one
paragraph on why the grouped split did not rescue the leaked version.

If you can write that paragraph you have understood the week. If you cannot,
that is the thing to ask about on Thursday, because the same idea returns in
Week 8 and again in Week 10.

## 5. Six commits

Each one a thing you did.

## Optional

Frequency encoding replaces a value with how often it occurs, and never looks at
the target. Encode `customer_id` that way and see what it is worth.

Then answer whether frequency encoding can leak. The answer is not simply no, and
working out when it can is worth more than the encoding is.
