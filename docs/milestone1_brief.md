# Milestone 1, the data audit

Practised on example files in the Thursday session of Week 3, and due before
the lecture on Thursday of Week 4, at 11:00. The exact date is on QMplus. Nothing is uploaded. Commit
`docs/milestone1_audit.md` and push it to your repository on github.qmul.ac.uk,
as in every week so far.

It is not marked on its own. It gets written feedback and it becomes the dataset
section of your final report, so it is worth doing once properly.

Two to four pages, in prose. A list is fine for the faults in part 3, as long as
every item says why.

## What it has to contain

### 1. A profile of both datasets

Produced by `src/profile.py`, not by hand. Point to `outputs/profile.json` and
pick out what matters, rather than pasting the whole thing in.

### 2. Your constraints, with reasons

What each column is allowed to be and why. At least one identity check. A
constraint you cannot justify in one line is an opinion, and writing them down is
how you find out which of yours are.

### 3. Every fault you found

For each one, what it is, how many rows, which check found it and which of your
other checks would have missed it, and what you propose to do about it.
Proposing to do nothing is allowed, and it has to be argued for.

### 4. Missingness

For every column with blanks, the mechanism you think produced them and your
evidence. On the penguins the evidence is in `Comments`, and more than one
mechanism sits behind the eleven missing sexes. On your retail data there are
forty-six blanks in one column and no evidence at all, and explaining why the
file you were handed in Week 1 had none of them is part of this.

### 5. The forty-six

What you now think about the unexplained `marketing_opt_in` values, having
profiled everything else. This is the third week they have come up, and it is the
week you take a position.

### 6. Three questions you cannot answer from the data

Each one addressed to a named role. The CRM owner is a role, and someone is not.

### The annotator exercise

Half a page. Code the ten comments yourself with `python src/agreement.py` and
put your letters beside the two readings from Thursday. Which comments you
hesitated over, where you differ from the readings and why, and what you would
do if you had to code all 344 rows by tomorrow. The useful
question is not who was right. It is what would have had to be recorded at the
time for the question not to arise.

## Where the marks will be

When this becomes part of your final report, parts 3 and 6 carry most of the
marks. Part 1 is a script running, and anyone can list seventeen broken rows.
Saying which check found them, which check would have missed them, and what you
propose to do about them is the audit. The three questions in part 6 are the
fastest way for a reader to tell whether you understood the data or described it.

Two of you can decide differently about the same fault and both be right. The
reasoning is what gets read.

## What to avoid

Imputing anything before you have said what you think caused the blank. Deleting
rows without counting them. Calling a dataset clean because it has no nulls.
Reporting a constraint that passed as though it were nothing, when a rule that
passed is evidence and worth a sentence.
