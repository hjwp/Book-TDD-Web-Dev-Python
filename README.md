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
make install
```

* Full test suite (probably, don't use this, it would take ages.)

```console
$ make test
```

* To test an individual chapter, eg:

```console
$ make test_chapter_06_explicit_waits_1
```

If you see a problem that seems to be related to submodules, try:

```console
make update-submodules
```


* Unit tests (tests for the tests for the tests in the testing book)

```console
$ ./run_test_tests.sh
```

# Windows / WSL notes

* `vagrant plugin install virtualbox_WSL2` is required


# Making changes to the book's code examples

Brief explanation:  each chapter's code examples are reflected in a branch of the example code repository,
https://github.com/hjwp/book-example
in branches named after the chapter, so eg chapter_02_unittest.asciidoc has a branch called chapter_02_unittest.

These branches are actually checked out, one by one, as submodules in source/<chapter-name>/superlists.
Each branch starts at the end of the previous chapter's branch.

Code listings _mostly_ map 1 to 1 with commits in the repo,
and they are sometimes marked with little tags, eg ch03l007,
meaning theoretically, the 7th listing in chapter 3, but that's not always accurate.

When the tests run, they start by creating a new folder in /tmp
checked out with the code from the end of the last chapter.

Then they go through the code listings in the book one by one,
and simulate typing them into to an editor.
If the code listing  has one of those little tags,
the tests check the commit in the repo to see if the listing matches the commit exactly.
(if there's no tag, there's some fiddly code based on string manipulation
that tries to figure out how to insert the code listing into the existing file contents at the right place)

When the tests come across a command, eg "ls",
they actually run "ls" in the temp directory,
to check whether the output that's printed in the book matches what would actually happen.

One of the most common commands is to run the tests, obviously,
so much so that if there is some console output in the book with no explicit command,
the tests assume it's a test run, so they run "./manage.py test" or equivalent.

In any case, back to our code listings - the point is that,
if we want to change one of our code listings, we also need to change the commit in the branch / submodule...

...and all of the commits that come after it.

...for that chapter and every subsequent chapter.


This is called "feeding through the changes"


## Changing a code listing

1. change the listing in the book, eg in in _chapter_03_unit_test_first_view.asciidoc_
2. open up ./source/chapter_03_unit_test_first_view/superlists in a terminal
3. do a `git rebase --interactive $previous-chapter-name`
4. identify the commit that matches the listing that you've changed, and mark it for `edit`
5. edit the file when prompted, make it match the book
6. continue the rebase, and deal with an merge conflicts as you go, woo.
7. `git push local` once you're happy.

## feeding thru the changes

Because we don't want to push WIP to github every time we change a chapter,
we use a local bare repository to push and pull chapters


```console
make ../book-example.git
```

will create it for you.

TODO:  helper to do `git remote add local` to each chapter/submodule

Now you can attempt to feed thru the latest changes to this branch/chapter with

```console
cd source
./feed_thru.sh chapter_03_unit_test_first_view chapter_04_philosophy_and_refactoring
# chapter/branch names will tab complete, helpfully.
```

if all goes well, you can then run

```console
./push-back.sh chapter_04_philosophy_and_refactoring
```

and move on to the next chapter. woo!


This may all seem a bit OTT,
but the point is that if we change a variable early on in the book,
git (along with the tests) will help us to make sure that it changes
all the way through all the subsequent chapters.
