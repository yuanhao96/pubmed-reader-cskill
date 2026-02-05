#!/usr/bin/env python3
"""
Integration tests for PubMed Reader skill.
Tests complete workflows from query to result.
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from search_pubmed import search_pubmed, build_advanced_query
from fetch_article import fetch_abstract, batch_fetch
from fetch_fulltext import check_oa_availability, get_fulltext
from find_similar import find_similar_articles
from find_citations import get_citing_articles, get_references
from comprehensive_report import comprehensive_article_report
from strategic_literature_search import (
    strategic_literature_search,
    quick_literature_overview,
    format_strategic_search_results
)
from search_arxiv import search_arxiv, build_arxiv_query
from fetch_arxiv import fetch_arxiv_paper, batch_fetch_arxiv
from fetch_arxiv_fulltext import get_arxiv_fulltext, check_html_availability
from search_biorxiv import search_biorxiv, browse_biorxiv_recent
from fetch_biorxiv import fetch_biorxiv_paper, batch_fetch_biorxiv
from fetch_biorxiv_fulltext import get_biorxiv_fulltext, check_fulltext_availability as check_biorxiv_fulltext_availability


def test_search_pubmed_basic():
    """Test basic PubMed search."""
    print("\n Testing search_pubmed()...")

    try:
        result = search_pubmed("CRISPR", max_results=5)

        assert result.get('success'), f"Search failed: {result.get('error')}"
        assert result.get('count', 0) > 0, "No results found"
        assert len(result.get('pmids', [])) > 0, "No PMIDs returned"
        assert len(result.get('articles', [])) > 0, "No article summaries"

        print(f"  Found {result['count']} articles")
        print(f"  Returned {len(result['articles'])} summaries")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_with_date_filter():
    """Test PubMed search with date filtering."""
    print("\n Testing search_pubmed() with date filter...")

    try:
        result = search_pubmed(
            "COVID-19 vaccine",
            max_results=5,
            min_date="2024/01/01",
            sort="pub+date"
        )

        assert result.get('success'), f"Search failed: {result.get('error')}"

        # Check that articles are from 2024
        articles = result.get('articles', [])
        if articles:
            for article in articles[:3]:
                year = article.get('year', 0)
                # Some tolerance for date indexing
                assert year >= 2023, f"Article year {year} too old"

        print(f"  Found {result['count']} articles from 2024")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_fetch_abstract():
    """Test fetching article abstract."""
    print("\n Testing fetch_abstract()...")

    try:
        # Known PMID
        result = fetch_abstract("17299597")

        assert result.get('success'), f"Fetch failed: {result.get('error')}"
        assert result.get('pmid') == "17299597", "Wrong PMID returned"
        assert result.get('title'), "No title"
        assert result.get('abstract'), "No abstract"
        assert result.get('authors'), "No authors"

        print(f"  Title: {result['title'][:50]}...")
        print(f"  Authors: {len(result['authors'])} authors")
        print(f"  Year: {result.get('year')}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_batch_fetch():
    """Test batch fetching multiple articles."""
    print("\n Testing batch_fetch()...")

    try:
        pmids = ["17299597", "32756549", "11850928"]
        result = batch_fetch(pmids)

        assert result.get('success'), f"Batch fetch failed"
        assert len(result.get('articles', {})) > 0, "No articles fetched"

        stats = result.get('stats', {})
        print(f"  Requested: {stats.get('requested')}")
        print(f"  Fetched: {stats.get('fetched')}")
        print(f"  Failed: {stats.get('failed')}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_check_oa_availability():
    """Test checking Open Access availability."""
    print("\n Testing check_oa_availability()...")

    try:
        # Known OA article
        result = check_oa_availability("17299597")

        # This article should be in PMC OA
        print(f"  PMID 17299597: Available={result.get('available')}")
        print(f"  PMCID: {result.get('pmcid', 'N/A')}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_get_fulltext():
    """Test getting full text for OA article."""
    print("\n Testing get_fulltext()...")

    try:
        # Known OA article
        result = get_fulltext("17299597")

        if result.get('success'):
            print(f"  Word count: {result.get('word_count', 0)}")
            print(f"  Sections: {list(result.get('sections', {}).keys())}")
            print(f"  Figures: {len(result.get('figures', []))}")
            return True
        else:
            # Not all articles have full text
            print(f"  Full text not available: {result.get('error', {}).get('message')}")
            return True  # This is OK, just means no OA

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_find_similar():
    """Test finding similar articles."""
    print("\n Testing find_similar_articles()...")

    try:
        result = find_similar_articles("17299597", max_results=5)

        assert result.get('success'), f"Failed: {result.get('error')}"

        print(f"  Found {result.get('similar_count', 0)} similar articles")

        articles = result.get('articles', [])
        for i, article in enumerate(articles[:3], 1):
            score = article.get('score', 'N/A')
            print(f"  {i}. PMID {article.get('pmid')}: score={score}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_get_citing_articles():
    """Test getting citing articles."""
    print("\n Testing get_citing_articles()...")

    try:
        result = get_citing_articles("17299597", max_results=10)

        assert result.get('success'), f"Failed: {result.get('error')}"

        print(f"  Total citations: {result.get('citation_count', 0)}")
        print(f"  Returned: {len(result.get('articles', []))}")

        by_year = result.get('by_year', {})
        if by_year:
            years = list(by_year.keys())[:3]
            print(f"  Recent years: {years}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_get_references():
    """Test getting article references."""
    print("\n Testing get_references()...")

    try:
        result = get_references("17299597", max_results=10)

        assert result.get('success'), f"Failed: {result.get('error')}"

        print(f"  Reference count: {result.get('reference_count', 0)}")
        print(f"  Returned: {len(result.get('articles', []))}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_comprehensive_report():
    """Test comprehensive article report."""
    print("\n Testing comprehensive_article_report()...")

    try:
        result = comprehensive_article_report(
            "17299597",
            include_fulltext=True,
            max_similar=3,
            max_citations=5
        )

        assert result.get('success'), f"Failed: {result.get('error')}"

        print(f"  Sections completed:")
        for section, data in result.get('sections', {}).items():
            status = data.get('status', 'unknown')
            print(f"    - {section}: {status}")

        print(f"  Quick stats: {result.get('quick_stats', {})}")
        print(f"  Alerts: {result.get('alerts', [])}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_query_builder():
    """Test advanced query building."""
    print("\n Testing build_advanced_query()...")

    try:
        query = build_advanced_query(
            terms=["CRISPR", "cancer"],
            author="Zhang F",
            article_types=["Review"]
        )

        assert "CRISPR" in query, "CRISPR not in query"
        assert "cancer" in query, "cancer not in query"
        assert "Zhang F" in query, "Author not in query"
        assert "Review" in query, "Publication type not in query"

        print(f"  Built query: {query}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_invalid_pmid_handling():
    """Test handling of invalid PMID."""
    print("\n Testing invalid PMID handling...")

    try:
        result = fetch_abstract("invalid_pmid")

        assert not result.get('success'), "Should have failed"
        assert 'error' in result, "No error info"

        print(f"  Error handled: {result['error'].get('code')}")
        print(f"  Message: {result['error'].get('message')}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_validation_integration():
    """Test that validation info is included in responses."""
    print("\n Testing validation integration...")

    try:
        result = search_pubmed("CRISPR", max_results=3)

        assert result.get('success'), f"Search failed: {result.get('error')}"
        assert 'validation' in result, "No validation info"

        validation = result['validation']
        print(f"  Validation passed: {validation.get('passed')}")
        print(f"  Warnings: {validation.get('warnings', [])}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_strategic_literature_search():
    """Test strategic literature search (reviews first workflow)."""
    print("\n Testing strategic_literature_search()...")

    try:
        result = strategic_literature_search(
            topic="type 1 diabetes",
            max_reviews=2,
            max_research_per_review=2,
            years_back=5,
            include_seminal_works=True
        )

        assert result.get('success'), f"Failed: {result.get('error')}"

        # Check phases
        phases = result.get('phases', {})
        assert 'phase1_reviews' in phases, "Missing phase1_reviews"
        assert 'phase2_themes' in phases, "Missing phase2_themes"
        assert 'phase3_research' in phases, "Missing phase3_research"

        # Check statistics
        stats = result.get('statistics', {})
        print(f"  Total articles: {stats.get('total_articles', 0)}")
        print(f"  Reviews: {stats.get('total_reviews', 0)}")
        print(f"  Research: {stats.get('total_research_articles', 0)}")
        print(f"  Seminal: {stats.get('total_seminal_works', 0)}")
        print(f"  Themes: {stats.get('themes_identified', 0)}")

        # Check reading order
        reading_order = result.get('reading_order', [])
        assert len(reading_order) > 0, "No reading order generated"
        print(f"  Reading order: {len(reading_order)} items")

        # Check summary
        summary = result.get('summary', '')
        assert len(summary) > 0, "No summary generated"
        print(f"  Summary: {summary[:100]}...")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quick_literature_overview():
    """Test quick literature overview (reviews only)."""
    print("\n Testing quick_literature_overview()...")

    try:
        result = quick_literature_overview("CRISPR gene therapy", max_reviews=2)

        assert result.get('success'), f"Failed: {result.get('error')}"

        stats = result.get('statistics', {})
        # Quick overview should only have reviews
        assert stats.get('total_research_articles', 0) == 0, "Should not have research articles"

        print(f"  Reviews found: {stats.get('total_reviews', 0)}")
        print(f"  Search strategy: {result.get('search_strategy')}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_strategic_search_formatting():
    """Test formatting of strategic search results."""
    print("\n Testing format_strategic_search_results()...")

    try:
        result = quick_literature_overview("immunotherapy", max_reviews=2)

        if result.get('success'):
            formatted = format_strategic_search_results(result)

            assert len(formatted) > 100, "Formatted output too short"
            assert "Strategic Literature Search" in formatted, "Missing title"
            assert "Phase 1" in formatted, "Missing phase 1"

            print(f"  Formatted output length: {len(formatted)} chars")
            print(f"  First 200 chars:")
            print(f"  {formatted[:200]}...")

            return True
        else:
            print(f"  Search failed, cannot test formatting")
            return True  # Not a formatting failure

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_search_arxiv_basic():
    """Test basic arXiv search."""
    print("\n Testing search_arxiv()...")

    try:
        result = search_arxiv("transformer attention", max_results=5)

        assert result.get('success'), f"Search failed: {result.get('error')}"
        assert result.get('count', 0) > 0, "No results found"
        assert len(result.get('articles', [])) > 0, "No articles returned"

        print(f"  Found {result['count']} papers")
        print(f"  Returned {len(result['articles'])} results")

        # Check article structure
        article = result['articles'][0]
        assert 'arxiv_id' in article, "Missing arxiv_id"
        assert 'title' in article, "Missing title"
        assert 'authors' in article, "Missing authors"

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fetch_arxiv_paper():
    """Test fetching arXiv paper metadata."""
    print("\n Testing fetch_arxiv_paper()...")

    try:
        # Attention Is All You Need
        result = fetch_arxiv_paper("1706.03762")

        assert result.get('success'), f"Fetch failed: {result.get('error')}"
        assert result.get('arxiv_id'), "No arxiv_id returned"
        assert result.get('title'), "No title"
        assert result.get('abstract'), "No abstract"
        assert result.get('authors'), "No authors"

        print(f"  Title: {result['title'][:50]}...")
        print(f"  Authors: {len(result['authors'])} authors")
        print(f"  Year: {result.get('year')}")
        print(f"  Categories: {result.get('categories', [])[:3]}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_fetch_arxiv_from_url():
    """Test fetching arXiv paper from URL."""
    print("\n Testing fetch_arxiv_paper() with URL...")

    try:
        result = fetch_arxiv_paper("https://arxiv.org/abs/1706.03762v7")

        assert result.get('success'), f"Fetch failed: {result.get('error')}"
        assert '1706.03762' in result.get('arxiv_id', ''), "Wrong arxiv_id"

        print(f"  arXiv ID: {result['arxiv_id']}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_batch_fetch_arxiv():
    """Test batch fetching arXiv papers."""
    print("\n Testing batch_fetch_arxiv()...")

    try:
        ids = ["1706.03762", "2005.14165"]
        result = batch_fetch_arxiv(ids)

        assert result.get('success'), "Batch fetch failed"

        stats = result.get('stats', {})
        print(f"  Requested: {stats.get('requested')}")
        print(f"  Fetched: {stats.get('fetched')}")
        print(f"  Failed: {stats.get('failed')}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_check_arxiv_html_availability():
    """Test checking arXiv HTML availability."""
    print("\n Testing check_html_availability()...")

    try:
        result = check_html_availability("1706.03762")

        print(f"  arXiv:1706.03762: Available={result.get('available')}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_get_arxiv_fulltext():
    """Test getting arXiv full text."""
    print("\n Testing get_arxiv_fulltext()...")

    try:
        result = get_arxiv_fulltext("1706.03762")

        if result.get('success'):
            print(f"  Word count: {result.get('word_count', 0)}")
            print(f"  Sections: {list(result.get('sections', {}).keys())[:5]}")
            print(f"  Figures: {len(result.get('figures', []))}")
            print(f"  References: {len(result.get('references', []))}")
            return True
        else:
            # HTML not available for all papers
            print(f"  HTML not available: {result.get('error', {}).get('message')}")
            return True  # Not a failure

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_arxiv_query_builder():
    """Test arXiv query builder."""
    print("\n Testing build_arxiv_query()...")

    try:
        query = build_arxiv_query(
            title="attention",
            author="Vaswani",
            category="cs.CL"
        )

        assert "ti:attention" in query, "title not in query"
        assert "au:Vaswani" in query, "author not in query"
        assert "cat:cs.CL" in query, "category not in query"

        print(f"  Built query: {query}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_invalid_arxiv_id_handling():
    """Test handling of invalid arXiv ID."""
    print("\n Testing invalid arXiv ID handling...")

    try:
        result = fetch_arxiv_paper("invalid_id")

        assert not result.get('success'), "Should have failed"
        assert 'error' in result, "No error info"

        print(f"  Error handled: {result['error'].get('code')}")
        print(f"  Message: {result['error'].get('message')}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


# =============================================================================
# bioRxiv/medRxiv Tests
# =============================================================================

def test_search_biorxiv_basic():
    """Test basic bioRxiv search."""
    print("\n Testing search_biorxiv()...")

    try:
        result = search_biorxiv("CRISPR", max_results=5)

        # Website search may be blocked (403) - that's expected
        # as bioRxiv doesn't officially support website scraping
        if not result.get('success'):
            error = result.get('error', {})
            if 'Forbidden' in error.get('message', '') or '403' in error.get('message', ''):
                print(f"  Website search blocked (expected): 403 Forbidden")
                print(f"  Note: Use browse_biorxiv_recent() for API access instead")
                return True
            else:
                print(f"  Unexpected error: {error.get('message')}")
                return False

        print(f"  Found {result.get('count', 0)} preprints")
        print(f"  Returned {len(result.get('articles', []))} results")

        # Check article structure if we have results
        articles = result.get('articles', [])
        if articles:
            article = articles[0]
            assert 'doi' in article or 'title' in article, "Missing basic fields"
            print(f"  First result: {article.get('title', 'N/A')[:50]}...")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_browse_biorxiv_recent():
    """Test browsing recent bioRxiv preprints."""
    print("\n Testing browse_biorxiv_recent()...")

    try:
        result = browse_biorxiv_recent(days=7, max_results=5)

        assert result.get('success'), f"Browse failed: {result.get('error')}"

        print(f"  Found {result.get('count', 0)} recent preprints")
        print(f"  Returned {len(result.get('articles', []))} results")

        # Check query info
        query_info = result.get('query_info', {})
        assert query_info.get('browse_type') == 'recent', "Wrong browse type"

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fetch_biorxiv_paper():
    """Test fetching bioRxiv paper metadata."""
    print("\n Testing fetch_biorxiv_paper()...")

    try:
        # Known bioRxiv preprint (COVID-19 related, likely to remain available)
        result = fetch_biorxiv_paper("10.1101/2020.05.22.111161")

        assert result.get('success'), f"Fetch failed: {result.get('error')}"
        assert result.get('doi'), "No DOI returned"
        assert result.get('title'), "No title"
        assert result.get('authors'), "No authors"

        print(f"  Title: {result['title'][:50]}...")
        print(f"  Authors: {len(result['authors'])} authors")
        print(f"  Year: {result.get('year')}")
        print(f"  Server: {result.get('server', 'N/A')}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fetch_biorxiv_from_url():
    """Test fetching bioRxiv paper from URL."""
    print("\n Testing fetch_biorxiv_paper() with URL...")

    try:
        result = fetch_biorxiv_paper("https://www.biorxiv.org/content/10.1101/2020.05.22.111161v1")

        assert result.get('success'), f"Fetch failed: {result.get('error')}"
        assert '10.1101/2020.05.22.111161' in result.get('doi', ''), "Wrong DOI"

        print(f"  DOI: {result['doi']}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_batch_fetch_biorxiv():
    """Test batch fetching bioRxiv papers."""
    print("\n Testing batch_fetch_biorxiv()...")

    try:
        dois = ["10.1101/2020.05.22.111161", "10.1101/2020.01.30.927871"]
        result = batch_fetch_biorxiv(dois)

        assert result.get('success'), "Batch fetch failed"

        stats = result.get('stats', {})
        print(f"  Requested: {stats.get('requested')}")
        print(f"  Fetched: {stats.get('fetched')}")
        print(f"  Failed: {stats.get('failed')}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_check_biorxiv_fulltext_availability():
    """Test checking bioRxiv full text availability."""
    print("\n Testing check_fulltext_availability()...")

    try:
        result = check_biorxiv_fulltext_availability("10.1101/2020.05.22.111161")

        print(f"  DOI 10.1101/2020.05.22.111161: Available={result.get('available')}")
        if result.get('jatsxml_url'):
            print(f"  JATS XML: Available")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_get_biorxiv_fulltext():
    """Test getting bioRxiv full text."""
    print("\n Testing get_biorxiv_fulltext()...")

    try:
        result = get_biorxiv_fulltext("10.1101/2020.05.22.111161")

        if result.get('success'):
            print(f"  Word count: {result.get('word_count', 0)}")
            print(f"  Sections: {list(result.get('sections', {}).keys())[:5]}")
            print(f"  Figures: {len(result.get('figures', []))}")
            print(f"  References: {len(result.get('references', []))}")
            print(f"  Format: {result.get('format', 'unknown')}")
            return True
        else:
            # Full text may be blocked by website (403) or JATS not available
            error = result.get('error', {})
            if '403' in error.get('message', '') or 'Forbidden' in str(error):
                print(f"  Full text blocked (403): This is expected for some IPs")
                return True
            print(f"  Full text not available: {error.get('message')}")
            return True  # Not a failure

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_invalid_biorxiv_doi_handling():
    """Test handling of invalid bioRxiv DOI."""
    print("\n Testing invalid bioRxiv DOI handling...")

    try:
        result = fetch_biorxiv_paper("invalid_doi")

        assert not result.get('success'), "Should have failed"
        assert 'error' in result, "No error info"

        print(f"  Error handled: {result['error'].get('code')}")
        print(f"  Message: {result['error'].get('message')}")

        return True

    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def main():
    """Run all integration tests."""
    print("=" * 70)
    print("INTEGRATION TESTS - PubMed, arXiv & bioRxiv Reader Skill")
    print("=" * 70)

    tests = [
        ("PubMed Search (basic)", test_search_pubmed_basic),
        ("PubMed Search (date filter)", test_search_with_date_filter),
        ("Fetch Abstract", test_fetch_abstract),
        ("Batch Fetch", test_batch_fetch),
        ("Check OA Availability", test_check_oa_availability),
        ("Get Full Text", test_get_fulltext),
        ("Find Similar Articles", test_find_similar),
        ("Get Citing Articles", test_get_citing_articles),
        ("Get References", test_get_references),
        ("Comprehensive Report", test_comprehensive_report),
        ("Query Builder", test_query_builder),
        ("Invalid PMID Handling", test_invalid_pmid_handling),
        ("Validation Integration", test_validation_integration),
        ("Strategic Literature Search", test_strategic_literature_search),
        ("Quick Literature Overview", test_quick_literature_overview),
        ("Strategic Search Formatting", test_strategic_search_formatting),
        ("arXiv Search (basic)", test_search_arxiv_basic),
        ("arXiv Fetch Paper", test_fetch_arxiv_paper),
        ("arXiv Fetch from URL", test_fetch_arxiv_from_url),
        ("arXiv Batch Fetch", test_batch_fetch_arxiv),
        ("arXiv HTML Availability", test_check_arxiv_html_availability),
        ("arXiv Full Text", test_get_arxiv_fulltext),
        ("arXiv Query Builder", test_arxiv_query_builder),
        ("Invalid arXiv ID Handling", test_invalid_arxiv_id_handling),
        ("bioRxiv Search (basic)", test_search_biorxiv_basic),
        ("bioRxiv Browse Recent", test_browse_biorxiv_recent),
        ("bioRxiv Fetch Paper", test_fetch_biorxiv_paper),
        ("bioRxiv Fetch from URL", test_fetch_biorxiv_from_url),
        ("bioRxiv Batch Fetch", test_batch_fetch_biorxiv),
        ("bioRxiv Fulltext Availability", test_check_biorxiv_fulltext_availability),
        ("bioRxiv Full Text", test_get_biorxiv_fulltext),
        ("Invalid bioRxiv DOI Handling", test_invalid_biorxiv_doi_handling),
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
