from app.crawler.parser import HTMLParser

FIXTURE_HTML = """
<!DOCTYPE html>
<html lang="en-US">
<head>
    <title> Test Page - SEO Crawler </title>
    <meta name="description" content="This is a test meta description.">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://example.com/canonical-path">
</head>
<body>
    <h1>Main Heading</h1>
    <h1>Second H1!</h1>
    <h2>Subheading 1</h2>
    <h2>Subheading 2</h2>
    
    <p>Check out our <a href="/about" rel="nofollow">About Us</a> page.</p>
    <p>And our <a href="https://external.com">External Link</a>.</p>
    <p>Invalid link <a href="javascript:void(0)">Click Here</a>.</p>
    
    <img src="/images/logo.png" alt="Company Logo">
    <img src="https://example.com/images/no-alt.jpg">
    <img src="/images/empty-alt.gif" alt="">
</body>
</html>
"""

def test_html_parser_metadata():
    parser = HTMLParser(FIXTURE_HTML, base_url="https://example.com")
    parsed = parser.parse()
    
    assert parsed.title == "Test Page - SEO Crawler"
    assert parsed.meta_description == "This is a test meta description."
    assert parsed.canonical_url == "https://example.com/canonical-path"
    assert parsed.language == "en-US"
    assert parsed.robots_meta == "index, follow"

def test_html_parser_missing_metadata():
    empty_html = "<html><body><h1>Hello</h1></body></html>"
    parser = HTMLParser(empty_html, base_url="https://example.com")
    parsed = parser.parse()
    
    assert parsed.title is None
    assert parsed.meta_description is None
    assert parsed.canonical_url is None
    assert parsed.language is None
    assert parsed.robots_meta is None

def test_html_parser_headings():
    parser = HTMLParser(FIXTURE_HTML, base_url="https://example.com")
    parsed = parser.parse()
    
    assert parsed.h1_tags == ["Main Heading", "Second H1!"]
    assert parsed.h2_tags == ["Subheading 1", "Subheading 2"]
    assert parsed.h3_tags == []

def test_html_parser_images():
    parser = HTMLParser(FIXTURE_HTML, base_url="https://example.com")
    parsed = parser.parse()
    
    assert len(parsed.images) == 3
    
    assert parsed.images[0].src == "https://example.com/images/logo.png"
    assert parsed.images[0].alt == "Company Logo"
    
    assert parsed.images[1].src == "https://example.com/images/no-alt.jpg"
    assert parsed.images[1].alt is None
    
    assert parsed.images[2].src == "https://example.com/images/empty-alt.gif"
    assert parsed.images[2].alt == ""

def test_html_parser_links():
    parser = HTMLParser(FIXTURE_HTML, base_url="https://example.com")
    parsed = parser.parse()
    
    assert len(parsed.links) == 2  # javascript link is filtered out
    
    assert parsed.links[0].href == "https://example.com/about"
    assert parsed.links[0].text == "About Us"
    assert parsed.links[0].is_nofollow is True
    
    assert parsed.links[1].href == "https://external.com"
    assert parsed.links[1].text == "External Link"
    assert parsed.links[1].is_nofollow is False
