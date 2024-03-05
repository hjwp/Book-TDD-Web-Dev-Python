# Test-Driven Web Development With Python, the book.

# License

The sources for this book are published under the Creative Commons Attribution
Non-Commercial No-Derivs license (CC-BY-NC-ND).

*I wouldn't recommend using this version to read the book.  Head over to
[obeythetestinggoat.com](https://www.obeythetestinggoat.com/pages/book.html)
when you can access a nicely formatted version of the full thing, still free
and under CC license.  And you'll also be able to buy an ebook or print version
if you feel like it.*

These sources are being made available for the purposes of curiosity 
(although if you're curious about the way the listings are tested,
i would definitely recommend https://github.com/cosmicpython/book instead)
and collaboration (typo-fixes by pull request are very much encouraged!).


# Building the book as HTML

- install [asciidoctor](http://asciidoctor.org/), and the *pygments/pygmentize* gem.
- `make build` will build each chapter as its own html file
- `make book.html` will create a single file
- `make chapter_05_post_and_database.html`, eg, will build chapter 5

# Running the tests

* Pre-requisites for the test suite:
```console   
$ pip install .
$ git submodule update --init
```

* Full test suite:
```console
$ make test
```

* To test an individual chapter, eg:
```console
$ make test_chapter_06_explicit_waits_1
```

* Unit tests (tests for the tests for the tests in the testing book)
```console
$ ./run_test_tests.sh
```

# Windows / WSL notes

* `vagrant plugin install virtualbox_WSL2` is required
