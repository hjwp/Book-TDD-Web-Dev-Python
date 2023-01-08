SOURCES := $(wildcard *.asciidoc)
HTML_PAGES := $(patsubst %.asciidoc, %.html, ${SOURCES})
TESTS := $(patsubst %.asciidoc, test_%, ${SOURCES})

RUN_ASCIIDOCTOR = asciidoctor -a source-highlighter=coderay -a stylesheet=asciidoctor.css -a linkcss -a icons=font -a compat-mode -a '!example-caption' -a last-update-label='License: Creative Commons <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode">CC-BY-NC-ND</a>. Last updated:'
RUN_OREILLY_FLAVOURED_ASCIIDOCTOR = ./asciidoc/asciidoctor/bin/asciidoctor -v --trace -d book --safe -b htmlbook --template-dir ./asciidoc/asciidoctor-htmlbook/htmlbook 

export PYTHONHASHSEED = 0
export PYTHONDONTWRITEBYTECODE = 1
export MOZ_HEADLESS = 1
export TMPDIR := $(HOME)/snap/firefox/common/tmp

$(TMPDIR):
	make -p $(TMPDIR)

book.html: $(SOURCES)

build: $(HTML_PAGES) $(TMPDIR)

test: build
	git submodule init
	python tests/update_source_repo.py
	./run_all_tests.sh

testall: build
	pytest --tb=short --color=yes --numprocesses=auto tests/test_chapter_*

testall4: build
	pytest --tb=short --color=yes --numprocesses=4 tests/test_chapter_*

%.html: %.asciidoc
	$(RUN_ASCIIDOCTOR) $<

oreilly.%.asciidoc: %.asciidoc
	$(RUN_OREILLY_FLAVOURED_ASCIIDOCTOR) $(subst oreilly.,,$@)


test_%: %.html
	env | sort
	pytest -s --tb=short ./tests/$@.py

silent_test_%: %.html
	python tests/update_source_repo.py $(subst silent_test_chapter_,,$@)
	py.test --tb=short ./tests/$(subst silent_,,$@).py

clean:
	rm -v $(HTML_PAGES)

.PHONY = test clean test_chapter_%
