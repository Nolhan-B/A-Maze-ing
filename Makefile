
PYTHON = python3
PIP = pip
MAIN = a_maze_ing.py
CONFIG = config.txt

TRASH = __pycache__ .mypy_cache *.pyc

all: install run

# 1. INSTALL 
install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt


# 2. RUN
run:
	$(PYTHON) $(MAIN) $(CONFIG)

# 3. DEBUG
debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

# 4. CLEAN 
clean:
	rm -rf $(TRASH)
	find . -type d -name "__pycache__" -exec rm -rf {} +

# 5. LINT
lint:
	flake8 .
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

# 6. LINT-STRICT
lint-strict:
	flake8 .
	mypy --strict .

# .PHONY
.PHONY: all install run debug clean lint lint-strict