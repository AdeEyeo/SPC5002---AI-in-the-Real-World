# SPC5002. One Makefile, and it grows with the repository.
#
# Each week's zip replaces this file with a longer version of itself. Every
# target you have ever been given still works, which is the point: the Week 12
# check clones your repository and runs `make setup && make run`, and `make run`
# was a Week 1 target.
#
# If you cannot say what a target does, ask on the Friday.

PY := python

# `python` only exists once the virtual environment is activated. Without this
# check, make prints "python: No such file or directory", which does not tell
# you that the fix is `source .venv/bin/activate`.
ifeq (,$(shell command -v $(PY) 2>/dev/null))
  ifneq (,$(shell command -v python3 2>/dev/null))
    PY := python3
  endif
endif

.PHONY: help setup test clean verify run ingest profile check agree

help:
	@echo "make run          run the Week 1 script, write outputs/metrics.json"
	@echo "make ingest       read the three sources, join, write the report and the joined table"
	@echo "make profile      profile both datasets, write outputs/profile.json"
	@echo "make check        run your constraints, write outputs/violations.csv"
	@echo "make agree        code the ten comments on your own, in silence"
	@echo ""
	@echo "make test         run every contract test in the repository"
	@echo "make verify       run profile and check twice and compare the outputs"
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

# the one that matters. It runs this week's two scripts twice, hashes the two
# files they write, and exits non-zero when the two runs differ: a check you
# cannot fail is not a check.
OUTS := outputs/profile.json outputs/violations.csv

verify:
	@$(PY) src/profile.py > /dev/null && $(PY) src/constraints.py > /dev/null
	@A=$$(shasum -a 256 $(OUTS) 2>/dev/null || sha256sum $(OUTS)); \
	 $(PY) src/profile.py > /dev/null && $(PY) src/constraints.py > /dev/null || exit 1; \
	 B=$$(shasum -a 256 $(OUTS) 2>/dev/null || sha256sum $(OUTS)); \
	 echo "$$A"; echo "$$B"; \
	 if [ "$$A" = "$$B" ]; then \
	   echo "the two runs match"; \
	 else \
	   echo "THE TWO RUNS DIFFER. Something in your code is not seeded,"; \
	   echo "or depends on the order a set or dict happened to be in,"; \
	   echo "or writes the time it ran."; \
	   exit 1; \
	 fi
