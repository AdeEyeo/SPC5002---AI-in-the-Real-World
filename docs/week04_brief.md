<!-- This is the Week 4 brief. It lives in docs/ rather than at the top of the
     repository because README.md is yours: Week 1's homework asks you to write
     it, and a later zip must not overwrite your own work. -->

# SPC5002 Week 4 lab

Your audit becomes a pipeline. Each decision from Milestone 1 becomes a function
with a name and a reason, a ledger accounts for every order that leaves, and two
measurements show where a cleaning step belongs and what it costs when it is in
the wrong place.

Thursday is teaching and practice in turns, on the example files in
`week04_thursday.zip`, with five tasks of about ten minutes and no work in your
repository. Friday is the lab, three hours in your repository with the
demonstrators, and it starts from this zip.

## Getting it into your repository

This week does not start a new repository. Copy everything inside this
`lab_week04` folder into your repository and let it replace the Makefile,
`requirements.txt` and `.gitignore`. Nothing of yours is in the zip, so nothing
of yours is overwritten.

Run these in a terminal, in the folder that holds both `lab_week01` and
`lab_week04`.

    cp -R lab_week04/. lab_week01/
    cd lab_week01
    source .venv/bin/activate          # Windows: .venv\Scripts\activate
    ls data                            # orders_joined.csv must be listed
    make setup
    make test
    git add -A
    git commit -m "Add the Week 4 lab: brief, homework and eight tests"
    jupyter lab

On Windows, drag everything from `lab_week04` into your repository in Explorer
and say yes to replacing, then run the rest in PowerShell.

Your joined table has to be in `data/` before you commit. Week 3 asked you to
copy it there, so it usually is. If `ls data` does not list `orders_joined.csv`,
run `make ingest` and then `cp outputs/orders_joined.csv data/`. If your
ingestion does not run, copy `orders_joined.csv` from the `week04_thursday`
folder instead. It is the same 1,996 orders rebuilt from the three sources, so
Week 4 does not wait for Weeks 2 and 3.

`make setup` installs matplotlib, which is new this week, and finds everything
else already there. Before you write anything, `make test` shows 1 failed, 23
passed and 6 errors once Weeks 1 to 3 are finished. The 23 are your 22 from the
first three weeks and the test that checks the penguin file is untouched, and
the rest need the code you write on Friday. Run this week's tests on their own
with `python -m pytest -q tests/test_week4_contract.py`, which shows 1 failed,
1 passed and 6 errors before any code.

## Working in JupyterLab

Everything after `jupyter lab` happens in JupyterLab, as in Weeks 2 and 3.

Run `source .venv/bin/activate` in every new JupyterLab terminal before anything
else, and look for `(.venv)` at the start of the prompt.

Make `src/cleaning.py` and `src/leak_lab.py` inside JupyterLab. Double-click
`src`, then File, New, Python File, then File, Rename Python File, and type only
`cleaning` or `leak_lab`, because the box keeps the `.py` for you.

Copy code from `docs/week04_slide_code.md`, which has every code box on Friday's
slides. Code copied out of the PDF loses its indentation, and Python needs it.

A notebook runs from its own folder, so in `notebooks/` the paths start
`../data/` and `../outputs/`.

If `make` is missing, which it usually is on Windows, run what the Makefile
would.

| make | without make |
|---|---|
| `make setup` | `python -m pip install -r requirements.txt` |
| `make clean-data` | `python src/cleaning.py` |
| `make leak-lab` | `python src/cleaning.py`, then `python src/leak_lab.py` |
| `make verify` | `python src/verify.py` |
| `make test` | `python -m pytest -q` |

## What is here

    data/penguins_raw.csv          unchanged from Week 3
    data/PENGUINS_SOURCE.md        unchanged from Week 3
    docs/week04_homework.md        what is due before the Week 5 lecture
    docs/week04_slide_code.md      every code box on Friday's slides, to copy from
    src/verify.py                  what make verify runs. Supplied, not yours to write.
    tests/test_week4_contract.py   eight tests you did not write
    src/                           you add cleaning.py and leak_lab.py
    notebooks/                     you add week04_sentinel.ipynb

## Task A, src/cleaning.py

One function per decision from **your** audit. The four on the slides remove 4,
4, 4 and 5 orders, seventeen in all. If your audit argued for something else,
implement what you argued.

Each step

- is named after what it does to the data, such as `drop_sentinel_delivery_times`,
  and not after the problem or the week
- takes the frame and the ledger, and returns a new frame without changing the
  one it was given
- records in the ledger what it removed and why
- carries its reason in its docstring, in the language of the business and not
  of pandas

The `Ledger` class is on Friday's slides and in Thursday's notebook. Copy it in,
because the week is about using it. A step that repairs or flags orders instead
of removing them records 0 removed, and its reason says what it changed, as
`mark_sentinel_delivery_times` does on Friday's slides.

`src/cleaning.py` reads `data/orders_joined.csv` and writes two files,
`outputs/orders_clean.csv` and `outputs/cleaning_ledger.csv`, the second with
the columns `step`, `before`, `after`, `removed` and `reason`. Before it prints
its summary or writes anything, it asserts that the orders removed equal the
orders the ledger names. That assertion is the point of the exercise.

Every function at the top level of the file needs a docstring, `clean` included.
Only `main` is excused. Where you had two defensible choices, write both
functions, call one, and say in its docstring which one and why. The rejected
option is the evidence that a decision was taken rather than a default accepted.

The 46 blank opt-ins stay blank. A function that does nothing,
`leave_marketing_opt_in_missing`, says why.

Cleaning the cleaned table must remove nothing. A test gives your script its own
output and fails if a second pass removes any row. A rule about what a value can
be passes. A rule measured against the rows in front of it, a z score or a
quantile, usually fails, and that is a reason to keep it out of the cleaning.

Two traps cost people an afternoon.

`df.drop(rows, inplace=True)` inside a step changes the frame the caller passed
in. Return `df[keep]` instead.

`df["col"].fillna(value, inplace=True)` does nothing at all in pandas 3 and
prints a `ChainedAssignmentError` warning. Write `df["col"] = df["col"].fillna(value)`.

## Task B, the sentinel before you remove it

In a notebook, `notebooks/week04_sentinel.ipynb`, reading the joined table so
that the five -999 rows are still there. The mean and standard deviation of
`delivery_days` with the five and without them, and the z score of a five-day
delivery both ways. Then min-max scale the real deliveries twice, once with the
smallest and largest values taken from the column with -999 still in it and once
from the real values alone, and draw the two histograms side by side.

Save the figure as `outputs/delivery_minmax.png` with `fig.savefig`. A `.png` is
gitignored, correctly, because a picture your code can redraw is not source.
Commit the notebook.

## Task C, src/leak_lab.py

Two measurements on your cleaned table, `outputs/orders_clean.csv`, both with the
six honest features from Week 1, `item_price`, `discount_pct`,
`customer_prior_orders`, `channel`, `category` and `payment_method`, and a
logistic regression. Repeat each over at least 20 seeds and report its spread.

Pair them. Both arms of a seed share one train and test split and differ in one
decision, so that the split's own noise cancels.

1. **The scaler fitted in the wrong place.** The same model twice, the scaler
   fitted on the training rows, then on every cleaned order before the split, at
   40, 80, 200, 500 and 1,000 training rows and at all of them.
2. **Outliers removed before the split.** An order whose `order_value` is more
   than three standard deviations from the mean is unusual. The honest arm
   decides that on the training rows, drops them from the training rows only and
   scores every test order. The other arm decides on every order and drops them
   from both sides of the split. Score the honest model on the other arm's
   cleaned test set as well, because that third number shows where the gap comes
   from.

Start from Thursday's notebook. Define `orders`, `NUM`, `CAT` and `onehot` at the
top of the file, as the notebook did, and its `split`, `score` and
`drop_outliers` cells then work unchanged. Friday's slides show the top of the
file, the scaler measurement written out and `main`. The outlier measurement is
yours, in the same shape, from Thursday's Task 5. Each measurement prints a line
per result and returns means and standard deviations.

Write both to `outputs/leak_lab.json`, with your own keys and a standard
deviation beside every number. Wrap counts in `int()` and numbers in `float()`,
and use string keys, or `json.dumps` refuses them. `make leak-lab` cleans and
then runs it.

One of these gives you nothing. The other does not. Write two sentences in
`docs/cleaning_decisions.md` on why.

## Committing

At least six commits, each one a thing you did. With Weeks 1 to 3 finished,
`make test` ends at 30 passed, and this week's eight pass on their own whether
or not they are. `make verify`, or `python src/verify.py`, runs `src/cleaning.py`
and `src/leak_lab.py` twice and fails if the two runs differ.

## Handing in

Until the GitHub setup is fixed, nothing is pushed. Upload one zip of your
repository to QMplus, made with one of these lines in the folder that holds
`lab_week01`. Both keep the hidden `.git` folder, so your commits come too, and
both leave out `.venv`. The zip is under 2 MB, and tens of megabytes means
`.venv` went in.

    zip -r homework.zip lab_week01 -x "lab_week01/.venv/*"   # Mac, Linux, JupyterHub
    tar -a -c -f homework.zip --exclude=.venv lab_week01      # Windows PowerShell

Once GitHub works, push as in Week 2, and the URL you gave on QMplus in Week 1
still stands.
