from app.crawler.audit import (
    CanonicalRule,
    H1Rule,
    ImageAltRule,
    MetaDescriptionRule,
    SEOAuditEngine,
    TitleRule,
)
from app.crawler.parser import ImageInfo, ParsedHTML


def test_title_rule():
    rule = TitleRule()
    page_url = "https://example.com"
    
    # Missing
    parsed = ParsedHTML(title=None)
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert "Missing" in issues[0].message
    
    # Empty
    parsed = ParsedHTML(title="   ")
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert "Empty" in issues[0].message
    
    # Too long
    parsed = ParsedHTML(title="A" * 61)
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert "excessively long" in issues[0].message
    
    # Good
    parsed = ParsedHTML(title="Good Title")
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 0

def test_meta_description_rule():
    rule = MetaDescriptionRule()
    page_url = "https://example.com"
    
    # Missing
    parsed = ParsedHTML(meta_description=None)
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    
    # Empty
    parsed = ParsedHTML(meta_description="")
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    
    # Too long
    parsed = ParsedHTML(meta_description="A" * 161)
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 1
    assert issues[0].severity == "warning"
    
    # Good
    parsed = ParsedHTML(meta_description="Good description.")
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 0

def test_h1_rule():
    rule = H1Rule()
    page_url = "https://example.com"
    
    # Missing
    parsed = ParsedHTML(h1_tags=[])
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    
    # Multiple
    parsed = ParsedHTML(h1_tags=["One", "Two"])
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 1
    assert issues[0].severity == "warning"
    
    # Good
    parsed = ParsedHTML(h1_tags=["Just One"])
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 0

def test_image_alt_rule():
    rule = ImageAltRule()
    page_url = "https://example.com"
    
    # Missing alt
    parsed = ParsedHTML(images=[ImageInfo(src="1.jpg", alt=None)])
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    
    # Empty alt
    parsed = ParsedHTML(images=[ImageInfo(src="2.jpg", alt="")])
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 1
    assert issues[0].severity == "warning"
    
    # Good alt
    parsed = ParsedHTML(images=[ImageInfo(src="3.jpg", alt="Good")])
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 0

def test_canonical_rule():
    rule = CanonicalRule()
    page_url = "https://example.com/page"
    
    # Missing
    parsed = ParsedHTML(canonical_url=None)
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 1
    assert issues[0].severity == "warning"
    
    # Malformed
    parsed = ParsedHTML(canonical_url="not-a-url")
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    
    # Pointing outside domain
    parsed = ParsedHTML(canonical_url="https://other.com/page")
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 1
    assert issues[0].severity == "warning"
    
    # Good
    parsed = ParsedHTML(canonical_url="https://example.com/other-page")
    issues = rule.evaluate(page_url, parsed)
    assert len(issues) == 0

def test_seo_audit_engine():
    engine = SEOAuditEngine()
    
    parsed = ParsedHTML(
        title="Test", 
        meta_description=None, 
        h1_tags=[],
        canonical_url="https://other.com",
        images=[ImageInfo(src="img.jpg", alt=None)]
    )
    
    issues = engine.run_audit("https://example.com", parsed)
    
    # Expecting: 
    # title is good
    # meta_desc is missing (1)
    # h1 is missing (1)
    # canonical points outside (1)
    # image missing alt (1)
    
    assert len(issues) == 4
