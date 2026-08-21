from app.crawler.url import (
    URLTracker,
    get_domain,
    is_http_or_https,
    is_same_domain,
    is_valid_url,
    normalize_url,
    resolve_url,
)


def test_is_http_or_https():
    assert is_http_or_https("http://example.com") is True
    assert is_http_or_https("https://example.com") is True
    assert is_http_or_https("ftp://example.com") is False
    assert is_http_or_https("mailto:test@example.com") is False
    assert is_http_or_https("example.com") is False

def test_is_valid_url():
    assert is_valid_url("https://example.com") is True
    assert is_valid_url("http://example.com/path") is True
    assert is_valid_url("https://example.com?query=1") is True
    # Invalid URLs
    assert is_valid_url("ftp://example.com") is False
    assert is_valid_url("example.com") is False
    assert is_valid_url("/relative/path") is False

def test_normalize_url():
    # Remove fragments
    assert normalize_url("https://example.com/#section") == "https://example.com"
    # Remove trailing slashes
    assert normalize_url("https://example.com/") == "https://example.com"
    assert normalize_url("https://example.com/path/") == "https://example.com/path"
    # Lowercase domain and scheme
    assert normalize_url("HTTPS://EXAMPLE.COM") == "https://example.com"
    # Complex URL
    assert (
        normalize_url("HTTP://Example.COM/Path/?query=1#frag")
        == "http://example.com/Path?query=1"
    )

def test_resolve_url():
    base = "https://example.com/blog/"
    assert resolve_url(base, "post-1") == "https://example.com/blog/post-1"
    assert resolve_url(base, "/about") == "https://example.com/about"
    assert resolve_url(base, "https://other.com") == "https://other.com"
    assert resolve_url(base, "?q=test") == "https://example.com/blog?q=test"
    assert resolve_url(base, "#section") == "https://example.com/blog"

def test_get_domain():
    assert get_domain("https://example.com/path") == "example.com"
    assert get_domain("http://sub.example.com") == "sub.example.com"
    assert get_domain("https://EXAMPLE.COM") == "example.com"

def test_is_same_domain():
    assert is_same_domain("https://example.com", "http://example.com/path") is True
    assert is_same_domain("https://example.com", "https://sub.example.com") is False
    assert is_same_domain("https://example.com", "https://other.com") is False

def test_url_tracker():
    tracker = URLTracker()
    
    url1 = "https://example.com/page/"
    url2 = "https://example.com/page#section"
    
    assert tracker.is_visited(url1) is False
    
    tracker.mark_visited(url1)
    
    assert tracker.is_visited(url1) is True
    assert tracker.is_visited(url2) is True  # Should match normalized form
    
    tracker.mark_visited(url2)  # Should not raise error, effectively a no-op
    
    assert tracker.is_visited("https://example.com/other") is False
