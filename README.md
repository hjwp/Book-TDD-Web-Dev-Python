# Test-Driven Web Development With Python, the book.

# License

The sources for this book are published under the Creative Commons Attribution
Non-Commercial No-Derivs license (CC-BY-NC-ND).

*I wouldn't recommend using this version to read the book.  Head over to
www.obeythetestinggoat.com when you can access a nicely formatted version
of the full thing, still free and under CC license.  And you'll also be 
able to buy an ebook or print version if you feel like it.*

These sources are being made available for the purposes of curiosity 
(others writing books may be interested in the test suite for example)
and collaboration (typo-fixes by pull request are very much encouraged).


# Building the book as HTML

- [install asciidoc](http://www.methods.co.nz/asciidoc/INSTALL.html)
- `make build` will build each chapter as its own html file
- `make book.html` will create a single file
- `make chapter_05.html`, eg, will build chapter 5

# Running the tests

* Pre-requisites for the test suite:

    mkvirtualenv --python=python3 tddbook
    pip install -r requirements.txt
    git submodule update --init

* Full test suite:

    make test

* To test an individual chapter, eg:

    make test_chapter_06

* Unit tests (tests for the tests for the tests in the testing book)

    ./run_test_tests.sh


# Building the the tutorial handout

*There may be licensing issues associated with running tutorials based on this
book without explicit permission from my publishers.  Please get in touch with
me first if you do want to run one.  Don't worry, it's always been fine in the
past, and I'm not intending to charge anything!*

The handout lives on a branch, which basically strips out everything but code
listings and commands, from chapters 1-6:

    git checkout workshop_handout
    make book.html

Then open book.html in Firefox, and hit "Save as" to save a version 
with a .html extension and an associated directory for images. Then
zip those two up together.

