#!/usr/bin/env python3
"""
Common helper utilities for PubMed Reader skill.
Provides ID validation, date handling, formatting, and temporal context.
"""

import re
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ID Validation
# =============================================================================

def validate_pmid(pmid: Any) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate PubMed ID format.

    Args:
        pmid: Value to validate (string or int)

    Returns:
        Tuple of (is_valid, normalized_pmid, error_message)

    Example:
        >>> validate_pmid("12345678")
        (True, "12345678", None)
        >>> validate_pmid("invalid")
        (False, None, "PMID must be a 1-8 digit number")
    """
    if pmid is None:
        return False, None, "PMID cannot be None"

    # Convert to string
    pmid_str = str(pmid).strip()

    # Check if empty
    if not pmid_str:
        return False, None, "PMID cannot be empty"

    # Remove common prefixes
    pmid_str = re.sub(r'^(PMID:?\s*)', '', pmid_str, flags=re.IGNORECASE)

    # Validate format: 1-8 digits
    if not re.match(r'^\d{1,8}$', pmid_str):
        return False, None, "PMID must be a 1-8 digit number"

    return True, pmid_str, None


def validate_pmcid(pmcid: Any) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate PubMed Central ID format.

    Args:
        pmcid: Value to validate

    Returns:
        Tuple of (is_valid, normalized_pmcid, error_message)

    Example:
        >>> validate_pmcid("PMC1790863")
        (True, "PMC1790863", None)
        >>> validate_pmcid("1790863")
        (True, "PMC1790863", None)
    """
    if pmcid is None:
        return False, None, "PMC ID cannot be None"

    pmcid_str = str(pmcid).strip().upper()

    if not pmcid_str:
        return False, None, "PMC ID cannot be empty"

    # Add PMC prefix if missing
    if re.match(r'^\d+$', pmcid_str):
        pmcid_str = f"PMC{pmcid_str}"

    # Validate format: PMC followed by digits
    if not re.match(r'^PMC\d+$', pmcid_str):
        return False, None, "PMC ID must be 'PMC' followed by digits"

    return True, pmcid_str, None


def validate_doi(doi: Any) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate DOI format.

    Args:
        doi: DOI to validate

    Returns:
        Tuple of (is_valid, normalized_doi, error_message)
    """
    if doi is None:
        return False, None, "DOI cannot be None"

    doi_str = str(doi).strip()

    # Remove common prefixes
    doi_str = re.sub(r'^(https?://)?(dx\.)?doi\.org/', '', doi_str)
    doi_str = re.sub(r'^doi:\s*', '', doi_str, flags=re.IGNORECASE)

    # Basic DOI format validation (starts with 10.)
    if not re.match(r'^10\.\d{4,}/\S+$', doi_str):
        return False, None, "Invalid DOI format"

    return True, doi_str, None


def extract_pmid_from_text(text: str) -> List[str]:
    """
    Extract PMIDs from text.

    Args:
        text: Text containing PMIDs

    Returns:
        List of extracted PMIDs

    Example:
        >>> extract_pmid_from_text("See PMID: 12345678 and PMID 87654321")
        ["12345678", "87654321"]
    """
    # Match various PMID formats
    patterns = [
        r'PMID:?\s*(\d{1,8})',
        r'PubMed\s*ID:?\s*(\d{1,8})',
        r'\bpmid(\d{1,8})\b',
    ]

    pmids = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        pmids.extend(matches)

    # Remove duplicates while preserving order
    seen = set()
    unique_pmids = []
    for pmid in pmids:
        if pmid not in seen:
            seen.add(pmid)
            unique_pmids.append(pmid)

    return unique_pmids


# =============================================================================
# Date Handling
# =============================================================================

def get_current_year() -> int:
    """Get current year."""
    return datetime.now().year


def get_current_date() -> str:
    """
    Get current date in PubMed format.

    Returns:
        Date string in YYYY/MM/DD format
    """
    return datetime.now().strftime("%Y/%m/%d")


def format_pubmed_date(year: Optional[int] = None,
                       month: Optional[int] = None,
                       day: Optional[int] = None) -> str:
    """
    Format date for PubMed API.

    Args:
        year: Year (defaults to current)
        month: Month (1-12)
        day: Day (1-31)

    Returns:
        Date string in YYYY/MM/DD format
    """
    now = datetime.now()

    year = year or now.year
    month = month or 1
    day = day or 1

    return f"{year:04d}/{month:02d}/{day:02d}"


def parse_pubmed_date(date_str: str) -> Optional[datetime]:
    """
    Parse PubMed date string.

    Args:
        date_str: Date in various formats

    Returns:
        datetime object or None
    """
    formats = [
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%Y %b %d",
        "%Y %b",
        "%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    return None


def get_date_range(days_back: int) -> Tuple[str, str]:
    """
    Get date range for last N days.

    Args:
        days_back: Number of days to go back

    Returns:
        Tuple of (min_date, max_date) in YYYY/MM/DD format
    """
    end = datetime.now()
    start = end - timedelta(days=days_back)

    return (
        start.strftime("%Y/%m/%d"),
        end.strftime("%Y/%m/%d")
    )


def extract_year(date_input: Any) -> Optional[int]:
    """
    Extract year from various date formats.

    Args:
        date_input: Date in various formats (str, dict, int)

    Returns:
        Year as integer or None
    """
    if isinstance(date_input, int):
        if 1800 <= date_input <= 2100:
            return date_input
        return None

    if isinstance(date_input, dict):
        if 'Year' in date_input:
            return int(date_input['Year'])
        return None

    if isinstance(date_input, str):
        # Try extracting 4-digit year
        match = re.search(r'\b(19|20)\d{2}\b', date_input)
        if match:
            return int(match.group())

    return None


# =============================================================================
# Author Formatting
# =============================================================================

def format_authors(authors: List[Dict[str, str]],
                   max_authors: int = 3,
                   style: str = "short") -> str:
    """
    Format author list for display.

    Args:
        authors: List of author dicts with LastName, ForeName, Initials
        max_authors: Maximum authors to show before "et al."
        style: "short" (initials) or "full" (full names)

    Returns:
        Formatted author string

    Example:
        >>> authors = [{"LastName": "Smith", "ForeName": "John", "Initials": "J"}]
        >>> format_authors(authors)
        "Smith J"
    """
    if not authors:
        return "Unknown authors"

    formatted = []

    for i, author in enumerate(authors[:max_authors]):
        last = author.get('LastName', '')
        first = author.get('ForeName', '')
        initials = author.get('Initials', '')

        if style == "short":
            if last and initials:
                formatted.append(f"{last} {initials}")
            elif last:
                formatted.append(last)
        else:
            if last and first:
                formatted.append(f"{last} {first}")
            elif last:
                formatted.append(last)

    result = ", ".join(formatted)

    if len(authors) > max_authors:
        result += ", et al."

    return result


def format_single_author(author: Dict[str, str]) -> str:
    """
    Format single author for display.

    Args:
        author: Author dict

    Returns:
        Formatted author name
    """
    last = author.get('LastName', '')
    initials = author.get('Initials', '')

    if last and initials:
        return f"{last} {initials}"
    return last or "Unknown"


# =============================================================================
# Citation Formatting
# =============================================================================

def format_citation(article: Dict[str, Any], style: str = "vancouver") -> str:
    """
    Format article citation.

    Args:
        article: Article metadata dict
        style: Citation style ("vancouver", "apa", "simple")

    Returns:
        Formatted citation string
    """
    authors = article.get('authors', [])
    title = article.get('title', 'Untitled')
    journal = article.get('journal', '')
    year = article.get('year', '')
    volume = article.get('volume', '')
    issue = article.get('issue', '')
    pages = article.get('pages', '')
    pmid = article.get('pmid', '')

    author_str = format_authors(authors, max_authors=6)

    if style == "vancouver":
        citation = f"{author_str}. {title}. {journal}."
        if year:
            citation += f" {year}"
        if volume:
            citation += f";{volume}"
        if issue:
            citation += f"({issue})"
        if pages:
            citation += f":{pages}"
        citation += "."
        if pmid:
            citation += f" PMID: {pmid}."
        return citation

    elif style == "simple":
        return f"{author_str} ({year}). {title}. {journal}. PMID: {pmid}"

    else:  # APA-like
        return f"{author_str} ({year}). {title}. {journal}, {volume}({issue}), {pages}."


# =============================================================================
# Text Processing
# =============================================================================

def clean_abstract(text: str) -> str:
    """
    Clean abstract text for display.

    Args:
        text: Raw abstract text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove XML/HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Fix common encoding issues
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')

    return text.strip()


def truncate_text(text: str, max_length: int = 500,
                  suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum characters
        suffix: Suffix to append if truncated

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    # Try to truncate at word boundary
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return truncated + suffix


def extract_structured_abstract(abstract_text: str) -> Dict[str, str]:
    """
    Extract sections from structured abstract.

    Args:
        abstract_text: Abstract text with section labels

    Returns:
        Dict mapping section names to content
    """
    sections = {}

    # Common section patterns
    patterns = [
        r'\b(BACKGROUND|INTRODUCTION):\s*',
        r'\b(METHODS?|MATERIALS?\s+AND\s+METHODS?):\s*',
        r'\b(RESULTS?):\s*',
        r'\b(CONCLUSIONS?|DISCUSSION):\s*',
        r'\b(OBJECTIVES?|AIMS?|PURPOSE):\s*',
    ]

    # Try to split by sections
    current_section = "Main"
    current_text = []

    for line in abstract_text.split('\n'):
        matched = False
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                # Save previous section
                if current_text:
                    sections[current_section] = ' '.join(current_text)
                # Start new section
                current_section = match.group(1).upper()
                current_text = [line[match.end():]]
                matched = True
                break

        if not matched:
            current_text.append(line)

    # Save last section
    if current_text:
        sections[current_section] = ' '.join(current_text)

    return sections


# =============================================================================
# API Helpers
# =============================================================================

def get_api_key() -> Optional[str]:
    """
    Get NCBI API key from environment.

    Returns:
        API key or None
    """
    return os.environ.get('NCBI_API_KEY')


def get_email() -> Optional[str]:
    """
    Get email for NCBI API from environment.

    Returns:
        Email or None
    """
    return os.environ.get('NCBI_EMAIL')


def build_api_params(base_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build API parameters with optional key and email.

    Args:
        base_params: Base parameters dict

    Returns:
        Parameters with api_key and email if available
    """
    params = base_params.copy()

    api_key = get_api_key()
    if api_key:
        params['api_key'] = api_key

    email = get_email()
    if email:
        params['email'] = email

    # Always include tool identifier
    params['tool'] = os.environ.get('NCBI_TOOL', 'pubmed-reader-cskill')

    return params


# =============================================================================
# Result Formatting
# =============================================================================

def format_search_result(article: Dict[str, Any],
                         index: int = 0,
                         include_abstract: bool = False) -> str:
    """
    Format single search result for display.

    Args:
        article: Article metadata
        index: Result number (1-based)
        include_abstract: Whether to include abstract

    Returns:
        Formatted result string
    """
    title = article.get('title', 'Untitled')
    authors = format_authors(article.get('authors', []))
    journal = article.get('journal', '')
    year = article.get('year', '')
    pmid = article.get('pmid', '')
    citations = article.get('citation_count')

    result = f"{index}. **{title}**"
    result += f"\n   Authors: {authors}"

    if journal and year:
        result += f"\n   Journal: {journal}, {year}"
    elif journal:
        result += f"\n   Journal: {journal}"

    result += f"\n   PMID: {pmid}"

    if citations is not None:
        result += f"\n   Cited by: {citations} articles"

    if include_abstract and article.get('abstract'):
        abstract = truncate_text(article['abstract'], 300)
        result += f"\n   Abstract: {abstract}"

    return result


def format_year_message(year_used: int, year_requested: Optional[int]) -> str:
    """
    Format message about year used vs requested.

    Args:
        year_used: Year actually used for query
        year_requested: Year originally requested (None if auto-detected)

    Returns:
        Informational message about year
    """
    if year_requested is None:
        return f"Using current year ({year_used})"
    elif year_used != year_requested:
        return f"Data for {year_requested} not available, using {year_used}"
    else:
        return f"Year: {year_used}"


# =============================================================================
# Main (for testing)
# =============================================================================

def main():
    """Test helper functions."""
    print("Testing PubMed Reader helpers...\n")

    # Test PMID validation
    print("1. Testing validate_pmid():")
    test_pmids = ["12345678", "PMID: 12345678", "invalid", None, "123456789"]
    for pmid in test_pmids:
        valid, normalized, error = validate_pmid(pmid)
        if valid:
            print(f"   '{pmid}' -> {normalized}")
        else:
            print(f"   '{pmid}' -> INVALID: {error}")

    # Test PMC ID validation
    print("\n2. Testing validate_pmcid():")
    test_pmcids = ["PMC1790863", "1790863", "pmc123", "invalid"]
    for pmcid in test_pmcids:
        valid, normalized, error = validate_pmcid(pmcid)
        if valid:
            print(f"   '{pmcid}' -> {normalized}")
        else:
            print(f"   '{pmcid}' -> INVALID: {error}")

    # Test date functions
    print("\n3. Testing date functions:")
    print(f"   Current date: {get_current_date()}")
    print(f"   Current year: {get_current_year()}")
    min_date, max_date = get_date_range(30)
    print(f"   Last 30 days: {min_date} to {max_date}")

    # Test author formatting
    print("\n4. Testing format_authors():")
    authors = [
        {"LastName": "Smith", "ForeName": "John", "Initials": "J"},
        {"LastName": "Jones", "ForeName": "Mary", "Initials": "M"},
        {"LastName": "Wilson", "ForeName": "Bob", "Initials": "B"},
        {"LastName": "Brown", "ForeName": "Alice", "Initials": "A"},
    ]
    print(f"   Short (3): {format_authors(authors, max_authors=3)}")
    print(f"   Full (2): {format_authors(authors, max_authors=2, style='full')}")

    # Test text extraction
    print("\n5. Testing extract_pmid_from_text():")
    text = "See PMID: 12345678 and PMID 87654321 for details."
    pmids = extract_pmid_from_text(text)
    print(f"   Extracted: {pmids}")

    print("\n All tests passed!")


if __name__ == "__main__":
    main()
