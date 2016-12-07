# Outline

TODO:

  - switch to chrome in all tags


> 1 day: Outside-in TDD with and without mocks (AKA - "listen to your tests").
> This day will start with a discussion of the "outside-in" technique, a way of
> deciding which tests to write, and what code to write, in what order, and how
> high-level tests interact with lower-level tests.  We'll do one run with
> familiar django/integration tests, and then we'll move on to working with
> mocks.  Using a practical example we'll be able to see many of the common
> problems with mocks, the difficulties they introduce, but also a real
> demonstration of the possible benefits mocks (or "purist" unit testing) can
> bring.  We'll conclude the day with a discussion of the pros and cons of
> different types of tests: end-to-end/functional vs integration vs unit tests.


* Intro and installations (15m, t=0)
* Our example app - tour (5m, t=15)
* Codebase tour (5m, t=20)
* Double-loop TDD demo (10m, t=25)
* Coding challenge 1:  building the "my lists" feature (45m, t=35)
* Outside-In TDD.  Examples + discussion (20m, t=1h15)
* Break (15m, t=1h35)
* Mocks demo: (10m, t=1h50)
* Next challenge: redo it with a more "purist" approach (15m, t=2h00)
* Mocks and "Listen to your tests" discussion. (25m, t=2h15)
* The pitfalls of mocking (15m, t=2h35)
* Recap + discussion:  the pros and cons of different types of test (15m, t=2h50)
* end (t=3h00)



# notes from live session
- have a better process for outside-in live code bit
- slides worked well for that bit
- and for the mocks bit
- live-coding was fine for mocks intro




# notes from prep

live code demo 1:
git checkout intermediate-workshop-start-harry
add url #, navbar-left, re-run ft
move down to test views
client.get /lists/my_lists/
assert 200 as well as template
add url
create placeholder view
render home instead of my lists
add my_lists template
inherit from base
add block content, h1

live code demo 2:
git checkout end-of-live-code
my_lists.html
user.list_set.all
mention other possibilities
list.name
then examples back in main prezzo


live code demo 3:
mockListClass
see problem with form
mockItemForm
passes but not saving.  hand over



# Welcome to the Intermediate TDD with Django Workshop

```installation instructions:
git clone https://github.com/hjwp/book-example/ tdd-workshop
cd tdd-workshop
git checkout intermediate-workshop-start
mkvirtualenv --python=python3 tdd-workshop  # or however you like to create virtualenvs
pip install -r requirements.txt

# Take a look around the site  with:
mkdir ../database
python manage.py migrate
python manage.py runserver

# Run the test suite and check everything passes:
pip install selenium
python manage.py test  # all but one should pass
```

If the functional tests give you any trouble, You can try switching from
`webdriver.Firefox()` to `webdriver.Chrome()`.  You will need to download a
thing called "chromedriver" (google it) and have it on the path (in the main
repo folder might also work)


color: apprentice? colorful? beachcomber? ironman?










# Intro

* pair up: beginners to sit next to more experienced people























# Our example app - tour

* Current state, demo
* Desired state, demo
























# Codebase tour


**Models**:  a list has many items:


```python: lists/models.py

class List(models.Model):
  pass


class Item(models.Model):
    text = models.TextField(default='')
    list = models.ForeignKey(List, default=None)

```














**Views**:

* home page
* create new list (and show errors back on home page if necessary)
* view existing list (and add extra items to it if necessary)


```python: lists/views.py
def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})
```














```python: lists/views.py
def new_list(request):
    form = ItemForm(data=request.POST)
    if form.is_valid():
        list_ = List.objects.create()
        form.save(for_list=list_)
        return redirect(list_)
    else:
        return render(request, 'home.html', {"form": form})
```




```python: lists/views.py
def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    form = ExistingListItemForm(for_list=list_)
    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)
    return render(request, 'list.html', {'list': list_, "form": form})
```




* forms deal with validation and creating new objects, they live in
  *lists/forms.py*.  We don't need them for the first part of this workshop.

* login/logout etc are handled by the accounts module, which we won't need to
  look at today.













# Double-loop TDD demo

* running the FT
* possible failure modes

* write a unit test
* make it pass














# Coding challenge 1:  building the "my lists" feature

ie: Get this FT to pass:

    python manage.py test functional_tests.test_my_lists

Ideally: using TDD. Add some unit tests, in *test_models.py* and *test_views.py*.  Get the FT to pass.

Tips:

* you'll probably need a foreign key from lists to the user model
* `request.user` will be available if user is logged in
* `request.user.is_authenticated()` is False if user is not logged in
* `list.get_absolute_url()` will give you a url you can use in an <a> tag for the lists page
* you will probably want a new template at *lists/templates/my_lists.html*, and a new URL + view for it.  You can inherit from base.html
* you will need to associate the creation of a new list with the current user, if they're logged in
* if you need a views test to have a logged-in user, you have two choices
  - `self.client.force_login(user)`
  - or, import and call the view function directly with an HttpRequest instance whose .user attribute is set.
* if you want to try manually logging in with persona, "anything@mockmyid.com" will "just work" (but use "localhost:8000" in your browser, not "127.0.0.1:800")

**Help**: Grab my version of the "my lists" template. it will tell you what you need your views to do

    git checkout origin/intermediate-workshop-end -- lists/templates/my_lists.html


//TODO: simplify my example my_lists.html











# Outside-In TDD.  Examples + discussion


Live code demo - programming by wishful thinking in the template














* we can work incrementally, small steps

* functional test
  * drives templates layer ('programming by wishful thinking')
    * drives views-layer tests
      * drive views-layer code
        * drive models-layer tests
          * drive models-layer-code


Additional illustrations

* next we want to associate owners with lists
* at the views layer, we need to save owner relationship at new list creation
* at the models layer, we need to implement saving owners for lists












```python lists/tests/test_views.py

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)

        self.client.post('/lists/new', data={'text': 'new item'})

        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)
```


```python lists/views.py

def new_list(request):
    form = ItemForm(data=request.POST)
    if form.is_valid():
        list_ = List()
        if request.user.is_authenticated():
            list_.owner = request.user
        list_.save()
        form.save(for_list=list_)
        return redirect(list_)
    else:
        return render(request, 'home.html', {"form": form})
```












```
======================================================================
ERROR: test_list_owner_is_saved_if_user_is_authenticated (lists.tests.test_views.NewListTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/harry/workspace/book-example/lists/tests/test_views.py", line 76, in test_list_owner_is_saved_if_user_is_authenticated
    self.assertEqual(list_.owner, user)
AttributeError: 'List' object has no attribute 'owner'

----------------------------------------------------------------------
```














So we move down to the models layer:


``` python lists/tests/test_models.py

    def test_lists_can_have_owners(self):
        user = User.objects.create(email='a@b.com')
        list_ = List.objects.create(owner=user)
        self.assertIn(list_, user.list_set.all())
```



```python lists/models.py

class List(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
```














Maybe we think everything should work now, we pop back up to run the FT:



```
======================================================================
ERROR: test_logged_in_users_lists_are_saved_as_my_lists
(functional_tests.test_my_lists.MyListsTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/harry/workspace/book-example/functional_tests/test_my_lists.py",
  line 48, in test_logged_in_users_lists_are_saved_as_my_lists
    self.browser.find_element_by_link_text('First list 1st item').click()
    [...]
selenium.common.exceptions.NoSuchElementException: Message: Unable to locate
element: {"method":"link text","selector":"First list 1st item"}
[...]
----------------------------------------------------------------------
```


Oh no!  what's happening?

  firefox ~/Dropbox/Book/images/intermediate-ws-ft-fail-ss1.png 













```html lists/templates/my_lists.html

          <li><a href="{{ list.get_absolute_url }}">{{ list.name }}</a></li>

```














Lists need a name attribute (what we'd programmed by wishful thinking)




```python lists/tests/test_models.py

    def test_list_name_is_first_item_text(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='first item')
        Item.objects.create(list=list_, text='second item')
        self.assertEqual(list_.name, 'first item')
```


```python lists/models.py

class List(models.Model):
    # ...

    @property
    def name(self):
        return self.item_set.first().text
```













# Discussion


* benefits of outside-in vs bottom-up
* when might it not work?


















# Break













# Next challenge: redo it with a more "purist" approach

* how many people have never used mocks?

* live demo of mocks



    git checkout intermediate-workshop-part2
    python manage.py test lists

* Objective: get this test to pass *before* we move onto the models layer

Tips:
* Test will probably need re-writing to use mocks

* `new_list` view has two "collaborators", 
  - `ItemForm` 
  - the `List` class
you will probably need to mock one or both of these
  - you need to check a list object is created
  - you need to check it has the owner assigned to it
  - either inside the `objects.create()` call,
  - or *before* calling `list_.save()`

    self.assertEqual(mock_list.save.called, True)

* No need to use mocks once you get to the models layer!

(for bonus points: testing that things happen in a particular order involves an advanced mocking technique involving custom `side_effect` functions. Look these up in the docs and try and use them, if you finish early)


Think about:
- are these mocky tests nice to work with?
- how are they driving the design, and the workflow?



# Mocks and "Listen to your tests" discussion.



Did you end up with a test like this?


```python lists/tests/test_views

    @patch('lists.views.List')
    def test_list_owner_is_saved_if_user_is_authenticated(self, mockListClass):
        mock_list = List.objects.create()
        mock_list.save = Mock()
        mockListClass.return_value = mock_list
        request = HttpRequest()
        request.user = Mock()
        request.user.is_authenticated.return_value = True
        request.POST['text'] = 'new list item'

        def check_owner_assigned():
            self.assertEqual(mock_list.owner, request.user)
        mock_list.save.side_effect = check_owner_assigned

        new_list(request)

        mock_list.save.assert_called_once_with()

```

yuck!


Why is this so hard? What are the tests trying to tell us?



```python lists/views.py
def new_list(request):
    form = ItemForm(data=request.POST)
    if form.is_valid():
        list_ = List()
        if request.user.is_authenticated():
            list_.owner = request.user
        list_.save()
        form.save(for_list=list_)
        return redirect(list_)
    else:
        return render(request, 'home.html', {"form": form})
```














What if it was easier?




```python lists/views.py
def new_list(request):
    form = NewListForm(data=request.POST)
    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(list_)
    return render(request, 'home.html', {'form': form})
```



And then we could write a "nice" mocky test like this, rather than a nasty one...



```python lists/tests/test_views.py
    @patch('lists.views.NewListForm')
    def test_saves_form_with_owner_if_form_valid(self, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True
        new_list(self.request)
        mock_form.save.assert_called_once_with(owner=self.request.user)
```






of course if we're going to go the whole way, we would rewrite all the tests:


```python lists/tests/test_views.py
    def test_passes_POST_data_to_NewListForm(self, mockNewListForm):

    def test_saves_form_with_owner_if_form_valid(self, mockNewListForm):

    def test_does_not_save_if_form_invalid(self, mockNewListForm):

    @patch('lists.views.redirect')
    def test_redirects_to_form_returned_object_if_form_valid(

    @patch('lists.views.render')
    def test_renders_home_template_with_form_if_form_invalid(
```












Same story at the forms layer:


```python lists/forms.py
class NewListForm(models.Form):

    def save(self, owner):
        list_ = List()
        if owner.is_authenticated():
            list_.owner = owner
        list_.save()
        item = Item()
        item.list = list_
        item.text = self.cleaned_data['text']
        item.save()
```


Which leads to tests that look like this:



```python lists/forms.py

class NewListFormTest(unittest.TestCase):

    @patch('lists.forms.List')  #1
    @patch('lists.forms.Item')  #2
    def test_save_creates_new_list_and_item_from_post_data(
        self, mockItem, mockList  #3
    ):
        mock_item = mockItem.return_value
        mock_list = mockList.return_value
        user = Mock()
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid() #4

        def check_item_text_and_list():
            self.assertEqual(mock_item.text, 'new item text')
            self.assertEqual(mock_item.list, mock_list)
            self.assertTrue(mock_list.save.called)
        mock_item.save.side_effect = check_item_text_and_list  #5

        form.save(owner=user)

        self.assertTrue(mock_item.save.called)  #6

```


yuck!  again.

But, again, this is a call to "listen to our tests"




```python lists/forms.py

class NewListForm(ItemForm):

    def save(self, owner):
        if owner.is_authenticated():
            List.create_new(first_item=self.cleaned_data['text'], owner=owner)
        else:
            List.create_new(first_item=self.cleaned_data['text'])
```


End result:

* Cleaner code at each layer
* views only handle extracting info from requests, choosing what kind of response to return
* forms handle validation of that data, and then hands off to..
* models layer is in charge of actually saving objects and relationships between them
* we can write tests at the model layer without mocks




# The pitfalls of mocking: debugging challenge!

git checkout intermediate-workshop-part3


Can you figure out what went wrong?



* lesson:  mocking requires clear identification of contracts, and testing same.



# Recap + discussion:  the pros and cons of different types of test



**Functional tests:**
    * Provide the best guarantee that your application really works correctly,
    from the point of view of the user.
    * But: it's a slower feedback cycle,
    * And they don't necessarily help you write clean code.

* **Integrated tests** (reliant on, e.g., the ORM or the Django Test Client):
    * Are quick to write,
    * Easy to understand,
    * Will warn you of any integration issues,
    * But may not always drive good design (that's up to you!).
    * And are usually slower than isolated tests

**Isolated ("mocky") tests:**
    * These involve the most hard work.
    * They can be harder to read and understand,
    * But: these are the best ones for guiding you towards better design.
    * And they run the fastest.













# THE END!


www.obeythetestinggoat.com

DISCOUNT CODE for oreilly.com: "AUTHD"

























# misc notes

color: apprentice? colorful? beachcomber?


