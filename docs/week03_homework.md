# Week 3 homework

Due Thursday 11:00 of Week 4, before the lecture. The exact date is on QMplus.
Nothing is uploaded. Push to the same repository on github.qmul.ac.uk, over SSH,
and the URL you gave on QMplus in Week 1 still stands.

Milestone 1 is the homework. Budget about eight hours, Thursday's session
included.

## 1. Finish Milestone 1

`docs/milestone1_audit.md`, against `docs/milestone1_brief.md`, with the
annotator exercise in it.

## 2. Make it run from a clean clone

`make profile`, `make check` and this week's seven tests run from a fresh clone,
`python -m pytest -q tests/test_week3_contract.py`. With Weeks 1 and 2 finished,
`make test` shows 22 passed.
`make verify` prints four hashes and `the two runs match`.

`data/orders_joined.csv` is committed, because a clean clone has no `outputs/`
and the Week 4 tests read the copy in `data/`.

## 3. The speaker grid

`docs/speaker_grid.md` has a section for each guest and the six questions every
guest is asked. Fill in this week's on Friday after the talk, and answer the
seventh question, which is for you alone, whether you could see yourself doing
that work and why. Four of these are what you choose a project from in the
spring, so keep it up.

## 4. Six commits

Each one a thing you did.
