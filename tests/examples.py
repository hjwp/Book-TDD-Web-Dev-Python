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
<pre><code><strong>sudo apt-get install git</strong>
<strong>sudo apt-get install python3</strong>
<strong>sudo apt-get install python3-pip</strong>
<strong>sudo pip-3.3 install virtualenv</strong></code></pre>
</div></div>"""
