#!/usr/bin/env python3
"""
bioRxiv/medRxiv full text retrieval.
Fetches and parses full text from JATS XML or HTML versions of preprints.

JATS XML is available via the jatsxml field in the API response.
HTML full text is available at biorxiv.org/content/[DOI].full
"""

import sys
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
import re
from typing import Optional, Dict, Any, List
import logging
import time

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))
from utils.validators.parameter_validator import (
    validate_biorxiv_doi_param,
    ValidationError,
)
from utils.cache_manager import get_cache, CacheManager
from utils.rate_limiter import throttle, report_success, report_error
from fetch_biorxiv import fetch_biorxiv_paper

logger = logging.getLogger(__name__)

# User agent for requests
USER_AGENT = 'pubmed-reader-cskill/1.4.0 (literature search tool)'


def check_fulltext_availability(
    doi: str,
    server: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check if full text is available for a bioRxiv/medRxiv preprint.

    Args:
        doi: Paper DOI
        server: Optional server hint ("biorxiv" or "medrxiv")

    Returns:
        Dict with availability info:
        - available: bool
        - jatsxml_url: URL to JATS XML if available
        - html_url: URL to HTML full text
        - pdf_url: Always available PDF URL
    """
    try:
        doi = validate_biorxiv_doi_param(doi)
    except ValidationError as e:
        return {"available": False, "error": e.message}

    # Fetch paper metadata to get JATS XML URL
    result = fetch_biorxiv_paper(doi, server=server)

    if not result.get("success"):
        return {
            "available": False,
            "doi": doi,
            "error": result.get("error", {}).get("message", "Paper not found")
        }

    jatsxml_url = result.get("jatsxml", "")
    srv = result.get("server", "biorxiv")

    return {
        "available": True,
        "doi": doi,
        "jatsxml_url": jatsxml_url if jatsxml_url else None,
        "html_url": f"https://www.{srv}.org/content/{doi}.full",
        "pdf_url": f"https://www.{srv}.org/content/{doi}.full.pdf",
        "server": srv,
        "message": "Full text available via JATS XML and HTML"
    }


def get_biorxiv_fulltext(
    doi: str,
    server: Optional[str] = None,
    use_cache: bool = True,
    prefer_jats: bool = True
) -> Dict[str, Any]:
    """
    Retrieve full text of a bioRxiv/medRxiv preprint.

    Args:
        doi: Paper DOI (e.g., "10.1101/2024.01.15.575889")
        server: Optional server hint ("biorxiv" or "medrxiv")
        use_cache: Whether to use cached data
        prefer_jats: If True, try JATS XML first, then HTML

    Returns:
        Dict containing:
        - success: bool
        - doi: Paper DOI
        - title: Paper title
        - sections: Dict of section name -> text
        - full_text: Complete text
        - figures: List of figure references
        - references: List of bibliography entries
        - word_count: Total word count
        - error: Error info if failed

    Example:
        >>> result = get_biorxiv_fulltext("10.1101/2024.01.15.575889")
        >>> if result['success']:
        ...     print(result['sections']['Introduction'])
    """
    # Validate
    try:
        doi = validate_biorxiv_doi_param(doi)
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
    cache_key = f"biorxiv_fulltext:{doi}"
    if use_cache:
        cached = get_cache().get(cache_key)
        if cached:
            logger.info(f"Cache hit for bioRxiv full text: {doi}")
            return cached

    # Get paper metadata first
    paper = fetch_biorxiv_paper(doi, server=server, use_cache=use_cache)
    if not paper.get("success"):
        return paper

    srv = paper.get("server", "biorxiv")
    jatsxml_url = paper.get("jatsxml", "")
    title = paper.get("title", "Untitled")

    result = None

    # Try JATS XML first if preferred and available
    if prefer_jats and jatsxml_url:
        result = _fetch_and_parse_jats(jatsxml_url, doi, title, srv)

    # Fall back to HTML if JATS failed or not preferred
    if not result or not result.get("success"):
        html_url = f"https://www.{srv}.org/content/{doi}.full"
        result = _fetch_and_parse_html(html_url, doi, title, srv)

    # Cache result
    if use_cache and result.get("success"):
        get_cache().set(cache_key, result, ttl=CacheManager.TTL_FULLTEXT)

    return result


def _fetch_and_parse_jats(url: str, doi: str, title: str, server: str) -> Dict[str, Any]:
    """
    Fetch and parse JATS XML full text.

    Args:
        url: URL to JATS XML
        doi: Paper DOI
        title: Paper title
        server: Server name

    Returns:
        Parsed full text dict
    """
    try:
        throttle()
        time.sleep(0.3)

        req = urllib.request.Request(url, headers={
            'User-Agent': USER_AGENT,
            'Accept': 'application/xml',
        })
        with urllib.request.urlopen(req, timeout=60) as response:
            xml_data = response.read().decode('utf-8')
        report_success()
    except urllib.error.HTTPError as e:
        report_error()
        return {
            "success": False,
            "doi": doi,
            "error": {
                "code": "HTTP_ERROR",
                "message": f"HTTP error {e.code} fetching JATS XML"
            }
        }
    except urllib.error.URLError as e:
        report_error()
        return {
            "success": False,
            "doi": doi,
            "error": {
                "code": "NETWORK_ERROR",
                "message": f"Failed to fetch JATS XML: {e}",
                "suggestion": "Check network connection and try again"
            }
        }

    return _parse_jats_xml(xml_data, doi, title, server)


def _parse_jats_xml(xml_data: str, doi: str, title: str, server: str) -> Dict[str, Any]:
    """
    Parse JATS XML structure.

    JATS (Journal Article Tag Suite) is a standard XML format for scientific articles.

    Args:
        xml_data: Raw XML content
        doi: Paper DOI
        title: Paper title
        server: Server name

    Returns:
        Parsed full text dict
    """
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        return {
            "success": False,
            "doi": doi,
            "error": {
                "code": "PARSE_ERROR",
                "message": f"Failed to parse JATS XML: {e}"
            }
        }

    # JATS namespace handling
    # bioRxiv JATS may or may not use namespaces
    ns = {}

    # Try to find namespace from root
    if root.tag.startswith('{'):
        ns_end = root.tag.find('}')
        ns['jats'] = root.tag[1:ns_end]

    def find_with_ns(elem, path):
        """Find element with or without namespace."""
        result = elem.find(path)
        if result is None and ns.get('jats'):
            ns_path = path.replace('/', '/{' + ns['jats'] + '}')
            if not ns_path.startswith('{'):
                ns_path = '{' + ns['jats'] + '}' + ns_path
            result = elem.find(ns_path)
        return result

    def findall_with_ns(elem, path):
        """Find all elements with or without namespace."""
        results = elem.findall(path)
        if not results and ns.get('jats'):
            ns_path = './/' + '{' + ns['jats'] + '}' + path.split('/')[-1]
            results = elem.findall(ns_path)
        return results

    # Extract title from XML if not provided
    if title == "Untitled":
        title_elem = find_with_ns(root, './/article-title')
        if title_elem is not None:
            title = _get_element_text(title_elem)

    # Extract abstract
    abstract = ""
    abstract_elem = find_with_ns(root, './/abstract')
    if abstract_elem is not None:
        abstract = _get_element_text(abstract_elem)

    # Extract body sections
    sections = {}
    if abstract:
        sections["Abstract"] = abstract

    body = find_with_ns(root, './/body')
    if body is not None:
        for sec in body.findall('.//sec') if not ns.get('jats') else body.findall('.//{' + ns['jats'] + '}sec'):
            # Get section title
            sec_title_elem = sec.find('title') if not ns.get('jats') else sec.find('{' + ns['jats'] + '}title')
            if sec_title_elem is not None:
                sec_title = _get_element_text(sec_title_elem).strip()
                # Get section content
                sec_content = _get_section_text(sec)
                if sec_title and sec_content:
                    sections[sec_title] = sec_content

    # Extract figures
    figures = []
    for fig in findall_with_ns(root, './/fig'):
        fig_id = fig.get('id', '')
        caption_elem = fig.find('.//caption') if not ns.get('jats') else fig.find('.//{' + ns['jats'] + '}caption')
        caption = _get_element_text(caption_elem) if caption_elem is not None else ""
        figures.append({
            "id": fig_id,
            "caption": caption[:500]
        })

    # Extract references
    references = []
    ref_list = find_with_ns(root, './/ref-list')
    if ref_list is not None:
        for ref in ref_list.findall('.//ref') if not ns.get('jats') else ref_list.findall('.//{' + ns['jats'] + '}ref'):
            ref_text = _get_element_text(ref)
            if ref_text and len(ref_text) > 10:
                references.append(ref_text)

    # Build full text
    full_text_parts = []
    for sec_name, content in sections.items():
        if sec_name.lower() != "references":
            full_text_parts.append(content)
    full_text = "\n\n".join(full_text_parts)

    word_count = len(full_text.split()) if full_text else 0

    if word_count < 50 and not sections:
        return {
            "success": False,
            "doi": doi,
            "error": {
                "code": "PARSE_ERROR",
                "message": "Could not extract meaningful content from JATS XML",
                "suggestion": f"Try the HTML version or PDF at https://www.{server}.org/content/{doi}.full.pdf"
            }
        }

    return {
        "success": True,
        "doi": doi,
        "title": title,
        "sections": sections,
        "full_text": full_text,
        "figures": figures,
        "references": references,
        "word_count": word_count,
        "html_url": f"https://www.{server}.org/content/{doi}.full",
        "pdf_url": f"https://www.{server}.org/content/{doi}.full.pdf",
        "source": server,
        "format": "jats"
    }


def _fetch_and_parse_html(url: str, doi: str, title: str, server: str) -> Dict[str, Any]:
    """
    Fetch and parse HTML full text.

    Args:
        url: URL to HTML full text
        doi: Paper DOI
        title: Paper title
        server: Server name

    Returns:
        Parsed full text dict
    """
    try:
        throttle()
        time.sleep(0.3)

        req = urllib.request.Request(url, headers={
            'User-Agent': USER_AGENT,
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
                "doi": doi,
                "error": {
                    "code": "NOT_AVAILABLE",
                    "message": f"HTML full text not available for {doi}",
                    "suggestion": f"Try the PDF at https://www.{server}.org/content/{doi}.full.pdf"
                }
            }
        return {
            "success": False,
            "doi": doi,
            "error": {
                "code": "HTTP_ERROR",
                "message": f"HTTP error {e.code} fetching HTML"
            }
        }
    except urllib.error.URLError as e:
        report_error()
        return {
            "success": False,
            "doi": doi,
            "error": {
                "code": "NETWORK_ERROR",
                "message": f"Failed to fetch HTML: {e}",
                "suggestion": "Check network connection and try again"
            }
        }

    return _parse_html_fulltext(html_data, doi, title, server)


def _parse_html_fulltext(html: str, doi: str, title: str, server: str) -> Dict[str, Any]:
    """
    Parse bioRxiv/medRxiv HTML page to extract structured content.

    Args:
        html: Raw HTML content
        doi: Paper DOI
        title: Paper title
        server: Server name

    Returns:
        Parsed full text dict
    """
    # Remove script and style tags
    html_clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html_clean = re.sub(r'<style[^>]*>.*?</style>', '', html_clean, flags=re.DOTALL | re.IGNORECASE)

    # Extract title if not provided
    if title == "Untitled":
        title = _extract_html_title(html_clean)

    # Extract abstract
    abstract = _extract_html_abstract(html_clean)

    # Extract sections
    sections = _extract_html_sections(html_clean)

    # Add abstract as first section if found
    if abstract:
        sections = {"Abstract": abstract, **sections}

    # Extract figures
    figures = _extract_html_figures(html_clean)

    # Extract references
    references = _extract_html_references(html_clean)

    # Build full text
    full_text_parts = []
    for section_name, content in sections.items():
        if section_name.lower() != "references":
            full_text_parts.append(content)
    full_text = "\n\n".join(full_text_parts)

    word_count = len(full_text.split()) if full_text else 0

    if word_count < 50 and not sections:
        return {
            "success": False,
            "doi": doi,
            "error": {
                "code": "PARSE_ERROR",
                "message": "Could not extract meaningful content from HTML",
                "suggestion": f"Try the PDF at https://www.{server}.org/content/{doi}.full.pdf"
            }
        }

    return {
        "success": True,
        "doi": doi,
        "title": title,
        "sections": sections,
        "full_text": full_text,
        "figures": figures,
        "references": references,
        "word_count": word_count,
        "html_url": f"https://www.{server}.org/content/{doi}.full",
        "pdf_url": f"https://www.{server}.org/content/{doi}.full.pdf",
        "source": server,
        "format": "html"
    }


def _get_element_text(elem) -> str:
    """Get all text from an XML element and its children."""
    if elem is None:
        return ""
    text_parts = []
    if elem.text:
        text_parts.append(elem.text)
    for child in elem:
        text_parts.append(_get_element_text(child))
        if child.tail:
            text_parts.append(child.tail)
    return ' '.join(text_parts).strip()


def _get_section_text(sec_elem) -> str:
    """Get text content from a JATS section, excluding nested sections."""
    text_parts = []

    for child in sec_elem:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

        # Skip nested sections and title
        if tag in ('sec', 'title'):
            continue

        # Include paragraphs and other content
        if tag == 'p':
            text_parts.append(_get_element_text(child))
        else:
            text_parts.append(_get_element_text(child))

    return ' '.join(text_parts).strip()


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


def _extract_html_title(html: str) -> str:
    """Extract paper title from HTML."""
    # Try highwire title class (bioRxiv uses Highwire Press)
    match = re.search(r'<h1[^>]*class="[^"]*highwire-cite-title[^"]*"[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
    if match:
        return _strip_tags(match.group(1))

    # Try standard title tag
    match = re.search(r'<title>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
    if match:
        title = _strip_tags(match.group(1))
        # Remove site suffix
        title = re.sub(r'\s*[\|\-]\s*(bioRxiv|medRxiv).*$', '', title, flags=re.IGNORECASE)
        return title

    return "Untitled"


def _extract_html_abstract(html: str) -> str:
    """Extract abstract from HTML."""
    # bioRxiv abstract pattern
    match = re.search(
        r'<div[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</div>',
        html, re.DOTALL | re.IGNORECASE
    )
    if match:
        content = match.group(1)
        # Remove heading
        content = re.sub(r'<h\d[^>]*>.*?Abstract.*?</h\d>', '', content, flags=re.DOTALL | re.IGNORECASE)
        return _strip_tags(content)

    # Try section with id="abstract"
    match = re.search(
        r'<section[^>]*id="abstract"[^>]*>(.*?)</section>',
        html, re.DOTALL | re.IGNORECASE
    )
    if match:
        content = match.group(1)
        content = re.sub(r'<h\d[^>]*>.*?</h\d>', '', content, flags=re.DOTALL)
        return _strip_tags(content)

    return ""


def _extract_html_sections(html: str) -> Dict[str, str]:
    """Extract named sections from HTML."""
    sections = {}

    # Try to find main content area
    main_content = html

    # bioRxiv uses specific section classes
    section_pattern = re.compile(
        r'<div[^>]*class="[^"]*section[^"]*"[^>]*>'
        r'.*?<h\d[^>]*>(.*?)</h\d>'
        r'(.*?)</div>',
        re.DOTALL | re.IGNORECASE
    )

    for match in section_pattern.finditer(main_content):
        heading = _strip_tags(match.group(1))
        content = _strip_tags(match.group(2))

        # Clean up heading
        heading = re.sub(r'^\d+\.?\s*', '', heading).strip()

        if heading and content and len(content) > 20:
            sections[heading] = content

    if sections:
        return sections

    # Fallback: split by h2/h3 headings
    heading_pattern = re.compile(r'<h[23][^>]*>(.*?)</h[23]>', re.DOTALL | re.IGNORECASE)
    headings = list(heading_pattern.finditer(main_content))

    for i, heading_match in enumerate(headings):
        heading = _strip_tags(heading_match.group(1))
        heading = re.sub(r'^\d+\.?\s*', '', heading).strip()

        # Get content between this heading and next
        start = heading_match.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(main_content)
        content = main_content[start:end]

        # Trim at structural elements
        for stop_tag in ['<footer', '<nav', '</article', '</main', '<div class="ref-list']:
            stop_idx = content.lower().find(stop_tag)
            if stop_idx > 0:
                content = content[:stop_idx]

        content = _strip_tags(content)

        if heading and content and len(content) > 20:
            sections[heading] = content

    return sections


def _extract_html_figures(html: str) -> List[Dict[str, str]]:
    """Extract figure references from HTML."""
    figures = []

    # bioRxiv figure pattern
    fig_pattern = re.compile(
        r'<div[^>]*class="[^"]*fig[^"]*"[^>]*id="([^"]*)"[^>]*>.*?'
        r'(?:<div[^>]*class="[^"]*caption[^"]*"[^>]*>(.*?)</div>)?',
        re.DOTALL | re.IGNORECASE
    )

    for match in fig_pattern.finditer(html):
        fig_id = match.group(1)
        caption = _strip_tags(match.group(2)) if match.group(2) else ""
        figures.append({
            "id": fig_id,
            "caption": caption[:500]
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
            "caption": caption[:500]
        })

    return figures


def _extract_html_references(html: str) -> List[str]:
    """Extract bibliography entries from HTML."""
    references = []

    # bioRxiv reference list pattern
    ref_pattern = re.compile(
        r'<li[^>]*class="[^"]*ref-content[^"]*"[^>]*>(.*?)</li>',
        re.DOTALL | re.IGNORECASE
    )

    for match in ref_pattern.finditer(html):
        ref_text = _strip_tags(match.group(1))
        ref_text = re.sub(r'^\s*\d+\.?\s*', '', ref_text)
        if ref_text and len(ref_text) > 10:
            references.append(ref_text)

    if references:
        return references

    # Try alternate pattern
    ref_section = re.search(
        r'(?:References|Bibliography|REFERENCES).*?(<ol[^>]*>.*?</ol>|<ul[^>]*>.*?</ul>)',
        html, re.DOTALL | re.IGNORECASE
    )
    if ref_section:
        li_pattern = re.compile(r'<li[^>]*>(.*?)</li>', re.DOTALL | re.IGNORECASE)
        for match in li_pattern.finditer(ref_section.group(1)):
            ref_text = _strip_tags(match.group(1))
            ref_text = re.sub(r'^\s*\d+\.?\s*', '', ref_text)
            if ref_text and len(ref_text) > 10:
                references.append(ref_text)

    return references


def format_biorxiv_fulltext(result: Dict[str, Any], max_words: Optional[int] = None) -> str:
    """
    Format bioRxiv full text for display.

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
    doi = result.get("doi", "")
    title = result.get("title", "Untitled")
    server = result.get("source", "biorxiv")

    lines.append(f"## Full Text: {server}:{doi}")
    lines.append("")
    lines.append(f"**Title**: {title}")
    lines.append(f"**Word Count**: {result.get('word_count', 0):,} words")
    lines.append(f"**Format**: {result.get('format', 'unknown').upper()}")
    lines.append("")

    # Display sections in standard order
    section_order = [
        "Abstract", "Introduction", "Background",
        "Methods", "Materials and Methods", "Experimental",
        "Results", "Findings",
        "Discussion", "Conclusion", "Conclusions",
    ]

    sections = result.get("sections", {})
    displayed = set()

    for section_name in section_order:
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

    # References
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
    """Test bioRxiv full text retrieval."""
    print("Testing bioRxiv Full Text Retrieval...\n")

    # Test availability check
    print("1. Check full text availability:")
    test_dois = ["10.1101/2020.05.22.111161", "10.1101/2020.01.30.927871"]

    for doi in test_dois:
        result = check_fulltext_availability(doi)
        status = "available" if result.get("available") else "not available"
        print(f"   {doi}: {status}")
        if result.get("jatsxml_url"):
            print(f"      JATS: Yes")

    # Test full text retrieval
    print("\n2. Fetch full text:")
    result = get_biorxiv_fulltext("10.1101/2020.05.22.111161")

    if result.get("success"):
        print(f"   Title: {result.get('title', '')[:60]}...")
        print(f"   Word count: {result.get('word_count', 0)}")
        print(f"   Sections: {list(result.get('sections', {}).keys())[:5]}")
        print(f"   Figures: {len(result.get('figures', []))}")
        print(f"   References: {len(result.get('references', []))}")
        print(f"   Format: {result.get('format', 'unknown')}")
    else:
        print(f"   Error: {result.get('error', {}).get('message')}")

    # Test formatted output
    print("\n3. Formatted output (truncated):")
    if result.get("success"):
        formatted = format_biorxiv_fulltext(result, max_words=50)
        for line in formatted.split('\n')[:30]:
            print(line)
        print("...")

    # Test unavailable paper
    print("\n4. Invalid DOI handling:")
    result = get_biorxiv_fulltext("10.1101/invalid.doi.12345")
    print(f"   Error: {result.get('error', {}).get('message')}")

    print("\nAll bioRxiv full text tests completed!")


if __name__ == "__main__":
    main()
