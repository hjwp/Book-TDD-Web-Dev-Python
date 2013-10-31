To build the book:

- [install asciidoc](http://www.methods.co.nz/asciidoc/INSTALL.html)
- `make build` will build each chapter as its own html file
- `make book.html` will create a single file

Pre-requisites for the test suite:

    mkvirtualenv --python=python3 tddbook
    pip install -r requirements.txt
    git submodule update --init

Full test suite:

    make test

To test an individual chapter, eg:

    make test_chapter_06

