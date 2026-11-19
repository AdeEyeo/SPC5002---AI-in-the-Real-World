# SPC5002 has one Makefile, and it grows with the repository because each week's
# zip replaces it with a longer version of itself.
#
# Every target you have ever been given still works, and this matters because
# the Week 12 check clones your repository and runs `make setup && make run`,
# where `make run` was a Week 1 target.
#
# If you cannot say what a target does, ask a demonstrator in the Friday lab.

PY := python

# The command `python` exists only once the virtual environment is activated, and
# the check below falls back to `python3` when it is missing, since otherwise make
# prints "python: No such file or directory", which does not tell you that the
# fix is `source .venv/bin/activate`.
ifeq (,$(shell command -v $(PY) 2>/dev/null))
  ifneq (,$(shell command -v python3 2>/dev/null))
    PY := python3
  endif
endif

.PHONY: help setup test clean verify run ingest profile check agree clean-data leak-lab features encoding-lab imbalance evaluate

help:
	@echo "make run          run the Week 1 script, write outputs/metrics.json"
	@echo "make ingest       read the three sources, join, write the report and the joined table"
	@echo "make profile      profile both datasets, write outputs/profile.json"
	@echo "make check        run your constraints, write outputs/violations.csv"
	@echo "make agree        code the ten comments on your own, in silence"
	@echo "make clean-data   run your cleaning, write outputs/orders_clean.csv and the ledger"
	@echo "make leak-lab     clean, then the two Week 4 measurements, write outputs/leak_lab.json"
	@echo "make features     fit the feature pipeline, score it with and without dates, write outputs/features.json"
	@echo "make encoding-lab three encodings of the customer, random and grouped, write outputs/encoding_lab.json"
	@echo "make imbalance    baselines, class weights and the matching threshold, write outputs/imbalance.json"
	@echo "make evaluate     your pipeline, two alternatives and your rule on the same 25 folds, write outputs/evaluation.json"
	@echo ""
	@echo "make test         run every contract test in the repository"
	@echo "make verify       run the evaluation script twice and compare the outputs"
	@echo "make clean        delete outputs and caches"

setup:
	$(PY) -m pip install -r requirements.txt

test:
	$(PY) -m pytest -q

clean:
	rm -rf outputs .pytest_cache
	find . -name '__pycache__' -type d -exec rm -rf {} +
	find . -name '.ipynb_checkpoints' -type d -exec rm -rf {} +

run:
	$(PY) src/run.py

ingest:
	$(PY) src/ingest.py

profile:
	$(PY) src/profile.py

check:
	$(PY) src/constraints.py

agree:
	$(PY) src/agreement.py

clean-data:
	$(PY) src/cleaning.py

# The leak lab reads the cleaned table, so this target runs the cleaning step
# before it starts the lab.
leak-lab: clean-data
	$(PY) src/leak_lab.py

features:
	$(PY) src/features.py

encoding-lab:
	$(PY) src/encoding_lab.py

imbalance:
	$(PY) src/imbalance.py

evaluate:
	$(PY) src/evaluate.py

# This is the target that matters. It runs this week's script twice, hashes the
# files it writes and exits non-zero when the two runs differ, because a check
# that cannot fail is not a check. The work is done in src/verify.py, which is
# supplied so that Windows, where make is usually missing, can run
# python src/verify.py.
verify:
	@$(PY) src/verify.py
