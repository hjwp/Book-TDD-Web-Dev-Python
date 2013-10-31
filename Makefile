SOURCES := $(wildcard *.asciidoc)
HTML_PAGES := $(patsubst %.asciidoc, %.html, ${SOURCES})
RUN_ASCIIDOC = python2.7 `which asciidoc` 

build: $(HTML_PAGES)

book.html: $(SOURCES)
	$(RUN_ASCIIDOC) book.asciidoc

test: build
	./run_all_tests.sh

%.html: %.asciidoc
	python2.7 `which asciidoc` $<

testtest01: chapter_01.html
	py.test -s ./tests/test_chapter_01.py

test_chapter_%: chapter_%.html
	py.test -s ./tests/$@.py

clean:
	rm -v $(HTML_PAGES)

.PHONY = test clean test_chapter_%
