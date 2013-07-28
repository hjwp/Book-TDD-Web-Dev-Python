Hi Python-Redditors!,

I'm somehow writing a book on TDD and Python for O'Reilly, despite feeling massively underqualified.  Please help me to instill the book with more wisdom than I can muster on my own!

Here's a link where you can take a look at what I have so far (8 chapters):

http://www.obeythetestinggoat.com

**My background:**

I've only been a professional programmer for about 4 years, but I was lucky enough to fall in with a bunch of XP fanatics at Resolver Systems, now [PythonAnywhere](http://www.pythonanywhere.com).  Over the past few years I've learned an awful lot, and I'm trying to share what I've learned with other people who are starting out. Someone described learning TDD as being a step on the journey from amateur coder to professional, maybe that's a good way of putting it.

For the past couple of years I've been running beginners' TDD / Django workshops at EuroPython and Pycons, and they've been well-received. They're probably what must have fooled O'Reilly into thinking I could write a book!

**The book**

The concept is to take the user through building a web app from scratch, but using full TDD all along the way.  That involves:

* Functional tests using Selenium
* "unit" tests using the Django test runner
* All Django goodness including views, models, templates, forms, admin etc
* Unit testing javascript
* Tips on deployment, and how to test against  a staging site

...and lots more.  You'll find a [proposed chapter outline](http://chimera.labs.oreilly.com/books/1234000000754/ch09.html) at the end of the book.

I've made a good start, 8 chapters, taking us all the way to deploying a minimum viable app, but I really need some more feedback.

* Am I covering the right stuff?  Would you add / remove any topics?
* Am I teaching what you consider to be best practice?  Some people, for example, think that touching the database in a thing you call a unit test is an absolute no-no (cf [past discussion on reddit](http://www.reddit.com/r/django/comments/1c67rl/is_tddjangotutorial_truly_a_good_resource_i_want/)).  Do you think that's important?  Should I acknowledge the controversy, and maybe refer people to an appendix which discusses how to avoid hitting the db in unit tests?  Or should I throw out the Django test runner?
* I'm also telling people to use a very belt & braces technique, where we write functional tests *and* unit tests for pretty much every single line of code.  Is that overkill? Or do you think that it's a good thing to learn, even if you later relax the rules when you get a bit more experience (I make this argument in chapter 4)
* My latest chapter is [all about deployment](http://chimera.labs.oreilly.com/books/1234000000754/ch08.html) -- lots of people do different things in this area, we had a good discussion of it on the Python-UK mailing list. What do you think of what I have so far?


**Why help?**

Perhaps you're thinking "Why should I help this guy to write a better book and make more money, despite the blatant massive lacunae in his knowledge?". 

Well, one thing that I hope will sway your cold, hard heart is that I am pledging to make the book available for free under a CC license, alongside the official paid-for printed and ebook versions. I insisted on that as part of my contract, and O'Reilly were totally happy with it (props to them for being forward-thinking).  I really hope that this book can distill something of the sum total of all the knowledge in the Python testing community, over and above my own, and be a useful resource for that whole community, and not just those that can afford to pay for a book...

If that's not enough, how about I promise I'll buy you a beer one day?


Thanks in advance, 
Harry

