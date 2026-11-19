<!-- The Week 8 brief sits in docs/ because README.md at the top of the repository
     is yours, written in the Week 1 homework, and a later zip must never
     overwrite it. -->

# SPC5002 Week 8 lab

The homework that follows this lab is described in `docs/week08_homework.md`, and the file `README_week08.txt` in the top folder gathers both documents in plain terms.

This lab carries Thursday's work into your repository through `src/evaluate.py`, which scores your pipeline, two alternatives and your Week 6 rule on the same 25 folds and reports every score with its spread, PR-AUC with its floor, and each alternative against your pipeline fold by fold. Apart from four lines the file is written for you, and each of those four lines is one that you wrote on Thursday.

| Task | What | Where | About |
|---|---|---|---|
| A | the four lines | `src/evaluate.py` | 40 minutes |
| B | run it and read what it says | `outputs/evaluation.json` | 30 minutes |
| C | start the evaluation note | `docs/evaluation_note.md` | the rest |

## Getting it into your repository

Copy everything inside this `lab_week08` folder into your repository, as in earlier weeks. The copy replaces the Makefile, `requirements.txt`, `.gitignore` and `src/verify.py`, adds `src/evaluate.py`, this brief, the homework, the note template, `README_week08.txt` and this week's tests, and writes the penguin files again unchanged. Because a second copy would replace your filled-in `src/evaluate.py` with the empty one, the copy is made once only.

Run the commands below in a terminal, in the folder that holds both `lab_week01` and `lab_week08`.

    cp -R lab_week08/. lab_week01/
    cd lab_week01
    source .venv/bin/activate          # Windows: .venv\Scripts\activate
    make test
    make evaluate
    git add -A
    git commit -m "Add the Week 8 lab"

On Windows you drag everything from `lab_week08` into your repository in Explorer, say yes to replacing, and run the remaining commands in PowerShell.

Nothing new is installed this week, but `src/evaluate.py` builds on your Week 5 `src/features.py` and reads `data/orders_clean.csv`, so both files have to be in the repository. Before any line is filled in, the command `python -m pytest -q tests/test_week8_contract.py` reports 1 failed and 5 errors, and `make evaluate` stops at the first empty line, as it should.

If `make` is not installed, you can run `python src/evaluate.py` in place of `make evaluate`, `python src/verify.py` in place of `make verify` and `python -m pytest -q` in place of `make test`.

## Task A, the four lines

Each of the four lines carries a comment that reads TODO or FIX, and they are described here in the order in which they appear in the file.

In `folds`, the line marked FIX shuffles with `random_state=0` on every pass of the loop, so the 25 folds as given are the same 5 folds five times. This is Thursday's Task 2, and the fix is the same as it was there.

In `fold_rows`, the line marked TODO sets `floor`, the share of returned orders in this test fold. The array `y[test]` holds the answers of the test fold, each 0 or 1, and the floor itself is Thursday's Task 4.

In `paired`, the line `diffs` is the difference fold by fold, this candidate minus your pipeline, and `a` and `b` are already there with 25 scores each on the same folds. In Thursday's Task 3 the question was what logistic regression gains over the tree, whereas here the question is what each change gains over your pipeline, as on Thursday's slide 20, so the subtraction runs the other way.

The next line, `wins`, is the number of folds in which this candidate is higher than your pipeline, which must be a single number.

If your Week 6 rule was not footwear and apparel, change `RULE` and `rule_scores` at the top of the file to your own rule, so that the comparison is made with the rule you priced.

## Task B, run it and read what it says

Running `make evaluate` prints a table and the paired comparisons and writes `outputs/evaluation.json` and `outputs/evaluation_folds.csv`, the second holding one row for every fold and candidate. On the reference cleaning the run takes about five seconds and prints the following.

                              ROC-AUC      sd    PR-AUC   floor   lift
    the rule                   0.5951  0.0291    0.2300  0.1900   1.21
    your pipeline              0.6188  0.0348    0.2623  0.1900   1.38
    class_weight balanced      0.6188  0.0335    0.2639  0.1900   1.39
    decision tree, depth 4     0.5861  0.0326    0.2342  0.1900   1.23
    paired with your pipeline, ROC-AUC on the same 25 folds
    class_weight balanced     +0.0001  sd 0.0023  higher in 13 of 25
    decision tree, depth 4    -0.0327  sd 0.0286  higher in  3 of 25
    the rule                  -0.0236  sd 0.0236  higher in  6 of 25

Your numbers move with your cleaning and your features, so the table above shows only what the reference cleaning gives.

Every sd is `np.std` over the 25 folds, which divides by 25, while the `.std()` of pandas divides by 24 and gives a slightly larger number, so you should say which of the two you use if you compute your own.

Read your numbers by asking which of the three differences is larger than its sd, whether your pipeline beats your own one-line rule in most folds and by how much, and what the lift says that PR-AUC alone does not, and write the answers down because the note asks for them.

## Task C, start the evaluation note

Copy `docs/evaluation_template.md` to `docs/evaluation_note.md` and start the note, which has five sections, each described in the homework. Sections 1 and 2 need only this lab's output, so they are the ones to finish before you leave.

## Before you leave

The command `make verify` runs the script twice and checks that the two runs wrote the same files. With every earlier week finished, `make test` ends at 49 passed and 1 failed, where the failed test is the one for the note, which is homework. Commit `src/evaluate.py` as soon as this week's other five tests pass.
