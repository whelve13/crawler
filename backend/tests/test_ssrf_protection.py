import pytest
from app.crawler.url import is_safe_url

def test_is_safe_url_public():
    assert is_safe_url("https://example.com") is True
    assert is_safe_url("http://google.com/path") is True

def test_is_safe_url_localhost():
    assert is_safe_url("http://localhost") is False
    assert is_safe_url("http://localhost:8000") is False
    assert is_safe_url("http://127.0.0.1") is False
    assert is_safe_url("http://127.0.0.1:8080") is False

def test_is_safe_url_ipv6_localhost():
    assert is_safe_url("http://[::1]") is False
    assert is_safe_url("http://[::1]:80") is False
    assert is_safe_url("http://[::ffff:127.0.0.1]") is False

def test_is_safe_url_private_ipv4():
    assert is_safe_url("http://10.0.0.1") is False
    assert is_safe_url("http://192.168.1.1") is False
    assert is_safe_url("http://172.16.0.1") is False

def test_is_safe_url_private_ipv6():
    # Unique local address (ULA)
    assert is_safe_url("http://[fc00::1]") is False
    assert is_safe_url("http://[fd12:3456:789a:1::1]") is False

def test_is_safe_url_unspecified():
    assert is_safe_url("http://0.0.0.0") is False
    assert is_safe_url("http://[::]") is False

def test_is_safe_url_link_local():
    assert is_safe_url("http://169.254.169.254") is False
    assert is_safe_url("http://[fe80::1]") is False

def test_is_safe_url_multicast():
    assert is_safe_url("http://224.0.0.1") is False
    assert is_safe_url("http://[ff02::1]") is False

def test_is_safe_url_docker_internal():
    assert is_safe_url("http://host.docker.internal") is False
