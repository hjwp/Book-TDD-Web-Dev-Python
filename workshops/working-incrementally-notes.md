
# Day 1 morning: Working incrementally

> 1/2 day: "working incrementally".  writing tests and getting them to pass is
> all very well, but it's still easy to get into trouble.  Have you ever set
> off to make some changes to your code, and found yourself several hours into
> the effort, with changes to half a dozen files, everything is broken, many
> tests failing, and starting to worry about how you're ever going to get
> things working again?  This course is aimed at teaching the technique of
> working incrementally -- how to make changes to a codebase in small steps,
> going from "working state to working state", based on a series of practical
> examples.

## Prep (which naturally everyone has already done, naturally)

```
mkvirtualenv tdd-workshop --python=python3
pip install 'django<1.10' selenium
git clone https://github.com/hjwp/book-example.git tdd-workshop
cd tdd-workshop
git checkout chapter_06
python manage.py test # should all pass.
```

Also, do this

```
git fetch --tags
pip install chromedriver_installer
```


* Intro (9.20)
  - Start in chapter 6
  - demo site as at end of 5, single to-do list
  - code tour
  - demo site as desired at end of 6, multiple to-do lists
  - get ppl to check out code, including modified FT
  - show how to run unit tests and FTs
  - explain the FT
  - give more hints about the desired solution - each list gets an id


Instructions:

    git checkout incremental-workshop-start
    git checkout -b working-incrementally



* First live-code session (10.00)
  - pairing? depends on numbers
  - have a go!
  - try to get to where you want to be
  - ideally, with a set of unit tests (but worry about them later if you like)
  - with a passing FT




* Discussion: on working incrementally (10.15)
  - how many people got it working?
  - was it hard?  what steps did you go through?
  - obv this is a simple example.
  - now let's do it the incremental way
  - BDUF vs lean discussion
  - start todo list
  - model layer
  - brief REST discussion

    * 'Adjust model so that items are associated with different lists'
    * 'Add unique URLs for each list'
    * 'Add a URL for creating a new list via POST'
    * 'Add URLs for adding a new item to an existing list via POST'


Planned future URLS:

    / 
    /lists/new
    /lists/<list identifier>/
    /lists/<list identifier>/add_item


* Demo: starting with an easy, small change (10.30)
  * off first task unique urls, and make it simpler
  * change redirect
  * new url, point at home page view
  * unit tests pass
  * FT to check progress
  * note regression: cannot add second element
  * fix in form, add action="/"
  * tests pass, commit.
  * refactor: new view
  * refactor to remove superfluous code
  * refactor/improve to use a separate template
  * we get a little further, now home page of francis has edith's stuff.
  * get to end and re-run FT again.
  * discussion - seems like a tiny step, but actually we've laid loads of groundwork

* Break. (10.45)

* Second live-coding session: new URL for creating a new list via POST (11:10)
  * point to book if we get stuck
  * checkout tag which includes failing unit test
  * create new url, for view that doesnt exist yet
  * create dummy view
  * make the unit tests pass one by one, redirect first, then saving data
  * point the form at the new URL
  * re-run the FT and confirm things still work
  * red/green/refactor:
    - remove redundant unit tests for `home_page`
    - strip out redundant code from `home_page`


* Discussion of first two small steps (11:25)
  - how did y'all get on?
  - any reactions?

* Final live-coding session:  try and finish! (12:00)
  - point to book for help

* Final discussion/show-and-tell (12:30)


