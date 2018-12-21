SOURCES := $(wildcard *.asciidoc)
HTML_PAGES := $(patsubst %.asciidoc, %.html, ${SOURCES})
	RUN_ASCIIDOCTOR = asciidoctor -a source-highlighter=coderay -a stylesheet=asciidoctor.css -a linkcss -a icons=font -a compat-mode -a '!example-caption' -a last-update-label='License: Creative Commons <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode">CC-BY-NC-ND</a>. Last updated:'
RUN_OREILLY_FLAVOURED_ASCIIDOCTOR = ./asciidoc/asciidoctor/bin/asciidoctor -v --trace -d book --safe -b htmlbook --template-dir ./asciidoc/asciidoctor-htmlbook/htmlbook 

book.html: $(SOURCES)

build: $(HTML_PAGES)

test: build
	git submodule init
	python3 update_source_repo.py
	PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 \
	./run_all_tests.sh

%.html: %.asciidoc
	$(RUN_ASCIIDOCTOR) $<

oreilly.%.asciidoc: %.asciidoc
	$(RUN_OREILLY_FLAVOURED_ASCIIDOCTOR) $(subst oreilly.,,$@)


test_%: %.html
	PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 MOZ_HEADLESS=1 \
	py.test -s --tb=short ./tests/$@.py

silent_test_%: %.html
	python3 update_source_repo.py $(subst silent_test_chapter_,,$@)
	PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 MOZ_HEADLESS=1 \
	py.test --tb=short ./tests/$(subst silent_,,$@).py

clean:
	rm -v $(HTML_PAGES)

.PHONY = test clean test_chapter_%
