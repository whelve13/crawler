from dataclasses import dataclass, field

from bs4 import BeautifulSoup

from app.crawler.url import is_valid_url, resolve_url


@dataclass
class ImageInfo:
    src: str
    alt: str | None


@dataclass
class LinkInfo:
    href: str
    text: str
    is_nofollow: bool


@dataclass
class ParsedHTML:
    title: str | None = None
    meta_description: str | None = None
    canonical_url: str | None = None
    language: str | None = None
    robots_meta: str | None = None
    h1_tags: list[str] = field(default_factory=list)
    h2_tags: list[str] = field(default_factory=list)
    h3_tags: list[str] = field(default_factory=list)
    images: list[ImageInfo] = field(default_factory=list)
    links: list[LinkInfo] = field(default_factory=list)


class HTMLParser:
    """
    Dedicated HTML parsing service.
    Separates extraction logic from crawler orchestration.
    """

    def __init__(self, html_content: str, base_url: str):
        self.base_url = base_url
        self.soup = BeautifulSoup(html_content, "html.parser")

    def parse(self) -> ParsedHTML:
        """Execute full parsing and return structured data."""
        return ParsedHTML(
            title=self._extract_title(),
            meta_description=self._extract_meta_description(),
            canonical_url=self._extract_canonical(),
            language=self._extract_language(),
            robots_meta=self._extract_robots_meta(),
            h1_tags=self._extract_headings("h1"),
            h2_tags=self._extract_headings("h2"),
            h3_tags=self._extract_headings("h3"),
            images=self._extract_images(),
            links=self._extract_links(),
        )

    def _extract_title(self) -> str | None:
        title_tag = self.soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        return None

    def _extract_meta_description(self) -> str | None:
        meta = self.soup.find("meta", attrs={"name": lambda x: x and x.lower() == "description"})
        if meta and meta.get("content"):
            return meta["content"].strip()
        return None

    def _extract_canonical(self) -> str | None:
        link_tag = self.soup.find("link", rel="canonical")
        if link_tag and link_tag.get("href"):
            return link_tag["href"].strip()
        return None

    def _extract_language(self) -> str | None:
        html_tag = self.soup.find("html")
        if html_tag and html_tag.get("lang"):
            return html_tag["lang"].strip()
        return None

    def _extract_robots_meta(self) -> str | None:
        meta = self.soup.find("meta", attrs={"name": lambda x: x and x.lower() == "robots"})
        if meta and meta.get("content"):
            return meta["content"].strip()
        return None

    def _extract_headings(self, tag_name: str) -> list[str]:
        headings = self.soup.find_all(tag_name)
        return [h.get_text(separator=" ", strip=True) for h in headings]

    def _extract_images(self) -> list[ImageInfo]:
        images = []
        for img in self.soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue
            
            resolved_src = resolve_url(self.base_url, src)
            if not is_valid_url(resolved_src):
                continue
                
            alt = img.get("alt")
            # If alt is present but empty, it's "", if missing, it's None. We preserve that distinction.
            images.append(ImageInfo(src=resolved_src, alt=alt))
        return images

    def _extract_links(self) -> list[LinkInfo]:
        extracted = []
        for a_tag in self.soup.find_all("a", href=True):
            href = a_tag["href"]
            resolved_href = resolve_url(self.base_url, href)
            
            if not is_valid_url(resolved_href):
                continue

            text = a_tag.get_text(separator=" ", strip=True)
            rel = a_tag.get("rel", [])
            # rel can be a list if multiple values exist, e.g., rel="nofollow noopener"
            if isinstance(rel, str):
                rel = [rel]
            is_nofollow = any(r.lower() == "nofollow" for r in rel)

            extracted.append(
                LinkInfo(
                    href=resolved_href,
                    text=text,
                    is_nofollow=is_nofollow,
                )
            )
        return extracted
