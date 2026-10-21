<!-- This is the Week 3 brief. It lives in docs/ rather than at the top of the
     repository because README.md is yours: Week 1's homework asks you to write
     it, and a later zip must not overwrite your own work. -->

# SPC5002 Week 3 lab

This week you profile two tables, write down what each column is allowed to be,
and audit what you find. One table is your own `orders_joined.csv`. The other is
field data from Antarctica that nobody tidied for teaching.

Thursday is a guided practice on example files, in `week03_thursday.zip`, and
needs nothing from Week 2. Friday is the guest's hour only. Milestone 1, the data
audit, is the same steps on the full data, in your repository, due before the
lecture on Thursday of Week 4, at 11:00.

## Getting it into your repository

This week does not start a new repository. Copy everything inside this
`lab_week03` folder into your repository and let it replace the Makefile. Nothing
of yours is in the zip, so nothing of yours is overwritten.

Run these in a terminal, in the folder that holds both `lab_week01` and
`lab_week03`.

    cp -R lab_week03/. lab_week01/
    cd lab_week01
    source .venv/bin/activate          # Windows: .venv\Scripts\activate
    make ingest
    cp outputs/orders_joined.csv data/
    make test
    git add -A
    git commit -m "Add the Week 3 lab, and my joined table in data/ for Weeks 3 and 4"
    jupyter lab

On Windows, drag everything from `lab_week03` into your repository in Explorer
and say yes to replacing, then run the rest in PowerShell.

`make ingest` rebuilds last week's joined table and the next line copies it into
`data/`. `outputs/` is never committed and `data/` is, so the copy is what a clean
clone of your repository sees, and the Week 3 and Week 4 tests read it from
there. Before you write anything, `make test` shows 16 passed, 1 failed and 5
errors. The 16 are your 15 from Weeks 1 and 2 and the test that checks the
penguin file is untouched.

If your Week 2 ingestion does not run, skip `make ingest` and copy
`orders_joined.csv` from the `week03_thursday` folder into `data/` instead. It is
the same 1,996 orders rebuilt from the three sources, so Week 3 does not wait
for Week 2. Run this week's tests on their own with
`python -m pytest -q tests/test_week3_contract.py`, which shows 1 passed, 1
failed and 5 errors before any code.

There are no new packages this week, so there is nothing to install.

## Working in JupyterLab

Everything after `jupyter lab` happens in JupyterLab, as in Week 2.

Run `source .venv/bin/activate` in every new JupyterLab terminal before anything
else, and look for `(.venv)` at the start of the prompt.

Make `src/profile.py` and `src/constraints.py` inside JupyterLab. Double-click
`src`, then File, New, Python File, then File, Rename Python File, and type only
`profile` or `constraints`, because the box keeps the `.py` for you.

Thursday's notebook is `week03_thursday.ipynb`, with its files beside it. Unzip
`week03_thursday.zip` inside your repository folder so that JupyterLab can see
it, and `.gitignore` keeps that folder out of your commits.

`src/agreement.py` asks you questions and waits for the answers, so run it in a
JupyterLab terminal and not from a notebook.

If `make` is missing, which it usually is on Windows, run what the Makefile
would. `make ingest` is `python src/ingest.py`, `make profile` is
`python src/profile.py`, `make check` is `python src/constraints.py` and
`make test` is `python -m pytest -q`.

## What is here

    data/penguins_raw.csv          344 rows, 17 columns. Real, and not tidied.
    data/PENGUINS_SOURCE.md        where it came from and how it was collected
    docs/milestone1_brief.md       what the audit has to contain
    docs/speaker_grid.md           the six questions every guest is asked
    src/agreement.py               the annotator exercise. Supplied, not yours to write.
    tests/test_week3_contract.py   seven tests you did not write
    src/                           you add profile.py and constraints.py

## The real dataset

Field measurements of nesting penguins at Palmer Station, Antarctica, collected
by Dr Kristen Gorman and the Palmer Station Long Term Ecological Research
programme in the 2007-08, 2008-09 and 2009-10 seasons. Published as collected,
under CC0.

Do not edit it. If you think a value is wrong, that belongs in your audit and not
in the file, and `test_you_did_not_edit_the_real_dataset` notices an edit.

Read `data/PENGUINS_SOURCE.md` before you open the CSV, because knowing who
collected a dataset and how changes what you notice in it.

## The task

### src/profile.py

Every column of both datasets, the same three questions. What type is it, how
many distinct values does it take, and how many are missing? Then a range for a
number, or the commonest few values for anything else. It writes
`outputs/profile.json`. The keys are yours to name, because the test checks that
you answered the questions and not that you used my words.

Do not skip a column because it looks boring. Two of the penguin columns hold a
single value each, and your profile should show which without being told.

### src/constraints.py

What each column is allowed to be, written so that it can fail. At least one
identity check, meaning a rule about more than one column at a time, and a
one-line reason with every rule, in the code. It writes
`outputs/violations.csv`, one row for each rule a row breaks.

Two traps cost people an afternoon.

`~s.between(a, b)` is True for every missing value, so the obvious way to write a
range check reports blanks as impossible values. Put `s.notna() &` in front of
it, because missing and impossible are different findings.

`order_value` is stored rounded to the penny, so an identity check written with
`==` flags 741 rows, and 729 of those are rounding. Compare to within a penny.

### Milestone 1

`docs/milestone1_audit.md`, against `docs/milestone1_brief.md`.

## The annotator exercise

On Thursday you see two prepared readings of the ten comment strings disagree on
half of them. For the milestone, code the ten yourself with
`python src/agreement.py`, which shows them one at a time and saves your letters
to `votes/me.json`. Then put your letters beside the two readings.

    python src/agreement.py votes/me.json week03_thursday/reader_A.json week03_thursday/reader_B.json

`votes/` is in `.gitignore`. Your letters go into the audit as a paragraph, not
into the repository as a file.

## Friday

Friday 9 October is the guest's hour, forty minutes of talk and twenty of
questions, from 10:00 to 11:00. There is no lab. Fill in this week's section of
`docs/speaker_grid.md` the same day, while the talk is fresh.

## Committing

At least six commits. `make test` ends at 22 passed once Weeks 1 and 2 are
finished, and this week's seven pass on their own whether or not they are.
`make verify` runs `src/profile.py` and `src/constraints.py` twice and fails if
the two runs differ.
