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


COMMAND_LISTING_WITH_CAPTION = """<div class="listingblock">
<div class="title">server commands</div>
<div class="content">
<pre><code>user@server:$ <strong>sudo apt-get install git</strong>
user@server:$ <strong>sudo apt-get install python3</strong>
user@server:$ <strong>sudo apt-get install python3-pip</strong>
user@server:$ <strong>sudo pip3 install virtualenv</strong></code></pre>
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
