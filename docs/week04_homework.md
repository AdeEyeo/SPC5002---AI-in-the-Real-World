# Week 4 homework

Due Thursday 11:00 of Week 5, before the lecture. The exact date is on QMplus.
Until the GitHub setup is fixed, hand in one zip of your repository on QMplus,
made as `docs/week04_brief.md` says. Once GitHub works, push to the same
repository on github.qmul.ac.uk instead.

About eight hours, Friday's lab included.

## 1. Finish the cleaning and the leak lab

`make clean-data` and `make leak-lab` run from a clean clone. With Weeks 1 to 3
finished, `make test` shows 30 passed, and this week's eight pass on their own
with `python -m pytest -q tests/test_week4_contract.py`. `make verify`, or
`python src/verify.py`, prints six hashes and `the two runs match`.

Add both targets to the Running this section of your `README.md`, for somebody
who clones the repository and will not email you.

## 2. `docs/cleaning_decisions.md`

One section per decision.

- what you did
- why
- what the alternative was
- **what would make you change your mind**

The last one is what gets read. A decision with no condition attached to it is a
preference.

Add the two sentences from Friday's Task C, on why one measurement gives nothing
and the other does not.

## 3. The imputation you did not do

Pick a column you chose to leave alone. One paragraph on what filling it would
have cost, stated in terms of something somebody would later measure rather than
in terms of the model.

The penguins are the worked example. Filling eleven blank sexes with the mode
shrinks the measured sexual dimorphism from 683.4 g to 655.9 g, on a dataset
collected to measure exactly that. Yours should be about the retail data.

## 4. The two measurements

Report both from `outputs/leak_lab.json`, each with its spread. If your numbers
differ from the lecture's, that is expected and interesting, so say why they
might.

Be careful about what you conclude from a difference smaller than its own
standard deviation. That is the whole of Week 8, arriving early.

## 5. Six commits

Each one a thing you did.

## Optional

The scaler measurement found nothing because a logistic regression puts the
shift a scaler applies into its intercept, and only the order of its scores
reaches the ROC-AUC. Swap the classifier for one that measures distances, such as
`KNeighborsClassifier(25)`, change nothing else, and see whether the gap is still
zero.

Then say what that tells you about how far the result generalises. It is a
result about a model, not about a rule.
