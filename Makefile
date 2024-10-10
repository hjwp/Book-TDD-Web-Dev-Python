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
	$(VENV)/bin/pytest --tb=short --color=yes tests/

.PHONY: testall
testall: build
	$(VENV)/bin/pytest --tb=short --color=yes --numprocesses=auto tests/test_chapter_*

.PHONY: testall4
testall4: build
	$(VENV)/bin/pytest --tb=short --color=yes --numprocesses=4 tests/test_chapter_*


.PHONY: test_%
test_%: %.html $(TMPDIR)
	$(VENV)/bin/pytest -s --tb=short ./tests/$@.py

.PHONY: clean-docker
clean-docker:
	docker ps -q || docker kill $$(docker ps -q)
	docker rmi -f busybox 
	docker rmi -f superlists 
	# env PATH=misc:$PATH

# exhaustively list all test targets for nice tab-completion
.PHONY: test_chapter_01
test_chapter_01: chapter_01.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_01.py
.PHONY: test_chapter_02_unittest
test_chapter_02_unittest: chapter_02_unittest.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_02_unittest.py
.PHONY: test_chapter_03_unit_test_first_view
test_chapter_03_unit_test_first_view: chapter_03_unit_test_first_view.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_03_unit_test_first_view.py
.PHONY: test_chapter_04_philosophy_and_refactoring
test_chapter_04_philosophy_and_refactoring: chapter_04_philosophy_and_refactoring.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_04_philosophy_and_refactoring.py
.PHONY: test_chapter_05_post_and_database
test_chapter_05_post_and_database: chapter_05_post_and_database.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_05_post_and_database.py
.PHONY: test_chapter_06_explicit_waits_1
test_chapter_06_explicit_waits_1: chapter_06_explicit_waits_1.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_06_explicit_waits_1.py
.PHONY: test_chapter_07_working_incrementally
test_chapter_07_working_incrementally: chapter_07_working_incrementally.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_07_working_incrementally.py
.PHONY: test_chapter_08_prettification
test_chapter_08_prettification: chapter_08_prettification.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_08_prettification.py
.PHONY: test_chapter_09_docker
test_chapter_09_docker: chapter_09_docker.html $(TMPDIR) $(VENV)/bin clean-docker
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_09_docker.py
.PHONY: test_chapter_10_production_readiness
test_chapter_10_production_readiness: chapter_10_production_readiness.html $(TMPDIR) $(VENV)/bin clean-docker
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_10_production_readiness.py
.PHONY: test_chapter_11_ansible
test_chapter_11_ansible: chapter_11_ansible.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_11_ansible.py
.PHONY: test_chapter_12_organising_test_files
test_chapter_12_organising_test_files: chapter_12_organising_test_files.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_12_organising_test_files.py
.PHONY: test_chapter_13_database_layer_validation
test_chapter_13_database_layer_validation: chapter_13_database_layer_validation.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_13_database_layer_validation.py
.PHONY: test_chapter_14_simple_form
test_chapter_14_simple_form: chapter_14_simple_form.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_14_simple_form.py
.PHONY: test_chapter_15_advanced_forms
test_chapter_15_advanced_forms: chapter_15_advanced_forms.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_15_advanced_forms.py
.PHONY: test_chapter_16_javascript
test_chapter_16_javascript: chapter_16_javascript.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_16_javascript.py
.PHONY: test_chapter_17_second_deploy
test_chapter_17_second_deploy: chapter_17_second_deploy.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_17_second_deploy.py
.PHONY: test_chapter_18_spiking_custom_auth
test_chapter_18_spiking_custom_auth: chapter_18_spiking_custom_auth.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_18_spiking_custom_auth.py
.PHONY: test_chapter_19_mocking_1
test_chapter_19_mocking_1: chapter_19_mocking_1.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_19_mocking_1.py
.PHONY: test_chapter_20_mocking_2
test_chapter_20_mocking_2: chapter_20_mocking_2.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_20_mocking_2.py
.PHONY: test_chapter_20_fixtures_and_wait_decorator
test_chapter_20_fixtures_and_wait_decorator: chapter_20_fixtures_and_wait_decorator.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_20_fixtures_and_wait_decorator.py
.PHONY: test_chapter_21_server_side_debugging
test_chapter_21_server_side_debugging: chapter_21_server_side_debugging.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_21_server_side_debugging.py
.PHONY: test_chapter_22_outside_in
test_chapter_22_outside_in: chapter_22_outside_in.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_22_outside_in.py
.PHONY: test_chapter_23_CI
test_chapter_23_CI: chapter_23_CI.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_23_CI.py
.PHONY: test_chapter_24_page_pattern
test_chapter_24_page_pattern: chapter_24_page_pattern.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_chapter_24_page_pattern.py


.PHONY: test_appendix_purist_unit_tests
test_appendix_purist_unit_tests: appendix_purist_unit_tests.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest -s --tb=short ./tests/test_appendix_purist_unit_tests.py

.PHONY: silent_test_%
silent_test_%: %.html $(TMPDIR) $(VENV)/bin
	$(VENV)/bin/pytest --tb=short ./tests/$(subst silent_,,$@).py

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
