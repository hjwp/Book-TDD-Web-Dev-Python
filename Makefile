SOURCES := $(wildcard chapter_*.asciidoc)
CHAPTER_TESTS := $(wildcard tests/test_chapter_*.py)
HTML_PAGES := $(patsubst %.asciidoc, %.html, ${SOURCES})
RUN_ASCIIDOC = asciidoctor -a source-highlighter=coderay -a linkcss -a icons=font -a compat-mode


book.html: $(SOURCES)

build: $(HTML_PAGES)

test: build
	git submodule init
	python3 update_source_repo.py
	./run_all_tests.sh

%.html: %.asciidoc
	$(RUN_ASCIIDOC) $<

test_chapter_%: chapter_%.html
	python3 update_source_repo.py $(subst test_chapter_,,$@)
	PYTHONHASHSEED=0 \
	DJANGO_LIVE_TEST_SERVER_ADDRESS=localhost:2000-7000 \
	py.test -s --tb=short ./tests/$@.py

silent_test_chapter_%: chapter_%.html
	python3 update_source_repo.py $(subst silent_test_chapter_,,$@)
	PYTHONHASHSEED=0 \
	DJANGO_LIVE_TEST_SERVER_ADDRESS=localhost:2000-7000 \
	py.test --tb=short ./tests/$(subst silent_,,$@).py

clean:
	rm -v $(HTML_PAGES)

.PHONY = test clean test_chapter_%
