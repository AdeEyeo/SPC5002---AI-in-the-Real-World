SPC5002 WEEK 8, WHAT IS IN THIS FOLDER AND WHAT YOU HAVE TO DO

WHAT THE WEEK IS ABOUT

This week you evaluate your own pipeline in a way that you can defend. Your
pipeline from Week 5, two alternatives and your Week 6 rule are scored on the
same 25 folds, which are 5 stratified folds shuffled with 5 different seeds,
and every score is reported together with its spread over those folds. PR-AUC
is reported beside its floor, which is the share of returned orders in the
test fold, and each alternative is compared with your pipeline fold by fold,
so that you can say which of your changes actually helped.

In the Friday lab you fill in the code and start the written note, and the
homework then finishes both and adds a section of your speaker grid for the
Week 9 guest lecture. Everything is done inside the repository that you built
in the earlier weeks, and this folder is copied into it once.

WHAT IS IN THIS FOLDER

The folder holds the following files, and the paragraphs after the listing say
what each of them is.

    lab_week08/
        README_week08.txt
        Makefile
        requirements.txt
        .gitignore
        data/penguins_raw.csv
        data/PENGUINS_SOURCE.md
        docs/week08_brief.md
        docs/week08_homework.md
        docs/evaluation_template.md
        docs/week08_slide_code.md
        src/evaluate.py
        src/verify.py
        tests/test_week8_contract.py

The file src/evaluate.py is the code you work on this week and is written for
you except for four lines marked TODO or FIX. Once those lines are filled in,
it scores your pipeline, two alternatives and your Week 6 rule on the same 25
folds and writes outputs/evaluation.json and outputs/evaluation_folds.csv,
which your evaluation note quotes.

The file src/verify.py is supplied and is not yours to write, and make verify
runs it, so that src/evaluate.py is run twice and the two runs are checked for
having written the same files. The Makefile collects the commands of every
week into targets such as make evaluate, make verify and make test, and
requirements.txt lists the packages with their exact versions, none of which
is new this week.

The folder tests holds six tests that you did not write and may not change.
They assert no score, since your cleaning and your features are yours, but
five of them run src/evaluate.py and check that it writes its report, that its
25 folds are 25 different folds, that every floor is the share of returns in
its own test fold, that the paired differences and the wins match the per-fold
scores, and that two runs agree, while the sixth checks that your evaluation
note exists with its five sections.

The folder docs holds the documents of the week. The brief,
docs/week08_brief.md, is the instruction sheet for the Friday lab, the
homework, docs/week08_homework.md, says what you hand in, and the template,
docs/evaluation_template.md, is the starting point of your evaluation note.
The file docs/week08_slide_code.md repeats every code box of the Friday
slides, so that you can copy the code with its indentation intact.

The folder data holds the penguin files, which are copied again unchanged, and
data/PENGUINS_SOURCE.md says where they come from.

HOW TO PUT THE FOLDER INTO YOUR REPOSITORY

Copy everything inside lab_week08 into your repository once only, because a
second copy would replace your filled-in src/evaluate.py with the empty one.
Run the commands below in a terminal, in the folder that holds both lab_week01
and lab_week08.

    cp -R lab_week08/. lab_week01/
    cd lab_week01
    source .venv/bin/activate          # Windows: .venv\Scripts\activate
    make test
    make evaluate
    git add -A
    git commit -m "Add the Week 8 lab"

On Windows you drag everything from lab_week08 into your repository in
Explorer, say yes to replacing, and run the remaining commands in PowerShell.
If make is not installed, you can run python src/evaluate.py in place of make
evaluate, python src/verify.py in place of make verify and python -m pytest -q
in place of make test.

The script src/evaluate.py builds on your Week 5 src/features.py and reads
data/orders_clean.csv, so both files have to be in the repository. Before any
line is filled in, the command python -m pytest -q
tests/test_week8_contract.py reports 1 failed and 5 errors, and make evaluate
stops at the first empty line, as it should.

WHAT YOU DO IN THE FRIDAY LAB

The lab has three tasks, A, B and C, and the full wording of each is in
docs/week08_brief.md.

Task A is to fill in the four lines of src/evaluate.py that are marked TODO or
FIX, and each of them repeats a line that you wrote in Thursday's notebook. In
folds, the line marked FIX must use the seed of its pass in place of the fixed
random_state=0, because as given the 25 folds are the same 5 folds five times.
In fold_rows, the line marked TODO sets floor to the share of returned orders
in the test fold. In paired, the line diffs is the difference fold by fold,
this candidate minus your pipeline, and the line wins is the number of folds
in which this candidate is higher, which must be a single number. If your Week
6 rule was not footwear and apparel, you also change RULE and rule_scores at
the top of the file so that they describe your own rule.

Task B is to run make evaluate and read what it prints, which is a table with
the ROC-AUC and its sd and the PR-AUC with its floor and lift for the rule,
your pipeline and the two alternatives, followed by the three paired
comparisons with your pipeline. Read it by asking which of the three
differences is larger than its sd, whether your pipeline beats your own
one-line rule in most folds and by how much, and what the lift says that
PR-AUC alone does not, and write the answers down because the note asks for
them.

Task C is to copy docs/evaluation_template.md to docs/evaluation_note.md and
start the note, whose sections 1 and 2 can be written from this lab's output
alone.

Before you leave the lab, run make verify, which should end with the line the
two runs match, and commit src/evaluate.py once this week's other five tests
pass.

WHAT YOU HAVE TO HAND IN

The homework has three parts that together take about five hours beyond the
Friday lab. Part A is the finished and committed src/evaluate.py, which means
that the four lines are filled in, that make evaluate and make verify pass,
that RULE and rule_scores describe your own Week 6 rule if it was not footwear
and apparel, and that make evaluate is listed under Running this in your
README.

Part B is the evaluation note in docs/evaluation_note.md, which is written in
prose over one to two pages, holds a single table and is aimed at a reader who
has not seen the module, since it becomes the evaluation section of your final
report. Every number in sections 1 to 3 comes from your own
outputs/evaluation.json or outputs/evaluation_folds.csv, and every sd is
np.std over the 25 folds. The note has five numbered sections.

Section 1 says how the numbers were made, which means the folds, their number,
how they were shuffled and stratified, and what each candidate is, in enough
detail for a stranger to make the same 25 folds. Section 2 holds the table
with each candidate's ROC-AUC and its sd and its PR-AUC with the floor and the
lift.

Section 3 sets each alternative against your pipeline through the mean
difference, its sd and the wins out of 25, and says which of the differences
you would call a finding and why. Because the 25 folds share training orders,
the differences are evidence but no statistical test, which you say once, and
you quote no p-value.

Section 4 takes one number that you reported before from a single split or
without a spread, in Milestone 1, Milestone 2 or a homework, reports it again
the Week 8 way and says whether your conclusion changes. Section 5 names at
least one thing that this evaluation cannot tell you and gives the reason. The
folds mix orders from the whole year, for example, so they say nothing about
how the model would do on next year's orders.

Section 3 is judged by whether a reader could tell, from what you wrote, which
of your changes actually helped, and section 4 is judged by honesty, so a
number that becomes less impressive when it is reported properly makes a good
section 4.

Part C is the Week 9 section of docs/speaker_grid.md for the guest lecture,
which means the six questions on the grid and a seventh of your own. After
Week 8, question 5 is the one to push on, by asking how the guest checks their
results and how they would notice an improvement that was not real.

WHEN THE ASSIGNMENT IS COMPLETE

Your repository then holds a finished and committed src/evaluate.py that
passes make evaluate and make verify, an evaluation note of one to two pages
with its five numbered sections and one table, a filled Week 9 section in
docs/speaker_grid.md, a README that lists make evaluate, and at least three
commits that each record one thing you did. With every earlier week finished,
make test ends at 50 passed, and this week's six tests pass on their own.

HOW YOU HAND IN

Until the GitHub setup is fixed, you hand in one zip of your repository on
QMplus, made in the folder that holds lab_week01. The zip is under 2 MB, so a
size of tens of megabytes means that .venv went in. Check the repository with
git status and git log --oneline, then move up one folder and make the zip
with the command for your system.

    git status
    git log --oneline
    cd ..
    zip -r homework.zip lab_week01 -x "lab_week01/.venv/*"   # Mac, Linux, JupyterHub
    tar -a -c -f homework.zip --exclude=.venv lab_week01      # Windows PowerShell
