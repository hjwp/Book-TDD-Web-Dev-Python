<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns="http://www.w3.org/1999/xhtml"
                exclude-result-prefixes="h">

  <!-- Add title heading elements for different admonition types that do not already have headings in markup -->
  <xsl:param name="add.title.heading.for.admonitions" select="1"/>  

  <!-- Override to print example captions without labels-->
  <xsl:template match="h:div[@data-type='example' and contains(@class, 'sourcecode')]/h:h5" mode="process-heading">
    <p>
      <xsl:apply-templates/>
    </p>
  </xsl:template>

  <!-- Insert SCRATCHPAD: heading for all sidebars with 'scratchpad' class -->
  <xsl:template match="h:aside[@data-type='sidebar' and contains(@class, 'scratchpad')]//h:h5">
    <h5>SCRATCHPAD:</h5>
    <xsl:apply-templates/>
  </xsl:template> 

  <!-- Fix for TOC having empty ol. Matches sections that contain only descendants with the notoc class. We do this by setting the TOC section depth to 1. -->
<xsl:template match="h:section[descendant::h:section[contains(@class, 'notoc')] and not(descendant::h:section[contains(@data-type, 'sect1') and not(contains(@class, 'notoc'))])]" mode="tocgen">
    <xsl:param name="toc.section.depth" select="1"/>
    <xsl:param name="inline.markup.in.toc" select="$inline.markup.in.toc"/>
    <xsl:choose>
      <!-- Don't output entry for section elements at a level that is greater than specified $toc.section.depth -->
      <xsl:when test="self::h:section[contains(@data-type, 'sect') and htmlbook:section-depth(.) != '' and htmlbook:section-depth(.) &gt; 1]"/>
      <!-- Don't output entry if a class of "notoc" is specified -->
      <xsl:when test="contains(@class, 'notoc')"/>
      <!-- Otherwise, go ahead -->
      <xsl:otherwise>
        <xsl:element name="li">
          <xsl:attribute name="data-type">
            <xsl:value-of select="@data-type"/>
          </xsl:attribute>
          <a>
            <xsl:attribute name="href">
              <xsl:call-template name="href.target">
                <xsl:with-param name="object" select="."/>
              </xsl:call-template>
            </xsl:attribute>
            <xsl:if test="$toc-include-labels = 1">
              <xsl:variable name="toc-entry-label">
                <xsl:apply-templates select="." mode="label.markup"/>
              </xsl:variable>
              <xsl:value-of select="normalize-space($toc-entry-label)"/>
              <xsl:if test="$toc-entry-label != ''">
                <xsl:value-of select="$label.and.title.separator"/>
              </xsl:if>
            </xsl:if>
            <xsl:choose>
              <xsl:when test="$inline.markup.in.toc = 1">
                <!-- Include inline elements in TOC entry -->
                <xsl:apply-templates select="." mode="title.markup"/>
              </xsl:when>
              <xsl:otherwise>
                <!-- Strip inline tagging from TOC entry: raw text only -->
                <xsl:variable name="title.markup">
                  <xsl:apply-templates select="." mode="title.markup"/>
                </xsl:variable>
                <xsl:value-of select="$title.markup"/>
              </xsl:otherwise>
            </xsl:choose>    
          </a>
          <!-- Make sure there are descendants that conform to $toc.section.depth restrictions before generating nested TOC <ol> -->
          <xsl:if test="descendant::h:section[not(contains(@data-type, 'sect')) or htmlbook:section-depth(.) &lt;= 1]|descendant::h:div[@data-type='part']">
            <ol>
              <xsl:apply-templates mode="tocgen">
                <xsl:with-param name="toc.section.depth" select="1"/>
              </xsl:apply-templates>
            </ol>
          </xsl:if>
        </xsl:element>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
                                                                              
</xsl:stylesheet>
