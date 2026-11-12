<!-- This is the Week 6 brief. It lives in docs/ rather than at the top of the
     repository because README.md is yours: Week 1's homework asks you to write
     it, and a later zip must not overwrite your own work. -->

# SPC5002 Week 6 assignment

Due Friday 13 November at 14:00, the day after the Week 8 lecture.

There is no lab this week. Friday 30 October is our guest's talk, and Week 7 is
reading week, so this assignment has two weeks and you do it on your own. It has
three parts, and only the first is code.

| Part | What | Where | About |
|---|---|---|---|
| A | Thursday's Tasks 1, 3 and 4 on your own pipeline | `src/imbalance.py`, four lines to fill in | under an hour |
| B | Milestone 2, the preprocessing note | `docs/milestone2_preprocessing.md` | 5 hours |
| C | The guest's section of your speaker grid | `docs/speaker_grid.md` | 30 minutes |

## Getting it into your repository

Copy everything inside this `lab_week06` folder into your repository, as in
earlier weeks. It replaces the Makefile, `requirements.txt`, `.gitignore` and
`src/verify.py`, adds `src/imbalance.py`, this brief, the Milestone 2 template and
this week's tests, and copies the penguin files again unchanged. Copy it once
only, because a second copy would replace your filled-in `src/imbalance.py` with
the empty one.

Run these in a terminal, in the folder that holds both `lab_week01` and
`lab_week06`.

    cp -R lab_week06/. lab_week01/
    cd lab_week01
    source .venv/bin/activate          # Windows: .venv\Scripts\activate
    make test
    git add -A
    git commit -m "Add the Week 6 assignment"

On Windows, drag everything from `lab_week06` into your repository in Explorer
and say yes to replacing, then run the rest in PowerShell.

Nothing new is installed. `src/imbalance.py` builds on your Week 5
`src/features.py` and reads `data/orders_clean.csv`, so both need to be there.
Before you fill anything in, this week's tests on their own,
`python -m pytest -q tests/test_week6_contract.py`, show 2 failed and 4 errors.

If `make` is missing, `make imbalance` is `python src/imbalance.py`,
`make verify` is `python src/verify.py` and `make test` is `python -m pytest -q`.

## Part A, src/imbalance.py

The file is written for you except four lines marked `TODO`. Each one is a line
you wrote in Thursday's notebook.

1. In `baselines`, `majority`, a 0 for every order.
2. In `baselines`, `rule`, your one-line rule as 0 and 1. Footwear and apparel is
   Thursday's. If the return rates in your cleaned table suggest a better single
   rule, one with a higher precision than footwear and apparel at a similar recall,
   use it, and change the words in `RULE` at the top of the file to match.
3. In `oof_proba`, the `cross_val_predict` line, with `method="predict_proba"`
   and column 1.
4. In `matching_threshold`, `pred`, True where `proba` is at least `t`.

Then `make imbalance`. It prints six lines and writes `outputs/imbalance.json`.
On the reference cleaning the matching threshold is 0.193, with 251 returns
found and 125 missed, the same as the class-weighted model. Your numbers move
with your cleaning and your features, and the shape should not.

`with_class_weight` sets `class_weight="balanced"` on the last step of your
pipeline, whatever you called it in Week 5. You do not need to change
`build_pipeline`.

`make verify` runs the script twice and checks that the two reports are
identical. Commit `src/imbalance.py` when it passes.

## Part B, Milestone 2, the preprocessing note

Copy `docs/milestone2_template.md` to `docs/milestone2_preprocessing.md` and
write it. Two to four pages, in prose. It is not separately marked. You get
written feedback against the report criteria, and it becomes the section of your
final report on what you did to the data and why.

The template has six parts, each with a short note on what goes in it. Two of
them carry the weight.

Part 1 is judged by whether a stranger could rebuild your dataset from the note
alone, without opening your code.

Part 4 is judged by whether the operations manager could tell, from what you
wrote, how many orders a week they would be asked to look at. Your
`outputs/imbalance.json` has the number of orders flagged at your threshold, out
of 1,979 in a year. Say what your operating point is, who would change it, and,
if you used `class_weight`, which threshold it is equivalent to.

## Part C, the speaker grid

Fill in the Week 6 section of `docs/speaker_grid.md` for Friday's guest, the six
questions and your own seventh, the same day if you can. Add one line on the
question from Thursday, what their system does with the cases it cannot handle,
who sees them, and what that costs.

## Committing and handing in

At least four commits, each one a thing you did. With every earlier week
finished, `make test` ends at 44 passed, and this week's six pass on their own.

Until the GitHub setup is fixed, upload one zip of your repository to QMplus, made
in the folder that holds `lab_week01`. The zip is under 2 MB, and tens of
megabytes means `.venv` went in.

    zip -r homework.zip lab_week01 -x "lab_week01/.venv/*"   # Mac, Linux, JupyterHub
    tar -a -c -f homework.zip --exclude=.venv lab_week01      # Windows PowerShell

If you are stuck during reading week, post on the QMplus forum. Week 8 starts
from this repository, so it is worth having it run from a clean clone before then.
