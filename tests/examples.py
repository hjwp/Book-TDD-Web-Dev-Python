CODE_LISTING_WITH_CAPTION = """<div class="exampleblock sourcecode">
<div class="title">functional_tests.py</div>
<div class="content">
<div class="listingblock">
<div class="content">
<pre class="CodeRay highlight"><code data-lang="python"><span class="keyword">from</span> <span class="include">selenium</span> <span class="keyword">import</span> <span class="include">webdriver</span>

browser = webdriver.Firefox()
browser.get(<span class="string"><span class="delimiter">'</span><span class="content">http://localhost:8000</span><span class="delimiter">'</span></span>)

<span class="keyword">assert</span> <span class="string"><span class="delimiter">'</span><span class="content">Django</span><span class="delimiter">'</span></span> <span class="keyword">in</span> browser.title</code></pre>
</div>
</div>
</div>
</div>"""

CODE_LISTING_WITH_CAPTION_AND_GIT_COMMIT_REF = """<div class="exampleblock sourcecode">
<div class="title">functional_tests/tests.py (ch06l001)</div>
<div class="content">
<div class="listingblock">
<div class="content">
<pre class="CodeRay highlight"><code data-lang="python"><span class="keyword">from</span> <span class="include">django.test</span> <span class="keyword">import</span> <span class="include">LiveServerTestCase</span>
<span class="keyword">from</span> <span class="include">selenium</span> <span class="keyword">import</span> <span class="include">webdriver</span>
<span class="keyword">from</span> <span class="include">selenium.webdriver.common.keys</span> <span class="keyword">import</span> <span class="include">Keys</span>
<span class="keyword">import</span> <span class="include">time</span>


<span class="keyword">class</span> <span class="class">NewVisitorTest</span>(LiveServerTestCase):

    <span class="keyword">def</span> <span class="function">setUp</span>(<span class="predefined-constant">self</span>):
        [...]</code></pre>
</div>
</div>
</div>
</div>"""


SERVER_COMMAND = """<div class="listingblock server-commands">
<div class="content">
<pre><code>elspeth@server:$ <strong>sudo do stuff</strong></code></pre>
</div></div>"""


COMMANDS_WITH_VIRTUALENV = """<div class="listingblock">
<div class="content">
<pre><code>$ <strong>source ../.venv/bin/activate</strong>
(virtualenv)$ <strong>python manage.py test lists</strong>
[...]
ImportError: No module named django</code></pre>
</div></div>"""


CODE_LISTING_WITH_DIFF_FORMATING_AND_COMMIT_REF = """<div class="listingblock sourcecode">
<div class="title">lists/tests/test_models.py (ch09l010)</div>
<div class="content"><div class="highlight"><pre><span class="gh">diff --git a/lists/tests/test_views.py b/lists/tests/test_views.py</span>
<span class="gh">index fc1eb64..9305bf8 100644</span>
<span class="gd">--- a/lists/tests/test_views.py</span>
<span class="gi">+++ b/lists/tests/test_views.py</span>
<span class="gu">@@ -81,33 +81,3 @@ class ListViewTest(TestCase):</span>
         self.assertTemplateUsed(response, 'list.html')
         self.assertEqual(response.context['list'], list)

<span class="gd">-</span>
<span class="gd">-</span>
<span class="gd">-class ListAndItemModelsTest(TestCase):</span>
<span class="gd">-</span>
<span class="gd">-    def test_saving_and_retrieving_items(self):</span>
[...]
</pre></div></div></div>"""


COMMAND_MADE_WITH_ATS = """
<div class="listingblock">
<div class="content">
<pre><code>$ <strong>grep id_new_item functional_tests/tests/test*</strong></code></pre>
</div></div>
"""

OUTPUT_WITH_SKIPME = """
<div class="listingblock skipme">
<div class="content"><div class="highlight"><pre><span class="k">try</span><span class="p">:</span>
    <span class="n">item</span><span class="o">.</span><span class="n">save</span><span class="p">()</span>
    <span class="bp">self</span><span class="o">.</span><span class="n">fail</span><span class="p">(</span><span class="s">'The full_clean should have raised an exception'</span><span class="p">)</span>
<span class="k">except</span> <span class="n">ValidationError</span><span class="p">:</span>
    <span class="k">pass</span>
</pre></div></div></div>"""


CODE_LISTING_WITH_SKIPME = """
<div class="listingblock sourcecode skipme">
<div class="title">lists/functional_tests/test_list_item_validation.py</div>
<div class="content"><div class="highlight"><pre>    <span class="k">def</span> <span class="nf">DONTtest_cannot_add_empty_list_items</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span>
</pre></div></div></div>"""

OUTPUTS_WITH_DOFIRST = """
<div class="listingblock dofirst-ch09l058">
<div class="content">
<pre><code>$ <strong>grep -r id_new_item lists/</strong>

lists/static/base.css:#id_new_item {
lists/templates/list.html:        &lt;input name="item_text" id="id_new_item"
placeholder="Enter a to-do item" /&gt;</code></pre>
</div></div>"""

OUTPUTS_WITH_CURRENTCONTENTS = """
<div class="listingblock sourcecode currentcontents">
<div class="title">superlists/urls.py</div>
<div class="content"><div class="highlight"><pre><span class="kn">from</span> <span class="nn">django.conf.urls</span> <span class="kn">import</span> <span class="n">patterns</span><span class="p">,</span> <span class="n">include</span><span class="p">,</span> <span class="n">url</span>

<span class="kn">from</span> <span class="nn">django.contrib</span> <span class="kn">import</span> <span class="n">admin</span>
<span class="n">admin</span><span class="o">.</span><span class="n">autodiscover</span><span class="p">()</span>

<span class="n">urlpatterns</span> <span class="o">=</span> <span class="n">patterns</span><span class="p">(</span><span class="s">''</span><span class="p">,</span>
    <span class="c"># Examples:</span>
    <span class="c"># url(r'^$', 'superlists.views.home', name='home'),</span>
    <span class="c"># url(r'^blog/', include('blog.urls')),</span>

    <span class="n">url</span><span class="p">(</span><span class="s">r'^admin/'</span><span class="p">,</span> <span class="n">include</span><span class="p">(</span><span class="n">admin</span><span class="o">.</span><span class="n">site</span><span class="o">.</span><span class="n">urls</span><span class="p">)),</span>
<span class="p">)</span>
<span class="kn">from</span> <span class="nn">django.conf.urls</span> <span class="kn">import</span> <span class="n">patterns</span><span class="p">,</span> <span class="n">include</span><span class="p">,</span> <span class="n">url</span>
</pre></div></div></div>"""

JASMINE_OUTPUT = """
<div class="listingblock jasmine-output">
<div class="content">
<pre>2 specs, 0 failures, randomized with seed 12345        finished in 0.01s

Superlists tests
  * check we know how to hide things
  * sense check our html fixture</pre>
</div>
"""

OUTPUT_WITH_CONTINUATION = """
<div class="listingblock">
<div class="content">
<pre><code>$ <strong>wget -O bootstrap.zip https://github.com/twbs/bootstrap/releases/download/\
v3.1.0/bootstrap-3.1.0-dist.zip</strong>
$ <strong>unzip bootstrap.zip</strong>
$ <strong>mkdir lists/static</strong>
$ <strong>mv dist lists/static/bootstrap</strong>
$ <strong>rm bootstrap.zip</strong></code></pre>
</div></div>
"""


OUTPUT_WITH_COMMANDS_INLINE = """
<div class="listingblock">
<div class="content">
<pre><code>$ <strong>python manage.py makemigrations</strong>
You are trying to add a non-nullable field 'list' to item without a default;
we can't do that (the database needs something to populate existing rows).
Please select a fix:
 1) Provide a one-off default now (will be set on all existing rows)
 2) Quit, and let me add a default in models.py
Select an option: <strong>1</strong>
Please enter the default value now, as valid Python
The datetime module is available, so you can do e.g. datetime.date.today()
&gt;&gt;&gt; <strong>''</strong>
Migrations for 'lists':
  0003_item_list.py:
    - Add field list to item</code></pre>
</div></div>
"""


CODE_LISTING_WITH_ASCIIDOCTOR_CALLOUTS = """
<div class="exampleblock sourcecode">
<div class="title">src/lists/templates/base.html (ch16l004)</div>
<div class="content">
<div class="listingblock">
<div class="content">
<pre class="pygments highlight"><code data-lang="html"><span></span>    <span class="tok-p">&lt;/</span><span class="tok-nt">div</span><span class="tok-p">&gt;</span>

    <span class="tok-p">&lt;</span><span class="tok-nt">script</span><span class="tok-p">&gt;</span>
<span class="tok-w">      </span><span class="tok-kd">const</span><span class="tok-w"> </span><span class="tok-nx">textInput</span><span class="tok-w"> </span><span class="tok-o">=</span><span class="tok-w"> </span><span class="tok-nb">document</span><span class="tok-p">.</span><span class="tok-nx">querySelector</span><span class="tok-p">(</span><span class="tok-s2">&quot;#id_text&quot;</span><span class="tok-p">);</span><span class="tok-w">  </span><i class="conum" data-value="1"></i><b>(1)</b>
<span class="tok-w">      </span><span class="tok-nx">textInput</span><span class="tok-p">.</span><span class="tok-nx">oninput</span><span class="tok-w"> </span><span class="tok-o">=</span><span class="tok-w"> </span><span class="tok-p">()</span><span class="tok-w"> </span><span class="tok-p">=&gt;</span><span class="tok-w"> </span><span class="tok-p">{</span><span class="tok-w">  </span><i class="conum" data-value="2"></i><b>(2)</b> <i class="conum" data-value="3"></i><b>(3)</b>
<span class="tok-w">        </span><span class="tok-kd">const</span><span class="tok-w"> </span><span class="tok-nx">errorMsg</span><span class="tok-w"> </span><span class="tok-o">=</span><span class="tok-w"> </span><span class="tok-nb">document</span><span class="tok-p">.</span><span class="tok-nx">querySelector</span><span class="tok-p">(</span><span class="tok-s2">&quot;.invalid-feedback&quot;</span><span class="tok-p">);</span>
<span class="tok-w">        </span><span class="tok-nx">errorMsg</span><span class="tok-p">.</span><span class="tok-nx">style</span><span class="tok-p">.</span><span class="tok-nx">display</span><span class="tok-w"> </span><span class="tok-o">=</span><span class="tok-w"> </span><span class="tok-s2">&quot;none&quot;</span><span class="tok-p">;</span><span class="tok-w">  </span><i class="conum" data-value="4"></i><b>(4)</b>
<span class="tok-w">      </span><span class="tok-p">}</span>
<span class="tok-w">    </span><span class="tok-p">&lt;/</span><span class="tok-nt">script</span><span class="tok-p">&gt;</span></code></pre>
</div>
</div>
</div>
</div>
"""


OUTPUT_WITH_CALLOUTS = """<div class="listingblock">
<div class="content">
<pre>$ <strong>python manage.py test functional_tests.test_list_item_validation</strong>
Creating test database for alias 'default'...
E
======================================================================
ERROR: test_cannot_add_empty_list_items
(functional_tests.test_list_item_validation.ItemValidationTest)
 ---------------------------------------------------------------------
Traceback (most recent call last):
  File "...goat-book/functional_tests/test_list_item_validation.py", line
15, in test_cannot_add_empty_list_items
    self.wait_for(lambda: self.assertEqual(  <i class="conum" data-value="1"></i><b>(1)</b>
  File "...goat-book/functional_tests/base.py", line 37, in wait_for
    raise e  <i class="conum" data-value="2"></i><b>(2)</b>
  File "...goat-book/functional_tests/base.py", line 34, in wait_for
    return fn()  <i class="conum" data-value="2"></i><b>(2)</b>
  File "...goat-book/functional_tests/test_list_item_validation.py", line
16, in &lt;lambda&gt;  <i class="conum" data-value="3"></i><b>(3)</b>
    self.browser.find_element_by_css_selector('.has-error').text,  <i class="conum" data-value="3"></i><b>(3)</b>
[...]
selenium.common.exceptions.NoSuchElementException: Message: Unable to locate
element: .has-error


 ---------------------------------------------------------------------
Ran 1 test in 10.575s

FAILED (errors=1)</pre>
</div>
</div>"""

EXAMPLE_DIFF_LISTING = """
<div class="exampleblock sourcecode small-code">
<div class="title">lists/templates/home.html (ch07l018)</div>
<div class="content">
<div class="listingblock">
<div class="content">
<pre class="CodeRay highlight"><code data-lang="diff">   &lt;body&gt;
<span class="line delete"><span class="delete">-</span>    &lt;h1&gt;<span class="eyecatcher">Your</span> To-Do list&lt;/h1&gt;</span>
<span class="line insert"><span class="insert">+</span>    &lt;h1&gt;<span class="eyecatcher">Start a new</span> To-Do list&lt;/h1&gt;</span>
     &lt;form method=&quot;POST&quot; action=&quot;/&quot;&gt;
       &lt;input name=&quot;item_text&quot; id=&quot;id_new_item&quot; placeholder=&quot;Enter a to-do item&quot; /&gt;
       {% csrf_token %}
     &lt;/form&gt;
<span class="line delete"><span class="delete">-</span>    &lt;table id=&quot;id_list_table&quot;&gt;</span>
<span class="line delete"><span class="delete">-</span>      {% for item in items %}</span>
<span class="line delete"><span class="delete">-</span>        &lt;tr&gt;&lt;td&gt;{{ forloop.counter }}: {{ item.text }}&lt;/td&gt;&lt;/tr&gt;</span>
<span class="line delete"><span class="delete">-</span>      {% endfor %}</span>
<span class="line delete"><span class="delete">-</span>    &lt;/table&gt;</span>
   &lt;/body&gt;</code></pre>
</div>
</div>
</div>
</div>
"""
