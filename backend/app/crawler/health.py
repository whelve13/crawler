from dataclasses import dataclass


@dataclass
class HealthIssue:
    url: str
    issue_type: str  # "broken_link", "redirect_loop", "redirect_chain", "timeout", "server_error"
    description: str


@dataclass
class URLHealth:
    url: str
    status_code: int | None = None
    error_type: str | None = None
    redirect_target: str | None = None
    
    @property
    def is_broken(self) -> bool:
        return (self.status_code and self.status_code >= 400) or self.error_type is not None


class LinkHealthAnalyzer:
    """
    Tracks and analyzes HTTP status codes, redirects, and link health across a crawl.
    """

    def __init__(self, max_redirect_chain: int = 4):
        self.max_redirect_chain = max_redirect_chain
        # url -> Health data
        self.health_data: dict[str, URLHealth] = {}
        # source_url -> target_url
        self.redirects: dict[str, str] = {}
        # source_page -> set(linked_urls)
        self.links: dict[str, set[str]] = {}

    def record_visit(
        self,
        url: str,
        status_code: int | None = None,
        error_type: str | None = None,
        redirect_target: str | None = None,
    ):
        """Record the HTTP response of a URL fetch."""
        self.health_data[url] = URLHealth(
            url=url,
            status_code=status_code,
            error_type=error_type,
            redirect_target=redirect_target,
        )
        if redirect_target:
            self.redirects[url] = redirect_target

    def record_links(self, page_url: str, linked_urls: set[str]):
        """Record all outgoing links found on a specific page."""
        if page_url not in self.links:
            self.links[page_url] = set()
        self.links[page_url].update(linked_urls)

    def get_redirect_chain(self, start_url: str) -> tuple[list[str], bool]:
        """
        Follows the redirect path for a URL.
        Returns a tuple of (chain_list, is_loop).
        """
        chain = []
        current = start_url
        is_loop = False
        
        while current in self.redirects:
            target = self.redirects[current]
            chain.append(target)
            if target in chain[:-1] or target == start_url:
                is_loop = True
                break
            current = target
            
        return chain, is_loop

    def analyze(self) -> list[HealthIssue]:
        """Analyze all recorded data to produce a list of health issues."""
        issues = []
        
        # 1. Analyze Redirects
        for url in self.redirects:
            chain, is_loop = self.get_redirect_chain(url)
            if is_loop:
                chain_str = " -> ".join([url] + chain)
                issues.append(HealthIssue(url, "redirect_loop", f"Redirect loop detected: {chain_str}"))
            elif len(chain) > self.max_redirect_chain:
                chain_str = " -> ".join([url] + chain)
                issues.append(HealthIssue(url, "redirect_chain", f"Excessive redirect chain ({len(chain)} hops): {chain_str}"))

        # 2. Analyze Broken Links
        # Any URL that was linked to, and we fetched, but returned a broken state
        for source_page, outgoing_links in self.links.items():
            for link in outgoing_links:
                # We trace the link through any redirects to find its final destination health
                chain, _ = self.get_redirect_chain(link)
                final_url = chain[-1] if chain else link
                
                if final_url in self.health_data:
                    health = self.health_data[final_url]
                    if health.is_broken:
                        if health.error_type:
                            msg = f"Linked URL failed with {health.error_type} (Found on {source_page})"
                            issues.append(HealthIssue(link, "connection_error", msg))
                        elif health.status_code:
                            msg = f"Linked URL returned {health.status_code} (Found on {source_page})"
                            issues.append(HealthIssue(link, "broken_link", msg))
                
        return issues
