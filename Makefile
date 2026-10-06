PYTHON = python3
PIP = $(PYTHON) -m pip
CONFIG = config.example.json
MAZE_WHEEL = mazegenerator-2.1.0-py3-none-any.whl

install:
	$(PIP) install -r requirements.txt
	$(PIP) install ./$(MAZE_WHEEL)

run:
	$(PYTHON) pac-man.py $(CONFIG) || True

debug:
	$(PYTHON) -m pdb pac-man.py $(CONFIG)

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf build dist

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict
