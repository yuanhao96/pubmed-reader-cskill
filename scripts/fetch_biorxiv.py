#!/usr/bin/env python3
"""
bioRxiv/medRxiv paper metadata and abstract retrieval using the bioRxiv API.
Fetches detailed information for specific preprints by DOI.

API docs: https://api.biorxiv.org/
"""

import sys
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error
import json
import re
from typing import Optional, List, Dict, Any
import logging
import time

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))
from utils.helpers import format_biorxiv_citation
from utils.validators.parameter_validator import (
    validate_biorxiv_doi_param,
    ValidationError,
)
from utils.cache_manager import get_cache, CacheManager
from utils.rate_limiter import throttle, report_success, report_error

logger = logging.getLogger(__name__)

# API Configuration
BIORXIV_API_URL = "https://api.biorxiv.org"

# User agent for requests
USER_AGENT = 'pubmed-reader-cskill/1.4.0 (literature search tool)'


def fetch_biorxiv_paper(
    doi: str,
    server: Optional[str] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Fetch metadata and abstract for a specific bioRxiv/medRxiv preprint.

    Args:
        doi: bioRxiv/medRxiv DOI (e.g., "10.1101/2024.01.15.575889")
             or URL "https://www.biorxiv.org/content/10.1101/2024.01.15.575889"
        server: Optional server hint ("biorxiv" or "medrxiv"). Auto-detected if not provided.
        use_cache: Whether to use cached data

    Returns:
        Dict containing:
        - success: bool
        - doi: Normalized DOI
        - title: Paper title
        - authors: List of author names
        - abstract: Full abstract text
        - posted_date: Original posting date
        - year: Posting year
        - category: Subject category
        - version: Paper version
        - license: License type
        - published: Journal publication info if published
        - jatsxml: URL to JATS XML
        - url: URL to paper page
        - pdf_url: URL to PDF
        - error: Error info if failed

    Example:
        >>> result = fetch_biorxiv_paper("10.1101/2024.01.15.575889")
        >>> print(result['title'])
    """
    # Validate and extract DOI
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
    cache_key = f"biorxiv_metadata:{doi}"
    if use_cache:
        cached = get_cache().get(cache_key)
        if cached:
            logger.info(f"Cache hit for bioRxiv paper: {doi}")
            return cached

    # Try both servers if not specified
    servers_to_try = [server] if server else ["biorxiv", "medrxiv"]

    last_error = None
    for srv in servers_to_try:
        if srv is None:
            continue

        result = _fetch_from_server(doi, srv)
        if result.get("success"):
            # Cache result
            if use_cache:
                get_cache().set(cache_key, result, ttl=CacheManager.TTL_METADATA)
            return result
        else:
            last_error = result.get("error", {})
            # If it's a NOT_FOUND error, try next server
            if last_error.get("code") == "NOT_FOUND" and len(servers_to_try) > 1:
                continue
            break

    # Return error
    return {
        "success": False,
        "doi": doi,
        "error": last_error or {
            "code": "NOT_FOUND",
            "message": f"Paper not found: {doi}",
            "suggestion": "Check the DOI and try again"
        }
    }


def _fetch_from_server(doi: str, server: str) -> Dict[str, Any]:
    """
    Fetch paper from specific server.

    Args:
        doi: Paper DOI
        server: Server name ("biorxiv" or "medrxiv")

    Returns:
        Paper metadata dict
    """
    # API endpoint: /details/[server]/[DOI]/na/json
    url = f"{BIORXIV_API_URL}/details/{server}/{doi}/na/json"

    try:
        throttle()
        time.sleep(0.3)

        req = urllib.request.Request(url, headers={
            'User-Agent': USER_AGENT,
            'Accept': 'application/json',
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            json_data = response.read().decode('utf-8')
        report_success()

    except urllib.error.HTTPError as e:
        report_error()
        if e.code == 404:
            return {
                "success": False,
                "doi": doi,
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Paper not found on {server}: {doi}",
                    "suggestion": "Check the DOI or try the other server"
                }
            }
        return {
            "success": False,
            "doi": doi,
            "error": {
                "code": "HTTP_ERROR",
                "message": f"HTTP error {e.code} fetching paper"
            }
        }
    except urllib.error.URLError as e:
        report_error()
        return {
            "success": False,
            "doi": doi,
            "error": {
                "code": "NETWORK_ERROR",
                "message": f"Failed to connect to {server} API: {e}",
                "suggestion": "Check network connection and try again"
            }
        }

    # Parse JSON response
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "doi": doi,
            "error": {
                "code": "PARSE_ERROR",
                "message": f"Failed to parse {server} API response: {e}"
            }
        }

    # Check for empty collection
    collection = data.get('collection', [])
    if not collection:
        return {
            "success": False,
            "doi": doi,
            "error": {
                "code": "NOT_FOUND",
                "message": f"Paper not found on {server}: {doi}",
                "suggestion": "Check the DOI or try the other server"
            }
        }

    # Get the most recent version
    article_data = collection[-1]  # Last item is most recent version

    # Parse article details
    return _parse_article_detail(article_data, doi, server)


def _parse_article_detail(item: Dict[str, Any], doi: str, server: str) -> Dict[str, Any]:
    """
    Parse detailed information from API response.

    Args:
        item: Dict from API collection
        doi: Paper DOI
        server: Server name

    Returns:
        Detailed article metadata dict
    """
    # Parse date
    posted_date = item.get('date', '')
    year = None
    if posted_date:
        year_match = re.search(r'(\d{4})', posted_date)
        if year_match:
            year = int(year_match.group(1))

    # Parse authors
    authors_str = item.get('authors', '')
    authors = []
    authors_detail = []
    if authors_str:
        # Authors are semicolon-separated
        author_parts = authors_str.split(';')
        for part in author_parts:
            name = part.strip()
            if name:
                authors.append(name)
                authors_detail.append({"name": name})

    return {
        "success": True,
        "doi": item.get('doi', doi),
        "title": item.get('title', 'Untitled'),
        "authors": authors,
        "authors_detail": authors_detail,
        "abstract": item.get('abstract', ''),
        "posted_date": posted_date,
        "year": year,
        "category": item.get('category', ''),
        "version": item.get('version', '1'),
        "type": item.get('type', 'preprint'),
        "license": item.get('license', ''),
        "published": item.get('published', ''),
        "jatsxml": item.get('jatsxml', ''),
        "author_corresponding": item.get('author_corresponding', ''),
        "author_corresponding_institution": item.get('author_corresponding_institution', ''),
        "url": f"https://www.{server}.org/content/{item.get('doi', doi)}",
        "pdf_url": f"https://www.{server}.org/content/{item.get('doi', doi)}.full.pdf",
        "server": server,
        "source": server
    }


def batch_fetch_biorxiv(
    dois: List[str],
    server: Optional[str] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Fetch metadata for multiple bioRxiv/medRxiv papers.

    Args:
        dois: List of DOIs
        server: Optional server hint ("biorxiv" or "medrxiv")
        use_cache: Whether to use cached data

    Returns:
        Dict containing:
        - success: bool
        - articles: Dict mapping doi -> article data
        - stats: Fetch statistics
    """
    if not dois:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "No DOIs provided"
            }
        }

    # Validate DOIs
    valid_dois = []
    for d in dois:
        try:
            valid_dois.append(validate_biorxiv_doi_param(d))
        except ValidationError:
            logger.warning(f"Skipping invalid DOI: {d}")

    if not valid_dois:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "No valid DOIs provided"
            }
        }

    articles = {}
    fetched = 0
    failed = 0

    # Fetch each paper
    for d in valid_dois:
        result = fetch_biorxiv_paper(d, server=server, use_cache=use_cache)

        if result.get("success"):
            articles[d] = result
            fetched += 1
        else:
            failed += 1
            logger.warning(f"Failed to fetch {d}: {result.get('error', {}).get('message')}")

    return {
        "success": fetched > 0,
        "articles": articles,
        "stats": {
            "requested": len(valid_dois),
            "fetched": fetched,
            "failed": failed
        }
    }


def format_biorxiv_paper(article: Dict[str, Any], include_abstract: bool = True) -> str:
    """
    Format bioRxiv paper for display.

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
    server = article.get("server", "biorxiv")

    lines.append(f"## {server.title()} Preprint: {article.get('doi', '')}")
    lines.append("")

    # Formatted reference
    citation = format_biorxiv_citation(article, style="vancouver")
    lines.append(f"**Reference**: {citation}")
    lines.append("")

    if include_abstract and article.get("abstract"):
        lines.append("**Abstract**:")
        lines.append(article["abstract"])
        lines.append("")

    # Category
    category = article.get("category")
    if category:
        lines.append(f"**Category**: {category}")

    # Version
    version = article.get("version")
    if version:
        lines.append(f"**Version**: {version}")

    # Publication status
    published = article.get("published")
    if published:
        lines.append(f"**Published**: {published}")

    # License
    license_info = article.get("license")
    if license_info:
        lines.append(f"**License**: {license_info}")

    # Links
    lines.append("")
    lines.append(f"**PDF**: {article.get('pdf_url', '')}")
    lines.append(f"**Page**: {article.get('url', '')}")

    return "\n".join(lines)


# =============================================================================
# Main (for testing)
# =============================================================================

def main():
    """Test bioRxiv paper fetching."""
    print("Testing bioRxiv Paper Fetch...\n")

    # Test fetching a specific paper
    print("1. Fetch specific paper:")
    result = fetch_biorxiv_paper("10.1101/2020.05.22.111161")

    if result.get("success"):
        print(f"   Title: {result['title'][:60]}...")
        print(f"   Authors: {len(result['authors'])} authors")
        print(f"   Year: {result.get('year')}")
        print(f"   Category: {result.get('category', 'N/A')}")
        print(f"   Server: {result.get('server', 'N/A')}")
    else:
        print(f"   Error: {result.get('error', {}).get('message')}")

    # Test with URL
    print("\n2. Fetch from URL:")
    result = fetch_biorxiv_paper("https://www.biorxiv.org/content/10.1101/2020.05.22.111161v1")

    if result.get("success"):
        print(f"   Title: {result['title'][:60]}...")
        print(f"   DOI: {result['doi']}")
    else:
        print(f"   Error: {result.get('error', {}).get('message')}")

    # Test batch fetch
    print("\n3. Batch fetch:")
    dois = ["10.1101/2020.05.22.111161", "10.1101/2020.01.30.927871"]
    result = batch_fetch_biorxiv(dois)

    if result.get("success"):
        stats = result.get("stats", {})
        print(f"   Requested: {stats.get('requested')}")
        print(f"   Fetched: {stats.get('fetched')}")
        print(f"   Failed: {stats.get('failed')}")
    else:
        print(f"   Error: {result.get('error', {}).get('message')}")

    # Test formatted output
    print("\n4. Formatted output:")
    result = fetch_biorxiv_paper("10.1101/2020.05.22.111161")
    if result.get("success"):
        formatted = format_biorxiv_paper(result)
        print(formatted)

    # Test invalid DOI
    print("\n5. Invalid DOI handling:")
    result = fetch_biorxiv_paper("invalid_doi")
    print(f"   Error: {result.get('error', {}).get('message')}")

    print("\nAll bioRxiv fetch tests completed!")


if __name__ == "__main__":
    main()
