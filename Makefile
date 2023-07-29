PHONY: requirements

requirements-dev.txt:
	pip-compile -q requirements-dev.in

requirements-test.txt:
	pip-compile -q requirements-test.in

requirements-tox.txt:
	pip-compile -q requirements-tox.in

requirements: requirements-dev.txt requirements-test.txt requirements-tox.txt
