# SPC5002 Week 8 homework

The homework has three parts that together take about five hours beyond the Friday lab, and only the first is code, most of which you write in the lab.

| Part | What | Where | About |
|---|---|---|---|
| A | `src/evaluate.py`, finished and committed | `src/evaluate.py` | done in the lab |
| B | the evaluation note, one to two pages | `docs/evaluation_note.md` | 4 hours |
| C | the guest's section of your speaker grid | `docs/speaker_grid.md` | 30 minutes |

## Part A, src/evaluate.py

Fill in the four lines from the Friday lab, commit `src/evaluate.py`, make sure that `make evaluate` and `make verify` both pass, and add `make evaluate` to the section Running this in your README.

If your Week 6 rule was not footwear and apparel, `RULE` and `rule_scores` have to describe your own rule.

## Part B, the evaluation note

Copy `docs/evaluation_template.md` to `docs/evaluation_note.md` and write the note there, in prose, over one to two pages, and put a single table in it. Every number in sections 1 to 3 must come from your own `outputs/evaluation.json` or `outputs/evaluation_folds.csv`, and every sd there is `np.std` over the 25 folds. The note becomes the evaluation section of your final report, so write it for a reader who has not seen the module.

Section 1 says how the numbers were made, which means the folds, their number, how they were shuffled and stratified, and what each candidate is, in enough detail for a stranger to make the same 25 folds.

Section 2 holds the table, which gives each candidate's ROC-AUC with its sd and its PR-AUC with the floor and the lift.

Section 3 sets each alternative against your pipeline through the mean difference, its sd and the wins out of 25, and says which of the differences you would call a finding and why. Because the 25 folds share training orders, the differences are evidence but no statistical test, which you should say once, and no p-value should be quoted.

Section 4 takes one number that you reported before from a single split or without a spread, in Milestone 1, Milestone 2 or a homework, reports it again the Week 8 way and says whether your conclusion changes.

Section 5 names at least one thing that this evaluation cannot tell you and gives the reason. The folds mix orders from the whole year, for example, so they say nothing about how the model would do on next year's orders.

Section 3 is judged by whether a reader could tell, from what you wrote, which of your changes actually helped, and section 4 is judged by honesty, so a number that becomes less impressive when it is reported properly makes a good section 4.

## Part C, the speaker grid

Fill in the Week 9 section of `docs/speaker_grid.md` for the guest lecture, which means the six questions on the grid and a seventh of your own. After Week 8, question 5 is the one to push on, by asking how the guest checks their results and how they would notice an improvement that was not real.

## Committing and handing in

Make at least three commits, each recording one thing that you did. With every earlier week finished, `make test` ends at 50 passed, and this week's six tests pass on their own.

Until the GitHub setup is fixed, you hand in one zip of your repository on QMplus, made in the folder that holds `lab_week01`. The zip is under 2 MB, so a size of tens of megabytes means that `.venv` went in.

    zip -r homework.zip lab_week01 -x "lab_week01/.venv/*"   # Mac, Linux, JupyterHub
    tar -a -c -f homework.zip --exclude=.venv lab_week01      # Windows PowerShell
