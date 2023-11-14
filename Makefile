SOURCES := $(wildcard *.asciidoc)
HTML_PAGES := $(patsubst %.asciidoc, %.html, ${SOURCES})
TESTS := $(patsubst %.asciidoc, test_%, ${SOURCES})

RUN_ASCIIDOCTOR = asciidoctor -a source-highlighter=coderay -a stylesheet=asciidoctor.css -a linkcss -a icons=font -a compat-mode -a '!example-caption' -a last-update-label='License: Creative Commons <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode">CC-BY-NC-ND</a>. Last updated:'
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
