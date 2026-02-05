# Changelog

All notable changes to PubMed Reader skill will be documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

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

## [Unreleased]

### Planned

- Add support for preprint servers (bioRxiv, medRxiv)
- Improve full text extraction for complex articles
- Add visualization of citation networks
- Support for non-English abstracts
