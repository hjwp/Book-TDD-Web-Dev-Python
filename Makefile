SOURCES := $(wildcard chapter_*.asciidoc)
CHAPTER_TESTS := $(wildcard tests/test_chapter_*.py)
HTML_PAGES := $(patsubst %.asciidoc, %.html, ${SOURCES})
RUN_ASCIIDOC = python2.7 `which asciidoc` 


book.html: $(SOURCES)

build: $(HTML_PAGES)

test: build
	git submodule init
	./update_source_repo.py
	./run_all_tests.sh

%.html: %.asciidoc
	$(RUN_ASCIIDOC) $<

test_chapter_%: chapter_%.html
	./update_source_repo.py $(subst test_chapter_,,$@)
	py.test -s ./tests/$@.py

clean:
	rm -v $(HTML_PAGES)

.PHONY = test clean test_chapter_%
