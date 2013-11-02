SOURCES := $(wildcard *.asciidoc)
HTML_PAGES := $(patsubst %.asciidoc, %.html, ${SOURCES})
RUN_ASCIIDOC = python2.7 `which asciidoc` 


book.html: $(SOURCES)

build: $(HTML_PAGES)

test: build
	./run_all_tests.sh

%.html: %.asciidoc
	$(RUN_ASCIIDOC) $<

test_chapter_%: chapter_%.html
	py.test -s ./tests/$@.py

clean:
	rm -v $(HTML_PAGES)

.PHONY = test clean test_chapter_%
