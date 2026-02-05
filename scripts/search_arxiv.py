#!/usr/bin/env python3
"""
arXiv search functionality using the arXiv API (Atom feed).
Provides search capabilities for preprints and scientific papers on arXiv.org.

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
from utils.helpers import format_arxiv_citation, extract_year
from utils.validators.parameter_validator import (
    validate_query_param,
    validate_max_results,
    ValidationError,
)
from utils.cache_manager import cache_search_results, get_cached_search
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


def search_arxiv(
    query: str,
    max_results: int = 20,
    start: int = 0,
    sort_by: str = "relevance",
    sort_order: str = "descending",
    category: Optional[str] = None,
    use_cache: bool = True,
    include_summaries: bool = True
) -> Dict[str, Any]:
    """
    Search arXiv for papers matching query.

    Args:
        query: Search query (supports arXiv field prefixes: ti:, au:, abs:, cat:, all:)
        max_results: Maximum results to return (1-2000)
        start: Offset for pagination (0-based)
        sort_by: Sort order ("relevance", "lastUpdatedDate", "submittedDate")
        sort_order: "ascending" or "descending"
        category: Filter by arXiv category (e.g., "cs.CL", "cs.AI", "q-bio")
        use_cache: Whether to use cached results
        include_summaries: Whether to include abstracts in results

    Returns:
        Dict containing:
        - success: bool
        - count: Total matching articles
        - articles: List of article metadata dicts
        - query_info: Search metadata
        - error: Error info if failed

    Example:
        >>> result = search_arxiv("transformer attention mechanism", max_results=10)
        >>> print(f"Found {result['count']} papers")
    """
    # Validate parameters
    try:
        query = validate_query_param(query)
        max_results = validate_max_results(max_results, maximum=2000)
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

    # Validate sort_by
    valid_sorts = ["relevance", "lastUpdatedDate", "submittedDate"]
    if sort_by not in valid_sorts:
        sort_by = "relevance"

    if sort_order not in ("ascending", "descending"):
        sort_order = "descending"

    # Build search query
    search_query = _build_search_query(query, category)

    # Check cache
    cache_key = f"arxiv:{search_query}:{max_results}:{start}:{sort_by}:{sort_order}"
    if use_cache:
        cached = get_cached_search(cache_key)
        if cached:
            logger.info(f"Cache hit for arXiv query: {query}")
            return cached

    # Build API request
    params = {
        "search_query": search_query,
        "start": start,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }

    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"

    try:
        # arXiv requires at least 3 seconds between requests
        throttle()
        time.sleep(0.5)  # Extra safety margin for arXiv

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
            "error": {
                "code": "NETWORK_ERROR",
                "message": f"Failed to connect to arXiv API: {e}",
                "suggestion": "Check network connection and try again"
            }
        }

    # Parse Atom XML response
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        return {
            "success": False,
            "error": {
                "code": "PARSE_ERROR",
                "message": f"Failed to parse arXiv API response: {e}"
            }
        }

    # Extract total results
    total_results_elem = root.find('opensearch:totalResults', NS)
    total_results = int(total_results_elem.text) if total_results_elem is not None else 0

    # Check for API error entries
    entries = root.findall('atom:entry', NS)
    if entries:
        first_id = entries[0].find('atom:id', NS)
        if first_id is not None and first_id.text and 'api/errors' in first_id.text:
            summary = entries[0].find('atom:summary', NS)
            error_msg = summary.text.strip() if summary is not None else "Unknown API error"
            return {
                "success": False,
                "error": {
                    "code": "API_ERROR",
                    "message": f"arXiv API error: {error_msg}"
                }
            }

    # Parse articles
    articles = []
    for entry in entries:
        article = _parse_entry(entry, include_summaries)
        if article:
            articles.append(article)

    result = {
        "success": True,
        "count": total_results,
        "articles": articles,
        "query_info": {
            "query": query,
            "search_query": search_query,
            "returned": len(articles),
            "total": total_results,
            "start": start,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "source": "arxiv"
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


def _build_search_query(query: str, category: Optional[str] = None) -> str:
    """
    Build arXiv search query string.

    If the query already contains field prefixes (ti:, au:, etc.), use as-is.
    Otherwise, wrap in all: for full-field search.

    Args:
        query: User search query
        category: Optional category filter

    Returns:
        Formatted arXiv query string
    """
    # Check if query already has field prefixes
    has_prefix = bool(re.search(r'\b(ti|au|abs|co|jr|cat|rn|all):', query))

    if not has_prefix:
        # Convert space-separated terms into all: prefix search
        terms = query.strip().split()
        if len(terms) == 1:
            search_query = f"all:{terms[0]}"
        else:
            # Use AND between terms for all: field
            parts = [f"all:{term}" for term in terms]
            search_query = "+AND+".join(parts)
    else:
        search_query = query

    # Add category filter
    if category:
        search_query = f"({search_query})+AND+cat:{category}"

    return search_query


def _parse_entry(entry: ET.Element, include_summary: bool = True) -> Optional[Dict[str, Any]]:
    """
    Parse single Atom entry into article dict.

    Args:
        entry: XML Element for one entry
        include_summary: Whether to include the abstract

    Returns:
        Article metadata dict or None
    """
    # Extract ID
    id_elem = entry.find('atom:id', NS)
    if id_elem is None:
        return None

    raw_id = id_elem.text.strip()
    # Extract arXiv ID from URL: http://arxiv.org/abs/2602.04557v1 -> 2602.04557v1
    arxiv_id = raw_id.split('/abs/')[-1] if '/abs/' in raw_id else raw_id

    # Title
    title_elem = entry.find('atom:title', NS)
    title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else "Untitled"
    title = re.sub(r'\s+', ' ', title)

    # Authors
    authors = []
    for author_elem in entry.findall('atom:author', NS):
        name_elem = author_elem.find('atom:name', NS)
        if name_elem is not None:
            name = name_elem.text.strip()
            authors.append(name)

    # Abstract/Summary
    summary = ""
    if include_summary:
        summary_elem = entry.find('atom:summary', NS)
        if summary_elem is not None:
            summary = summary_elem.text.strip().replace('\n', ' ')
            summary = re.sub(r'\s+', ' ', summary)

    # Published date
    published_elem = entry.find('atom:published', NS)
    published = published_elem.text.strip() if published_elem is not None else ""

    # Updated date
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

    # Primary category
    primary_cat_elem = entry.find('arxiv:primary_category', NS)
    primary_category = primary_cat_elem.get('term', '') if primary_cat_elem is not None else (categories[0] if categories else "")

    # DOI
    doi_elem = entry.find('arxiv:doi', NS)
    doi = doi_elem.text.strip() if doi_elem is not None else None

    # Journal reference
    journal_ref_elem = entry.find('arxiv:journal_ref', NS)
    journal_ref = journal_ref_elem.text.strip() if journal_ref_elem is not None else None

    # Comment (often contains page count, conference info)
    comment_elem = entry.find('arxiv:comment', NS)
    comment = comment_elem.text.strip() if comment_elem is not None else None

    # Links
    pdf_link = None
    html_link = None
    for link_elem in entry.findall('atom:link', NS):
        rel = link_elem.get('rel', '')
        link_type = link_elem.get('type', '')
        href = link_elem.get('href', '')
        link_title = link_elem.get('title', '')

        if link_title == 'pdf' or link_type == 'application/pdf':
            pdf_link = href
        elif rel == 'alternate' and link_type == 'text/html':
            html_link = href

    article = {
        "arxiv_id": arxiv_id,
        "title": title,
        "authors": authors,
        "year": year,
        "published": published,
        "updated": updated,
        "categories": categories,
        "primary_category": primary_category,
        "doi": doi,
        "journal_ref": journal_ref,
        "comment": comment,
        "pdf_url": pdf_link or f"https://arxiv.org/pdf/{arxiv_id}",
        "html_url": f"https://arxiv.org/html/{arxiv_id}",
        "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
        "source": "arxiv"
    }

    if include_summary:
        article["abstract"] = summary

    return article


def build_arxiv_query(
    terms: Optional[List[str]] = None,
    title: Optional[str] = None,
    author: Optional[str] = None,
    abstract: Optional[str] = None,
    category: Optional[str] = None,
    boolean_op: str = "AND"
) -> str:
    """
    Build advanced arXiv query with field prefixes.

    Args:
        terms: General search terms (uses all: prefix)
        title: Title search terms (uses ti: prefix)
        author: Author name (uses au: prefix)
        abstract: Abstract search terms (uses abs: prefix)
        category: Category filter (uses cat: prefix)
        boolean_op: Operator between terms (AND, OR)

    Returns:
        Formatted arXiv query string

    Example:
        >>> query = build_arxiv_query(title="attention", author="Vaswani", category="cs.CL")
        >>> print(query)
        "ti:attention AND au:Vaswani AND cat:cs.CL"
    """
    parts = []

    if terms:
        term_parts = [f"all:{term}" for term in terms]
        parts.append(f"({f' {boolean_op} '.join(term_parts)})")

    if title:
        parts.append(f"ti:{title}")

    if author:
        parts.append(f"au:{author}")

    if abstract:
        parts.append(f"abs:{abstract}")

    if category:
        parts.append(f"cat:{category}")

    return " AND ".join(parts)


def search_arxiv_by_category(
    category: str,
    query: Optional[str] = None,
    max_results: int = 20,
    sort_by: str = "submittedDate",
    **kwargs
) -> Dict[str, Any]:
    """
    Search arXiv within a specific category.

    Args:
        category: arXiv category (e.g., "cs.CL", "cs.AI", "q-bio.BM")
        query: Optional additional search terms
        max_results: Maximum results
        sort_by: Sort order
        **kwargs: Additional args for search_arxiv

    Returns:
        Search results
    """
    if query:
        full_query = f"cat:{category} AND all:{query}"
    else:
        full_query = f"cat:{category}"

    return search_arxiv(full_query, max_results=max_results, sort_by=sort_by, **kwargs)


def format_arxiv_search_results(results: Dict[str, Any]) -> str:
    """
    Format arXiv search results for display.

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

    lines.append(f"## arXiv Search Results: \"{query_info.get('query', '')}\"")
    lines.append("")
    lines.append(f"Found {count:,} papers. Showing {len(articles)}:")
    lines.append("")

    for i, article in enumerate(articles, 1):
        citation = format_arxiv_citation(article, style="vancouver")
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
    """Test arXiv search functionality."""
    print("Testing arXiv Search...\n")

    # Test basic search
    print("1. Basic search (LLM memory):")
    results = search_arxiv("LLM memory", max_results=5)

    if results["success"]:
        print(f"   Found {results['count']} total papers")
        print(f"   Retrieved {len(results.get('articles', []))} results")
        for article in results.get("articles", [])[:3]:
            print(f"   - {article['arxiv_id']}: {article['title'][:60]}...")
    else:
        print(f"   Error: {results.get('error', {}).get('message')}")

    # Test category search
    print("\n2. Category search (cs.CL):")
    results = search_arxiv_by_category("cs.CL", "language model", max_results=3)

    if results["success"]:
        print(f"   Found {results['count']} papers in cs.CL")

    # Test query building
    print("\n3. Query builder:")
    query = build_arxiv_query(
        title="attention",
        author="Vaswani",
        category="cs.CL"
    )
    print(f"   Built query: {query}")

    # Test formatted output
    print("\n4. Formatted output:")
    results = search_arxiv("transformer", max_results=3)
    if results["success"]:
        formatted = format_arxiv_search_results(results)
        print(formatted)

    print("\nAll arXiv search tests completed!")


if __name__ == "__main__":
    main()
