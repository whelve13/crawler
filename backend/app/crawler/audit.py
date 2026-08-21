from dataclasses import dataclass

from app.crawler.parser import ParsedHTML
from app.crawler.url import get_domain, is_valid_url


@dataclass
class SEOIssue:
    rule_id: str
    severity: str  # "error", "warning", "info"
    message: str
    element: str | None = None


class SEORule:
    """Base class for all SEO rules."""

    @property
    def rule_id(self) -> str:
        raise NotImplementedError

    def evaluate(self, page_url: str, parsed: ParsedHTML) -> list[SEOIssue]:
        raise NotImplementedError


class TitleRule(SEORule):
    @property
    def rule_id(self) -> str:
        return "title"

    def evaluate(self, page_url: str, parsed: ParsedHTML) -> list[SEOIssue]:
        issues = []
        if parsed.title is None:
            issues.append(SEOIssue(self.rule_id, "error", "Missing title tag"))
        else:
            title = parsed.title.strip()
            if not title:
                issues.append(SEOIssue(self.rule_id, "error", "Empty title tag"))
            elif len(title) > 60:
                issues.append(
                    SEOIssue(
                        self.rule_id,
                        "warning",
                        f"Title is excessively long ({len(title)} chars > 60)",
                    )
                )
        return issues


class MetaDescriptionRule(SEORule):
    @property
    def rule_id(self) -> str:
        return "meta_description"

    def evaluate(self, page_url: str, parsed: ParsedHTML) -> list[SEOIssue]:
        issues = []
        if parsed.meta_description is None:
            issues.append(SEOIssue(self.rule_id, "error", "Missing meta description"))
        else:
            desc = parsed.meta_description.strip()
            if not desc:
                issues.append(SEOIssue(self.rule_id, "error", "Empty meta description"))
            elif len(desc) > 160:
                issues.append(
                    SEOIssue(
                        self.rule_id,
                        "warning",
                        f"Meta description is excessively long ({len(desc)} chars > 160)",
                    )
                )
        return issues


class H1Rule(SEORule):
    @property
    def rule_id(self) -> str:
        return "h1"

    def evaluate(self, page_url: str, parsed: ParsedHTML) -> list[SEOIssue]:
        issues = []
        count = len(parsed.h1_tags)
        if count == 0:
            issues.append(SEOIssue(self.rule_id, "error", "Missing H1 element"))
        elif count > 1:
            issues.append(
                SEOIssue(self.rule_id, "warning", f"Multiple H1 elements found ({count})")
            )
        return issues


class ImageAltRule(SEORule):
    @property
    def rule_id(self) -> str:
        return "image_alt"

    def evaluate(self, page_url: str, parsed: ParsedHTML) -> list[SEOIssue]:
        issues = []
        for img in parsed.images:
            if img.alt is None:
                issues.append(
                    SEOIssue(
                        self.rule_id,
                        "error",
                        "Image missing alt attribute",
                        element=img.src,
                    )
                )
            elif not img.alt.strip():
                issues.append(
                    SEOIssue(
                        self.rule_id,
                        "warning",
                        "Image has empty alt attribute (verify if decorative)",
                        element=img.src,
                    )
                )
        return issues


class CanonicalRule(SEORule):
    @property
    def rule_id(self) -> str:
        return "canonical"

    def evaluate(self, page_url: str, parsed: ParsedHTML) -> list[SEOIssue]:
        issues = []
        if parsed.canonical_url is None:
            issues.append(SEOIssue(self.rule_id, "warning", "Missing canonical URL"))
        else:
            canonical = parsed.canonical_url.strip()
            if not canonical or not is_valid_url(canonical):
                issues.append(
                    SEOIssue(self.rule_id, "error", f"Malformed canonical URL: {canonical}")
                )
            else:
                page_domain = get_domain(page_url)
                canonical_domain = get_domain(canonical)
                if page_domain != canonical_domain:
                    issues.append(
                        SEOIssue(
                            self.rule_id,
                            "warning",
                            f"Canonical URL points outside expected domain ({canonical_domain})",
                        )
                    )
        return issues


class SEOAuditEngine:
    """
    Engine to run a suite of SEO rules against parsed HTML content.
    """

    def __init__(self):
        self.rules: list[SEORule] = [
            TitleRule(),
            MetaDescriptionRule(),
            H1Rule(),
            ImageAltRule(),
            CanonicalRule(),
        ]

    def add_rule(self, rule: SEORule):
        self.rules.append(rule)

    def run_audit(self, page_url: str, parsed: ParsedHTML) -> list[SEOIssue]:
        all_issues = []
        for rule in self.rules:
            all_issues.extend(rule.evaluate(page_url, parsed))
        return all_issues
