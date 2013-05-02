CODE_LISTING_WITH_CAPTION = """<div class="listingblock">
<div class="content"><!-- Generator: GNU source-highlight 3.1.6
by Lorenzo Bettini
http://www.lorenzobettini.it
http://www.gnu.org/software/src-highlite -->
<pre><tt><span style="font-weight: bold"><span style="color: #000080">from</span></span> selenium <span style="font-weight: bold"><span style="color: #000080">import</span></span> webdriver

browser <span style="color: #990000">=</span> webdriver<span style="color: #990000">.</span><span style="font-weight: bold"><span style="color: #000000">Firefox</span></span><span style="color: #990000">()</span>
browser<span style="color: #990000">.</span><span style="font-weight: bold"><span style="color: #000000">get</span></span><span style="color: #990000">(</span><span style="color: #FF0000">'http://localhost:8000'</span><span style="color: #990000">)</span>

<span style="font-weight: bold"><span style="color: #0000FF">assert</span></span> <span style="color: #FF0000">'Django'</span> <span style="font-weight: bold"><span style="color: #0000FF">in</span></span> browser<span style="color: #990000">.</span>title</tt></pre></div></div>&#13;

<div class="paragraph caption"><p>functional_tests.py</p></div>&#13;
"""

