from app.crawler.url import is_safe_url


def test_ssrf_protection():
    assert not is_safe_url("http://localhost:8000")
    assert not is_safe_url("http://127.0.0.1/admin")
    assert not is_safe_url("http://10.0.0.5/api")
    assert not is_safe_url("http://192.168.1.1")
    assert not is_safe_url("http://169.254.169.254")
    assert not is_safe_url("http://[::1]")
    assert not is_safe_url("http://host.docker.internal")
    
    assert is_safe_url("https://google.com")
    assert is_safe_url("https://999.md")
