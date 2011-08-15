#!/usr/bin/make

BOOTSTRAP_PYTHON=python
PASTE_INI_FILE=development.ini

.PHONY: all
all: build

.PHONY: build
build: bin/paster

.PHONY: bootstrap
bootstrap bin/buildout:
	$(BOOTSTRAP_PYTHON) bootstrap.py

.PHONY: buildout
buildout bin/paster bin/nosetests: bin/buildout buildout.cfg bootstrap.py
	bin/buildout

.PHONY: run
run: build
	bin/paster serve $(PASTE_INI_FILE) --reload

.PHONY: clean
clean:
	rm -f .installed.cfg
	rm -rf bin
	rm -rf parts
	rm -rf pyquiz.egg-info
	rm -rf develop-eggs
	rm -f .coverage
	rm -rf python

.PHONY: realclean
realclean: clean
	rm -rf eggs
	rm -rf var/Data.fs*
	rm -rf src/pyquiz
	find . -name '*.py[co]' -exec rm -f {} \;
	find . -name '*.mo' -exec rm -f {} +
	find . -name 'LC_MESSAGES' -exec rmdir -p --ignore-fail-on-non-empty {} +


# Tests

.PHONY: test
test: bin/nosetests
	bin/nosetests


# Translations

.PHONY: init-catalog
init-catalog: build
	bin/python setup.py init_catalog --locale=$(LOCALE)

.PHONY: extract-translations
extract-translations: build
	bin/python setup.py extract_messages

.PHONY: update-translations
update-translations: extract-translations
	bin/python setup.py update_catalog

.PHONY: compile-translations
compile-translations:
	bin/python setup.py compile_catalog


# Helpers

.PHONY: ubuntu-environment
ubuntu-environment:
	sudo apt-get install build-essential python-all-dev \
	libc6-dev gettext libicu-dev libjpeg62-dev
