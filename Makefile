include subtrees/z_quantum_actions/Makefile


coverage:
	qvm -S &
	quilc -S &
	$(PYTHON) -m pytest -m "not integration" \
		--cov=src \
		--cov-fail-under=$(MIN_COVERAGE) tests \
		--no-cov-on-fail \
		--cov-report xml \
		&& echo Code coverage Passed the $(MIN_COVERAGE)% mark!

github_actions-default:
	apt-get update
	apt-get install -y python3.7-venv

	# For some reason, having numpy installed globally makes mypy fail.
	python3 -m pip uninstall -y numpy

	python3 -m venv ${VENV} && \
		${VENV}/bin/python3 -m pip install --upgrade pip && \
		${VENV}/bin/python3 -m pip install ./z-quantum-core && \
		${VENV}/bin/python3 -m pip install -e '.[develop]'

	# For some reason, mypy fails unless we re-install ruamel.yaml.
	${VENV}/bin/python3 -m pip uninstall -y ruamel.yaml
	${VENV}/bin/python3 -m pip install ruamel.yaml

build-system-deps:
	$(PYTHON) -m pip install setuptools wheel "setuptools_scm>=6.0"
