<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="#all"
    version="2.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0">
    
    
    <xsl:output method="xml" indent="yes"/>
    <xsl:strip-space elements="*"/>
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <!-- Verbreitung -->
    <!-- wrap all //entry/usg in usg[@type='verbreitung'] 
    <xsl:template match="usg">
        <xsl:copy>
            <xsl:variable name="parent" select="."/>
            <usg type="verbreitung">
                <xsl:for-each-group select="descendant::node()" group-starting-with="usg[@type='geo']">      
                    <xsl:apply-templates select="$parent/node()[descendant-or-self::node() intersect current-group()]" mode="subtree"/>
                </xsl:for-each-group>
            </usg>
        </xsl:copy>
    </xsl:template>
    
    
    <xsl:template match="node()" mode="subtree">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates select="node()[descendant-or-self::node() intersect current-group()]" mode="subtree"/>
        </xsl:copy>
        
    </xsl:template>
-->
    <xsl:template match="usg[@type='geo'][1]">
        <usg type="verbreitung">
            <xsl:copy-of select="."/>
            <xsl:for-each select="following-sibling::usg[@type='geo']">
                <xsl:copy-of select="."/>
            </xsl:for-each>
        </usg>
    </xsl:template>
    
    <xsl:template match="usg[@type='geo'][position() != 1]"/>
            
            <!-- copy each <usg type="geo"> -->

        
     

    
    <!-- add <note type="kommentar"> after verbreitung and before first <form type="dialect"> -->
    
    <!-- find all <form type="dialect"> containing geo from "STir" and change value of //pron[@xml:id] to "bar-IT" -->
    
    <!-- wrap <sense> if not at least 2 layers -->
    
    <!-- Add @type on <re> (either "wortbildung" or "redenwendung") -->


</xsl:stylesheet>