# Title:
TDD study group: Goat herding for beginner and intermediate testers

# Category:
Testing

# Python level:
Novice

# Domain level:
Novice


# Description
A study group based on the book "TDD with Python" (available at obeythetestinggoat.com).  Attendees will be able to go through the book alone or in pairs, at their own pace.  Three suggested "tracks" are provided (Beginner, Intermediate, and "Devops") to help pick a path through the book's 22 chapters.  The author and other experienced TDDers will be on hand to facilitate and answer questions.

# Audience
Beginners or Intermediate-level testers looking to deepen their TDD skills.

# Objectives

    What will attendees get out of your talk? When they leave the room, what will they know that they didn't know before?*

Beginners should be able to get a solid understanding of TDD, unit testing and functional testing, and some of the basics of web development too.  Intermediate-level testers should be able to experiment with more advanced techniques, like mocking, testing against servers,  using tests to verify server deployments, testing javascript, testing 3rd party API integrations, setting up CI, and a hands-on investigation of the pros and cons of isolated unit tests against more integrated tests.

# Detailed Abstract

[The book](http://www.obeythetestinggoat.com) has 22 chapters in total, and can take a reader from complete TDD beginner up through a wide range of intermediate techniques, like mocking, javascript testing, outside-in TDD, test isolation, test-driven server deployment automation, continuous integration, 3rd-party API integration, and more.  Rather than have to follow a fixed path through a subset of these topics, and find yourself waiting for those less experienced to catch up, or lost when the rest of the class pulls ahead of you, come along and choose your own path, and progress at your own speed.

Why come and do this in a tutorial session, rather than just go through it at home in my own time, I hear you ask?  Several possible reasons

* The author, and several other experienced TDD'ers will be on hand to answer your questions and help you if you get stuck.

* Several different tracks will be offered, to help you find the content you're interested in, and save you from wasting time on material that's too simple or too advanced for you.

* You will have the option of pairing up with someone else in your track, to be able to help each other through the chapters (nothing helps you learn like having to explain what you know to someone else!)

* Plus, will you, *actually* find the time to go through this stuff on your own?  Booking a slot in a tutorial is a wonderful way of overcoming prevarication, and, no matter how much you get through in the session, there'll be plenty more of the book for you to go through when you get back home...


# Outline

After 10 minutes of intro and welcome, introducing myself and the teaching assistants, I'll give a brief overview of the whole book, and then outline the suggested tracks.  Once people have chosen a track, I'll encourage them to pair-program within their track

## Beginner track

* Start from beginning!
* pre-requs to get stuff installed
* Then as far as you can get!  1-5 is good progress, then 6, 7, then skip to 10 if you don't want the brain-damage of server deploys


## Intermediate TDD skills track

* Chapter 7, layout and styling
* Chapter 13, Testing JavaScript
* Chapter 18, Outside-In TDD
* Chapter 19, "Listen to your tests"
* Chapter 22, Fast Test Slow test
* Appendix E: investigate a BDD tool (hint: use behave and django-behave)


## Devops track

* Chapter 7, layout and styling
* Chapter 8, manual provisioning
* Chapter 9, automated deployments
* Chapter 17, Fixtures, Logging and server-side debugging
* Appendix C, Ansible


## Mocking Overload Track

* Chapter 15, Mocking in JavaScript
* Chapter 16, Mocking in Python
* Chapter 18, Outside-In TDD
* Chapter 19, "Listen to your tests"


# More info

There are no absolute pre-requisites for this tutorial, as the book contains 
[detailed installation instructions](http://chimera.labs.oreilly.com/books/1234000000754/pr02.html#_required_software_installations) for all the software
you'll need.  With that said, if you want to save some time sitting around waiting to download software over the saturated conference wifi, you might find it worthwhile going through said [instructions](http://chimera.labs.oreilly.com/books/1234000000754/pr02.html#_required_software_installations) before you show up!

All the source code for the book can be found at 

    https://github.com/hjwp/book-example/

And each chapter has its own branch, eg `chapter_04_philosophy_and_refactoring`, `chapter_15`, `appendix_III` etc


# Additional notes

The "study group" format is a reaction to one of the criticisms of the general tutorial format, which is that not everyone learns at the same speed, so you usually find that some people are bored and some people are a bit lost when you try and teach the same materials to a whole group.

However, I gather that "study-group" style tutorials don't always go down well -- people complain that they're not structured enough, or that there's no additional value compared to just doing it alone at home.  So that's why I tried to anticipate that possible criticism, by

* Providing a structure, by outlining different "tracks"
* Encouraging people to pair-program
* Making sure that I'm on hand, and other TDD experts too, to help people when they get stuck

I'm experimenting with this format for the first time at PyconUK which is next weekend (19th-21st September), so I'll be able to write up a few experience notes after that, and include them here.


Student Handout


