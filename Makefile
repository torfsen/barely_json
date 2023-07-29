PHONY: requirements

requirements-dev.txt: requirements-dev.in
	pip-compile -q requirements-dev.in

requirements-test.txt: requirements-test.in
	pip-compile -q requirements-test.in

requirements-tox.txt: requirements-tox.in
	pip-compile -q requirements-tox.in

requirements: requirements-dev.txt requirements-test.txt requirements-tox.txt
