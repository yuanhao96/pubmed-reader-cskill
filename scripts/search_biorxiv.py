#!/usr/bin/env python3
"""
bioRxiv/medRxiv search functionality.
Provides search capabilities for preprints on bioRxiv and medRxiv.

Since bioRxiv has no keyword search API, this module implements:
1. Website search parsing - https://www.biorxiv.org/search/[query]
2. Date browsing via official API - https://api.biorxiv.org/details/[server]/[dates]

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
from datetime import datetime, timedelta
import logging
import time

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))
from utils.helpers import format_biorxiv_citation, extract_year
from utils.validators.parameter_validator import (
    validate_query_param,
    validate_max_results,
    ValidationError,
)
from utils.cache_manager import cache_search_results, get_cached_search
from utils.rate_limiter import throttle, report_success, report_error

logger = logging.getLogger(__name__)

# API Configuration
BIORXIV_API_URL = "https://api.biorxiv.org"
BIORXIV_SEARCH_URL = "https://www.biorxiv.org/search"
MEDRXIV_SEARCH_URL = "https://www.medrxiv.org/search"

# User agent for requests
USER_AGENT = 'pubmed-reader-cskill/1.4.0 (literature search tool)'


def search_biorxiv(
    query: str,
    max_results: int = 20,
    server: str = "biorxiv",
    sort_by: str = "relevance_rank",
    use_cache: bool = True,
    include_summaries: bool = True
) -> Dict[str, Any]:
    """
    Search bioRxiv/medRxiv for preprints matching query.

    Uses website search since the API doesn't support keyword search.

    Args:
        query: Search query (free text)
        max_results: Maximum results to return (1-200)
        server: "biorxiv" or "medrxiv"
        sort_by: Sort order ("relevance_rank", "publication_date")
        use_cache: Whether to use cached results
        include_summaries: Whether to include abstracts in results

    Returns:
        Dict containing:
        - success: bool
        - count: Total matching articles (approximate)
        - articles: List of article metadata dicts
        - query_info: Search metadata
        - error: Error info if failed

    Example:
        >>> result = search_biorxiv("CRISPR gene editing", max_results=10)
        >>> print(f"Found {result['count']} papers")
    """
    # Validate parameters
    try:
        query = validate_query_param(query)
        max_results = validate_max_results(max_results, maximum=200)
    except ValidationError as e:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": e.message,
                "param": e.param_name,
                "suggestion": e.suggestion
            }
        }

    # Validate server
    server = server.lower()
    if server not in ("biorxiv", "medrxiv"):
        server = "biorxiv"

    # Check cache
    cache_key = f"biorxiv_search:{server}:{query}:{max_results}:{sort_by}"
    if use_cache:
        cached = get_cached_search(cache_key)
        if cached:
            logger.info(f"Cache hit for {server} query: {query}")
            return cached

    # Build search URL
    base_url = BIORXIV_SEARCH_URL if server == "biorxiv" else MEDRXIV_SEARCH_URL

    # Encode query for URL
    encoded_query = urllib.parse.quote(query)

    # Build search parameters
    # bioRxiv/medRxiv search format: /search/query%20terms
    # With parameters: ?page=0&numresults=20&sort=relevance-rank
    params = {
        "numresults": min(max_results, 75),  # Max per page is 75
        "sort": sort_by.replace("_", "-"),
    }

    url = f"{base_url}/{encoded_query}?{urllib.parse.urlencode(params)}"

    try:
        throttle()
        time.sleep(0.3)  # Reasonable rate limiting

        req = urllib.request.Request(url, headers={
            'User-Agent': USER_AGENT,
            'Accept': 'text/html',
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            html_data = response.read().decode('utf-8')
        report_success()
    except urllib.error.URLError as e:
        report_error()
        return {
            "success": False,
            "error": {
                "code": "NETWORK_ERROR",
                "message": f"Failed to connect to {server} search: {e}",
                "suggestion": "Check network connection and try again"
            }
        }

    # Parse HTML response
    articles = _parse_search_results(html_data, include_summaries, server)
    total_count = _extract_result_count(html_data)

    # Limit results
    articles = articles[:max_results]

    result = {
        "success": True,
        "count": total_count,
        "articles": articles,
        "query_info": {
            "query": query,
            "returned": len(articles),
            "total": total_count,
            "sort_by": sort_by,
            "server": server,
            "source": server
        },
        "validation": {
            "passed": True,
            "warnings": []
        }
    }

    # Cache results
    if use_cache:
        cache_search_results(cache_key, result)

    return result


def browse_biorxiv_recent(
    days: int = 7,
    server: str = "biorxiv",
    category: Optional[str] = None,
    max_results: int = 100,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Browse recent bioRxiv/medRxiv preprints using the official API.

    Args:
        days: Number of days to look back (1-30)
        server: "biorxiv" or "medrxiv"
        category: Optional subject category filter
        max_results: Maximum results to return
        use_cache: Whether to use cached results

    Returns:
        Dict containing:
        - success: bool
        - count: Number of articles found
        - articles: List of article metadata dicts
        - query_info: Browse metadata
        - error: Error info if failed

    Example:
        >>> result = browse_biorxiv_recent(days=7, server="medrxiv")
        >>> print(f"Found {result['count']} recent preprints")
    """
    # Validate parameters
    days = max(1, min(30, days))
    server = server.lower()
    if server not in ("biorxiv", "medrxiv"):
        server = "biorxiv"

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    # Check cache
    cache_key = f"biorxiv_browse:{server}:{start_str}:{end_str}:{category}:{max_results}"
    if use_cache:
        cached = get_cached_search(cache_key)
        if cached:
            logger.info(f"Cache hit for {server} browse: {start_str} to {end_str}")
            return cached

    # Build API URL
    # API endpoint: /details/[server]/[start_date]/[end_date]/[cursor]/json
    url = f"{BIORXIV_API_URL}/details/{server}/{start_str}/{end_str}/0/json"

    all_articles = []
    cursor = 0

    while len(all_articles) < max_results:
        try:
            throttle()
            time.sleep(0.3)

            current_url = f"{BIORXIV_API_URL}/details/{server}/{start_str}/{end_str}/{cursor}/json"

            req = urllib.request.Request(current_url, headers={
                'User-Agent': USER_AGENT,
                'Accept': 'application/json',
            })
            with urllib.request.urlopen(req, timeout=30) as response:
                json_data = response.read().decode('utf-8')
            report_success()

            data = json.loads(json_data)

            # Check for API messages
            messages = data.get('messages', [])
            if messages:
                for msg in messages:
                    if msg.get('status') == 'no posts found':
                        break

            collection = data.get('collection', [])
            if not collection:
                break

            # Parse articles
            for item in collection:
                article = _parse_api_article(item, server)

                # Filter by category if specified
                if category:
                    article_cat = article.get('category', '').lower()
                    if category.lower() not in article_cat:
                        continue

                all_articles.append(article)

                if len(all_articles) >= max_results:
                    break

            # Check if there are more pages
            messages = data.get('messages', [{}])
            if messages:
                total_str = messages[0].get('total', '0')
                try:
                    total = int(total_str)
                except (ValueError, TypeError):
                    total = 0
            else:
                total = 0
            cursor += len(collection)

            if cursor >= total:
                break

        except urllib.error.URLError as e:
            report_error()
            if not all_articles:
                return {
                    "success": False,
                    "error": {
                        "code": "NETWORK_ERROR",
                        "message": f"Failed to connect to {server} API: {e}",
                        "suggestion": "Check network connection and try again"
                    }
                }
            break  # Return what we have
        except json.JSONDecodeError as e:
            report_error()
            if not all_articles:
                return {
                    "success": False,
                    "error": {
                        "code": "PARSE_ERROR",
                        "message": f"Failed to parse {server} API response: {e}"
                    }
                }
            break

    result = {
        "success": True,
        "count": len(all_articles),
        "articles": all_articles[:max_results],
        "query_info": {
            "browse_type": "recent",
            "days": days,
            "start_date": start_str,
            "end_date": end_str,
            "category": category,
            "returned": len(all_articles[:max_results]),
            "server": server,
            "source": server
        },
        "validation": {
            "passed": True,
            "warnings": []
        }
    }

    # Cache results
    if use_cache:
        cache_search_results(cache_key, result)

    return result


def _parse_search_results(html: str, include_summaries: bool, server: str) -> List[Dict[str, Any]]:
    """
    Parse bioRxiv/medRxiv search results HTML.

    Args:
        html: Raw HTML content
        include_summaries: Whether to extract abstracts
        server: "biorxiv" or "medrxiv"

    Returns:
        List of article metadata dicts
    """
    articles = []

    # Find all search result items
    # bioRxiv uses <li class="search-result-highwire-citation">
    result_pattern = re.compile(
        r'<li[^>]*class="[^"]*search-result[^"]*"[^>]*>(.*?)</li>',
        re.DOTALL | re.IGNORECASE
    )

    for match in result_pattern.finditer(html):
        result_html = match.group(1)
        article = _parse_search_result_item(result_html, include_summaries, server)
        if article:
            articles.append(article)

    # Alternative pattern for different HTML structure
    if not articles:
        # Try article class pattern
        article_pattern = re.compile(
            r'<article[^>]*>(.*?)</article>',
            re.DOTALL | re.IGNORECASE
        )

        for match in article_pattern.finditer(html):
            article_html = match.group(1)
            article = _parse_search_result_item(article_html, include_summaries, server)
            if article:
                articles.append(article)

    return articles


def _parse_search_result_item(html: str, include_summary: bool, server: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single search result item.

    Args:
        html: HTML for one search result
        include_summary: Whether to extract abstract
        server: Server name for URLs

    Returns:
        Article metadata dict or None
    """
    # Extract DOI from link
    doi_match = re.search(r'href="[^"]*/(10\.\d{4,}/[^"]+)"', html)
    if not doi_match:
        # Try alternate pattern
        doi_match = re.search(r'data-doi="([^"]+)"', html)

    if not doi_match:
        return None

    doi = doi_match.group(1)
    # Clean DOI
    doi = re.sub(r'["\s].*$', '', doi)

    # Extract title
    title_match = re.search(
        r'<span[^>]*class="[^"]*highwire-cite-title[^"]*"[^>]*>(.*?)</span>',
        html, re.DOTALL | re.IGNORECASE
    )
    if not title_match:
        title_match = re.search(r'<h3[^>]*>(.*?)</h3>', html, re.DOTALL)
    if not title_match:
        title_match = re.search(r'<a[^>]*class="[^"]*title[^"]*"[^>]*>(.*?)</a>', html, re.DOTALL)

    title = _strip_tags(title_match.group(1)) if title_match else "Untitled"

    # Extract authors
    authors = []
    authors_match = re.search(
        r'<span[^>]*class="[^"]*highwire-cite-authors[^"]*"[^>]*>(.*?)</span>',
        html, re.DOTALL | re.IGNORECASE
    )
    if authors_match:
        author_html = authors_match.group(1)
        # Parse individual author names
        author_spans = re.findall(
            r'<span[^>]*class="[^"]*highwire-citation-author[^"]*"[^>]*>(.*?)</span>',
            author_html, re.DOTALL | re.IGNORECASE
        )
        for span in author_spans:
            name = _strip_tags(span).strip()
            if name and name not in [',', ';']:
                authors.append(name)

    # Extract date
    date_match = re.search(
        r'<span[^>]*class="[^"]*highwire-cite-metadata-date[^"]*"[^>]*>(.*?)</span>',
        html, re.DOTALL | re.IGNORECASE
    )
    posted_date = ""
    year = None
    if date_match:
        posted_date = _strip_tags(date_match.group(1)).strip()
        year_match = re.search(r'(\d{4})', posted_date)
        if year_match:
            year = int(year_match.group(1))

    # Extract abstract if requested
    abstract = ""
    if include_summary:
        abstract_match = re.search(
            r'<p[^>]*class="[^"]*highwire-cite-snippet[^"]*"[^>]*>(.*?)</p>',
            html, re.DOTALL | re.IGNORECASE
        )
        if abstract_match:
            abstract = _strip_tags(abstract_match.group(1)).strip()

    # Build article dict
    article = {
        "doi": doi,
        "title": title,
        "authors": authors,
        "year": year,
        "posted_date": posted_date,
        "abstract": abstract if include_summary else "",
        "url": f"https://www.{server}.org/content/{doi}",
        "pdf_url": f"https://www.{server}.org/content/{doi}.full.pdf",
        "source": server
    }

    return article


def _parse_api_article(item: Dict[str, Any], server: str) -> Dict[str, Any]:
    """
    Parse article from bioRxiv API response.

    Args:
        item: Dict from API collection
        server: Server name

    Returns:
        Normalized article dict
    """
    doi = item.get('doi', '')

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
    if authors_str:
        # Authors are semicolon-separated
        author_parts = authors_str.split(';')
        for part in author_parts:
            name = part.strip()
            if name:
                authors.append(name)

    return {
        "doi": doi,
        "title": item.get('title', 'Untitled'),
        "authors": authors,
        "year": year,
        "posted_date": posted_date,
        "abstract": item.get('abstract', ''),
        "category": item.get('category', ''),
        "version": item.get('version', '1'),
        "type": item.get('type', 'preprint'),
        "license": item.get('license', ''),
        "published": item.get('published', ''),
        "jatsxml": item.get('jatsxml', ''),
        "url": f"https://www.{server}.org/content/{doi}",
        "pdf_url": f"https://www.{server}.org/content/{doi}.full.pdf",
        "source": server
    }


def _extract_result_count(html: str) -> int:
    """
    Extract total result count from search page.

    Args:
        html: Search results HTML

    Returns:
        Total count (approximate)
    """
    # Look for result count in various formats
    patterns = [
        r'(\d+)\s+results?',
        r'Results?\s*:\s*(\d+)',
        r'Showing\s+\d+\s*-\s*\d+\s+of\s+(\d+)',
        r'Found\s+(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return int(match.group(1))

    return 0


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


def format_biorxiv_search_results(results: Dict[str, Any]) -> str:
    """
    Format bioRxiv search results for display.

    Args:
        results: Search results dict

    Returns:
        Formatted string for display
    """
    if not results.get("success"):
        error = results.get("error", {})
        return f"Search failed: {error.get('message', 'Unknown error')}"

    lines = []
    query_info = results.get("query_info", {})
    count = results.get("count", 0)
    articles = results.get("articles", [])
    server = query_info.get("server", "biorxiv")

    if query_info.get("browse_type") == "recent":
        lines.append(f"## Recent {server.title()} Preprints")
        lines.append("")
        lines.append(f"Last {query_info.get('days', 7)} days. Showing {len(articles)} of {count}:")
    else:
        query = query_info.get("query", "")
        lines.append(f"## {server.title()} Search Results: \"{query}\"")
        lines.append("")
        lines.append(f"Found {count:,} preprints. Showing {len(articles)}:")

    lines.append("")

    for i, article in enumerate(articles, 1):
        citation = format_biorxiv_citation(article, style="vancouver")
        lines.append(f"{i}. {citation}")
        if article.get("abstract"):
            abstract = article["abstract"][:200] + "..." if len(article.get("abstract", "")) > 200 else article.get("abstract", "")
            lines.append(f"   Abstract: {abstract}")
        lines.append("")

    return "\n".join(lines)


# =============================================================================
# Main (for testing)
# =============================================================================

def main():
    """Test bioRxiv search functionality."""
    print("Testing bioRxiv Search...\n")

    # Test website search
    print("1. Website search (CRISPR):")
    results = search_biorxiv("CRISPR", max_results=5)

    if results["success"]:
        print(f"   Found {results['count']} total preprints")
        print(f"   Retrieved {len(results.get('articles', []))} results")
        for article in results.get("articles", [])[:3]:
            print(f"   - {article.get('doi', 'N/A')}: {article.get('title', 'N/A')[:50]}...")
    else:
        print(f"   Error: {results.get('error', {}).get('message')}")

    # Test browse recent
    print("\n2. Browse recent (last 7 days):")
    results = browse_biorxiv_recent(days=7, max_results=5)

    if results["success"]:
        print(f"   Found {results['count']} recent preprints")
        for article in results.get("articles", [])[:3]:
            print(f"   - {article.get('doi', 'N/A')}: {article.get('title', 'N/A')[:50]}...")
    else:
        print(f"   Error: {results.get('error', {}).get('message')}")

    # Test medRxiv search
    print("\n3. medRxiv search (COVID):")
    results = search_biorxiv("COVID-19", max_results=5, server="medrxiv")

    if results["success"]:
        print(f"   Found {results['count']} medRxiv preprints")
    else:
        print(f"   Error: {results.get('error', {}).get('message')}")

    # Test formatted output
    print("\n4. Formatted output:")
    results = search_biorxiv("machine learning", max_results=3)
    if results["success"]:
        formatted = format_biorxiv_search_results(results)
        print(formatted)

    print("\nAll bioRxiv search tests completed!")


if __name__ == "__main__":
    main()
