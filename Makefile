PELICAN := .venv/bin/pelican
.PHONY: setup html preview publish check
setup:
	python3.12 -m venv .venv
	.venv/bin/python -m pip install -r requirements.txt
html:
	$(PELICAN) -s pelicanconf.py --fatal warnings
preview: html
	.venv/bin/python -m http.server 8000 --bind 127.0.0.1 --directory build
publish:
	$(PELICAN) -s publishconf.py --fatal warnings
check: publish
	.venv/bin/python tests/check.py
