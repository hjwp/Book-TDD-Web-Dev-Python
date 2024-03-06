SOURCES := $(wildcard *.asciidoc)
HTML_PAGES := $(patsubst %.asciidoc, %.html, ${SOURCES})
TESTS := $(patsubst %.asciidoc, test_%, ${SOURCES})

RUN_ASCIIDOCTOR = asciidoctor -a source-highlighter=pygments -a pygments-style=default -a stylesheet=asciidoctor.css -a linkcss -a icons=font -a compat-mode -a '!example-caption' -a last-update-label='License: Creative Commons <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode">CC-BY-NC-ND</a>. Last updated:'
RUN_OREILLY_FLAVOURED_ASCIIDOCTOR = ./asciidoc/asciidoctor/bin/asciidoctor -v --trace -d book --safe -b htmlbook --template-dir ./asciidoc/asciidoctor-htmlbook/htmlbook 

export PYTHONHASHSEED = 0
export PYTHONDONTWRITEBYTECODE = 1
export MOZ_HEADLESS = 1
# for warning introduce in selenium 4.10
export PYTHONWARNINGS=ignore::ResourceWarning

# required for firefox snap to work via geckodriver.
export TMPDIR := $(HOME)/snap/firefox/common/tmp
$(TMPDIR):
	mkdir -p $(TMPDIR)

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

.PHONY: build
build: $(HTML_PAGES) $(TMPDIR)

.PHONY: test
test: build
	git submodule init
	python tests/update_source_repo.py
	pytest --tb=short --color=yes tests/

.PHONY: testall
testall: build
	pytest --tb=short --color=yes --numprocesses=auto tests/test_chapter_*

.PHONY: testall4
testall4: build
	pytest --tb=short --color=yes --numprocesses=4 tests/test_chapter_*

%.html: %.asciidoc
	$(RUN_ASCIIDOCTOR) $<

.PHONY: oreilly.%.asciidoc
oreilly.%.asciidoc: %.asciidoc
	$(RUN_OREILLY_FLAVOURED_ASCIIDOCTOR) $(subst oreilly.,,$@)


.PHONY: test_%
test_%: %.html $(TMPDIR)
	pytest -s --tb=short ./tests/$@.py

# exhaustively list for nice tab-completion
#
.PHONY: test_chapter_01
test_chapter_01: chapter_01.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_01.py
.PHONY: test_chapter_02_unittest
test_chapter_02_unittest: chapter_02_unittest.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_02_unittest.py
.PHONY: test_chapter_03_unit_test_first_view
test_chapter_03_unit_test_first_view: chapter_03_unit_test_first_view.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_03_unit_test_first_view.py
.PHONY: test_chapter_04_philosophy_and_refactoring
test_chapter_04_philosophy_and_refactoring: chapter_04_philosophy_and_refactoring.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_04_philosophy_and_refactoring.py
.PHONY: test_chapter_05_post_and_database
test_chapter_05_post_and_database: chapter_05_post_and_database.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_05_post_and_database.py
.PHONY: test_chapter_06_explicit_waits_1
test_chapter_06_explicit_waits_1: chapter_06_explicit_waits_1.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_06_explicit_waits_1.py
.PHONY: test_chapter_07_working_incrementally
test_chapter_07_working_incrementally: chapter_07_working_incrementally.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_07_working_incrementally.py
.PHONY: test_chapter_08_prettification
test_chapter_08_prettification: chapter_08_prettification.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_08_prettification.py
.PHONY: test_chapter_09_docker
test_chapter_09_docker: chapter_09_docker.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_09_docker.py
.PHONY: test_chapter_10_production_readiness
test_chapter_10_production_readiness: chapter_10_production_readiness.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_10_production_readiness.py
.PHONY: test_chapter_11_ansible
test_chapter_11_ansible: chapter_11_ansible.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_11_ansible.py
.PHONY: test_chapter_12_organising_test_files
test_chapter_12_organising_test_files: chapter_12_organising_test_files.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_12_organising_test_files.py
.PHONY: test_chapter_13_database_layer_validation
test_chapter_13_database_layer_validation: chapter_13_database_layer_validation.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_13_database_layer_validation.py
.PHONY: test_chapter_14_simple_form
test_chapter_14_simple_form: chapter_14_simple_form.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_14_simple_form.py
.PHONY: test_chapter_15_advanced_forms
test_chapter_15_advanced_forms: chapter_15_advanced_forms.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_15_advanced_forms.py
.PHONY: test_chapter_javascript
test_chapter_javascript: chapter_javascript.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_javascript.py
.PHONY: test_chapter_deploying_validation
test_chapter_deploying_validation: chapter_deploying_validation.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_deploying_validation.py
.PHONY: test_chapter_spiking_custom_auth
test_chapter_spiking_custom_auth: chapter_spiking_custom_auth.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_spiking_custom_auth.py
.PHONY: test_chapter_mocking
test_chapter_mocking: chapter_mocking.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_mocking.py
.PHONY: test_chapter_fixtures_and_wait_decorator
test_chapter_fixtures_and_wait_decorator: chapter_fixtures_and_wait_decorator.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_fixtures_and_wait_decorator.py
.PHONY: test_chapter_server_side_debugging
test_chapter_server_side_debugging: chapter_server_side_debugging.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_server_side_debugging.py
.PHONY: test_chapter_outside_in
test_chapter_outside_in: chapter_outside_in.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_outside_in.py
.PHONY: test_chapter_purist_unit_tests
test_chapter_purist_unit_tests: chapter_purist_unit_tests.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_purist_unit_tests.py
.PHONY: test_chapter_CI
test_chapter_CI: chapter_CI.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_CI.py
.PHONY: test_chapter_page_pattern
test_chapter_page_pattern: chapter_page_pattern.html $(TMPDIR)
	pytest -s --tb=short ./tests/test_chapter_page_pattern.py



.PHONY: silent_test_%
silent_test_%: %.html $(TMPDIR)
	pytest --tb=short ./tests/$(subst silent_,,$@).py

.PHONY: unit-test
unit-test: chapter_01.html
	SKIP_CHAPTER_SUBMODULES=1 ./tests/update_source_repo.py
	./run_test_tests.sh

.PHONY: clean
clean:
	rm -rf $(TMPDIR)
	rm -v $(HTML_PAGES)

.PHONY = test clean test_chapter_%
