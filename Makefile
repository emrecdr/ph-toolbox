#!make
-include .env
export $(shell sed 's/=.*//' .env)
PYTHONPATH = ${PWD}
export PYTHONPATH


PWD ?= pwd_unknown
PROJECT_NAME = $(notdir $(PWD))


.PHONY: dev-up
dev-up:
	pipenv install --dev

requirements.txt: Pipfile
	pipenv lock -r > requirements.txt

.PHONY: test-clean
test-clean: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr .htmlcov/
	rm -fr .htmlpytest/
	rm -fr .pytest_cache

.PHONY: test
test:
	mkdir -p .htmlpytest
	mkdir -p .htmlcov
	pipenv run pytest -v

.PHONY: test-clean-run
test-clean-run: test-clean test

.PHONY: test-pdb
test-pdb:
	pipenv run pytest -xvv --tb=short --log-file-level=DEBUG --pdb

.PHONY: show-cov
show-cov:
	pipenv run python -c "import webbrowser; webbrowser.open_new_tab('file://${PWD}/.htmlcov/index.html')"

.PHONY: show-tests
show-tests:
	pipenv run python -c "import webbrowser; webbrowser.open_new_tab('file://${PWD}/.htmlpytest/report.html')"

.PHONY: lint
lint:
	pipenv run pre-commit run --hook-stage=manual --all-files
