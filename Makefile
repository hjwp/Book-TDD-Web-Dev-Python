SHELL := /bin/bash

SOURCES := $(wildcard *.asciidoc)
HTML_PAGES := $(patsubst %.asciidoc, %.html, ${SOURCES})
TESTS := $(patsubst %.asciidoc, test_%, ${SOURCES})
VENV ?= .venv

RUN_ASCIIDOCTOR = asciidoctor -a source-highlighter=pygments -a pygments-style=default -a stylesheet=asciidoctor.css -a linkcss -a icons=font -a compat-mode -a '!example-caption' -a last-update-label='License: Creative Commons <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode">CC-BY-NC-ND</a>. Last updated:'

export PYTHONHASHSEED = 0
export PYTHONDONTWRITEBYTECODE = 1
export MOZ_HEADLESS = 1
# for warning introduce in selenium 4.10
export PYTHONWARNINGS=ignore::ResourceWarning

export TMPDIR_CLEANUP = false

part%.forbook.asciidoc: part%.asciidoc
	cat $(subst .forbook.,.,$@)  \
		| sed 's/^== /= /' \
		| sed '/partintro/d' \
		| sed '/^--$$/d' \
		> $@



book.html: part1.forbook.asciidoc
book.html: part2.forbook.asciidoc
book.html: part3.forbook.asciidoc
book.html: part4.forbook.asciidoc
book.html: $(SOURCES)


%.html: %.asciidoc  # build an individual chapter's html page
	$(RUN_ASCIIDOCTOR) $<

.PHONY: build
build: $(HTML_PAGES) $(TMPDIR)


$(VENV)/bin:
	which uv && uv venv $(VENV)|| python3 -m venv $(VENV)
	which uv && uv pip install -e . || $(VENV)/bin/pip install -e .

.PHONY: install
install: $(VENV)/bin
	which brew && brew install asciidoctor tree || apt install -y asciidoctor tree

.PHONY: update-submodules
update-submodules:
	git submodule update --init --recursive
	$(VENV)/bin/python tests/update_source_repo.py

# this is to allow for a git remote called "local" for eg ./source/feed-thru-cherry-pick.sh
../book-example.git:
	mkdir -p ../book-example.git
	git init --bare ../book-example.git

.PHONY: test
test: build update-submodules $(VENV)/bin
	$(VENV)/bin/pytest tests/

.PHONY: testall
testall: build
	$(VENV)/bin/pytest --numprocesses=auto tests/test_chapter_*

.PHONY: testall4
testall4: build
	$(VENV)/bin/pytest --numprocesses=4 tests/test_chapter_*


.PHONY: test_%
test_%: %.html $(TMPDIR)
	$(VENV)/bin/pytest -s --no-summary ./tests/$@.py

.PHONY: xmllint_%
xmllint_%: %.asciidoc
	asciidoctor -b docbook $< -o - | sed \
		-e 's/&mdash;/\&#8212;/g' \
		-e 's/&ldquo;/\&#8220;/g' \
		-e 's/&rdquo;/\&#8221;/g' \
		-e 's/&lsquo;/\&#8216;/g' \
		-e 's/&rsquo;/\&#8217;/g' \
		-e 's/&hellip;/\&#8230;/g' \
		-e 's/&nbsp;/\&#160;/g' \
		-e 's/&times;/\&#215;/g' \
		| xmllint --noent --noout -


%.xml: %.asciidoc
	asciidoctor -b docbook $<

.PHONY: check-links
check-links: book.html
	python check-links.py book.html

.PHONY: clean-docker
clean-docker:
	-docker kill $$(docker ps -q)
	docker rmi -f busybox
	docker rmi -f superlists
	# env PATH=misc:$PATH

.PHONY: get-sudo
get-sudo:
	sudo echo 'need sudo access for this test'

.PHONY: no-runservers
no-runservers:
	-pkill -f runserver

# exhaustively list all test targets for nice tab-completion
.PHONY: test_chapter_01
test_chapter_01: chapter_01.html $(TMPDIR) $(VENV)/bin no-runservers
	$(VENV)/bin/pytest -s ./tests/test_chapter_01.py
.PHONY: test_chapter_02_unittest
test_chapter_02_unittest: chapter_02_unittest.html $(TMPDIR) $(VENV)/bin no-runservers
	$(VENV)/bin/pytest -s ./tests/test_chapter_02_unittest.py
.PHONY: test_chapter_03_unit_test_first_view
test_chapter_03_unit_test_first_view: chapter_03_unit_test_first_view.html $(TMPDIR) $(VENV)/bin no-runservers
	$(VENV)/bin/pytest -s ./tests/test_chapter_03_unit_test_first_view.py
.PHONY: test_chapter_04_philosophy_and_refactoring
test_chapter_04_philosophy_and_refactoring: chapter_04_philosophy_and_refactoring.html $(TMPDIR) $(VENV)/bin no-runservers
	$(VENV)/bin/pytest -s ./tests/test_chapter_04_philosophy_and_refactoring.py
.PHONY: test_chapter_05_post_and_database
test_chapter_05_post_and_database: chapter_05_post_and_database.html $(TMPDIR) $(VENV)/bin no-runservers
	$(VENV)/bin/pytest -s ./tests/test_chapter_05_post_and_database.py
.PHONY: test_chapter_06_explicit_waits_1
test_chapter_06_explicit_waits_1: chapter_06_explicit_waits_1.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_06_explicit_waits_1.py
.PHONY: test_chapter_07_working_incrementally
test_chapter_07_working_incrementally: chapter_07_working_incrementally.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_07_working_incrementally.py
.PHONY: test_chapter_08_prettification
test_chapter_08_prettification: chapter_08_prettification.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_08_prettification.py
.PHONY: test_chapter_09_docker
test_chapter_09_docker: chapter_09_docker.html $(TMPDIR) $(VENV)/bin clean-docker
	$(VENV)/bin/pytest -s ./tests/test_chapter_09_docker.py
.PHONY: test_chapter_10_production_readiness
test_chapter_10_production_readiness: get-sudo chapter_10_production_readiness.html $(TMPDIR) $(VENV)/bin clean-docker
	$(VENV)/bin/pytest -s ./tests/test_chapter_10_production_readiness.py
.PHONY: test_chapter_11_server_prep
test_chapter_11_server_prep: chapter_11_server_prep.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_11_server_prep.py
.PHONY: test_chapter_13_organising_test_files
.PHONY: test_chapter_12_ansible
test_chapter_12_ansible: chapter_12_ansible.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_12_ansible.py
.PHONY: test_chapter_13_organising_test_files
test_chapter_13_organising_test_files: chapter_13_organising_test_files.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_13_organising_test_files.py
.PHONY: test_chapter_14_database_layer_validation
test_chapter_14_database_layer_validation: chapter_14_database_layer_validation.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_14_database_layer_validation.py
.PHONY: test_chapter_15_simple_form
test_chapter_15_simple_form: chapter_15_simple_form.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_15_simple_form.py
.PHONY: test_chapter_16_advanced_forms
test_chapter_16_advanced_forms: chapter_16_advanced_forms.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_16_advanced_forms.py
.PHONY: test_chapter_17_javascript
test_chapter_17_javascript: chapter_17_javascript.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_17_javascript.py
.PHONY: test_chapter_18_second_deploy
test_chapter_18_second_deploy: chapter_18_second_deploy.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_18_second_deploy.py
.PHONY: test_chapter_19_spiking_custom_auth
test_chapter_19_spiking_custom_auth: chapter_19_spiking_custom_auth.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_19_spiking_custom_auth.py
.PHONY: test_chapter_20_mocking_1
test_chapter_20_mocking_1: chapter_20_mocking_1.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_20_mocking_1.py
.PHONY: test_chapter_21_mocking_2
test_chapter_21_mocking_2: chapter_21_mocking_2.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_21_mocking_2.py
.PHONY: test_chapter_22_fixtures_and_wait_decorator
test_chapter_22_fixtures_and_wait_decorator: chapter_22_fixtures_and_wait_decorator.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_22_fixtures_and_wait_decorator.py
.PHONY: test_chapter_23_debugging_prod
test_chapter_23_debugging_prod: get-sudo chapter_23_debugging_prod.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_23_debugging_prod.py
.PHONY: test_chapter_24_outside_in
test_chapter_24_outside_in: chapter_24_outside_in.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_24_outside_in.py
.PHONY: test_chapter_25_CI
test_chapter_25_CI: chapter_25_CI.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_25_CI.py
.PHONY: test_chapter_26_page_pattern
test_chapter_26_page_pattern: chapter_26_page_pattern.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_chapter_26_page_pattern.py


.PHONY: test_appendix_purist_unit_tests
test_appendix_purist_unit_tests: appendix_purist_unit_tests.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s ./tests/test_appendix_purist_unit_tests.py

.PHONY: silent_test_%
silent_test_%: %.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest ./tests/$(subst silent_,,$@).py

.PHONY: unit-test
unit-test: chapter_01.html $(VENV)/bin
	SKIP_CHAPTER_SUBMODULES=1 ./tests/update_source_repo.py
	source $(VENV)/bin/activate && ./run_test_tests.sh
	# this is a hack to make 'Archive the temp dir' step work in CI
	echo "tests" > .tmpdir.unit-test

.PHONY: clean
clean:
	rm -rf $(TMPDIR)
	rm -v $(HTML_PAGES)
