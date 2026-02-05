---
name: pubmed-reader-cskill
description: PubMed article reader and literature explorer for biologists - search articles, read abstracts and full text, follow citations, find similar papers, and extract key information from biomedical literature using NCBI E-utilities and BioC PMC APIs
---

# PubMed Reader - Biomedical Literature Explorer

A comprehensive Claude Code skill for reading PubMed articles like a real biologist would - browsing pages, extracting information, following citations, and discovering related research through the biomedical literature network.

## When to Use This Skill

This skill should be activated when the user:

- **Explores a research domain**: "Give me an overview of type 1 diabetes", "Literature review on CRISPR", "I want to understand cancer immunotherapy"
- **Searches for literature**: "Search PubMed for CRISPR", "Find papers about cancer immunotherapy", "Literature review on Alzheimer's biomarkers"
- **Wants strategic literature search**: "Start with review articles on...", "Find reviews first then research papers", "What are the key papers on..."
- **Reads specific articles**: "Read PMID 12345678", "Get abstract for this paper", "Show me the full text"
- **Explores citations**: "What papers cite this?", "Find citing articles for PMID X", "Show references"
- **Finds related work**: "Find similar papers", "Related articles to this study", "More papers like this"
- **Mentions PMIDs or PMCIDs**: Any query containing "PMID", "PMC", or article identifiers

### Keywords That Trigger Activation

**Strategic Search Keywords**: literature overview, domain overview, understand the field, review articles first, seminal works, foundational papers, key papers, reading order, explore the literature

**Search Keywords**: pubmed, search, find articles, papers, literature, biomedical, medical literature, scientific papers, research articles

**Action Keywords**: read, get, fetch, abstract, full text, summary, extract, download

**Exploration Keywords**: similar articles, related papers, citations, cited by, references, citing articles

**Identifier Keywords**: PMID, PMC, PubMed ID, article ID, DOI

## How It Works

### Architecture Overview

This skill uses two complementary APIs from NCBI:

1. **E-utilities API** (https://eutils.ncbi.nlm.nih.gov/entrez/eutils/)
   - ESearch: Search PubMed with complex queries
   - EFetch: Retrieve article abstracts and metadata
   - ESummary: Get document summaries
   - ELink: Find related/citing articles
   - EInfo: Database information and field definitions

2. **BioC PMC API** (https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi)
   - Full text retrieval for ~3 million Open Access articles
   - Structured XML/JSON with sections, paragraphs, figures

### Data Flow

```
User Query
    │
    ▼
┌─────────────────┐
│  Query Parser   │ ──▶ Detect intent (search/read/explore)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  E-utilities    │ ──▶ ESearch, EFetch, ELink, ESummary
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  BioC API       │ ──▶ Full text for Open Access articles
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Response       │ ──▶ Formatted results for user
│  Formatter      │
└─────────────────┘
```

## Data Source: NCBI E-utilities and BioC API

### E-utilities Overview

The Entrez Programming Utilities (E-utilities) are nine server-side programs providing stable access to NCBI's Entrez databases, including PubMed with over 35 million citations.

**Base URL**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

### Available E-utilities

| Utility | Endpoint | Purpose |
|---------|----------|---------|
| **ESearch** | `esearch.fcgi` | Search database, return UIDs |
| **EFetch** | `efetch.fcgi` | Retrieve full records |
| **ESummary** | `esummary.fcgi` | Get document summaries |
| **ELink** | `elink.fcgi` | Find related/linked records |
| **EInfo** | `einfo.fcgi` | Database statistics and fields |
| **EPost** | `epost.fcgi` | Upload UID lists to History |
| **ESpell** | `espell.fcgi` | Spelling suggestions |
| **ECitMatch** | `ecitmatch.cgi` | Match citations to PMIDs |
| **EGQuery** | `egquery.fcgi` | Search all databases |

### BioC PMC API

Provides full-text access to PubMed Central Open Access articles in structured format.

**Endpoint Pattern**:
```
https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_[format]/[ID]/[encoding]
```

**Parameters**:
- `format`: `xml` or `json`
- `ID`: PMID (e.g., 17299597) or PMC ID (e.g., PMC1790863)
- `encoding`: `unicode` or `ascii`

### Rate Limits and API Key

| Access Level | Rate Limit | Requirements |
|--------------|------------|--------------|
| Without API Key | 3 requests/second | None |
| With API Key | 10 requests/second | Free NCBI account |
| Enhanced | Custom | Contact NCBI |

**Get your API key**: https://www.ncbi.nlm.nih.gov/account/settings/

## Workflows

### Workflow 1: Search PubMed for Articles

**User says**: "Search PubMed for CRISPR gene editing 2024"

**Process**:
1. Parse search query and extract terms
2. Build ESearch URL with parameters
3. Execute search with date filters
4. Fetch summaries for top results
5. Format and present results

**Script**: `scripts/search_pubmed.py`

**Example Query**:
```
esearch.fcgi?db=pubmed&term=CRISPR+gene+editing&mindate=2024/01/01&maxdate=2024/12/31&retmax=20&sort=relevance
```

**Output Format**:
```
## PubMed Search Results: "CRISPR gene editing 2024"

Found 1,234 articles. Showing top 20:

1. **CRISPR-Cas9 advances in cancer therapy** (2024)
   Authors: Smith J, Jones M, et al.
   Journal: Nature Medicine
   PMID: 38123456

2. **Novel CRISPR delivery systems for in vivo editing** (2024)
   Authors: Chen L, Wang X, et al.
   Journal: Cell
   PMID: 38234567

[...]
```

### Workflow 2: Read Article Abstract

**User says**: "Read abstract for PMID 38123456"

**Process**:
1. Validate PMID format
2. Fetch abstract via EFetch
3. Parse XML response
4. Extract title, authors, abstract, keywords, MeSH terms
5. Format for reading

**Script**: `scripts/fetch_article.py`

**Example Query**:
```
efetch.fcgi?db=pubmed&id=38123456&rettype=abstract&retmode=xml
```

**Output Format**:
```
## Article: PMID 38123456

**Title**: CRISPR-Cas9 advances in cancer therapy

**Authors**: Smith J, Jones M, Wilson K, et al.

**Journal**: Nature Medicine, 2024 Mar;30(3):456-467

**DOI**: 10.1038/s41591-024-12345-6

**Abstract**:
Recent advances in CRISPR-Cas9 technology have revolutionized
cancer therapy approaches. This review examines [...]

**Keywords**: CRISPR, gene editing, cancer therapy, immunotherapy

**MeSH Terms**: CRISPR-Cas Systems, Neoplasms/therapy, Gene Editing
```

### Workflow 3: Get Full Text (Open Access)

**User says**: "Get full text of PMID 17299597"

**Process**:
1. Check if article is in PMC Open Access subset
2. Convert PMID to PMC ID if needed
3. Fetch full text via BioC API
4. Parse sections (Introduction, Methods, Results, Discussion)
5. Present structured full text

**Script**: `scripts/fetch_fulltext.py`

**Example Query**:
```
https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/17299597/unicode
```

**Output Format**:
```
## Full Text: PMID 17299597 (PMC1790863)

**Title**: [Article Title]

### Abstract
[Abstract text...]

### Introduction
[Introduction paragraphs...]

### Methods
[Methods section...]

### Results
[Results with figures/tables references...]

### Discussion
[Discussion paragraphs...]

### References
[Reference list...]
```

### Workflow 4: Find Similar Articles

**User says**: "Find similar articles to PMID 20210808"

**Process**:
1. Use ELink with `neighbor_score` command
2. Get similarity scores for related articles
3. Fetch summaries for top matches
4. Present ranked by relevance

**Script**: `scripts/find_similar.py`

**Example Query**:
```
elink.fcgi?dbfrom=pubmed&db=pubmed&id=20210808&cmd=neighbor_score&linkname=pubmed_pubmed
```

**Output Format**:
```
## Similar Articles to PMID 20210808

Based on shared MeSH terms, citations, and content similarity:

1. **[Title]** (Score: 95/100)
   PMID: 21234567
   Journal: Cell, 2021

2. **[Title]** (Score: 89/100)
   PMID: 20345678
   Journal: Nature, 2020

[...]
```

### Workflow 5: Find Citing Articles

**User says**: "What papers cite PMID 17299597?"

**Process**:
1. Use ELink with `pubmed_pubmed_citedin` linkname
2. Retrieve all PMIDs citing the source article
3. Fetch summaries and publication dates
4. Sort by date and present

**Script**: `scripts/find_citations.py`

**Example Query**:
```
elink.fcgi?dbfrom=pubmed&db=pubmed&id=17299597&linkname=pubmed_pubmed_citedin
```

**Output Format**:
```
## Articles Citing PMID 17299597

This article has been cited 234 times:

### 2024 (15 citations)
1. **[Title]** - Smith et al., Nature (PMID: 38123456)
2. **[Title]** - Jones et al., Cell (PMID: 38234567)

### 2023 (42 citations)
[...]
```

### Workflow 6: Strategic Literature Search (Reviews First)

**User says**: "Give me a literature overview of type 1 diabetes" or "Literature review on CRISPR" or "I want to understand the field of cancer immunotherapy"

**Process** (How a Real Biologist Explores Literature):
1. **Phase 1 - Domain Overview**: Search for review articles first (systematic reviews, meta-analyses)
2. **Phase 2 - Theme Extraction**: Extract key themes, MeSH terms, and concepts from reviews
3. **Phase 3 - Primary Research**: Find research articles organized by identified themes
4. **Phase 4 - Seminal Works**: Identify highly-cited foundational papers (>100 citations)
5. **Generate Reading Order**: Suggest optimal sequence: reviews → seminal → research by theme

**Script**: `scripts/strategic_literature_search.py`

**Example Query**:
```
strategic_literature_search("type 1 diabetes pathogenesis", max_reviews=5)
```

**Output Format**:
```
# Strategic Literature Search: type 1 diabetes pathogenesis

## Executive Summary
Literature search on 'type 1 diabetes pathogenesis' identified 28 key articles.
Start with 'Pathogenesis of Type 1 Diabetes...' (Genes, 2022) for domain overview.
Key themes: autoimmunity, beta cells, genetics. Most cited foundational work:
'Type 1 Diabetes Mellitus' with 1,200 citations.

## Phase 1: Review Articles (Start Here)
*Read these first for domain overview*

### 1. Pathogenesis of Type 1 Diabetes: Established Facts and New Insights
**Authors**: Zajec A et al.
**Journal**: Genes, 2022
**PMID**: 35456512
**Key themes**: autoimmunity, beta-cell destruction, environmental factors

### 2. Type 1 Diabetes Mellitus
**Authors**: Katsarou A et al.
**Journal**: Nature Reviews Disease Primers, 2017
**PMID**: 28358037
...

## Phase 2: Key Themes Identified
- **autoimmunity** (mentioned in 4 reviews)
- **beta-cell** (mentioned in 3 reviews)
- **genetics** (mentioned in 3 reviews)
...

## Phase 3: Primary Research by Theme

### Theme: Autoimmunity
1. **T-cell mediated destruction mechanisms...** (234 citations)
   Journal of Immunology, 2023 | PMID: 37123456

### Theme: Beta-cell
1. **Beta-cell stress and dysfunction in T1D...** (156 citations)
   Diabetes, 2022 | PMID: 36234567
...

## Phase 4: Seminal Works (Foundational Papers)
*Highly-cited papers that shaped the field*

1. **Staging presymptomatic type 1 diabetes** (2,100 citations - landmark)
   Diabetes Care, 2015 | PMID: 26404926

2. **Type 1 Diabetes Mellitus** (1,200 citations - highly influential)
   Nature Reviews Disease Primers, 2017 | PMID: 28358037
...

## Suggested Reading Order

**Start with Overview**
⭐ 1. [review] PMID 35456512 - Pathogenesis of Type 1 Diabetes...
   *Start with domain overview*
○ 2. [review] PMID 28358037 - Type 1 Diabetes Mellitus...
   *Additional perspective*

**Foundational Papers**
⭐ 3. [seminal] PMID 26404926 - Staging presymptomatic type 1...
   *Foundational paper (2,100 citations)*

**Deep Dive by Theme**
○ 4. [research] PMID 37123456 - T-cell mediated destruction...
   *Primary research on autoimmunity*
```

**Key Features**:
- Mimics how experienced researchers explore unfamiliar domains
- Reviews first → establishes context before diving into details
- Automatic theme extraction from MeSH terms and keywords
- Identifies seminal works for foundational understanding
- Generates optimal reading order with priorities

---

### Workflow 7: Comprehensive Article Report

**User says**: "Give me a complete overview of this paper PMID 17299597"

**Process**:
1. Fetch full article metadata (EFetch)
2. Get abstract and keywords
3. Find similar articles (ELink neighbor)
4. Find citing articles (ELink citedin)
5. Attempt full text retrieval (BioC API)
6. Compile comprehensive report

**Script**: `scripts/comprehensive_report.py`

**Output Format**:
```
## Comprehensive Report: PMID 17299597

### Article Information
- **Title**: [Title]
- **Authors**: [Author list]
- **Journal**: [Journal], [Year]
- **DOI**: [DOI]
- **Citations**: 234 (as of [date])

### Abstract
[Full abstract...]

### Full Text Available
[Yes/No - if yes, summary of sections]

### Similar Articles (Top 5)
1. [Similar article 1]
2. [Similar article 2]
[...]

### Recent Citations (Top 10)
1. [Citing article 1]
2. [Citing article 2]
[...]

### Key Information Extracted
- **Main Findings**: [Extracted from abstract]
- **Methods Used**: [Extracted from methods if available]
- **Keywords/MeSH**: [List]
```

## Available Scripts

### Core Scripts

#### `scripts/search_pubmed.py`
Search PubMed with complex queries including date ranges, field filters, and sorting.

```python
from search_pubmed import search_pubmed

results = search_pubmed(
    query="CRISPR cancer therapy",
    max_results=20,
    min_date="2023/01/01",
    sort="relevance"
)
```

**Functions**:
- `search_pubmed(query, max_results, min_date, max_date, sort)` - Main search function
- `build_search_query(terms, fields)` - Build advanced queries with field tags
- `parse_search_results(xml_response)` - Parse ESearch XML response

#### `scripts/fetch_article.py`
Retrieve article abstracts, metadata, and full bibliographic information.

```python
from fetch_article import fetch_abstract, fetch_metadata

abstract = fetch_abstract(pmid="38123456")
metadata = fetch_metadata(pmid="38123456", include_mesh=True)
```

**Functions**:
- `fetch_abstract(pmid)` - Get abstract text
- `fetch_metadata(pmid, include_mesh, include_keywords)` - Get full metadata
- `batch_fetch(pmids, batch_size)` - Fetch multiple articles efficiently

#### `scripts/fetch_fulltext.py`
Retrieve full text for PubMed Central Open Access articles.

```python
from fetch_fulltext import get_fulltext, check_oa_availability

is_available = check_oa_availability(pmid="17299597")
if is_available:
    fulltext = get_fulltext(pmid="17299597", format="json")
```

**Functions**:
- `check_oa_availability(pmid)` - Check if full text available in PMC OA
- `get_fulltext(pmid, format)` - Retrieve full text in XML or JSON
- `extract_sections(bioc_data)` - Parse into structured sections
- `pmid_to_pmcid(pmid)` - Convert between identifiers

#### `scripts/find_similar.py`
Find related articles using NCBI's similarity algorithms.

```python
from find_similar import find_similar_articles

similar = find_similar_articles(
    pmid="20210808",
    max_results=10,
    include_scores=True
)
```

**Functions**:
- `find_similar_articles(pmid, max_results, include_scores)` - Get similar papers
- `find_by_mesh_terms(pmid, max_results)` - Find papers sharing MeSH terms
- `find_by_author(pmid)` - Find other papers by same authors

#### `scripts/find_citations.py`
Discover articles that cite a given paper.

```python
from find_citations import get_citing_articles, get_references

citing = get_citing_articles(pmid="17299597", sort_by_date=True)
refs = get_references(pmid="17299597")
```

**Functions**:
- `get_citing_articles(pmid, sort_by_date, max_results)` - Papers citing this one
- `get_references(pmid)` - References cited by this paper
- `get_citation_network(pmid, depth)` - Build citation graph

#### `scripts/comprehensive_report.py`
Generate complete literature analysis combining all data sources.

```python
from comprehensive_report import comprehensive_article_report

report = comprehensive_article_report(
    pmid="17299597",
    include_fulltext=True,
    max_similar=5,
    max_citations=10
)
```

**Functions**:
- `comprehensive_article_report(pmid, **options)` - Full report for one article
- `literature_overview(query, max_articles)` - Overview of a research topic
- `compare_articles(pmids)` - Compare multiple articles

#### `scripts/strategic_literature_search.py`
Strategic literature search: reviews first, then research articles - like a real biologist.

```python
from strategic_literature_search import strategic_literature_search

# Full strategic search
result = strategic_literature_search(
    topic="type 1 diabetes pathogenesis",
    max_reviews=5,
    max_research_per_review=3,
    years_back=5,
    include_seminal_works=True
)

# Quick overview (reviews only)
from strategic_literature_search import quick_literature_overview
quick = quick_literature_overview("CRISPR gene therapy", max_reviews=3)

# Deep analysis with focus areas
from strategic_literature_search import deep_literature_analysis
deep = deep_literature_analysis(
    "cancer immunotherapy",
    focus_areas=["checkpoint inhibitors", "CAR-T cells"]
)
```

**Functions**:
- `strategic_literature_search(topic, **options)` - Full 4-phase strategic search
- `quick_literature_overview(topic, max_reviews)` - Quick review-only search
- `deep_literature_analysis(topic, focus_areas)` - Comprehensive analysis
- `format_strategic_search_results(result)` - Format results for display

**Search Strategy**:
1. Phase 1: Find review articles for domain overview
2. Phase 2: Extract themes from reviews (MeSH terms, keywords)
3. Phase 3: Find primary research articles by theme
4. Phase 4: Identify seminal/highly-cited foundational papers
5. Generate optimal reading order

### Utility Scripts

#### `scripts/utils/helpers.py`
Common utilities for date handling, ID validation, and formatting.

**Functions**:
- `validate_pmid(pmid)` - Validate PMID format
- `validate_pmcid(pmcid)` - Validate PMC ID format
- `format_authors(author_list)` - Format author names
- `format_date(date_dict)` - Format publication dates
- `extract_year(date_string)` - Extract year from various formats

#### `scripts/utils/cache_manager.py`
Intelligent caching for API responses.

**Functions**:
- `cache_response(key, data, ttl)` - Cache API response
- `get_cached(key)` - Retrieve from cache
- `clear_cache(older_than)` - Clean old entries

#### `scripts/utils/rate_limiter.py`
Respect NCBI rate limits.

**Functions**:
- `RateLimiter(requests_per_second)` - Rate limiter class
- `throttle()` - Wait if needed to stay within limits

### Validators

#### `scripts/utils/validators/parameter_validator.py`
Validate user inputs.

#### `scripts/utils/validators/response_validator.py`
Validate API responses and data quality.

## Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `PMID not found` | Invalid or nonexistent PMID | Verify PMID is correct |
| `Rate limit exceeded` | Too many requests | Wait and retry, or use API key |
| `Full text not available` | Article not in PMC OA | Access only abstract via EFetch |
| `Network timeout` | Server slow/unreachable | Retry with exponential backoff |
| `Invalid search query` | Syntax error in query | Check query syntax, escape special chars |

### Error Response Format

All functions return errors in consistent format:

```python
{
    "success": False,
    "error": {
        "code": "PMID_NOT_FOUND",
        "message": "PMID 99999999 does not exist in PubMed",
        "suggestion": "Verify the PMID or search by title/author"
    }
}
```

## Mandatory Validations

Before making API calls, the following validations are performed:

1. **PMID Validation**: Must be 1-8 digit number
2. **PMC ID Validation**: Must match pattern `PMC\d+`
3. **Query Validation**: Check for injection risks, validate field tags
4. **Date Validation**: Ensure valid date format (YYYY/MM/DD)
5. **Parameter Bounds**: Enforce max_results limits

## Performance and Caching

### Caching Strategy

| Data Type | Cache TTL | Rationale |
|-----------|-----------|-----------|
| Article metadata | 30 days | Rarely changes |
| Search results | 1 hour | New articles published daily |
| Citation counts | 7 days | Updates less frequently |
| Full text | 30 days | Static once published |

### Cache Location

Cache files stored in: `data/cache/`

### Rate Limiting

Default configuration respects NCBI limits:
- Without API key: 3 requests/second
- With API key: 10 requests/second

Configure via environment variable:
```bash
export NCBI_API_KEY="your_api_key_here"
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NCBI_API_KEY` | None | NCBI API key for higher rate limits |
| `NCBI_EMAIL` | None | Required for production use |
| `NCBI_TOOL` | `pubmed-reader` | Tool identifier |
| `PUBMED_CACHE_DIR` | `data/cache` | Cache directory |
| `PUBMED_CACHE_TTL` | `86400` | Default cache TTL in seconds |

### Configuration File

Optional `config.json` in `assets/`:

```json
{
    "api_key": null,
    "email": "your.email@example.com",
    "tool_name": "pubmed-reader",
    "cache": {
        "enabled": true,
        "directory": "data/cache",
        "default_ttl": 86400
    },
    "rate_limit": {
        "requests_per_second": 3
    },
    "defaults": {
        "max_search_results": 20,
        "sort_order": "relevance"
    }
}
```

## Usage Examples

### Example 1: Strategic Literature Search (Reviews First)

```
User: "I want to understand the field of type 1 diabetes - give me a literature overview"

Response:
# Strategic Literature Search: type 1 diabetes

## Executive Summary
Literature search on 'type 1 diabetes' identified 32 key articles.
Start with 'Pathogenesis of Type 1 Diabetes: Established Facts and New Insights'
(Genes, 2022) for domain overview. Key themes: autoimmunity, beta-cell, genetics.
Most cited foundational work: 'Type 1 Diabetes Mellitus' with 1,892 citations.

## Search Statistics
- **Total articles identified**: 32
- **Review articles**: 5
- **Research articles**: 15
- **Seminal works**: 12
- **Key themes identified**: 8

## Phase 1: Review Articles (Start Here)
*Read these first for domain overview*

### 1. Pathogenesis of Type 1 Diabetes: Established Facts and New Insights
**Authors**: Zajec A et al.
**Journal**: Genes, 2022
**PMID**: 35456512
**Key themes**: autoimmunity, beta-cell destruction, environmental factors, epigenetics

### 2. Type 1 Diabetes Mellitus
**Authors**: Katsarou A et al.
**Journal**: Nature Reviews Disease Primers, 2017
**PMID**: 28358037
**Key themes**: epidemiology, pathophysiology, treatment advances

### 3. Type 1 diabetes mellitus as a disease of the β-cell
**Authors**: Roep BO et al.
**Journal**: Nature Reviews Endocrinology, 2021
**PMID**: 33293704
**Key themes**: beta-cell dysfunction, immune interaction

## Phase 2: Key Themes Identified
- **autoimmunity** (mentioned in 5 reviews)
- **beta-cell** (mentioned in 4 reviews)
- **genetics** (mentioned in 3 reviews)
- **immunotherapy** (mentioned in 3 reviews)
- **prevention** (mentioned in 2 reviews)

## Phase 3: Primary Research by Theme

### Theme: Autoimmunity
1. **T-cell mediated beta-cell destruction in NOD mice** (456 citations)
   Journal of Immunology, 2021 | PMID: 34123456
2. **Regulatory T cells in type 1 diabetes** (234 citations)
   Diabetes, 2022 | PMID: 35234567

### Theme: Beta-cell
1. **Beta-cell stress responses in T1D pathogenesis** (312 citations)
   Cell Metabolism, 2023 | PMID: 36345678

## Phase 4: Seminal Works (Foundational Papers)
1. **Staging presymptomatic type 1 diabetes** (2,100 citations - landmark)
   Diabetes Care, 2015 | PMID: 26404926
2. **Type 1 Diabetes Mellitus** (1,892 citations - highly influential)
   Nature Reviews Disease Primers, 2017 | PMID: 28358037
3. **An Anti-CD3 Antibody, Teplizumab, in Relatives at Risk** (890 citations)
   NEJM, 2019 | PMID: 31180194

## Suggested Reading Order

**Start with Overview**
⭐ 1. [review] PMID 35456512 - Pathogenesis of Type 1 Diabetes...
   *Start with domain overview*
○ 2. [review] PMID 28358037 - Type 1 Diabetes Mellitus
   *Comprehensive disease primer*

**Foundational Papers**
⭐ 3. [seminal] PMID 26404926 - Staging presymptomatic type 1 diabetes
   *Foundational paper (2,100 citations) - defines disease stages*
⭐ 4. [seminal] PMID 31180194 - Teplizumab trial
   *Landmark prevention trial*

**Deep Dive by Theme**
○ 5. [research] PMID 34123456 - T-cell mediated destruction
   *Primary research on autoimmunity*
○ 6. [research] PMID 36345678 - Beta-cell stress responses
   *Primary research on beta-cell*
```

### Example 2: Basic Literature Search

```
User: "Search PubMed for mRNA vaccine development"

Response:
## PubMed Search: "mRNA vaccine development"

Found 3,456 articles. Showing top 10:

1. **mRNA vaccines: From research to clinical development**
   Authors: Pardi N, Hogan MJ, et al.
   Journal: Nature Reviews Drug Discovery, 2023
   PMID: 36123456
   Cited by: 892 articles

2. **Advances in mRNA-LNP vaccine technology for infectious diseases**
   Authors: Verbeke R, Lentacker I, et al.
   Journal: Molecular Therapy, 2024
   PMID: 37234567
   Cited by: 156 articles

[...]
```

### Example 2: Read Specific Article

```
User: "Read PMID 32756549"

Response:
## Article: PMID 32756549

**Title**: Safety and immunogenicity of two RNA-based COVID-19 vaccine candidates

**Authors**: Walsh EE, Frenck RW Jr, Falsey AR, et al.

**Journal**: New England Journal of Medicine, 2020 Oct 14;383(25):2439-2450

**DOI**: 10.1056/NEJMoa2027906

**Abstract**:
BACKGROUND: BNT162b1 and BNT162b2 are lipid nanoparticle-formulated,
nucleoside-modified RNA vaccines that encode the SARS-CoV-2 spike protein...

[Full abstract continues...]

**Keywords**: COVID-19 vaccines, mRNA vaccines, SARS-CoV-2, immunogenicity

**Publication Types**: Clinical Trial, Phase 1; Clinical Trial, Phase 2
```

### Example 3: Explore Citations

```
User: "What papers cite PMID 32756549?"

Response:
## Citations for PMID 32756549

This landmark COVID-19 vaccine study has been cited 4,521 times.

### Most Recent (2024)
1. **Long-term efficacy of mRNA COVID-19 vaccines: A systematic review**
   Chen X, et al. Lancet Infectious Diseases (PMID: 38456789)

2. **Comparative immunogenicity of mRNA and protein-based vaccines**
   Williams K, et al. Nature Medicine (PMID: 38345678)

### Most Cited
1. **Safety and Efficacy of the BNT162b2 mRNA COVID-19 Vaccine**
   Polack FP, et al. NEJM, 2020 (PMID: 33301246)
   Cited 12,456 times

[...]
```

### Example 4: Find Similar Research

```
User: "Find similar articles to PMID 32756549"

Response:
## Similar Articles to PMID 32756549

Based on shared subjects, citations, and content:

1. **An mRNA Vaccine against SARS-CoV-2 — Preliminary Report** (Score: 98)
   Jackson LA, et al. NEJM, 2020
   PMID: 32663912
   Similarity: Same vaccine platform, similar trial design

2. **Phase I/II study of COVID-19 RNA vaccine BNT162b1** (Score: 95)
   Mulligan MJ, et al. Nature, 2020
   PMID: 32785213
   Similarity: Same vaccine candidate, different population

[...]
```

### Example 5: Comprehensive Analysis

```
User: "Give me a complete overview of PMID 32756549"

Response:
## Comprehensive Report: PMID 32756549

### Article Information
- **Title**: Safety and immunogenicity of two RNA-based COVID-19 vaccine candidates
- **Authors**: Walsh EE, et al. (25 authors)
- **Journal**: New England Journal of Medicine
- **Published**: October 14, 2020
- **DOI**: 10.1056/NEJMoa2027906
- **Total Citations**: 4,521

### Impact Assessment
- **Citation Velocity**: 1,506 citations/year
- **Altmetric Score**: 24,567 (Top 0.01% of all research)
- **Most Cited By**: Vaccine development studies

### Abstract
[Full abstract...]

### Related Research
- Similar articles: 45 closely related papers
- By same authors: 23 papers on mRNA vaccines
- Citing articles: 4,521 papers

### Key Contributions
1. First phase 1/2 data for BNT162b2 vaccine
2. Established dose selection for phase 3
3. Demonstrated favorable safety profile

### Full Text Access
- PMC Available: Yes (PMC7889054)
- Access: Open Access
```

## Advanced Features

### Building Complex Queries

Use PubMed field tags for precise searches:

```
User: "Search for CRISPR articles in Nature from 2023 by Zhang lab"

Query built:
CRISPR[Title] AND Nature[Journal] AND 2023[Publication Date] AND Zhang F[Author]
```

**Available Field Tags**:
- `[Title]`, `[Title/Abstract]` - Title and abstract search
- `[Author]` - Author name
- `[Journal]` - Journal name
- `[MeSH Terms]` - Medical Subject Headings
- `[Publication Date]` - Date filters
- `[Article Type]` - Reviews, Clinical Trials, etc.

### Boolean Operators

Support for AND, OR, NOT:
- "CRISPR AND cancer" - Both terms required
- "CRISPR OR TALEN" - Either term
- "CRISPR NOT review" - Exclude reviews

### Date Ranges

- Last N days: "CRISPR papers from last 30 days"
- Specific year: "CRISPR papers from 2024"
- Date range: "CRISPR papers 2020-2023"

## Troubleshooting

### Issue: No results returned

**Possible causes**:
1. Query too specific - Try broader terms
2. Date range too narrow - Expand date range
3. Field tags incorrect - Check field syntax

**Solution**: Start with simple query, then add filters

### Issue: Full text not available

**Cause**: Article not in PMC Open Access subset

**Solution**:
- Abstract is always available via EFetch
- Check if preprint exists on bioRxiv/medRxiv
- Contact library for institutional access

### Issue: Rate limit errors

**Cause**: Exceeded 3 requests/second

**Solution**:
1. Get free NCBI API key (increases to 10/sec)
2. Add delays between requests
3. Use batch fetching for multiple PMIDs

## API Reference Quick Guide

### ESearch (Search)
```
Base: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
Required: db=pubmed, term=[query]
Optional: retmax, retstart, sort, mindate, maxdate
```

### EFetch (Get records)
```
Base: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi
Required: db=pubmed, id=[pmid]
Optional: rettype (abstract, medline), retmode (xml, text)
```

### ELink (Find links)
```
Base: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi
Required: dbfrom=pubmed, db=pubmed, id=[pmid]
Key linknames: pubmed_pubmed (similar), pubmed_pubmed_citedin (citing)
```

### BioC PMC (Full text)
```
Base: https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi
Format: /BioC_[xml|json]/[PMID|PMC_ID]/[unicode|ascii]
```

## Limitations

1. **Full text access**: Limited to ~3M PMC Open Access articles
2. **Rate limits**: 3 req/sec without key, 10 req/sec with key
3. **Citation data**: May lag behind actual publications
4. **Real-time**: Updates propagate within 24 hours

## Getting Started

1. **Optional**: Get NCBI API key at https://www.ncbi.nlm.nih.gov/account/settings/
2. **Configure**: Set `NCBI_API_KEY` environment variable
3. **Use**: Ask Claude to search, read, or explore PubMed articles

No API key is required for basic usage at lower rates.
