CODE_LISTING_WITH_CAPTION = """<div class="listingblock sourcecode">
<div class="title">functional_tests.py</div>
<div class="content"><!-- Generator: GNU source-highlight 3.1.6
by Lorenzo Bettini
http://www.lorenzobettini.it
http://www.gnu.org/software/src-highlite -->
<pre><tt><span style="font-weight: bold"><span style="color: #000080">from</span></span> selenium <span style="font-weight: bold"><span style="color: #000080">import</span></span> webdriver

browser <span style="color: #990000">=</span> webdriver<span style="color: #990000">.</span><span style="font-weight: bold"><span style="color: #000000">Firefox</span></span><span style="color: #990000">()</span>
browser<span style="color: #990000">.</span><span style="font-weight: bold"><span style="color: #000000">get</span></span><span style="color: #990000">(</span><span style="color: #FF0000">'http://localhost:8000'</span><span style="color: #990000">)</span>

<span style="font-weight: bold"><span style="color: #0000FF">assert</span></span> <span style="color: #FF0000">'Django'</span> <span style="font-weight: bold"><span style="color: #0000FF">in</span></span> browser<span style="color: #990000">.</span>title</tt></pre></div></div>"""

CODE_LISTING_WITH_CAPTION_AND_GIT_COMMIT_REF = """<div class="listingblock sourcecode">
<div class="listingblock sourcecode">
<div class="title">functional_tests/tests.py (ch07l001)</div>
<div class="content"><div class="highlight"><pre><span class="k">class</span> <span class="nc">NewVisitorTest</span><span class="p">(</span><span class="n">LiveServerTestCase</span><span class="p">):</span>
    <span class="p">[</span><span class="o">...</span><span class="p">]</span>


    <span class="k">def</span> <span class="nf">test_layout_and_styling</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span>
        <span class="c"># Edith goes to the home page</span>
        <span class="bp">self</span><span class="o">.</span><span class="n">browser</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">live_server_url</span><span class="p">)</span>

        <span class="c"># She notices the input box is nicely centered</span>
        <span class="n">inputbox</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">browser</span><span class="o">.</span><span class="n">find_element_by_tag_name</span><span class="p">(</span><span class="s">'input'</span><span class="p">)</span>
        <span class="n">window_width</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">browser</span><span class="o">.</span><span class="n">get_window_size</span><span class="p">()[</span><span class="s">'width'</span><span class="p">]</span>
        <span class="bp">self</span><span class="o">.</span><span class="n">assertAlmostEqual</span><span class="p">(</span>
            <span class="n">inputbox</span><span class="o">.</span><span class="n">location</span><span class="p">[</span><span class="s">'x'</span><span class="p">]</span> <span class="o">+</span> <span class="n">inputbox</span><span class="o">.</span><span class="n">size</span><span class="p">[</span><span class="s">'width'</span><span class="p">]</span> <span class="o">/</span> <span class="mi">2</span><span class="p">,</span>
            <span class="n">window_width</span> <span class="o">/</span> <span class="mi">2</span><span class="p">,</span>
            <span class="n">delta</span><span class="o">=</span><span class="mi">3</span>
        <span class="p">)</span>
</pre></div></div></div>"""


SERVER_COMMAND = """<div class="listingblock server-commands">
<div class="content">
<pre><code>elspeth@server:$ <strong>sudo do stuff</strong></code></pre>
</div></div>"""


COMMANDS_WITH_VIRTUALENV = """<div class="listingblock">
<div class="content">
<pre><code>$ <strong>source ../virtualenv/bin/activate</strong>
(virtualenv)$ <strong>python3 manage.py test lists</strong>
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


COMMAND_MADE_WITH_ATS="""
<div class="listingblock">
<div class="content">
<pre><code>$ <strong>grep id_new_item functional_tests/tests/test*</strong></code></pre>
</div></div>
"""

OUTPUT_WITH_SKIPME="""
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

OUTPUT_QUNIT = """
<div class="listingblock qunit-output">
<div class="title">Expected results from Qunit in browser</div>
<div class="content">
<pre><code>2 assertions of 2 passed, 0 failed.
1. smoke test (0, 2, 2)</code></pre>
</div></div>"""

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
<pre><code>$ <strong>python3 manage.py makemigrations</strong>
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
<div class="listingblock sourcecode">
<div class="title">functional_tests.py</div>
<div class="content">
<pre class="pygments highlight"><code data-lang="python"><span class="tok-kn">from</span> <span class="tok-nn">selenium</span> <span class="tok-kn">import</span> <span class="tok-n">webdriver</span>
<span class="tok-kn">import</span> <span class="tok-nn">unittest</span>

<span class="tok-k">class</span> <span class="tok-nc">NewVisitorTest</span><span class="tok-p">(</span><span class="tok-n">unittest</span><span class="tok-o">.</span><span class="tok-n">TestCase</span><span class="tok-p">):</span>  <i class="conum" data-value="1"></i><b>(1)</b>

    <span class="tok-k">def</span> <span class="tok-nf">setUp</span><span class="tok-p">(</span><span class="tok-bp">self</span><span class="tok-p">):</span>  <i class="conum" data-value="3"></i><b>(3)</b>
        <span class="tok-bp">self</span><span class="tok-o">.</span><span class="tok-n">browser</span> <span class="tok-o">=</span> <span class="tok-n">webdriver</span><span class="tok-o">.</span><span class="tok-n">Firefox</span><span class="tok-p">()</span>

    <span class="tok-k">def</span> <span class="tok-nf">tearDown</span><span class="tok-p">(</span><span class="tok-bp">self</span><span class="tok-p">):</span>  <i class="conum" data-value="3"></i><b>(3)</b>
        <span class="tok-bp">self</span><span class="tok-o">.</span><span class="tok-n">browser</span><span class="tok-o">.</span><span class="tok-n">quit</span><span class="tok-p">()</span>

    <span class="tok-k">def</span> <span class="tok-nf">test_can_start_a_list_and_retrieve_it_later</span><span class="tok-p">(</span><span class="tok-bp">self</span><span class="tok-p">):</span>  <i class="conum" data-value="2"></i><b>(2)</b>
        <span class="tok-c"># Edith has heard about a cool new online to-do app. She goes</span>
        <span class="tok-c"># to check out its homepage</span>
        <span class="tok-bp">self</span><span class="tok-o">.</span><span class="tok-n">browser</span><span class="tok-o">.</span><span class="tok-n">get</span><span class="tok-p">(</span><span class="tok-s">&#39;http://localhost:8000&#39;</span><span class="tok-p">)</span>

        <span class="tok-c"># She notices the page title and header mention to-do lists</span>
        <span class="tok-bp">self</span><span class="tok-o">.</span><span class="tok-n">assertIn</span><span class="tok-p">(</span><span class="tok-s">&#39;To-Do&#39;</span><span class="tok-p">,</span> <span class="tok-bp">self</span><span class="tok-o">.</span><span class="tok-n">browser</span><span class="tok-o">.</span><span class="tok-n">title</span><span class="tok-p">)</span>  <i class="conum" data-value="4"></i><b>(4)</b>
        <span class="tok-bp">self</span><span class="tok-o">.</span><span class="tok-n">fail</span><span class="tok-p">(</span><span class="tok-s">&#39;Finish the test!&#39;</span><span class="tok-p">)</span>  <i class="conum" data-value="5"></i><b>(5)</b>

        <span class="tok-c"># She is invited to enter a to-do item straight away</span>
        <span class="tok-p">[</span><span class="tok-o">...</span><span class="tok-n">rest</span> <span class="tok-n">of</span> <span class="tok-n">comments</span> <span class="tok-k">as</span> <span class="tok-n">before</span><span class="tok-p">]</span>

<span class="tok-k">if</span> <span class="tok-n">__name__</span> <span class="tok-o">==</span> <span class="tok-s">&#39;__main__&#39;</span><span class="tok-p">:</span>  <i class="conum" data-value="6"></i><b>(6)</b>
    <span class="tok-n">unittest</span><span class="tok-o">.</span><span class="tok-n">main</span><span class="tok-p">(</span><span class="tok-n">warnings</span><span class="tok-o">=</span><span class="tok-s">&#39;ignore&#39;</span><span class="tok-p">)</span>  <i class="conum" data-value="7"></i><b>(7)</b></code></pre>
</div>
</div>
"""
