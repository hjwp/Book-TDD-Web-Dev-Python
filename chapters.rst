===================================================
PART 1 - An introduction to Test-Driven Development
===================================================

1: What is TDD?  
---------------

* Some evangelism
* XP and Kent Beck, Agile methods
* TDD versus testing afterwards, 
* Outline methodology

current tutorial : 800 words, no illustrations. this shouldn't be more than 3-5
pages really

--> 5 pages


2: A simple example (?)
-----------------------

eg Roman numerals, as per "Dive Into Python.". Slightly boring topic, everyone
uses it, but it will do for now. 

* basic test - convert I
* I-III
* V + X
* VI, VII, VIII
* IV and IX 
* ...

* Start simple, include exceptions. Aim to show:
* unittest, how to run tests, possibly setUp, tearDown
* red / green / refactor:  the test/code cycle
* making the minimal change
* show how design grows organically, but stays neat
* the psychological effect
* as per Beck. "Am I saying you should always code like this? No.  I'm saying you should always *be able to*.


In DIP, this is pp 183-205, so 22 pages. I'd aim for half that.

--> 10 pages  (maybe split this into multiple chapters?)

===> total for part 1: 15 pages

===================================================
PART 2 - Using TDD to build a basic web application
===================================================

3: Our first functional test with Selenium
------------------------------------------


* Briefly discuss difference between functional testing (AKA acceptance
  testing, integration testing, whatever) and unit testing
* Write first test - Introduce Selenium, `setUp`, `tearDown`
* Demonstrate we can get it to open a web browser, and navigate to a web page
  eg - google.com

currently maybe 228 lines, 1200 words.
--> 5 pages



4: Getting Django set-up and running
------------------------------------

* Change our test to look for the test server
* Switch to Django LiveServerTestCase. Explain
* Get the first test running and failing for a sensible reason
* Create django project `django-admin.py startproject`
* It worked!

--> 3 pages


5: A static front page
----------------------

* Look for "Welcome to the Forums", or similar
* `urls.py`, `direct_to_template` ?

--> 3 pages


6: Super-users and the Django admin site
----------------------------------------

* Extend FT to try and log in
* Explain the admin site
* Database setup, `settings.py`, `syncdb`, `admin.py`
* `runserver` to show login code
* Explain difference between test database and real database
* Fixtures

--> 7 pages


7: First unit tests and Database model 
--------------------------------------

* Distinction between unit tests and functional tests
* Extend FT to try and create a new topic
* new app
* `models.py`
* test/code cycle

--> 7 pages



8: Testing a view
-----------------

* urls.py again
* Test view as a function
* assert on string contents

--> 4 pages

9: Django's template system
----------------------------

* Introduce template syntax
* Keep testing as a function
* The, introduce the Django Test Client

--> 6 pages



10: Reflections: what to test, what not to test
-----------------------------------------------

* "Don't test constants"
* Test logic
* Tests for simple stuff should be simple, so not much effort

--> 3 pages


11: Simple Forms
----------------

* Manually coded HTML
* Refactor test classes

--> 5 pages


12: User Authentication
-----------------------

* Sign up, login/logout
* Email?

--> 5 pages


13: More advanced forms
-----------------------

* Use Django Forms classes

--> 6 pages


14: On Refactoring
------------------

* Martin Fowler
* Tests critical
* Methodical process - explain step by step

--> 4 pages


15: Pagination
--------------

* Extend various old unit tests and FTs

--> 3 pages


===> total for part 2: 60 pages



======================================================
PART 3: More advanced testing for a more advanced site
======================================================

15: Notifications
------------------------------

* Django Notifications, for post edits
--> 5 pages


16: Adding style with MarkDown
------------------------------

* Using an external library

--> 5 pages


17: Switching to OAuth: Mocking
-------------------------------

* "Don't store passwords"
* Discuss challenges of external dependencies

--> 7 pages


18: Getting Dynamic: Testing Javascript part 1
----------------------------------------------

* Simple input validation
* Choose JS unit testing framework (probably Qunit, or YUI)

--> 6 pages


19: Testing Javascript part 2 - Ajax
------------------------------------

* Dynamic previews of post input

--> 5 pages


20: Getting pretty: Bootstrap
-----------------------------

* Bring in nicer UI elements

--> 4 pages


21: Getting pretty: Gravatar
----------------------------

* pictures for users

--> 4 pages


22: The bottomless web page
---------------------------

* More javascript bells and whistles

--> 3 pages

===> total for part 3: 39 pages


==============================
PART 4: Getting seriously sexy
==============================

24: Switching to a proper Database: PostgreSQL
----------------------------------------------

* show how Django makes this easy

--> 10 pages


21: Websockets and Async on the server-side
-------------------------------------------

* we want dynamic notifications of when new posts appear on a thread we're
  looking at
* Need to spin up, Tornado/Twisted/Gevent as well as Django LiveServerTestCase
* FT opens multiple browser tabs in parallel
* Big change!

--> 20 pages



22: Continuous Integration 
--------------------------

* Need to build 3 server types
* Jenkins (or maybe buildbot)
* Need to adapt Fts, maybe rely less on LiveServerTestCase

--> 15 pages


23: Caching for screamingly fast performance
--------------------------------------------

* unit testing `memcached`
* Functionally testing performance
* Apache `ab` testing

--> 15 pages


===> total for part 4: 60 pages


