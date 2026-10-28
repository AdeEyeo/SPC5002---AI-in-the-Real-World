<!-- This is the Week 5 brief. It lives in docs/ rather than at the top of the
     repository because README.md is yours: Week 1's homework asks you to write
     it, and a later zip must not overwrite your own work. -->

# SPC5002 Week 5 lab

Your cleaned table becomes features. Every step that learns a number goes into
one pipeline, the date gives up what it holds, and a customer's return rate is
measured three ways, one of which is the biggest leak of the term so far.

Thursday is teaching and practice in turns, on the example files in
`week05_thursday.zip`, with six open tasks and no work in your repository.
Friday is the lab, three hours in your repository with the demonstrators, and it
starts from this zip.

## Getting it into your repository

This week does not start a new repository. Copy everything inside this
`lab_week05` folder into your repository and let it replace the Makefile,
`requirements.txt`, `.gitignore` and `src/verify.py`, which now checks this
week's two scripts instead of Week 4's. Nothing of yours is in the zip, so
nothing of yours is overwritten.

Run these in a terminal, in the folder that holds both `lab_week01` and
`lab_week05`.

    cp -R lab_week05/. lab_week01/
    cd lab_week01
    source .venv/bin/activate          # Windows: .venv\Scripts\activate
    make clean-data
    cp outputs/orders_clean.csv data/
    make test
    git add -A
    git commit -m "Add the Week 5 lab and my cleaned table in data/"
    jupyter lab

On Windows, drag everything from `lab_week05` into your repository in Explorer
and say yes to replacing, then run the rest in PowerShell, where `cp` works as
written.

This week starts from your own cleaning, so `data/orders_clean.csv` is the table
your Week 4 `src/cleaning.py` writes, copied out of `outputs/`. `outputs/` is
gitignored and `data/` is not, so the copy is what a clean clone will find. If
your cleaning does not run, copy `orders_clean.csv` from the `week05_thursday`
folder instead. It is the 1,979 orders of the reference cleaning, so Week 5 does
not wait for Week 4.

Nothing new is installed this week, so `make setup` can be skipped. Before you
write anything,
`make test` shows 2 failed, 30 passed and 6 errors once Weeks 1 to 4 are
finished. The 30 are your tests from the first four weeks, and the rest need the
code you write on Friday. Run this week's tests on their own with
`python -m pytest -q tests/test_week5_contract.py`, which shows 2 failed and
6 errors before any code.

## Working in JupyterLab

Everything after `jupyter lab` happens in JupyterLab, as in Weeks 2 to 4.

Run `source .venv/bin/activate` in every new JupyterLab terminal before anything
else, and look for `(.venv)` at the start of the prompt.

Make `src/features.py` and `src/encoding_lab.py` inside JupyterLab. Double-click
`src`, then File, New, Python File, then File, Rename Python File, and type only
`features` or `encoding_lab`, because the box keeps the `.py` for you.

Copy code from `docs/week05_slide_code.md`, which has every code box on Friday's
slides. Code copied out of the PDF loses its indentation, and Python needs it.

If `make` is missing, which it usually is on Windows, run what the Makefile
would.

| make | without make |
|---|---|
| `make setup` | `python -m pip install -r requirements.txt` |
| `make clean-data` | `python src/cleaning.py` |
| `make features` | `python src/features.py` |
| `make encoding-lab` | `python src/encoding_lab.py` |
| `make verify` | `python src/verify.py` |
| `make test` | `python -m pytest -q` |

## What is here

    data/penguins_raw.csv          unchanged from Week 4
    data/PENGUINS_SOURCE.md        unchanged from Week 4
    docs/week05_homework.md        what is due before the Week 6 lecture
    docs/week05_slide_code.md      every code box on Friday's slides, to copy from
    src/verify.py                  what make verify runs. Supplied, not yours to write.
    tests/test_week5_contract.py   eight tests you did not write
    src/                           you add features.py and encoding_lab.py

## Task A, src/features.py

Thursday's Tasks 1 and 2, in a file. It defines two things the tests import.

`build_pipeline()` returns a scikit-learn `Pipeline` that is not yet fitted. Every
step that learns a number from the data is inside it. The imputer learns a
median, the scaler a mean and a standard deviation, the one-hot encoder the list
of categories. Fitted inside cross-validation, each of them learns from the
training folds only. Give it `numeric`, `categorical` and `target_encode`
arguments, so that `encoding_lab.py` can build the variants it needs from the
same function.

`feature_frame(df)` returns the raw columns you hand to cross-validation. It may
derive things from a row's own values, such as the day of the week from that
row's date. It may not use the target, and it may not aggregate over rows other
than the one it is building. It leaves `returned` and `order_id` out, and it does
not change the frame it is given.

The test that matters measures the correlation of every numeric column of
`feature_frame(df)` with `returned`. On honest features the largest here is
0.0466. A customer's return rate computed on every order reaches 0.6888, and the
test fails anything above 0.5. Another test fails `features.py` if it calls
`fit_transform`, or a `groupby` that touches `returned`. Fitting the pipeline
itself with `.fit` is fine.

## Task B, the date

Thursday's Task 3. Six numbers from `order_date`, in a function that
`feature_frame` calls, each from the order's own date and nothing else. A day
count needs a fixed starting day, such as 1 January 2025, rather than the
earliest date in the table, so that a row's value depends on that row alone.

`main` in `features.py` scores the pipeline with and without the six date
features and writes both, each with its standard deviation, to
`outputs/features.json`. Report the difference against its own standard
deviation before you conclude anything about it.

Then write the date feature that would leak, the count of the customer's orders
in 2025, in a function you never call, with a docstring saying why. Keeping the
rejected version is the same habit as Week 4. No test can catch this one, because
its leak is one of time rather than of the label, so the docstring is where it is
caught.

## Task C, src/encoding_lab.py

Thursday's Tasks 4 and 5 and the grouped split. It imports `build_pipeline`,
`feature_frame` and `cv_auc` from `features.py`, and scores three ways to give
the model a customer's return rate.

1. No customer rate, one-hot encoding only.
2. `customer_id` target encoded inside the pipeline, through
   `build_pipeline(target_encode=["customer_id"])`.
3. The customer's rate computed on every order, before the split, as a column.

Score each twice, with a random split and with `StratifiedGroupKFold` grouped on
`customer_id`, so that no customer is in training and test at once. Every score
gets its standard deviation over the 25 folds.

Add how close each version of the column is to the order's own label, the group
mean, `TargetEncoder` with `fit` then `transform`, and `TargetEncoder` with
`fit_transform`, as in Thursday's smoothing cells. Then the rows per level of every
categorical column, `customer_id` included, as in Thursday's Task 6.

Write it all to `outputs/encoding_lab.json`, with your own keys. Wrap counts in
`int()` and numbers in `float()`, and use string keys, or `json.dumps` refuses
them. `make encoding-lab` runs it.

The leaked column is built here on purpose, because this is the file where the
mistake is measured. `features.py` has to stay clean.

## Committing

At least six commits, each one a thing you did. With Weeks 1 to 4 finished,
`make test` ends at 38 passed. Without them, this week's eight still pass on
their own with `python -m pytest -q tests/test_week5_contract.py`. `make verify`, or `python src/verify.py`, runs
`src/features.py` and `src/encoding_lab.py` twice and fails if the two runs
differ.

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
