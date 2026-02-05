#!/usr/bin/env python3
"""
Tests for helper utilities.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from utils.helpers import (
    validate_pmid,
    validate_pmcid,
    validate_doi,
    extract_pmid_from_text,
    get_current_year,
    get_current_date,
    format_pubmed_date,
    get_date_range,
    extract_year,
    format_authors,
    clean_abstract,
    truncate_text,
)


def test_validate_pmid():
    """Test PMID validation."""
    print("\n Testing validate_pmid()...")

    test_cases = [
        ("12345678", True, "12345678"),
        ("PMID: 12345678", True, "12345678"),
        ("PMID:12345678", True, "12345678"),
        ("1", True, "1"),
        ("12345678", True, "12345678"),
        ("invalid", False, None),
        ("123456789", False, None),  # Too long
        (None, False, None),
        ("", False, None),
    ]

    all_passed = True
    for value, should_pass, expected in test_cases:
        is_valid, normalized, error = validate_pmid(value)

        if should_pass:
            if not is_valid:
                print(f"  FAIL: '{value}' should be valid")
                all_passed = False
            elif normalized != expected:
                print(f"  FAIL: '{value}' -> '{normalized}', expected '{expected}'")
                all_passed = False
            else:
                print(f"  PASS: '{value}' -> '{normalized}'")
        else:
            if is_valid:
                print(f"  FAIL: '{value}' should be invalid")
                all_passed = False
            else:
                print(f"  PASS: '{value}' correctly rejected")

    return all_passed


def test_validate_pmcid():
    """Test PMC ID validation."""
    print("\n Testing validate_pmcid()...")

    test_cases = [
        ("PMC1790863", True, "PMC1790863"),
        ("pmc1790863", True, "PMC1790863"),
        ("1790863", True, "PMC1790863"),
        ("invalid", False, None),
        (None, False, None),
    ]

    all_passed = True
    for value, should_pass, expected in test_cases:
        is_valid, normalized, error = validate_pmcid(value)

        if should_pass:
            if not is_valid or normalized != expected:
                print(f"  FAIL: '{value}' -> '{normalized}', expected '{expected}'")
                all_passed = False
            else:
                print(f"  PASS: '{value}' -> '{normalized}'")
        else:
            if is_valid:
                print(f"  FAIL: '{value}' should be invalid")
                all_passed = False
            else:
                print(f"  PASS: '{value}' correctly rejected")

    return all_passed


def test_extract_pmid_from_text():
    """Test PMID extraction from text."""
    print("\n Testing extract_pmid_from_text()...")

    test_cases = [
        ("See PMID: 12345678", ["12345678"]),
        ("PMID 12345678 and PMID: 87654321", ["12345678", "87654321"]),
        ("No PMIDs here", []),
        ("PubMed ID: 11111111", ["11111111"]),
    ]

    all_passed = True
    for text, expected in test_cases:
        result = extract_pmid_from_text(text)
        if result != expected:
            print(f"  FAIL: '{text[:30]}...' -> {result}, expected {expected}")
            all_passed = False
        else:
            print(f"  PASS: Found {len(result)} PMID(s)")

    return all_passed


def test_date_functions():
    """Test date handling functions."""
    print("\n Testing date functions...")

    all_passed = True

    # Test get_current_year
    year = get_current_year()
    expected_year = datetime.now().year
    if year != expected_year:
        print(f"  FAIL: get_current_year() returned {year}, expected {expected_year}")
        all_passed = False
    else:
        print(f"  PASS: get_current_year() = {year}")

    # Test get_current_date
    date = get_current_date()
    if not date or len(date) != 10:  # YYYY/MM/DD
        print(f"  FAIL: get_current_date() returned invalid date: {date}")
        all_passed = False
    else:
        print(f"  PASS: get_current_date() = {date}")

    # Test format_pubmed_date
    formatted = format_pubmed_date(2024, 6, 15)
    if formatted != "2024/06/15":
        print(f"  FAIL: format_pubmed_date() returned {formatted}")
        all_passed = False
    else:
        print(f"  PASS: format_pubmed_date() = {formatted}")

    # Test get_date_range
    min_date, max_date = get_date_range(30)
    if not min_date or not max_date:
        print(f"  FAIL: get_date_range() returned invalid range")
        all_passed = False
    else:
        print(f"  PASS: get_date_range(30) = {min_date} to {max_date}")

    return all_passed


def test_extract_year():
    """Test year extraction from various formats."""
    print("\n Testing extract_year()...")

    test_cases = [
        (2024, 2024),
        ("2024 Jan 15", 2024),
        ({"Year": "2024"}, 2024),
        ("January 2023", 2023),
        ("invalid", None),
    ]

    all_passed = True
    for value, expected in test_cases:
        result = extract_year(value)
        if result != expected:
            print(f"  FAIL: extract_year({value}) = {result}, expected {expected}")
            all_passed = False
        else:
            print(f"  PASS: extract_year({value}) = {result}")

    return all_passed


def test_format_authors():
    """Test author formatting."""
    print("\n Testing format_authors()...")

    authors = [
        {"LastName": "Smith", "ForeName": "John", "Initials": "J"},
        {"LastName": "Jones", "ForeName": "Mary", "Initials": "M"},
        {"LastName": "Wilson", "ForeName": "Bob", "Initials": "B"},
        {"LastName": "Brown", "ForeName": "Alice", "Initials": "A"},
    ]

    all_passed = True

    # Test short format
    result = format_authors(authors, max_authors=2)
    if "Smith J" not in result or "et al" not in result:
        print(f"  FAIL: Short format incorrect: {result}")
        all_passed = False
    else:
        print(f"  PASS: Short format: {result}")

    # Test full format
    result = format_authors(authors, max_authors=2, style="full")
    if "Smith John" not in result:
        print(f"  FAIL: Full format incorrect: {result}")
        all_passed = False
    else:
        print(f"  PASS: Full format: {result}")

    # Test empty list
    result = format_authors([])
    if result != "Unknown authors":
        print(f"  FAIL: Empty list should return 'Unknown authors'")
        all_passed = False
    else:
        print(f"  PASS: Empty list handled")

    return all_passed


def test_clean_abstract():
    """Test abstract text cleaning."""
    print("\n Testing clean_abstract()...")

    test_cases = [
        ("Normal text", "Normal text"),
        ("Text  with   spaces", "Text with spaces"),
        ("<b>Bold</b> text", "Bold text"),
        ("&amp; &lt; &gt;", "& < >"),
    ]

    all_passed = True
    for input_text, expected in test_cases:
        result = clean_abstract(input_text)
        if result != expected:
            print(f"  FAIL: '{input_text}' -> '{result}', expected '{expected}'")
            all_passed = False
        else:
            print(f"  PASS: Text cleaned correctly")

    return all_passed


def test_truncate_text():
    """Test text truncation."""
    print("\n Testing truncate_text()...")

    all_passed = True

    # Test normal truncation
    text = "This is a long text that should be truncated"
    result = truncate_text(text, max_length=20)
    if len(result) > 23:  # 20 + "..."
        print(f"  FAIL: Truncation too long: {len(result)}")
        all_passed = False
    else:
        print(f"  PASS: Truncated to {len(result)} chars")

    # Test short text (no truncation needed)
    short = "Short"
    result = truncate_text(short, max_length=20)
    if result != short:
        print(f"  FAIL: Short text was modified")
        all_passed = False
    else:
        print(f"  PASS: Short text unchanged")

    return all_passed


def main():
    """Run all helper tests."""
    print("=" * 70)
    print("HELPER UTILITY TESTS")
    print("=" * 70)

    tests = [
        ("PMID Validation", test_validate_pmid),
        ("PMC ID Validation", test_validate_pmcid),
        ("PMID Extraction", test_extract_pmid_from_text),
        ("Date Functions", test_date_functions),
        ("Year Extraction", test_extract_year),
        ("Author Formatting", test_format_authors),
        ("Abstract Cleaning", test_clean_abstract),
        ("Text Truncation", test_truncate_text),
    ]

    results = []
    for test_name, test_func in tests:
        passed = test_func()
        results.append((test_name, passed))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {test_name}")

    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)

    print(f"\nResults: {passed_count}/{total_count} passed")

    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
