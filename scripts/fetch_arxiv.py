#!/usr/bin/env python3
"""
arXiv paper metadata and abstract retrieval using the arXiv API.
Fetches detailed information for specific arXiv papers by ID.

API docs: https://info.arxiv.org/help/api/user-manual.html
"""

import sys
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any
import logging
import re
import time

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))
from utils.helpers import format_arxiv_citation
from utils.validators.parameter_validator import (
    validate_arxiv_id_param,
    validate_query_param,
    ValidationError,
)
from utils.cache_manager import get_cache, CacheManager
from utils.rate_limiter import throttle, report_success, report_error

logger = logging.getLogger(__name__)

# API Configuration
ARXIV_API_URL = "https://export.arxiv.org/api/query"

# Atom XML namespaces
NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
    'arxiv': 'http://arxiv.org/schemas/atom',
}


def fetch_arxiv_paper(
    arxiv_id: str,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Fetch metadata and abstract for a specific arXiv paper.

    Args:
        arxiv_id: arXiv paper ID (e.g., "2602.04557v1", "2602.04557",
                  or URL "https://arxiv.org/abs/2602.04557v1")
        use_cache: Whether to use cached data

    Returns:
        Dict containing:
        - success: bool
        - arxiv_id: Normalized arXiv ID
        - title: Paper title
        - authors: List of author names
        - abstract: Full abstract text
        - published: Publication date
        - updated: Last update date
        - year: Publication year
        - categories: List of arXiv categories
        - primary_category: Primary category
        - doi: DOI if available
        - journal_ref: Journal reference if published
        - comment: Author comments
        - pdf_url: URL to PDF
        - html_url: URL to HTML version
        - error: Error info if failed

    Example:
        >>> result = fetch_arxiv_paper("2602.04557v1")
        >>> print(result['title'])
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
    cache_key = f"arxiv_metadata:{arxiv_id}"
    if use_cache:
        cached = get_cache().get(cache_key)
        if cached:
            logger.info(f"Cache hit for arXiv paper: {arxiv_id}")
            return cached

    # Fetch via API using id_list
    params = {
        "id_list": arxiv_id,
        "max_results": 1,
    }

    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"

    try:
        throttle()
        time.sleep(0.5)  # Extra safety for arXiv rate limit

        req = urllib.request.Request(url, headers={
            'User-Agent': 'pubmed-reader-cskill/1.3.0 (literature search tool)'
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            xml_data = response.read().decode('utf-8')
        report_success()
    except urllib.error.URLError as e:
        report_error()
        return {
            "success": False,
            "arxiv_id": arxiv_id,
            "error": {
                "code": "NETWORK_ERROR",
                "message": f"Failed to connect to arXiv API: {e}",
                "suggestion": "Check network connection and try again"
            }
        }

    # Parse XML
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        return {
            "success": False,
            "arxiv_id": arxiv_id,
            "error": {
                "code": "PARSE_ERROR",
                "message": f"Failed to parse arXiv response: {e}"
            }
        }

    # Find entry
    entries = root.findall('atom:entry', NS)
    if not entries:
        return {
            "success": False,
            "arxiv_id": arxiv_id,
            "error": {
                "code": "NOT_FOUND",
                "message": f"arXiv paper not found: {arxiv_id}",
                "suggestion": "Check the arXiv ID and try again"
            }
        }

    entry = entries[0]

    # Check for error entries
    id_elem = entry.find('atom:id', NS)
    if id_elem is not None and 'api/errors' in (id_elem.text or ''):
        summary = entry.find('atom:summary', NS)
        error_msg = summary.text.strip() if summary is not None else "Unknown error"
        return {
            "success": False,
            "arxiv_id": arxiv_id,
            "error": {
                "code": "API_ERROR",
                "message": f"arXiv API error: {error_msg}"
            }
        }

    # Parse the entry
    article = _parse_entry_detail(entry)
    article["success"] = True

    # Cache result
    if use_cache:
        get_cache().set(cache_key, article, ttl=CacheManager.TTL_METADATA)

    return article


def _parse_entry_detail(entry: ET.Element) -> Dict[str, Any]:
    """
    Parse detailed information from an Atom entry.

    Args:
        entry: XML Element for one entry

    Returns:
        Detailed article metadata dict
    """
    # ID
    id_elem = entry.find('atom:id', NS)
    raw_id = id_elem.text.strip() if id_elem is not None else ""
    arxiv_id = raw_id.split('/abs/')[-1] if '/abs/' in raw_id else raw_id

    # Title
    title_elem = entry.find('atom:title', NS)
    title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else "Untitled"
    title = re.sub(r'\s+', ' ', title)

    # Authors with affiliations
    authors = []
    authors_detail = []
    for author_elem in entry.findall('atom:author', NS):
        name_elem = author_elem.find('atom:name', NS)
        if name_elem is not None:
            name = name_elem.text.strip()
            authors.append(name)

            # Check for affiliation
            affil_elem = author_elem.find('arxiv:affiliation', NS)
            affiliation = affil_elem.text.strip() if affil_elem is not None else None
            authors_detail.append({
                "name": name,
                "affiliation": affiliation
            })

    # Abstract
    summary_elem = entry.find('atom:summary', NS)
    abstract = ""
    if summary_elem is not None:
        abstract = summary_elem.text.strip().replace('\n', ' ')
        abstract = re.sub(r'\s+', ' ', abstract)

    # Dates
    published_elem = entry.find('atom:published', NS)
    published = published_elem.text.strip() if published_elem is not None else ""

    updated_elem = entry.find('atom:updated', NS)
    updated = updated_elem.text.strip() if updated_elem is not None else ""

    # Year
    year = None
    if published:
        year_match = re.search(r'(\d{4})', published)
        if year_match:
            year = int(year_match.group(1))

    # Categories
    categories = []
    for cat_elem in entry.findall('atom:category', NS):
        term = cat_elem.get('term', '')
        if term:
            categories.append(term)

    primary_cat_elem = entry.find('arxiv:primary_category', NS)
    primary_category = primary_cat_elem.get('term', '') if primary_cat_elem is not None else (categories[0] if categories else "")

    # DOI
    doi_elem = entry.find('arxiv:doi', NS)
    doi = doi_elem.text.strip() if doi_elem is not None else None

    # Journal reference
    journal_ref_elem = entry.find('arxiv:journal_ref', NS)
    journal_ref = journal_ref_elem.text.strip() if journal_ref_elem is not None else None

    # Comment
    comment_elem = entry.find('arxiv:comment', NS)
    comment = comment_elem.text.strip() if comment_elem is not None else None

    # Links
    pdf_link = f"https://arxiv.org/pdf/{arxiv_id}"
    html_link = f"https://arxiv.org/html/{arxiv_id}"
    for link_elem in entry.findall('atom:link', NS):
        link_title = link_elem.get('title', '')
        link_type = link_elem.get('type', '')
        href = link_elem.get('href', '')
        if link_title == 'pdf' or link_type == 'application/pdf':
            pdf_link = href

    return {
        "arxiv_id": arxiv_id,
        "title": title,
        "authors": authors,
        "authors_detail": authors_detail,
        "abstract": abstract,
        "published": published,
        "updated": updated,
        "year": year,
        "categories": categories,
        "primary_category": primary_category,
        "doi": doi,
        "journal_ref": journal_ref,
        "comment": comment,
        "pdf_url": pdf_link,
        "html_url": html_link,
        "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
        "source": "arxiv"
    }


def batch_fetch_arxiv(
    arxiv_ids: List[str],
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Fetch metadata for multiple arXiv papers.

    Args:
        arxiv_ids: List of arXiv IDs
        use_cache: Whether to use cached data

    Returns:
        Dict containing:
        - success: bool
        - articles: Dict mapping arxiv_id -> article data
        - stats: Fetch statistics
    """
    if not arxiv_ids:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "No arXiv IDs provided"
            }
        }

    # Validate IDs
    valid_ids = []
    for aid in arxiv_ids:
        try:
            valid_ids.append(validate_arxiv_id_param(aid))
        except ValidationError:
            logger.warning(f"Skipping invalid arXiv ID: {aid}")

    if not valid_ids:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "No valid arXiv IDs provided"
            }
        }

    articles = {}
    fetched = 0
    failed = 0

    # Check cache first
    ids_to_fetch = []
    for aid in valid_ids:
        if use_cache:
            cache_key = f"arxiv_metadata:{aid}"
            cached = get_cache().get(cache_key)
            if cached:
                articles[aid] = cached
                fetched += 1
                continue
        ids_to_fetch.append(aid)

    # Fetch remaining via API (batch using id_list)
    if ids_to_fetch:
        params = {
            "id_list": ",".join(ids_to_fetch),
            "max_results": len(ids_to_fetch),
        }

        url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"

        try:
            throttle()
            time.sleep(0.5)

            req = urllib.request.Request(url, headers={
                'User-Agent': 'pubmed-reader-cskill/1.3.0 (literature search tool)'
            })
            with urllib.request.urlopen(req, timeout=60) as response:
                xml_data = response.read().decode('utf-8')
            report_success()

            root = ET.fromstring(xml_data)
            entries = root.findall('atom:entry', NS)

            for entry in entries:
                article = _parse_entry_detail(entry)
                aid = article.get("arxiv_id", "")
                if aid:
                    article["success"] = True
                    articles[aid] = article
                    fetched += 1

                    if use_cache:
                        cache_key = f"arxiv_metadata:{aid}"
                        get_cache().set(cache_key, article, ttl=CacheManager.TTL_METADATA)

        except (urllib.error.URLError, ET.ParseError) as e:
            report_error()
            failed += len(ids_to_fetch)
            logger.error(f"Batch fetch failed: {e}")

    return {
        "success": fetched > 0,
        "articles": articles,
        "stats": {
            "requested": len(valid_ids),
            "fetched": fetched,
            "failed": failed
        }
    }


def format_arxiv_paper(article: Dict[str, Any], include_abstract: bool = True) -> str:
    """
    Format arXiv paper for display.

    Args:
        article: Paper metadata dict
        include_abstract: Whether to include abstract

    Returns:
        Formatted string for display
    """
    if not article.get("success"):
        error = article.get("error", {})
        return f"Error: {error.get('message', 'Unknown error')}"

    lines = []

    lines.append(f"## arXiv Paper: {article.get('arxiv_id', '')}")
    lines.append("")

    # Formatted reference
    citation = format_arxiv_citation(article, style="vancouver")
    lines.append(f"**Reference**: {citation}")
    lines.append("")

    if include_abstract and article.get("abstract"):
        lines.append("**Abstract**:")
        lines.append(article["abstract"])
        lines.append("")

    # Categories
    categories = article.get("categories", [])
    if categories:
        lines.append(f"**Categories**: {', '.join(categories)}")

    # Comment
    comment = article.get("comment")
    if comment:
        lines.append(f"**Comment**: {comment}")

    # Journal reference
    journal_ref = article.get("journal_ref")
    if journal_ref:
        lines.append(f"**Published in**: {journal_ref}")

    # Links
    lines.append("")
    lines.append(f"**PDF**: {article.get('pdf_url', '')}")
    lines.append(f"**HTML**: {article.get('html_url', '')}")

    return "\n".join(lines)


# =============================================================================
# Main (for testing)
# =============================================================================

def main():
    """Test arXiv paper fetching."""
    print("Testing arXiv Paper Fetch...\n")

    # Test fetching a specific paper
    print("1. Fetch specific paper (Attention Is All You Need):")
    result = fetch_arxiv_paper("1706.03762")

    if result.get("success"):
        print(f"   Title: {result['title'][:60]}...")
        print(f"   Authors: {', '.join(result['authors'][:3])}...")
        print(f"   Year: {result.get('year')}")
        print(f"   Categories: {result.get('categories', [])}")
    else:
        print(f"   Error: {result.get('error', {}).get('message')}")

    # Test with URL
    print("\n2. Fetch from URL:")
    result = fetch_arxiv_paper("https://arxiv.org/abs/1706.03762v7")

    if result.get("success"):
        print(f"   Title: {result['title'][:60]}...")
        print(f"   arXiv ID: {result['arxiv_id']}")

    # Test batch fetch
    print("\n3. Batch fetch:")
    ids = ["1706.03762", "2005.14165"]
    result = batch_fetch_arxiv(ids)

    if result.get("success"):
        stats = result.get("stats", {})
        print(f"   Requested: {stats.get('requested')}")
        print(f"   Fetched: {stats.get('fetched')}")

    # Test formatted output
    print("\n4. Formatted output:")
    result = fetch_arxiv_paper("1706.03762")
    if result.get("success"):
        formatted = format_arxiv_paper(result)
        print(formatted)

    # Test invalid ID
    print("\n5. Invalid ID handling:")
    result = fetch_arxiv_paper("invalid_id")
    print(f"   Error: {result.get('error', {}).get('message')}")

    print("\nAll arXiv fetch tests completed!")


if __name__ == "__main__":
    main()
