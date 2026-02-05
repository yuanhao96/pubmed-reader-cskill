#!/usr/bin/env python3
"""
arXiv HTML full text retrieval.
Fetches and parses HTML versions of arXiv papers from arxiv.org/html/{id}.

Not all arXiv papers have HTML versions - only those processed by the
LaTeXML pipeline. Falls back to informing user about PDF availability.
"""

import sys
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error
import re
from typing import Optional, Dict, Any, List
import logging
import time

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))
from utils.validators.parameter_validator import (
    validate_arxiv_id_param,
    ValidationError,
)
from utils.cache_manager import get_cache, CacheManager
from utils.rate_limiter import throttle, report_success, report_error

logger = logging.getLogger(__name__)

# arXiv HTML base URL
ARXIV_HTML_URL = "https://arxiv.org/html"


def check_html_availability(arxiv_id: str) -> Dict[str, Any]:
    """
    Check if an arXiv paper has an HTML version.

    Args:
        arxiv_id: arXiv paper ID

    Returns:
        Dict with availability info:
        - available: bool
        - html_url: URL if available
        - pdf_url: Always available PDF URL
    """
    try:
        arxiv_id = validate_arxiv_id_param(arxiv_id)
    except ValidationError as e:
        return {"available": False, "error": e.message}

    html_url = f"{ARXIV_HTML_URL}/{arxiv_id}"

    try:
        throttle()
        time.sleep(0.3)

        req = urllib.request.Request(html_url, method='HEAD', headers={
            'User-Agent': 'pubmed-reader-cskill/1.3.0 (literature search tool)'
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            status = response.status
            report_success()
    except urllib.error.HTTPError as e:
        report_error()
        if e.code == 404:
            return {
                "available": False,
                "arxiv_id": arxiv_id,
                "html_url": None,
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
                "message": "HTML version not available. PDF is available."
            }
        return {
            "available": False,
            "arxiv_id": arxiv_id,
            "error": f"HTTP error {e.code}"
        }
    except urllib.error.URLError as e:
        report_error()
        return {
            "available": False,
            "arxiv_id": arxiv_id,
            "error": f"Network error: {e}"
        }

    return {
        "available": True,
        "arxiv_id": arxiv_id,
        "html_url": html_url,
        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
        "message": "HTML full text available"
    }


def get_arxiv_fulltext(
    arxiv_id: str,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Retrieve full text of an arXiv paper from its HTML version.

    Args:
        arxiv_id: arXiv paper ID (e.g., "2602.04557v1")
        use_cache: Whether to use cached data

    Returns:
        Dict containing:
        - success: bool
        - arxiv_id: Paper ID
        - title: Paper title
        - sections: Dict of section name -> text
        - full_text: Complete text
        - figures: List of figure references
        - references: List of bibliography entries
        - word_count: Total word count
        - error: Error info if failed

    Example:
        >>> result = get_arxiv_fulltext("2602.04557v1")
        >>> if result['success']:
        ...     print(result['sections']['Introduction'])
    """
    # Validate
    try:
        arxiv_id = validate_arxiv_id_param(arxiv_id)
    except ValidationError as e:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": e.message,
                "suggestion": e.suggestion
            }
        }

    # Check cache
    cache_key = f"arxiv_fulltext:{arxiv_id}"
    if use_cache:
        cached = get_cache().get(cache_key)
        if cached:
            logger.info(f"Cache hit for arXiv full text: {arxiv_id}")
            return cached

    # Fetch HTML
    html_url = f"{ARXIV_HTML_URL}/{arxiv_id}"

    try:
        throttle()
        time.sleep(0.5)

        req = urllib.request.Request(html_url, headers={
            'User-Agent': 'pubmed-reader-cskill/1.3.0 (literature search tool)',
            'Accept': 'text/html',
        })
        with urllib.request.urlopen(req, timeout=60) as response:
            html_data = response.read().decode('utf-8')
        report_success()
    except urllib.error.HTTPError as e:
        report_error()
        if e.code == 404:
            return {
                "success": False,
                "arxiv_id": arxiv_id,
                "error": {
                    "code": "NOT_AVAILABLE",
                    "message": f"HTML full text not available for arXiv:{arxiv_id}",
                    "suggestion": f"Not all papers have HTML versions. Try the PDF at https://arxiv.org/pdf/{arxiv_id}"
                }
            }
        return {
            "success": False,
            "arxiv_id": arxiv_id,
            "error": {
                "code": "HTTP_ERROR",
                "message": f"HTTP error {e.code} fetching HTML"
            }
        }
    except urllib.error.URLError as e:
        report_error()
        return {
            "success": False,
            "arxiv_id": arxiv_id,
            "error": {
                "code": "NETWORK_ERROR",
                "message": f"Failed to fetch HTML: {e}",
                "suggestion": "Check network connection and try again"
            }
        }

    # Parse HTML (without external dependencies - use regex-based extraction)
    result = _parse_arxiv_html(html_data, arxiv_id)

    # Cache result
    if use_cache and result.get("success"):
        get_cache().set(cache_key, result, ttl=CacheManager.TTL_FULLTEXT)

    return result


def _parse_arxiv_html(html: str, arxiv_id: str) -> Dict[str, Any]:
    """
    Parse arXiv HTML page to extract structured content.

    Uses regex-based extraction to avoid external dependencies.
    arXiv HTML uses LaTeXML classes: ltx_section, ltx_abstract, ltx_para,
    ltx_figure, ltx_bibitem, etc.

    Args:
        html: Raw HTML content
        arxiv_id: Paper ID for reference

    Returns:
        Parsed full text dict
    """
    # Remove script and style tags
    html_clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html_clean = re.sub(r'<style[^>]*>.*?</style>', '', html_clean, flags=re.DOTALL | re.IGNORECASE)

    # Extract title
    title = _extract_title(html_clean)

    # Extract abstract
    abstract = _extract_abstract(html_clean)

    # Extract sections
    sections = _extract_sections(html_clean)

    # Add abstract as first section if found
    if abstract:
        sections = {"Abstract": abstract, **sections}

    # Extract figures
    figures = _extract_figures(html_clean)

    # Extract bibliography
    references = _extract_references(html_clean)

    # Build full text
    full_text_parts = []
    for section_name, content in sections.items():
        if section_name != "References":
            full_text_parts.append(content)
    full_text = "\n\n".join(full_text_parts)

    word_count = len(full_text.split()) if full_text else 0

    if word_count < 50 and not sections:
        return {
            "success": False,
            "arxiv_id": arxiv_id,
            "error": {
                "code": "PARSE_ERROR",
                "message": "Could not extract meaningful content from HTML",
                "suggestion": f"The HTML page may use non-standard formatting. Try the PDF at https://arxiv.org/pdf/{arxiv_id}"
            }
        }

    return {
        "success": True,
        "arxiv_id": arxiv_id,
        "title": title,
        "sections": sections,
        "full_text": full_text,
        "figures": figures,
        "references": references,
        "word_count": word_count,
        "html_url": f"{ARXIV_HTML_URL}/{arxiv_id}",
        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
        "source": "arxiv"
    }


def _strip_tags(html: str) -> str:
    """Remove HTML tags and clean whitespace."""
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&#\d+;', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _extract_title(html: str) -> str:
    """Extract paper title from HTML."""
    # Try LaTeXML title
    match = re.search(r'<h1[^>]*class="[^"]*ltx_title[^"]*"[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
    if match:
        return _strip_tags(match.group(1))

    # Try standard HTML title tag
    match = re.search(r'<title>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
    if match:
        title = _strip_tags(match.group(1))
        # Remove " - arXiv" suffix
        title = re.sub(r'\s*[-|]\s*arXiv.*$', '', title)
        return title

    return "Untitled"


def _extract_abstract(html: str) -> str:
    """Extract abstract from HTML."""
    # LaTeXML abstract
    match = re.search(
        r'<div[^>]*class="[^"]*ltx_abstract[^"]*"[^>]*>(.*?)</div>',
        html, re.DOTALL | re.IGNORECASE
    )
    if match:
        content = match.group(1)
        # Remove the "Abstract" heading if present
        content = re.sub(r'<h\d[^>]*>.*?Abstract.*?</h\d>', '', content, flags=re.DOTALL | re.IGNORECASE)
        return _strip_tags(content)

    # Standard abstract block
    match = re.search(
        r'<blockquote[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</blockquote>',
        html, re.DOTALL | re.IGNORECASE
    )
    if match:
        content = match.group(1)
        content = re.sub(r'<span[^>]*class="[^"]*descriptor[^"]*"[^>]*>.*?</span>', '', content, flags=re.DOTALL)
        return _strip_tags(content)

    return ""


def _extract_sections(html: str) -> Dict[str, str]:
    """
    Extract named sections from HTML.

    Looks for LaTeXML section structure (ltx_section) and standard h2/h3 headings.
    """
    sections = {}

    # Try LaTeXML sections
    section_pattern = re.compile(
        r'<section[^>]*class="[^"]*ltx_section[^"]*"[^>]*>'
        r'.*?<h\d[^>]*class="[^"]*ltx_title[^"]*"[^>]*>(.*?)</h\d>'
        r'(.*?)</section>',
        re.DOTALL | re.IGNORECASE
    )

    for match in section_pattern.finditer(html):
        heading = _strip_tags(match.group(1))
        content = _strip_tags(match.group(2))

        # Clean up section name
        heading = re.sub(r'^\d+\.?\s*', '', heading)  # Remove numbering
        heading = heading.strip()

        if heading and content and len(content) > 20:
            sections[heading] = content

    if sections:
        return sections

    # Fallback: try standard heading + content extraction
    # Split by h2 tags
    h2_pattern = re.compile(r'<h2[^>]*>(.*?)</h2>', re.DOTALL | re.IGNORECASE)
    headings = list(h2_pattern.finditer(html))

    for i, heading_match in enumerate(headings):
        heading = _strip_tags(heading_match.group(1))
        heading = re.sub(r'^\d+\.?\s*', '', heading).strip()

        # Get content between this heading and next heading
        start = heading_match.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(html)
        content = html[start:end]

        # Trim at next major structural element
        for stop_tag in ['<footer', '<nav', '</article', '</main']:
            stop_idx = content.find(stop_tag)
            if stop_idx > 0:
                content = content[:stop_idx]

        content = _strip_tags(content)

        if heading and content and len(content) > 20:
            sections[heading] = content

    return sections


def _extract_figures(html: str) -> List[Dict[str, str]]:
    """Extract figure references from HTML."""
    figures = []

    # LaTeXML figures
    fig_pattern = re.compile(
        r'<figure[^>]*class="[^"]*ltx_figure[^"]*"[^>]*id="([^"]*)"[^>]*>.*?'
        r'(?:<figcaption[^>]*>(.*?)</figcaption>)?.*?</figure>',
        re.DOTALL | re.IGNORECASE
    )

    for match in fig_pattern.finditer(html):
        fig_id = match.group(1)
        caption = _strip_tags(match.group(2)) if match.group(2) else ""
        figures.append({
            "id": fig_id,
            "caption": caption
        })

    if figures:
        return figures

    # Fallback: standard figure tags
    fig_pattern2 = re.compile(
        r'<figure[^>]*>.*?(?:<figcaption[^>]*>(.*?)</figcaption>)?.*?</figure>',
        re.DOTALL | re.IGNORECASE
    )

    for i, match in enumerate(fig_pattern2.finditer(html)):
        caption = _strip_tags(match.group(1)) if match.group(1) else ""
        figures.append({
            "id": f"fig{i+1}",
            "caption": caption
        })

    return figures


def _extract_references(html: str) -> List[str]:
    """Extract bibliography entries from HTML."""
    references = []

    # LaTeXML bibliography items
    bib_pattern = re.compile(
        r'<li[^>]*class="[^"]*ltx_bibitem[^"]*"[^>]*>(.*?)</li>',
        re.DOTALL | re.IGNORECASE
    )

    for match in bib_pattern.finditer(html):
        ref_text = _strip_tags(match.group(1))
        # Remove leading numbering like [1], [2], etc.
        ref_text = re.sub(r'^\s*\[\d+\]\s*', '', ref_text)
        if ref_text and len(ref_text) > 10:
            references.append(ref_text)

    if references:
        return references

    # Fallback: look for reference list
    ref_section = re.search(
        r'(?:References|Bibliography|REFERENCES).*?(<ol[^>]*>.*?</ol>|<ul[^>]*>.*?</ul>)',
        html, re.DOTALL | re.IGNORECASE
    )
    if ref_section:
        li_pattern = re.compile(r'<li[^>]*>(.*?)</li>', re.DOTALL | re.IGNORECASE)
        for match in li_pattern.finditer(ref_section.group(1)):
            ref_text = _strip_tags(match.group(1))
            ref_text = re.sub(r'^\s*\[\d+\]\s*', '', ref_text)
            if ref_text and len(ref_text) > 10:
                references.append(ref_text)

    return references


def format_arxiv_fulltext(result: Dict[str, Any], max_words: Optional[int] = None) -> str:
    """
    Format arXiv full text for display.

    Args:
        result: Full text result dict
        max_words: Optional word limit per section

    Returns:
        Formatted string for display
    """
    if not result.get("success"):
        error = result.get("error", {})
        return f"Error: {error.get('message', 'Unknown error')}"

    lines = []
    arxiv_id = result.get("arxiv_id", "")
    title = result.get("title", "Untitled")

    lines.append(f"## Full Text: arXiv:{arxiv_id}")
    lines.append("")
    lines.append(f"**Title**: {title}")
    lines.append(f"**Word Count**: {result.get('word_count', 0):,} words")
    lines.append("")

    # Display sections in standard order
    section_order = [
        "Abstract", "Introduction", "Related Work", "Background",
        "Methods", "Methodology", "Method", "Approach",
        "Experiments", "Results", "Evaluation",
        "Discussion", "Conclusion", "Conclusions",
    ]

    sections = result.get("sections", {})
    displayed = set()

    for section_name in section_order:
        # Case-insensitive match
        for actual_name, content in sections.items():
            if actual_name.lower() == section_name.lower() and actual_name not in displayed:
                if max_words:
                    words = content.split()
                    if len(words) > max_words:
                        content = " ".join(words[:max_words]) + "..."
                lines.append(f"### {actual_name}")
                lines.append("")
                lines.append(content)
                lines.append("")
                displayed.add(actual_name)
                break

    # Display remaining sections
    for section_name, content in sections.items():
        if section_name not in displayed:
            if max_words:
                words = content.split()
                if len(words) > max_words:
                    content = " ".join(words[:max_words]) + "..."
            lines.append(f"### {section_name}")
            lines.append("")
            lines.append(content)
            lines.append("")

    # Figures
    figures = result.get("figures", [])
    if figures:
        lines.append(f"### Figures ({len(figures)} total)")
        for fig in figures[:10]:
            caption = fig.get("caption", "")[:150]
            lines.append(f"- {fig.get('id', 'Fig')}: {caption}")
        lines.append("")

    # References count
    references = result.get("references", [])
    if references:
        lines.append(f"### References ({len(references)} total)")
        for ref in references[:5]:
            lines.append(f"- {ref[:150]}...")
        if len(references) > 5:
            lines.append(f"- ... and {len(references) - 5} more")
        lines.append("")

    return "\n".join(lines)


# =============================================================================
# Main (for testing)
# =============================================================================

def main():
    """Test arXiv full text retrieval."""
    print("Testing arXiv Full Text Retrieval...\n")

    # Test availability check
    print("1. Check HTML availability:")
    test_ids = ["1706.03762", "2602.04557v1"]

    for aid in test_ids:
        result = check_html_availability(aid)
        status = "available" if result.get("available") else "not available"
        print(f"   arXiv:{aid}: {status}")

    # Test full text retrieval
    print("\n2. Fetch full text:")
    result = get_arxiv_fulltext("1706.03762")

    if result.get("success"):
        print(f"   Title: {result.get('title', '')[:60]}...")
        print(f"   Word count: {result.get('word_count', 0)}")
        print(f"   Sections: {list(result.get('sections', {}).keys())}")
        print(f"   Figures: {len(result.get('figures', []))}")
        print(f"   References: {len(result.get('references', []))}")
    else:
        print(f"   Error: {result.get('error', {}).get('message')}")

    # Test formatted output
    print("\n3. Formatted output (truncated):")
    if result.get("success"):
        formatted = format_arxiv_fulltext(result, max_words=50)
        for line in formatted.split('\n')[:30]:
            print(line)
        print("...")

    # Test unavailable paper
    print("\n4. Unavailable paper handling:")
    result = get_arxiv_fulltext("9999.99999")
    print(f"   Error: {result.get('error', {}).get('message')}")

    print("\nAll arXiv full text tests completed!")


if __name__ == "__main__":
    main()
