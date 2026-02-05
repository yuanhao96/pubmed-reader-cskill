---
name: pubmed-reader-cskill
description: PubMed, arXiv, bioRxiv, and medRxiv reader and literature explorer for scientists - search articles and preprints, read abstracts and full text, follow citations, find similar papers, and extract key information from biomedical and scientific literature using NCBI E-utilities, BioC PMC, arXiv, and bioRxiv/medRxiv APIs
---

# PubMed, arXiv & bioRxiv Reader - Scientific Literature Explorer

A comprehensive Claude Code skill for reading PubMed, arXiv, bioRxiv, and medRxiv articles like a real scientist would - browsing pages, extracting information, following citations, and discovering related research through biomedical and scientific literature networks.

## When to Use This Skill

This skill should be activated when the user:

- **Explores a research domain**: "Give me an overview of type 1 diabetes", "Literature review on CRISPR", "I want to understand cancer immunotherapy"
- **Searches for literature**: "Search PubMed for CRISPR", "Find papers about cancer immunotherapy", "Literature review on Alzheimer's biomarkers"
- **Searches arXiv**: "Search arXiv for transformer attention", "Find arXiv papers on LLM memory", "arXiv papers about diffusion models"
- **Searches bioRxiv/medRxiv**: "Search bioRxiv for CRISPR", "Find preprints about COVID-19 on medRxiv", "Recent bioRxiv papers on gene therapy"
- **Reads bioRxiv papers**: "Read bioRxiv 10.1101/2024.01.15.575889", "Get preprint at biorxiv.org/content/10.1101/..."
- **Gets bioRxiv full text**: "Get full text of bioRxiv preprint", "Read the full bioRxiv paper"
- **Wants strategic literature search**: "Start with review articles on...", "Find reviews first then research papers", "What are the key papers on..."
- **Reads specific articles**: "Read PMID 12345678", "Get abstract for this paper", "Show me the full text"
- **Reads arXiv papers**: "Read arXiv 2602.04557", "Get the paper at arxiv.org/abs/2301.12345", "Show arXiv paper 1706.03762"
- **Gets arXiv full text**: "Get full text of arXiv 2602.04557v1", "Read the full arXiv paper"
- **Explores citations**: "What papers cite this?", "Find citing articles for PMID X", "Show references"
- **Finds related work**: "Find similar papers", "Related articles to this study", "More papers like this"
- **Mentions PMIDs or PMCIDs**: Any query containing "PMID", "PMC", or article identifiers
- **Mentions arXiv IDs or URLs**: Any query containing "arXiv", arXiv IDs (YYMM.NNNNN), or arxiv.org URLs

### Keywords That Trigger Activation

**Strategic Search Keywords**: literature overview, domain overview, understand the field, review articles first, seminal works, foundational papers, key papers, reading order, explore the literature

**PubMed Search Keywords**: pubmed, search, find articles, papers, literature, biomedical, medical literature, scientific papers, research articles

**arXiv Search Keywords**: arxiv, arXiv, preprint, preprints, cs.CL, cs.AI, cs.LG, cs.CV, machine learning papers, AI papers, deep learning papers, NLP papers, computer science papers, physics papers, math papers, quantitative biology

**bioRxiv/medRxiv Search Keywords**: biorxiv, bioRxiv, medrxiv, medRxiv, preprint, preprints, 10.1101, biology preprint, medical preprint, life sciences preprint, COVID preprint, gene therapy preprint

**Action Keywords**: read, get, fetch, abstract, full text, summary, extract, download

**Exploration Keywords**: similar articles, related papers, citations, cited by, references, citing articles

**Identifier Keywords**: PMID, PMC, PubMed ID, article ID, DOI, arXiv ID, arxiv.org

## Mandatory Reference Formatting

**CRITICAL: When citing articles in any output, Claude MUST use strictly formatted NLM/Vancouver-style references.** This is the standard format used by PubMed, MEDLINE, and biomedical journals worldwide.

### Standard Reference Format (NLM/Vancouver)

Every article mentioned in the output MUST be cited using this exact format:

```
AuthorLastName Initials, Author2 Initials, et al. Article title. Journal Name. Year;Volume(Issue):Pages. doi:DOI. PMID: XXXXXXXX.
```

**Complete example:**
```
Walsh EE, Frenck RW Jr, Falsey AR, et al. Safety and immunogenicity of two RNA-based COVID-19 vaccine candidates. N Engl J Med. 2020;383(25):2439-2450. doi:10.1056/NEJMoa2027906. PMID: 32756549.
```

### Formatting Rules

1. **Authors**: Last name followed by initials (no periods), separated by commas. Use "et al." after 6 authors.
2. **Title**: Full article title, ending with a period.
3. **Journal**: Use standard journal abbreviation or full name, followed by a period.
4. **Year/Volume/Pages**: Year immediately followed by semicolon, volume, issue in parentheses, colon, and page range. End with period.
5. **DOI**: Prefix with "doi:" — include when available.
6. **PMID**: Always include as "PMID: XXXXXXXX." at the end.
7. **PMC**: If full text is available, append "PMCXXXXXXX." after PMID.

### When to Apply This Format

- **Search results**: Each article in search results must include a formatted reference line
- **Article reads**: The article header must include the full formatted reference
- **Citation lists**: All citing/cited articles must use this format
- **Similar articles**: Each similar article must include a formatted reference
- **Strategic literature searches**: All articles in reviews, research, and seminal works sections
- **Comprehensive reports**: All referenced articles throughout the report

### Output Template for Article Listings

When listing multiple articles (search results, citations, similar articles), use:

```
1. AuthorLastName Initials, et al. Title. Journal. Year;Vol(Issue):Pages. doi:DOI. PMID: XXXXX.

2. AuthorLastName Initials, et al. Title. Journal. Year;Vol(Issue):Pages. doi:DOI. PMID: XXXXX.
```

### Output Template for Single Article Read

When displaying a single article's details:

```
## Article: PMID XXXXXXXX

**Reference**: AuthorLastName Initials, et al. Title. Journal. Year;Vol(Issue):Pages. doi:DOI. PMID: XXXXX.

**Abstract**:
[Abstract text...]

**Keywords**: [keywords]
**MeSH Terms**: [terms]
```

### Helper Functions

Use `format_citation(article, style="vancouver")` from `scripts/utils/helpers.py` to generate properly formatted references. Use `format_reference_list(articles, style="vancouver")` to format a list of articles.

---

## How It Works

### Architecture Overview

This skill uses three complementary APIs:

1. **NCBI E-utilities API** (https://eutils.ncbi.nlm.nih.gov/entrez/eutils/)
   - ESearch: Search PubMed with complex queries
   - EFetch: Retrieve article abstracts and metadata
   - ESummary: Get document summaries
   - ELink: Find related/citing articles
   - EInfo: Database information and field definitions

2. **BioC PMC API** (https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi)
   - Full text retrieval for ~3 million Open Access articles
   - Structured XML/JSON with sections, paragraphs, figures

3. **arXiv API** (https://export.arxiv.org/api/query)
   - Search arXiv preprints with field prefixes (ti:, au:, abs:, cat:)
   - Retrieve paper metadata, abstracts, and categories via Atom XML
   - HTML full text at https://arxiv.org/html/{id} (LaTeXML-rendered papers)

4. **bioRxiv/medRxiv API** (https://api.biorxiv.org)
   - Same API serves both bioRxiv and medRxiv using `server` parameter
   - DOI-based metadata retrieval via `/details/[server]/[DOI]/na/json`
   - Date-based browsing via `/details/[server]/[start_date]/[end_date]/[cursor]/json`
   - Full text via JATS XML or HTML at `biorxiv.org/content/[DOI].full`

### Data Flow

```
User Query
    │
    ▼
┌─────────────────┐
│  Query Parser   │ ──▶ Detect intent + source (PubMed/arXiv)
└─────────────────┘
    │
    ├──▶ PubMed queries ──▶ E-utilities + BioC API
    │
    └──▶ arXiv queries  ──▶ arXiv Atom API + HTML full text
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

### arXiv API

The arXiv API provides free access to metadata and abstracts for over 2 million preprints across physics, mathematics, computer science, quantitative biology, and more.

**Search Endpoint**: `https://export.arxiv.org/api/query`

**Parameters**:
- `search_query`: Search terms with field prefixes (ti:, au:, abs:, cat:, all:)
- `id_list`: Comma-separated arXiv IDs for direct lookup
- `start`: Pagination offset (0-based)
- `max_results`: Results per page (max 2000)
- `sortBy`: `relevance`, `lastUpdatedDate`, `submittedDate`
- `sortOrder`: `ascending`, `descending`

**Field Prefixes**: `ti:` (title), `au:` (author), `abs:` (abstract), `cat:` (category), `all:` (all fields)

**arXiv HTML Full Text**: `https://arxiv.org/html/{id}` - LaTeXML-rendered HTML (not all papers)

### bioRxiv/medRxiv API

**Details Endpoint**: `https://api.biorxiv.org/details/[server]/[DOI]/na/json`
- `server`: "biorxiv" or "medrxiv"
- `DOI`: Full DOI (e.g., 10.1101/2024.01.15.575889)

**Browse Endpoint**: `https://api.biorxiv.org/details/[server]/[start_date]/[end_date]/[cursor]/json`
- Returns 100 papers per page
- Use cursor for pagination

**DOI Formats**:
- Legacy: `10.1101/YYYY.MM.DD.XXXXXX`
- New: `10.64898/YYYY.MM.DD.XXXXXX`

**Full Text**: JATS XML via `jatsxml` field, HTML at `biorxiv.org/content/[DOI].full`

### Rate Limits

**NCBI E-utilities**:

| Access Level | Rate Limit | Requirements |
|--------------|------------|--------------|
| Without API Key | 3 requests/second | None |
| With API Key | 10 requests/second | Free NCBI account |
| Enhanced | Custom | Contact NCBI |

**Get your API key**: https://www.ncbi.nlm.nih.gov/account/settings/

**arXiv API**:

| Rule | Limit |
|------|-------|
| Request interval | 1 request per 3 seconds minimum |
| Max results per request | 2000 |
| Max total results | 30000 (across pagination) |
| Authentication | None required |

**bioRxiv/medRxiv API**:

| Rule | Limit |
|------|-------|
| Request interval | No documented limit (use reasonable delays) |
| Results per page | 100 |
| Authentication | None required |

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

1. Smith J, Jones M, Wilson K, et al. CRISPR-Cas9 advances in cancer therapy. Nat Med. 2024;30(3):456-467. doi:10.1038/s41591-024-12345-6. PMID: 38123456.

2. Chen L, Wang X, Zhang Y, et al. Novel CRISPR delivery systems for in vivo editing. Cell. 2024;187(5):1102-1118. doi:10.1016/j.cell.2024.01.012. PMID: 38234567.

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

**Reference**: Smith J, Jones M, Wilson K, et al. CRISPR-Cas9 advances in cancer therapy. Nat Med. 2024;30(3):456-467. doi:10.1038/s41591-024-12345-6. PMID: 38123456.

**Abstract**:
Recent advances in CRISPR-Cas9 technology have revolutionized
cancer therapy approaches. This review examines [...]

**Keywords**: CRISPR, gene editing, cancer therapy, immunotherapy

**MeSH Terms**: CRISPR-Cas Systems, Neoplasms/therapy, Gene Editing

**Full Text**: Available (PMC7889054)
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

1. (Score: 95) Author1 AB, Author2 CD, et al. Article title here. Cell. 2021;184(12):3100-3115. doi:10.1016/j.cell.2021.03.001. PMID: 21234567.

2. (Score: 89) Author3 EF, Author4 GH, et al. Another related article. Nature. 2020;586(7831):583-588. doi:10.1038/s41586-020-2789-1. PMID: 20345678.

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
1. Smith J, Brown A, et al. Article title. Nature. 2024;625(7994):100-110. doi:10.1038/xxx. PMID: 38123456.
2. Jones M, Lee K, et al. Another citing article. Cell. 2024;187(2):350-365. doi:10.1016/xxx. PMID: 38234567.

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

**Reference**: Author1 AB, Author2 CD, et al. Full article title. Journal Name. Year;Vol(Issue):Pages. doi:DOI. PMID: 17299597. PMC1790863.

- **Citations**: 234 (as of [date])
- **Citations/year**: 15.6
- **Full Text**: Available (PMC1790863)

### Abstract
[Full abstract...]

### Similar Articles (Top 5)

1. Smith J, Jones M, et al. Similar article title. Cell. 2021;184(12):3100. doi:10.1016/xxx. PMID: 21234567.
2. Chen L, Wang X, et al. Another similar article. Nature. 2020;586:583. doi:10.1038/xxx. PMID: 20345678.
[...]

### Recent Citations (Top 10)

1. Author AB, Author CD, et al. Citing article title. Journal. 2024;Vol:Pages. doi:DOI. PMID: XXXXX.
2. Author EF, Author GH, et al. Another citing article. Journal. 2024;Vol:Pages. doi:DOI. PMID: XXXXX.
[...]

### Key Information Extracted
- **Main Findings**: [Extracted from abstract]
- **Methods Used**: [Extracted from methods if available]
- **Keywords/MeSH**: [List]
```

### Workflow 8: Search arXiv for Papers

**User says**: "Search arXiv for LLM memory", "Find arXiv papers about diffusion models"

**Process**:
1. Parse search query and extract terms
2. Build arXiv API query with field prefixes (all:, ti:, au:, cat:)
3. Call `search_arxiv()` from `scripts/search_arxiv.py`
4. Format results with arXiv citation format

**Example query**:
```python
from search_arxiv import search_arxiv, build_arxiv_query

# Basic search
results = search_arxiv("LLM memory", max_results=10)

# Advanced search with category filter
results = search_arxiv("ti:attention AND au:Vaswani", category="cs.CL", max_results=10)

# Category search
from search_arxiv import search_arxiv_by_category
results = search_arxiv_by_category("cs.AI", "reasoning", max_results=10)
```

**Output format**:
```
## arXiv Search Results: "LLM memory"

Found 1,234 papers. Showing 10:

1. Smith A, Jones B, et al. Memory-Augmented Language Models for Long-Context Understanding. arXiv:2501.12345. 2025. [cs.CL].
   Abstract: We propose a novel memory architecture...

2. Chen X, Wang Y, et al. Efficient Long-Term Memory in Transformers. arXiv:2412.67890. 2024. [cs.LG].
   Abstract: This paper introduces...
```

### Workflow 9: Read arXiv Paper

**User says**: "Read arXiv 2602.04557", "Get arXiv paper 1706.03762"

**Process**:
1. Extract and validate arXiv ID
2. Call `fetch_arxiv_paper()` from `scripts/fetch_arxiv.py`
3. Format as structured reference with abstract

**Example query**:
```python
from fetch_arxiv import fetch_arxiv_paper

result = fetch_arxiv_paper("2602.04557v1")
# Also accepts URLs: fetch_arxiv_paper("https://arxiv.org/abs/2602.04557v1")
```

**Output format**:
```
## arXiv Paper: 2602.04557v1

**Reference**: Smith A, Jones B, et al. Paper Title Here. arXiv:2602.04557v1. 2026. [cs.CL].

**Abstract**:
[Full abstract text...]

**Categories**: cs.CL, cs.AI
**Comment**: 15 pages, 8 figures, accepted at ACL 2026
**PDF**: https://arxiv.org/pdf/2602.04557v1
**HTML**: https://arxiv.org/html/2602.04557v1
```

### Workflow 10: Get arXiv Full Text (HTML)

**User says**: "Get full text of arXiv 2602.04557v1", "Read the full paper from arxiv.org/html/2602.04557v1"

**Process**:
1. Extract and validate arXiv ID
2. Fetch HTML from https://arxiv.org/html/{id}
3. Parse LaTeXML structure to extract sections, figures, references
4. Return structured full text

**Example query**:
```python
from fetch_arxiv_fulltext import get_arxiv_fulltext, check_html_availability

# Check if HTML is available
avail = check_html_availability("2602.04557v1")

# Get full text
result = get_arxiv_fulltext("2602.04557v1")
print(result['sections']['Introduction'])
```

**Output format**:
```
## Full Text: arXiv:2602.04557v1

**Title**: Paper Title Here
**Word Count**: 8,500 words

### Abstract
[Abstract text...]

### Introduction
[Introduction text...]

### Methods
[Methods text...]

### Results
[Results text...]

### Conclusion
[Conclusion text...]

### Figures (5 total)
- fig1: Caption for figure 1
- fig2: Caption for figure 2

### References (42 total)
- First reference...
- Second reference...
```

**Note**: Not all arXiv papers have HTML versions. Only papers processed by the LaTeXML pipeline are available. If HTML is not available, the user will be directed to the PDF.

### Workflow 11: Search bioRxiv/medRxiv for Preprints

**User says**: "Search bioRxiv for CRISPR", "Find medRxiv preprints about COVID-19"

**Process**:
1. Parse search query and extract terms
2. Call `search_biorxiv()` from `scripts/search_biorxiv.py`
3. Format results with bioRxiv citation format

**Example query**:
```python
from search_biorxiv import search_biorxiv, browse_biorxiv_recent

# Website search
results = search_biorxiv("CRISPR gene editing", max_results=10)

# Search medRxiv
results = search_biorxiv("COVID-19 vaccine", max_results=10, server="medrxiv")

# Browse recent papers
results = browse_biorxiv_recent(days=7, server="biorxiv", max_results=20)
```

**Output format**:
```
## bioRxiv Search Results: "CRISPR gene editing"

Found 1,234 preprints. Showing 10:

1. Smith J, Jones M, et al. Novel CRISPR delivery systems for in vivo editing. bioRxiv. 2024. doi:10.1101/2024.01.15.575889. [Preprint]. [Genetics].
   Abstract: We developed a novel delivery system for...

2. Chen L, Wang X, et al. CRISPR-based gene therapy advances. bioRxiv. 2024. doi:10.1101/2024.01.10.573456. [Preprint]. [Molecular Biology].
   Abstract: Recent advances in...
```

### Workflow 12: Read bioRxiv/medRxiv Paper

**User says**: "Read bioRxiv 10.1101/2024.01.15.575889", "Get preprint at biorxiv.org/content/10.1101/..."

**Process**:
1. Extract and validate bioRxiv/medRxiv DOI
2. Call `fetch_biorxiv_paper()` from `scripts/fetch_biorxiv.py`
3. Format as structured reference with abstract

**Example query**:
```python
from fetch_biorxiv import fetch_biorxiv_paper, batch_fetch_biorxiv

# Fetch single paper
result = fetch_biorxiv_paper("10.1101/2024.01.15.575889")
# Also accepts URLs: fetch_biorxiv_paper("https://www.biorxiv.org/content/10.1101/...")

# Batch fetch
results = batch_fetch_biorxiv(["10.1101/2024.01.15.575889", "10.1101/2024.01.10.573456"])
```

**Output format**:
```
## bioRxiv Preprint: 10.1101/2024.01.15.575889

**Reference**: Smith J, Jones M, et al. Paper Title Here. bioRxiv. 2024. doi:10.1101/2024.01.15.575889. [Preprint]. [Genetics].

**Abstract**:
[Full abstract text...]

**Category**: Genetics
**Version**: 2
**License**: CC-BY-NC-ND 4.0
**PDF**: https://www.biorxiv.org/content/10.1101/2024.01.15.575889.full.pdf
**Page**: https://www.biorxiv.org/content/10.1101/2024.01.15.575889
```

### Workflow 13: Get bioRxiv/medRxiv Full Text

**User says**: "Get full text of bioRxiv preprint 10.1101/2024.01.15.575889", "Read the full bioRxiv paper"

**Process**:
1. Extract and validate bioRxiv/medRxiv DOI
2. Fetch JATS XML or HTML full text
3. Parse structure to extract sections, figures, references
4. Return structured full text

**Example query**:
```python
from fetch_biorxiv_fulltext import get_biorxiv_fulltext, check_fulltext_availability

# Check availability
avail = check_fulltext_availability("10.1101/2024.01.15.575889")

# Get full text (tries JATS XML first, then HTML)
result = get_biorxiv_fulltext("10.1101/2024.01.15.575889")
print(result['sections']['Introduction'])
```

**Output format**:
```
## Full Text: bioRxiv:10.1101/2024.01.15.575889

**Title**: Paper Title Here
**Word Count**: 8,500 words
**Format**: JATS

### Abstract
[Abstract text...]

### Introduction
[Introduction text...]

### Materials and Methods
[Methods text...]

### Results
[Results text...]

### Discussion
[Discussion text...]

### Figures (5 total)
- fig1: Overview of the experimental design...
- fig2: Results of gene expression analysis...

### References (42 total)
- First reference...
- Second reference...
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

#### `scripts/search_arxiv.py`
Search arXiv for preprints and scientific papers.

```python
from search_arxiv import search_arxiv, build_arxiv_query

# Basic search
results = search_arxiv("LLM memory", max_results=10)

# With category filter
results = search_arxiv("attention mechanism", category="cs.CL", max_results=10)
```

**Functions**:
- `search_arxiv(query, max_results, start, sort_by, sort_order, category)` - Main search
- `build_arxiv_query(terms, title, author, abstract, category)` - Build advanced query
- `search_arxiv_by_category(category, query, max_results)` - Search within category
- `format_arxiv_search_results(results)` - Format for display

#### `scripts/fetch_arxiv.py`
Fetch arXiv paper metadata and abstracts by ID.

```python
from fetch_arxiv import fetch_arxiv_paper, batch_fetch_arxiv

paper = fetch_arxiv_paper("1706.03762")
batch = batch_fetch_arxiv(["1706.03762", "2005.14165"])
```

**Functions**:
- `fetch_arxiv_paper(arxiv_id)` - Get paper metadata and abstract
- `batch_fetch_arxiv(arxiv_ids)` - Fetch multiple papers
- `format_arxiv_paper(article)` - Format for display

#### `scripts/fetch_arxiv_fulltext.py`
Retrieve full text from arXiv HTML versions (LaTeXML-rendered papers).

```python
from fetch_arxiv_fulltext import get_arxiv_fulltext, check_html_availability

avail = check_html_availability("2602.04557v1")
fulltext = get_arxiv_fulltext("2602.04557v1")
```

**Functions**:
- `check_html_availability(arxiv_id)` - Check if HTML version exists
- `get_arxiv_fulltext(arxiv_id)` - Retrieve and parse HTML full text
- `format_arxiv_fulltext(result, max_words)` - Format for display

#### `scripts/search_biorxiv.py`
Search bioRxiv/medRxiv for preprints.

```python
from search_biorxiv import search_biorxiv, browse_biorxiv_recent

# Website search
results = search_biorxiv("CRISPR", max_results=10)

# Browse recent papers
results = browse_biorxiv_recent(days=7, server="medrxiv")
```

**Functions**:
- `search_biorxiv(query, max_results, server, sort_by)` - Website search
- `browse_biorxiv_recent(days, server, category, max_results)` - API date browsing
- `format_biorxiv_search_results(results)` - Format for display

#### `scripts/fetch_biorxiv.py`
Fetch bioRxiv/medRxiv paper metadata and abstracts by DOI.

```python
from fetch_biorxiv import fetch_biorxiv_paper, batch_fetch_biorxiv

paper = fetch_biorxiv_paper("10.1101/2024.01.15.575889")
batch = batch_fetch_biorxiv(["10.1101/...", "10.1101/..."])
```

**Functions**:
- `fetch_biorxiv_paper(doi, server)` - Get paper metadata and abstract
- `batch_fetch_biorxiv(dois, server)` - Fetch multiple papers
- `format_biorxiv_paper(article)` - Format for display

#### `scripts/fetch_biorxiv_fulltext.py`
Retrieve full text from bioRxiv/medRxiv via JATS XML or HTML.

```python
from fetch_biorxiv_fulltext import get_biorxiv_fulltext, check_fulltext_availability

avail = check_fulltext_availability("10.1101/2024.01.15.575889")
fulltext = get_biorxiv_fulltext("10.1101/2024.01.15.575889")
```

**Functions**:
- `check_fulltext_availability(doi, server)` - Check full text availability
- `get_biorxiv_fulltext(doi, server, prefer_jats)` - Retrieve and parse full text
- `format_biorxiv_fulltext(result, max_words)` - Format for display

### Utility Scripts

#### `scripts/utils/helpers.py`
Common utilities for date handling, ID validation, and formatting.

**Functions**:
- `validate_pmid(pmid)` - Validate PMID format
- `validate_pmcid(pmcid)` - Validate PMC ID format
- `validate_arxiv_id(arxiv_id)` - Validate arXiv ID format
- `extract_arxiv_id_from_text(text)` - Extract arXiv IDs from text
- `validate_biorxiv_doi(doi)` - Validate bioRxiv/medRxiv DOI format
- `extract_biorxiv_doi_from_text(text)` - Extract bioRxiv/medRxiv DOIs from text
- `format_biorxiv_citation(article, style)` - Format bioRxiv/medRxiv citation
- `format_authors(author_list)` - Format author names
- `format_citation(article, style)` - Format NLM/Vancouver citation
- `format_arxiv_citation(article, style)` - Format arXiv citation
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

1. Zajec A, et al. Pathogenesis of Type 1 Diabetes: Established Facts and New Insights. Genes. 2022;13(4):706. PMID: 35456512.
   **Key themes**: autoimmunity, beta-cell destruction, environmental factors, epigenetics

2. Katsarou A, et al. Type 1 Diabetes Mellitus. Nat Rev Dis Primers. 2017;3:17016. PMID: 28358037.
   **Key themes**: epidemiology, pathophysiology, treatment advances

3. Roep BO, et al. Type 1 diabetes mellitus as a disease of the beta-cell. Nat Rev Endocrinol. 2021;17(3):150-161. PMID: 33293704.
   **Key themes**: beta-cell dysfunction, immune interaction

## Phase 2: Key Themes Identified
- **autoimmunity** (mentioned in 5 reviews)
- **beta-cell** (mentioned in 4 reviews)
- **genetics** (mentioned in 3 reviews)
- **immunotherapy** (mentioned in 3 reviews)
- **prevention** (mentioned in 2 reviews)

## Phase 3: Primary Research by Theme

### Theme: Autoimmunity
1. Author A, et al. T-cell mediated beta-cell destruction in NOD mice. J Immunol. 2021;206(5):1012-1023. PMID: 34123456. (456 citations)
2. Author B, et al. Regulatory T cells in type 1 diabetes. Diabetes. 2022;71(8):1745-1758. PMID: 35234567. (234 citations)

### Theme: Beta-cell
1. Author C, et al. Beta-cell stress responses in T1D pathogenesis. Cell Metab. 2023;35(1):89-102. PMID: 36345678. (312 citations)

## Phase 4: Seminal Works (Foundational Papers)
1. Insel RA, et al. Staging presymptomatic type 1 diabetes. Diabetes Care. 2015;38(10):1964-1974. PMID: 26404926. (2,100 citations - landmark)
2. Katsarou A, et al. Type 1 Diabetes Mellitus. Nat Rev Dis Primers. 2017;3:17016. PMID: 28358037. (1,892 citations - highly influential)
3. Herold KC, et al. An Anti-CD3 Antibody, Teplizumab, in Relatives at Risk for Type 1 Diabetes. N Engl J Med. 2019;381(7):603-613. PMID: 31180194. (890 citations)

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

1. Pardi N, Hogan MJ, et al. mRNA vaccines: From research to clinical development. Nat Rev Drug Discov. 2023;22(4):267-284. PMID: 36123456. (Cited by: 892)

2. Verbeke R, Lentacker I, et al. Advances in mRNA-LNP vaccine technology for infectious diseases. Mol Ther. 2024;32(1):34-56. PMID: 37234567. (Cited by: 156)

[...]
```

### Example 2: Read Specific Article

```
User: "Read PMID 32756549"

Response:
## Article: PMID 32756549

**Reference**: Walsh EE, Frenck RW Jr, Falsey AR, et al. Safety and immunogenicity of two RNA-based COVID-19 vaccine candidates. N Engl J Med. 2020;383(25):2439-2450. doi:10.1056/NEJMoa2027906. PMID: 32756549.

**Abstract**:
BACKGROUND: BNT162b1 and BNT162b2 are lipid nanoparticle-formulated,
nucleoside-modified RNA vaccines that encode the SARS-CoV-2 spike protein...

[Full abstract continues...]

**Keywords**: COVID-19 vaccines, mRNA vaccines, SARS-CoV-2, immunogenicity
**MeSH Terms**: COVID-19 Vaccines, mRNA, SARS-CoV-2, Immunogenicity
**Publication Types**: Clinical Trial, Phase 1; Clinical Trial, Phase 2
```

### Example 3: Explore Citations

```
User: "What papers cite PMID 32756549?"

Response:
## Citations for PMID 32756549

This landmark COVID-19 vaccine study has been cited 4,521 times.

### Most Recent (2024)
1. Chen X, et al. Long-term efficacy of mRNA COVID-19 vaccines: A systematic review. Lancet Infect Dis. 2024;24(3):312-325. PMID: 38456789.

2. Williams K, et al. Comparative immunogenicity of mRNA and protein-based vaccines. Nat Med. 2024;30(1):45-58. PMID: 38345678.

### Most Cited
1. Polack FP, et al. Safety and Efficacy of the BNT162b2 mRNA COVID-19 Vaccine. N Engl J Med. 2020;383(27):2603-2615. doi:10.1056/NEJMoa2034577. PMID: 33301246. (Cited 12,456 times)

[...]
```

### Example 4: Find Similar Research

```
User: "Find similar articles to PMID 32756549"

Response:
## Similar Articles to PMID 32756549

Based on shared subjects, citations, and content:

1. [Score: 98] Jackson LA, et al. An mRNA Vaccine against SARS-CoV-2 - Preliminary Report. N Engl J Med. 2020;383(20):1920-1931. doi:10.1056/NEJMoa2022483. PMID: 32663912.
   Similarity: Same vaccine platform, similar trial design

2. [Score: 95] Mulligan MJ, et al. Phase I/II study of COVID-19 RNA vaccine BNT162b1 in adults. Nature. 2020;586(7830):589-593. doi:10.1038/s41586-020-2639-4. PMID: 32785213.
   Similarity: Same vaccine candidate, different population

[...]
```

### Example 5: Comprehensive Analysis

```
User: "Give me a complete overview of PMID 32756549"

Response:
## Comprehensive Report: PMID 32756549

### Reference
Walsh EE, Frenck RW Jr, Falsey AR, et al. Safety and immunogenicity of two RNA-based COVID-19 vaccine candidates. N Engl J Med. 2020;383(25):2439-2450. doi:10.1056/NEJMoa2027906. PMID: 32756549. PMC7889054.

### Impact Assessment
- **Total Citations**: 4,521
- **Citation Velocity**: 1,506 citations/year
- **Most Cited By**: Vaccine development studies

### Abstract
[Full abstract...]

### Top Citing Articles
1. Polack FP, et al. Safety and Efficacy of the BNT162b2 mRNA COVID-19 Vaccine. N Engl J Med. 2020;383(27):2603-2615. PMID: 33301246. (12,456 citations)
2. Baden LR, et al. Efficacy and Safety of the mRNA-1273 SARS-CoV-2 Vaccine. N Engl J Med. 2021;384(5):403-416. PMID: 33378609. (8,234 citations)

### Similar Articles
1. [Score: 98] Jackson LA, et al. An mRNA Vaccine against SARS-CoV-2 - Preliminary Report. N Engl J Med. 2020;383(20):1920-1931. PMID: 32663912.
2. [Score: 95] Mulligan MJ, et al. Phase I/II study of COVID-19 RNA vaccine BNT162b1. Nature. 2020;586(7830):589-593. PMID: 32785213.

### Key Contributions
1. First phase 1/2 data for BNT162b2 vaccine
2. Established dose selection for phase 3
3. Demonstrated favorable safety profile

### Full Text Access
- PMC Available: Yes (PMC7889054)
- Access: Open Access
```

### Example 6: Search arXiv

```
User: "Search arXiv for LLM memory augmentation"

Response:
## arXiv Search Results: "LLM memory augmentation"

Found 456 papers. Showing 10:

1. Smith A, Jones B, et al. Memory-Augmented Language Models for Long-Context Understanding. arXiv:2501.12345. 2025. [cs.CL].
   Abstract: We propose a novel memory architecture that enables language models to...

2. Chen X, Wang Y, et al. Efficient Long-Term Memory in Transformers via Retrieval. arXiv:2412.67890. 2024. [cs.LG].
   Abstract: This paper introduces a retrieval-based approach to...

[...]
```

### Example 7: Read arXiv Paper

```
User: "Read arXiv 1706.03762"

Response:
## arXiv Paper: 1706.03762v7

**Reference**: Vaswani A, Shazeer N, Parmar N, et al. Attention Is All You Need. arXiv:1706.03762. 2017. [cs.CL].

**Abstract**:
The dominant sequence transduction models are based on complex recurrent or
convolutional neural networks that include an encoder and a decoder...

**Categories**: cs.CL, cs.AI
**Comment**: 15 pages, 5 figures
**Published in**: Advances in Neural Information Processing Systems 30 (NIPS 2017)
**PDF**: https://arxiv.org/pdf/1706.03762
**HTML**: https://arxiv.org/html/1706.03762
```

### Example 8: Get arXiv Full Text

```
User: "Get full text of arXiv 2602.04557v1"

Response:
## Full Text: arXiv:2602.04557v1

**Title**: Paper Title Here
**Word Count**: 8,500 words

### Abstract
[Full abstract...]

### Introduction
[Full introduction text...]

### Methods
[Full methods text...]

### Results
[Full results text...]

### Conclusion
[Full conclusion text...]

### Figures (5 total)
- fig1: Architecture overview showing the model pipeline...
- fig2: Comparison of performance across benchmarks...

### References (42 total)
- Vaswani A, et al. Attention Is All You Need. NeurIPS 2017.
- Devlin J, et al. BERT: Pre-training of Deep Bidirectional Transformers. NAACL 2019.
- ...and 40 more
```

### Example 9: Search bioRxiv

```
User: "Search bioRxiv for CRISPR delivery systems"

Response:
## bioRxiv Search Results: "CRISPR delivery systems"

Found 456 preprints. Showing 10:

1. Smith J, Jones M, et al. Novel lipid nanoparticle delivery of CRISPR-Cas9 for in vivo gene editing. bioRxiv. 2024. doi:10.1101/2024.01.15.575889. [Preprint]. [Genetics].
   Abstract: We developed a novel lipid nanoparticle formulation for efficient delivery...

2. Chen X, Wang Y, et al. AAV-mediated CRISPR delivery to the central nervous system. bioRxiv. 2024. doi:10.1101/2024.01.10.573456. [Preprint]. [Neuroscience].
   Abstract: Adeno-associated virus vectors provide a promising approach...

[...]
```

### Example 10: Read bioRxiv Preprint

```
User: "Read bioRxiv 10.1101/2024.01.15.575889"

Response:
## bioRxiv Preprint: 10.1101/2024.01.15.575889

**Reference**: Smith J, Jones M, Wilson K, et al. Novel lipid nanoparticle delivery of CRISPR-Cas9 for in vivo gene editing. bioRxiv. 2024. doi:10.1101/2024.01.15.575889. [Preprint]. [Genetics].

**Abstract**:
We developed a novel lipid nanoparticle formulation for efficient delivery of CRISPR-Cas9 components to target tissues in vivo. Our approach achieves [...]

**Category**: Genetics
**Version**: 2
**License**: CC-BY-NC-ND 4.0

**PDF**: https://www.biorxiv.org/content/10.1101/2024.01.15.575889.full.pdf
**Page**: https://www.biorxiv.org/content/10.1101/2024.01.15.575889
```

### Example 11: Browse Recent medRxiv Preprints

```
User: "Show me recent COVID-19 preprints on medRxiv from the last week"

Response:
## Recent medRxiv Preprints

Last 7 days. Showing 20 of 156:

1. Author A, Author B, et al. Long-term immune responses following mRNA vaccination. medRxiv. 2024. doi:10.1101/2024.02.01.578123. [Preprint]. [Infectious Diseases].
   Abstract: We analyzed long-term antibody levels in a cohort of 5,000 individuals...

2. Author C, Author D, et al. Effectiveness of updated boosters against emerging variants. medRxiv. 2024. doi:10.1101/2024.01.30.577456. [Preprint]. [Epidemiology].
   Abstract: Using data from a national surveillance program...

[...]
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
