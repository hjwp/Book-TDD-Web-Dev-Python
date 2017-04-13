<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns="http://www.w3.org/1999/xhtml"
                exclude-result-prefixes="h">

  <!-- Do add border div for figure images in animal series -->
  <xsl:param name="figure.border.div" select="1"/>

  <!-- This param is required for animal_theme_sass, but not the old animal_theme -->
  <!-- Generate separate footnote-call markers, so that we don't
       need to rely on AH counters to do footnote numbering -->
  <xsl:param name="process.footnote.callouts.only" select="1"/>


<xsl:template name="string-replace-all">
  <xsl:param name="text"/>
  <xsl:param name="replace"/>
  <xsl:param name="by"/>
  <xsl:choose>
    <xsl:when test="contains($text, $replace)">
      <xsl:value-of select="substring-before($text,$replace)"/>
      <xsl:value-of select="$by"/>
      <xsl:call-template name="string-replace-all">
        <xsl:with-param name="text" select="substring-after($text,$replace)"/>
        <xsl:with-param name="replace" select="$replace"/>
        <xsl:with-param name="by" select="$by"/>
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$text"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="h:img/@src">
  <xsl:choose>
  <xsl:when test="contains(., 'callouts/')">
    <xsl:variable name="newtext">
      <xsl:call-template name="string-replace-all">
        <xsl:with-param name="text" select="."/>
        <xsl:with-param name="replace" select="'png'"/>
        <xsl:with-param name="by" select="'pdf'"/>
      </xsl:call-template>
    </xsl:variable>
     <xsl:attribute name="src">
        <xsl:value-of select="$newtext"/>
     </xsl:attribute>
  </xsl:when>
  <xsl:otherwise>
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
   </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="programlisting|screen|synopsis" mode="class.value">
  <xsl:param name="class" select="local-name(.)"/>
  <xsl:choose>
    <xsl:when test="@role">
      <xsl:value-of select="concat($class, ' ', @role)"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$class"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template match="figure|table|example" mode="label.markup">
  <xsl:variable name="pchap"
                select="ancestor::chapter
                        |ancestor::appendix
                        |ancestor::article[ancestor::book]"/>

  <xsl:variable name="prefix">
    <xsl:if test="count($pchap) &gt; 0">
      <xsl:apply-templates select="$pchap" mode="label.markup"/>
    </xsl:if>
  </xsl:variable>

  <xsl:choose>
    <xsl:when test="@label">
      <xsl:value-of select="@label"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:choose>
        <xsl:when test="$prefix != ''">
          <xsl:choose>
            <xsl:when test="ancestor::chapter and count(/book//chapter) = 1"/>
            <xsl:otherwise>
              <xsl:apply-templates select="$pchap" mode="label.markup"/>
              <xsl:apply-templates select="$pchap" mode="intralabel.punctuation"/>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:number format="1" from="chapter|appendix" level="any"/>
        </xsl:when>


 <!-- Oneoff taken from Labels.xsl -->
 <!-- ORM: Use P- for Preface, ala Frame (or I- for Introduction in MMs); see RT #45135 -->
        <xsl:when test="ancestor::preface">
          <xsl:variable name="thispreface" select="ancestor::preface"/>
          <xsl:variable name="title">
            <xsl:value-of select="$thispreface/title"/>
          </xsl:variable>
          <xsl:choose>
            <xsl:when test="contains($title, 'Preface')">
              <xsl:text>P</xsl:text>
              <xsl:apply-templates select="$thispreface" mode="intralabel.punctuation"/>
              <xsl:number format="1" from="preface" level="any"/>
            </xsl:when>
            <xsl:when test="contains($title, 'Prerequisites')">
              <xsl:text>P</xsl:text>
              <xsl:apply-templates select="$thispreface" mode="intralabel.punctuation"/>
              <xsl:number format="1" from="preface" level="any"/>
            </xsl:when>
             <!-- Oneoff starts here - I'm just putting Setup there so that it registers instead of running the otherwise message and so that S is put in there. -->
            <xsl:when test="contains($title, 'Setup')">
              <xsl:text>S</xsl:text>
              <xsl:apply-templates select="$thispreface" mode="intralabel.punctuation"/>
              <xsl:number format="1" from="preface" level="any"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:message>WARNING: Formal object (<xsl:value-of select="local-name()"/>) encountered in nonstandard &lt;preface&gt; (title=<xsl:value-of select="$title"/>, id=<xsl:value-of select="@id"/>). Please change markup or contact toolsreq@oreilly.com to discuss desired caption labels.</xsl:message>
              <xsl:text>**LABEL TBD**</xsl:text>
              <xsl:apply-templates select="$thispreface" mode="intralabel.punctuation"/>
              <xsl:number format="1" from="preface" level="any"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:when>
        
  <!-- Use uppercase roman numerals for parts -->
        <xsl:when test="ancestor::part">
          <xsl:variable name="ppart"
            select="ancestor::part"/>
          <xsl:variable name="part_prefix">
            <xsl:if test="count($ppart) &gt; 0">
              <xsl:apply-templates select="$ppart" mode="label.markup"/>
            </xsl:if>
          </xsl:variable>
          <xsl:if test="$part_prefix != ''">
            <xsl:apply-templates select="$ppart" mode="label.markup"/>
            <!-- This allows us to use hyphen as label separator in fig captions -->
            <xsl:apply-templates select="." mode="intralabel.punctuation"/>
          </xsl:if>
          <xsl:number format="1" from="part" level="any"/>
        </xsl:when>
        
        <xsl:otherwise>
          <xsl:number format="1" from="book|article" level="any"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


</xsl:stylesheet>
