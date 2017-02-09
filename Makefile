SOURCES := $(wildcard *.asciidoc)
HTML_PAGES := $(patsubst %.asciidoc, %.html, ${SOURCES})
RUN_ASCIIDOCTOR = asciidoctor -a source-highlighter=coderay -a linkcss -a icons=font -a compat-mode
RUN_OREILLY_FLAVOURED_ASCIIDOCTOR = ./asciidoc/asciidoctor/bin/asciidoctor -v --trace -d book --safe -b htmlbook --template-dir ./asciidoc/asciidoctor-htmlbook/htmlbook 

book.html: $(SOURCES)

build: $(HTML_PAGES)

test: build
	git submodule init
	python3 update_source_repo.py
	./run_all_tests.sh

%.html: %.asciidoc
	$(RUN_ASCIIDOCTOR) $<

oreilly.%.asciidoc: %.asciidoc
	$(RUN_OREILLY_FLAVOURED_ASCIIDOCTOR) $(subst oreilly.,,$@)


test_%: %.html
	PYTHONHASHSEED=0 \
	DJANGO_LIVE_TEST_SERVER_ADDRESS=localhost:2000-7000 \
	py.test -s --tb=short ./tests/$@.py

silent_test_%: %.html
	python3 update_source_repo.py $(subst silent_test_chapter_,,$@)
	PYTHONHASHSEED=0 \
	DJANGO_LIVE_TEST_SERVER_ADDRESS=localhost:2000-7000 \
	py.test --tb=short ./tests/$(subst silent_,,$@).py

clean:
	rm -v $(HTML_PAGES)

.PHONY = test clean test_chapter_%
