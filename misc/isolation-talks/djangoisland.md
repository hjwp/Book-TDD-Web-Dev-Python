Outside-In TDD, Test Isolation, and Mocking
===========================================

* Harry Percival, @hjwp, www.obeythetestinggoat.com

* Outside-in TDD?

* DHH "TDD is Dead":  agree? disagree?

* No idea?

* Who doesn't know what a mock is?





 # PS if you're coming to my tutorial tomorrow:  **INSTALL STUFF**

 * Python 3.3+
 * Django 1.7 (from 1.7.x stable branch on gh)
 * Selenium
 * Firefox

 -- instructions in preface of my book, available online,
    www.obeythetestinggoat.com


































Conclusion
==========

*Listen to your tests*

- ppl complain about "too many mocks": are there architectural solutions that
  would solve your problem?

- Ports & Adapters Hexagonal / Clean architecture
- Functional Core Imperative Shell

- are you testing at the right level?

*Further reading*

- see chapter 22 in my book (available free online) for a reading list.
  www.obeythetestinggoat.com








































# What do we want from our tests anyway?

* Correctness
* Clean, maintainable code
* Productive workflow












































# On the Pros and Cons of Different Types of Test

Functional tests::

    * Provide the best guarantee that your application really works correctly,
      from the point of view of the user.
    * But: it's a slower feedback cycle,
    * And they don't necessarily help you write clean code.

Integrated tests (reliant on, eg, the ORM or the Django Test Client)::

    * Are quick to write,
    * Easy to understand,
    * Will warn you of any integration issues,
    * But may not always drive good design (that's up to you!).
    * And are usually slower than isolated tests

Isolated ("mocky") tests::

    * These involve the most hard work.
    * They can be harder to read and understand,
    * But: these are the best ones for guiding you towards better design.
    * And they run the fastest.













# PS If you're coming to my tutorial tomorrow:  **INSTALL STUFF**

* Python 3.3+
* Django 1.7 (from 1.7.x stable branch on gh)
* Selenium
* Firefox

-- instructions in preface of my book, available online, 
   www.obeythetestinggoat.com



















