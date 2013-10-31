SOURCES := $(wildcard *.asciidoc)
HTML_PAGES := $(patsubst %.asciidoc, %.html, ${SOURCES})

build: $(HTML_PAGES)

test: build
	./run_all_tests.sh

%.html: %.asciidoc
	asciidoc $<

clean:
	rm -v $(HTML_PAGES)

.PHONY = test clean
