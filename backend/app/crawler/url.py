from urllib.parse import urldefrag, urljoin, urlparse


def is_http_or_https(url: str) -> bool:
    """Check if the URL has an HTTP or HTTPS scheme."""
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https")

import ipaddress
import socket

def is_valid_url(url: str) -> bool:
    """Basic validation to ensure URL has a scheme and network location."""
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc) and is_http_or_https(url)

def is_safe_url(url: str) -> bool:
    """
    SSRF Protection: Validates that the URL does not resolve to an internal,
    private, or loopback IP address (IPv4 and IPv6).
    """
    if not is_valid_url(url):
        return False
        
    hostname = urlparse(url).hostname
    if not hostname:
        return False
        
    # Remove IPv6 brackets if present
    hostname = hostname.strip("[]")
        
    # Block explicit internal hostnames
    if hostname in ("localhost", "host.docker.internal"):
        return False
        
    try:
        # Use getaddrinfo to fetch both IPv4 and IPv6 addresses
        # socket.AF_UNSPEC means both IPv4 and IPv6
        # socket.SOCK_STREAM is used to restrict the results just to TCP (to avoid duplicates)
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        
        if not addr_info:
            return False
            
        for _, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)
            
            # Check for IPv4-mapped IPv6 addresses (e.g. ::ffff:127.0.0.1)
            if ip_obj.version == 6 and ip_obj.ipv4_mapped:
                ip_obj = ip_obj.ipv4_mapped
            
            # Block private, loopback, link-local, multicast, reserved, etc.
            if (
                ip_obj.is_private or 
                ip_obj.is_loopback or 
                ip_obj.is_link_local or 
                ip_obj.is_multicast or
                ip_obj.is_reserved or
                ip_obj.is_unspecified
            ):
                return False
            
    except (socket.gaierror, ValueError):
        # ValueError can occur if ipaddress.ip_address fails to parse
        return False
        
    return True

def normalize_url(url: str) -> str:
    """
    Normalize the URL by:
    1. Removing the fragment.
    2. Removing trailing slashes.
    3. Lowercasing the scheme and domain.
    """
    # Remove fragment
    url, _ = urldefrag(url)
    
    parsed = urlparse(url)
    
    # Lowercase scheme and netloc (domain)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    
    # Reconstruct the normalized URL components
    # path, params, query, fragment
    path = parsed.path
    if path == "/":
        path = ""
    elif path.endswith("/"):
        path = path[:-1]
        
    normalized = f"{scheme}://{netloc}{path}"
    
    if parsed.params:
        normalized += f";{parsed.params}"
    if parsed.query:
        normalized += f"?{parsed.query}"
        
    return normalized

def resolve_url(base_url: str, target_url: str) -> str:
    """Resolve a potentially relative URL against a base URL and normalize it."""
    joined = urljoin(base_url, target_url)
    return normalize_url(joined)

def get_domain(url: str) -> str:
    """Extract the domain (netloc) from a URL."""
    return urlparse(url).netloc.lower()

def is_same_domain(url1: str, url2: str) -> bool:
    """Compare if two URLs belong to the exact same domain."""
    return get_domain(url1) == get_domain(url2)

class URLTracker:
    """
    Tracks visited URLs to prevent duplicate crawling.
    All URLs are normalized before being added.
    """
    def __init__(self):
        self._visited: set[str] = set()
        
    def mark_visited(self, url: str) -> None:
        """Mark a URL as visited."""
        normalized = normalize_url(url)
        self._visited.add(normalized)
        
    def is_visited(self, url: str) -> bool:
        """Check if a URL has already been visited."""
        normalized = normalize_url(url)
        return normalized in self._visited
