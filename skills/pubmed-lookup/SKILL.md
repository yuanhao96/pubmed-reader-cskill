---
name: pubmed-lookup
description: This skill should be used when the user asks to "search PubMed", "find papers about", "read PMID", "get abstract for PMID", "get full text of PMID", "find similar articles to PMID", "what papers cite PMID", or mentions a PMID/PMC identifier. Use for direct PubMed operations: searching by query, reading abstracts, fetching full text, finding similar articles, and finding citing articles.
---

# PubMed Lookup — Search, Read, Cite, Explore

Use this skill for direct PubMed operations on known articles or simple searches: searching by query, reading an abstract by PMID, fetching full text, finding similar articles, and finding citing articles.

## When to Use This Skill

- **Search**: "Search PubMed for CRISPR", "Find papers about cancer immunotherapy"
- **Read abstract**: "Read PMID 38123456", "Get abstract for PMID X"
- **Full text**: "Get full text of PMID 17299597", "Read PMC1790863"
- **Similar articles**: "Find similar articles to PMID X", "Related papers"
- **Citing articles**: "What papers cite PMID X?", "Find citing articles for PMID X"
- **Identifiers**: Any query containing PMID, PMC, or PubMed article identifiers

### Keywords That Trigger Activation

`search pubmed`, `find papers`, `find articles`, `read pmid`, `get abstract`, `full text pmid`, `full text pmc`, `similar articles`, `related articles`, `related papers`, `citing articles`, `what papers cite`, `papers that cite`, `cited by`, `pmid`, `pmc`, `pubmed search`, `literature search`, `biomedical literature`

### Do NOT use for

- "Give me a literature overview of X" → use `pubmed-deep`
- "Literature review on X" → use `pubmed-deep`
- "Comprehensive report on PMID X" → use `pubmed-deep`
- arXiv queries → use `arxiv`
- bioRxiv/medRxiv queries → use `biorxiv`

## Mandatory Reference Formatting

**CRITICAL: Always cite articles using NLM/Vancouver format:**

```
AuthorLastName Initials, Author2 Initials, et al. Article title. Journal Name. Year;Volume(Issue):Pages. doi:DOI. PMID: XXXXXXXX.
```

Example:
```
Walsh EE, Frenck RW Jr, Falsey AR, et al. Safety and immunogenicity of two RNA-based COVID-19 vaccine candidates. N Engl J Med. 2020;383(25):2439-2450. doi:10.1056/NEJMoa2027906. PMID: 32756549.
```

Rules:
1. Authors: Last name + initials (no periods). Use "et al." after 6 authors.
2. Title: Full title ending with period.
3. Journal: Standard abbreviation or full name.
4. Year;Volume(Issue):Pages ending with period.
5. DOI: prefix with "doi:"
6. PMID: always last as "PMID: XXXXXXXX."
7. PMC: append "PMCXXXXXXX." after PMID if full text available.

## Data Sources

### NCBI E-utilities API

**Base URL**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

| Utility | Endpoint | Purpose |
|---------|----------|---------|
| ESearch | `esearch.fcgi` | Search PubMed, return PMIDs |
| EFetch | `efetch.fcgi` | Retrieve abstracts and metadata |
| ESummary | `esummary.fcgi` | Get document summaries |
| ELink | `elink.fcgi` | Find related/citing articles |

**Rate limits**: 3 req/sec (no key), 10 req/sec (with `NCBI_API_KEY` env var)

### BioC PMC API

Full text for ~3M Open Access articles.

```
https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/[PMID]/unicode
```

## Workflow 1: Search PubMed

**User says**: "Search PubMed for CRISPR gene editing 2024"

**Script**: `scripts/search_pubmed.py`

**Process**:
1. Parse query and extract terms, date filters, field tags
2. Build ESearch URL
3. Execute search
4. Fetch ESummary for top results
5. Format with NLM citations

**Example API call**:
```
esearch.fcgi?db=pubmed&term=CRISPR+gene+editing&mindate=2024/01/01&maxdate=2024/12/31&retmax=20&sort=relevance
```

**Output**:
```
## PubMed Search Results: "CRISPR gene editing 2024"

Found 1,234 articles. Showing top 20:

1. Smith J, Jones M, Wilson K, et al. CRISPR-Cas9 advances in cancer therapy. Nat Med. 2024;30(3):456-467. doi:10.1038/s41591-024-12345-6. PMID: 38123456.
```

**Field tags**: `[Title]`, `[Author]`, `[Journal]`, `[MeSH Terms]`, `[Publication Date]`, `[Article Type]`
**Boolean**: AND, OR, NOT
**Date formats**: "last 30 days", "from 2024", "2020-2023"

## Workflow 2: Read Article Abstract

**User says**: "Read abstract for PMID 38123456"

**Script**: `scripts/fetch_article.py`

**Process**:
1. Validate PMID (1–8 digit number)
2. `efetch.fcgi?db=pubmed&id=PMID&rettype=abstract&retmode=xml`
3. Parse XML: title, authors, abstract, keywords, MeSH terms
4. Format output

**Output**:
```
## Article: PMID 38123456

**Reference**: Smith J, Jones M, Wilson K, et al. CRISPR-Cas9 advances in cancer therapy. Nat Med. 2024;30(3):456-467. doi:10.1038/s41591-024-12345-6. PMID: 38123456.

**Abstract**:
[Abstract text...]

**Keywords**: CRISPR, gene editing, cancer therapy
**MeSH Terms**: CRISPR-Cas Systems, Neoplasms/therapy, Gene Editing
**Full Text**: Available (PMC7889054)
```

## Workflow 3: Get Full Text (Open Access)

**User says**: "Get full text of PMID 17299597"

**Script**: `scripts/fetch_fulltext.py`

**Process**:
1. Check PMC Open Access availability
2. Convert PMID → PMC ID if needed
3. `https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMID/unicode`
4. Parse sections: Introduction, Methods, Results, Discussion

**Output**:
```
## Full Text: PMID 17299597 (PMC1790863)

### Abstract
[...]

### Introduction
[...]

### Methods
[...]

### Results
[...]

### Discussion
[...]

### References
[...]
```

**Note**: Only ~3M Open Access articles have full text. If unavailable, fall back to abstract only.

## Workflow 4: Find Similar Articles

**User says**: "Find similar articles to PMID 20210808"

**Script**: `scripts/find_similar.py`

**Process**:
1. `elink.fcgi?dbfrom=pubmed&db=pubmed&id=PMID&cmd=neighbor_score&linkname=pubmed_pubmed`
2. Get similarity scores
3. Fetch ESummary for top matches

**Output**:
```
## Similar Articles to PMID 20210808

1. (Score: 95) Author1 AB, Author2 CD, et al. Article title. Cell. 2021;184(12):3100-3115. doi:10.1016/j.cell.2021.03.001. PMID: 21234567.
```

## Workflow 5: Find Citing Articles

**User says**: "What papers cite PMID 17299597?"

**Script**: `scripts/find_citations.py`

**Process**:
1. `elink.fcgi?dbfrom=pubmed&db=pubmed&id=PMID&linkname=pubmed_pubmed_citedin`
2. Retrieve all citing PMIDs
3. Fetch summaries, sort by date

**Output**:
```
## Articles Citing PMID 17299597

This article has been cited 234 times:

### 2024 (15 citations)
1. Smith J, Brown A, et al. Article title. Nature. 2024;625(7994):100-110. doi:10.1038/xxx. PMID: 38123456.
```

## Error Handling

| Error | Solution |
|-------|----------|
| PMID not found | Verify PMID is correct |
| Rate limit exceeded | Use NCBI_API_KEY or wait |
| Full text not available | Use abstract via EFetch |
| Network timeout | Retry with exponential backoff |

## Available Scripts

- `scripts/search_pubmed.py` — `search_pubmed(query, max_results, min_date, max_date, sort)`
- `scripts/fetch_article.py` — `fetch_abstract(pmid)`, `fetch_metadata(pmid, include_mesh)`
- `scripts/fetch_fulltext.py` — `get_fulltext(pmid, format)`, `check_oa_availability(pmid)`
- `scripts/find_similar.py` — `find_similar_articles(pmid, max_results, include_scores)`
- `scripts/find_citations.py` — `get_citing_articles(pmid, sort_by_date)`, `get_references(pmid)`
- `scripts/utils/helpers.py` — `format_citation(article, style="vancouver")`
- `scripts/utils/cache_manager.py` — `cache_response(key, data, ttl)`, `get_cached(key)`
- `scripts/utils/rate_limiter.py` — `RateLimiter(requests_per_second)`

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `NCBI_API_KEY` | None | API key for 10 req/sec |
| `NCBI_EMAIL` | None | Required for production use |
| `PUBMED_CACHE_DIR` | `data/cache` | Cache directory |
