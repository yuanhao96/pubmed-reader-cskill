# Changelog

All notable changes to PubMed & arXiv Reader skill will be documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

## [1.4.0] - 2026-02-05

### Added

**bioRxiv/medRxiv Support:**
- `search_biorxiv()`: Search bioRxiv/medRxiv preprints via website search
- `browse_biorxiv_recent()`: Browse recent preprints by date via official API
- `fetch_biorxiv_paper()`: Fetch preprint metadata and abstract by DOI
- `batch_fetch_biorxiv()`: Fetch multiple preprints in batch
- `get_biorxiv_fulltext()`: Retrieve and parse full text via JATS XML or HTML
- `check_fulltext_availability()`: Check if full text is available
- `format_biorxiv_citation()`: Format bioRxiv/medRxiv papers in Vancouver-style references
- `validate_biorxiv_doi()`: Validate bioRxiv/medRxiv DOI format (10.1101 and 10.64898 prefixes)
- `validate_biorxiv_doi_param()`: Parameter validator for bioRxiv/medRxiv DOIs
- `extract_biorxiv_doi_from_text()`: Extract bioRxiv/medRxiv DOIs from text

**New Scripts:**
- `scripts/search_biorxiv.py`: bioRxiv/medRxiv website search and API browsing
- `scripts/fetch_biorxiv.py`: bioRxiv/medRxiv paper metadata/abstract retrieval
- `scripts/fetch_biorxiv_fulltext.py`: bioRxiv/medRxiv JATS XML and HTML full text parsing

**New Workflows in SKILL.md:**
- Workflow 11: Search bioRxiv/medRxiv for Preprints
- Workflow 12: Read bioRxiv/medRxiv Paper
- Workflow 13: Get bioRxiv/medRxiv Full Text

**New Tests:**
- 8 bioRxiv integration tests (search, browse, fetch, batch, fulltext, validation)
- Total test count: 32

### Changed

- Renamed skill from "PubMed & arXiv Reader" to "PubMed, arXiv & bioRxiv Reader"
- Updated SKILL.md description to include bioRxiv/medRxiv capabilities
- Updated activation keywords for bioRxiv/medRxiv triggers (biorxiv, medrxiv, 10.1101, etc.)
- Updated architecture overview to include bioRxiv/medRxiv API
- Added bioRxiv/medRxiv rate limit documentation
- Updated helpers.py with bioRxiv DOI validation and citation formatting
- Updated parameter_validator.py with bioRxiv DOI validation

### Data Coverage

**bioRxiv/medRxiv:**
- 200,000+ preprints on bioRxiv
- 100,000+ preprints on medRxiv
- Full text via JATS XML (structured) or HTML
- No authentication required

## [1.3.0] - 2026-02-05

### Added

**arXiv Support:**
- `search_arxiv()`: Search arXiv papers with field prefixes (ti:, au:, abs:, cat:, all:)
- `build_arxiv_query()`: Build advanced arXiv queries with Boolean operators
- `search_arxiv_by_category()`: Search within specific arXiv categories (cs.CL, cs.AI, etc.)
- `fetch_arxiv_paper()`: Fetch paper metadata and abstract by arXiv ID
- `batch_fetch_arxiv()`: Fetch multiple papers in one request
- `get_arxiv_fulltext()`: Retrieve and parse HTML full text from arxiv.org/html/{id}
- `check_html_availability()`: Check if HTML version exists for a paper
- `format_arxiv_citation()`: Format arXiv papers in Vancouver-style references
- `validate_arxiv_id()`: Validate arXiv ID format (modern YYMM.NNNNN and legacy)
- `validate_arxiv_id_param()`: Parameter validator for arXiv IDs
- `extract_arxiv_id_from_text()`: Extract arXiv IDs from text

**New Scripts:**
- `scripts/search_arxiv.py`: arXiv search via Atom API
- `scripts/fetch_arxiv.py`: arXiv paper metadata/abstract retrieval
- `scripts/fetch_arxiv_fulltext.py`: arXiv HTML full text parsing

**New Workflows in SKILL.md:**
- Workflow 8: Search arXiv for Papers
- Workflow 9: Read arXiv Paper
- Workflow 10: Get arXiv Full Text (HTML)

**New Tests:**
- 8 arXiv integration tests (search, fetch, batch, fulltext, query builder, validation)
- Total test count: 24

### Changed

- Renamed skill from "PubMed Reader" to "PubMed & arXiv Reader"
- Updated SKILL.md description to include arXiv capabilities
- Updated activation keywords for arXiv triggers (arxiv, preprint, cs.CL, cs.AI, etc.)
- Updated architecture overview to include arXiv API
- Added arXiv rate limit documentation
- Updated helpers.py with arXiv ID validation and citation formatting
- Updated parameter_validator.py with arXiv ID validation

### Data Coverage

**arXiv:**
- 2+ million preprints across all categories
- Physics, Mathematics, Computer Science, Quantitative Biology, and more
- HTML full text for LaTeXML-processed papers
- No authentication required

## [1.0.0] - 2026-02-04

### Added

**Core Functionality:**
- `search_pubmed()`: Search PubMed with complex queries, date filters, sorting
- `fetch_abstract()`: Retrieve article abstracts and full metadata
- `batch_fetch()`: Efficiently fetch multiple articles
- `get_fulltext()`: Retrieve full text for Open Access articles
- `find_similar_articles()`: Find related papers using NCBI algorithms
- `get_citing_articles()`: Discover papers that cite a given article
- `get_references()`: Get papers cited by an article
- `comprehensive_article_report()`: All-in-one comprehensive analysis

**Search Features:**
- Natural language query support
- Date range filtering (by year, date range, relative days)
- Field-specific searching (title, author, journal, MeSH)
- Publication type filtering (reviews, clinical trials, etc.)
- Result sorting (relevance, date, author, journal)
- Advanced query builder with Boolean operators

**Data Sources:**
- NCBI E-utilities API for PubMed access
- BioC PMC API for full text retrieval
- PMC ID Converter API for identifier translation

**Analysis Capabilities:**
- Citation metrics (total, per year, recent velocity)
- Citation network exploration (citing, cited by)
- Similar article discovery with similarity scores
- Literature overview for topics
- Article comparison

**Utilities:**
- File-based cache with configurable TTL
- Adaptive rate limiter respecting NCBI limits
- Comprehensive validation system
- Author and citation formatting
- Date handling and extraction

### Data Coverage

**Databases:**
- PubMed: 35+ million citations
- PMC Open Access: ~3 million full-text articles

**Rate Limits:**
- Without API key: 3 requests/second
- With API key: 10 requests/second

### Known Limitations

- Full text only available for PMC Open Access articles (~3M of 35M+)
- Citation data may lag behind actual publications
- Rate limits apply to all E-utilities usage
- No access to paywalled journal content (by design)

### Test Coverage

- 13 integration tests
- 8 helper utility tests
- All tests passing

### Planned for v2.0

- Batch search across multiple queries
- Export to citation managers (BibTeX, RIS)
- Semantic similarity using embeddings
- Automatic literature review generation
- Integration with reference management tools

## [1.1.0] - 2026-02-04

### Added

**Strategic Literature Search (Reviews First Workflow):**
- `strategic_literature_search()`: 4-phase strategic search like real biologists do
  - Phase 1: Find review articles for domain overview
  - Phase 2: Extract key themes from reviews (MeSH terms, keywords)
  - Phase 3: Find primary research articles organized by theme
  - Phase 4: Identify seminal/highly-cited foundational papers
- `quick_literature_overview()`: Fast review-only search for quick domain understanding
- `deep_literature_analysis()`: Comprehensive search with focus areas
- `format_strategic_search_results()`: Beautiful formatted output

**New Features:**
- Automatic theme extraction from review articles
- Review article scoring and ranking (recency, journal quality, article type)
- Seminal work identification (papers with >100 citations)
- Reading order generation with priorities (⭐ high, ○ medium)
- Executive summary generation

**New Workflow:**
- Workflow 6 in SKILL.md: Strategic Literature Search
- Example usage patterns for domain exploration

### Changed

- Updated SKILL.md with new workflow documentation
- Added strategic search keywords to activation triggers
- Expanded "When to Use" section for domain exploration queries

### Why This Update

This implements a biologist's approach to literature exploration:
1. Start with reviews to understand the landscape
2. Extract themes to guide further reading
3. Find primary research by theme of interest
4. Identify foundational papers for deep understanding
5. Get a suggested reading order

## [1.2.0] - 2026-02-04

### Added

**Strictly Formatted References (NLM/Vancouver Style):**
- Mandatory NLM/Vancouver-style reference formatting for all article citations in output
- New "Mandatory Reference Formatting" section in SKILL.md with rules and templates
- Enhanced `format_citation()` in helpers.py with DOI and PMC ID support
- New `format_authors_apa()` helper for APA-style author formatting
- New `format_reference_list()` helper for batch formatting multiple articles

### Changed

- Updated all output format examples in SKILL.md to use strict Vancouver-style references
- Updated workflow examples (Search, Read Abstract, Citations, Similar Articles, Comprehensive Report, Strategic Literature Search) with formatted references
- Improved `format_citation()` to produce proper NLM/Vancouver format with DOI, PMID, and PMC

### Why This Update

Biomedical literature should always be cited in proper NLM/Vancouver format — the standard used by PubMed, MEDLINE, and most biomedical journals. This ensures consistent, professional, and verifiable references in all skill output.

## [1.5.0] - 2026-02-17

### Changed

**Skill Architecture Refactor:**
- Split monolithic `SKILL.md` into 4 focused, specialized skill files in `skills/` directory
- `SKILL-pubmed-lookup.md`: Simple PubMed operations — search, read abstract, fetch full text, find similar/citing articles
- `SKILL-pubmed-deep.md`: Strategic literature search and comprehensive per-article reports
- `SKILL-arxiv.md`: All arXiv operations — search, read abstracts, fetch HTML full text
- `SKILL-biorxiv.md`: All bioRxiv/medRxiv operations — search, read abstracts, fetch JATS/HTML full text
- Each skill now has explicit `Do NOT use for` guidance directing to sibling skills for cleaner routing
- Archived original `SKILL.md` as `SKILL.md.archive`

### Why This Update

The original single `SKILL.md` grew to cover PubMed, arXiv, and bioRxiv/medRxiv in one file, making it harder for Claude to select the right behavior for a given query. Splitting into domain-specific skills improves activation precision, reduces context bloat per invocation, and makes each skill's scope immediately clear.

## [Unreleased]

### Planned

- Improve full text extraction for complex articles
- Add visualization of citation networks
- Support for non-English abstracts
- Export to citation managers (BibTeX, RIS)
