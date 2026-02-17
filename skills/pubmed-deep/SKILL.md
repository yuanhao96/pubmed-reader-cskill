---
name: pubmed-deep
description: This skill should be used when the user asks for "literature overview", "literature review", "understand the field", "domain overview", "review articles first", "seminal works", "foundational papers", "key papers", "reading order", "explore the literature", "comprehensive report on PMID", "full analysis of PMID", or "deep dive". Use for strategic multi-phase literature search (reviews-first) and complete per-article comprehensive reports.
---

# PubMed Deep — Strategic Search & Comprehensive Reports

Use this skill when the user wants to explore an unfamiliar research domain (reviews-first strategy) or get a full analysis of one specific article (comprehensive report).

## When to Use This Skill

- **Domain exploration**: "Give me a literature overview of type 1 diabetes", "I want to understand the field of cancer immunotherapy", "Literature review on CRISPR"
- **Strategic search**: "Start with review articles on...", "Find reviews first then research papers", "What are the key papers on..."
- **Comprehensive report**: "Give me a complete overview of PMID X", "Comprehensive analysis of this paper"

### Keywords That Trigger Activation

`literature overview`, `literature review`, `understand the field`, `domain overview`, `review articles first`, `seminal works`, `foundational papers`, `key papers`, `reading order`, `explore the literature`, `comprehensive report`, `complete overview of pmid`, `full analysis of pmid`, `deep dive`

### Do NOT use for

- Simple searches ("Search PubMed for X") → use `pubmed-lookup`
- Reading a single abstract ("Read PMID X") → use `pubmed-lookup`
- Finding similar/citing articles → use `pubmed-lookup`
- arXiv queries → use `arxiv`
- bioRxiv/medRxiv queries → use `biorxiv`

## Mandatory Reference Formatting

**CRITICAL: Always cite articles using NLM/Vancouver format:**

```
AuthorLastName Initials, et al. Title. Journal. Year;Vol(Issue):Pages. doi:DOI. PMID: XXXXXXXX.
```

## Data Source

**Base URL**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

| Utility | Endpoint | Purpose |
|---------|----------|---------|
| ESearch | `esearch.fcgi` | Search with filters |
| EFetch | `efetch.fcgi` | Retrieve metadata and abstracts |
| ELink | `elink.fcgi` | Find related/citing articles |

**Rate limits**: 3 req/sec (no key), 10 req/sec (with `NCBI_API_KEY`)

## Workflow 6: Strategic Literature Search (Reviews First)

**User says**: "Give me a literature overview of type 1 diabetes" or "Literature review on CRISPR"

**Script**: `scripts/strategic_literature_search.py`

**Process** (How a real biologist explores literature):
1. **Phase 1 — Domain Overview**: Search for review articles first (`[Article Type]:"Review"`)
2. **Phase 2 — Theme Extraction**: Extract key themes, MeSH terms, and concepts from reviews
3. **Phase 3 — Primary Research**: Find research articles organized by identified themes
4. **Phase 4 — Seminal Works**: Identify highly-cited foundational papers (>100 citations)
5. **Generate Reading Order**: Suggest optimal sequence: reviews → seminal → research by theme

**Example**:
```python
from strategic_literature_search import strategic_literature_search

result = strategic_literature_search(
    topic="type 1 diabetes pathogenesis",
    max_reviews=5,
    max_research_per_review=3,
    years_back=5,
    include_seminal_works=True
)
```

**Output**:
```
# Strategic Literature Search: type 1 diabetes pathogenesis

## Executive Summary
Literature search identified 28 key articles. Start with 'Pathogenesis of Type 1 Diabetes...' (Genes, 2022) for domain overview. Key themes: autoimmunity, beta cells, genetics.

## Phase 1: Review Articles (Start Here)
*Read these first for domain overview*

1. Zajec A et al. Pathogenesis of Type 1 Diabetes. Genes. 2022;13(4):706. PMID: 35456512.
   **Key themes**: autoimmunity, beta-cell destruction, environmental factors

## Phase 2: Key Themes Identified
- **autoimmunity** (mentioned in 4 reviews)
- **beta-cell** (mentioned in 3 reviews)

## Phase 3: Primary Research by Theme

### Theme: Autoimmunity
1. Author A, et al. T-cell mediated destruction. J Immunol. 2021. PMID: 34123456. (456 citations)

## Phase 4: Seminal Works
1. Insel RA, et al. Staging presymptomatic type 1 diabetes. Diabetes Care. 2015. PMID: 26404926. (2,100 citations)

## Suggested Reading Order
⭐ 1. [review] PMID 35456512 — domain overview
⭐ 2. [seminal] PMID 26404926 — foundational paper (2,100 citations)
○  3. [research] PMID 34123456 — autoimmunity deep dive
```

**Functions**:
- `strategic_literature_search(topic, max_reviews, max_research_per_review, years_back, include_seminal_works)`
- `quick_literature_overview(topic, max_reviews)` — reviews only
- `deep_literature_analysis(topic, focus_areas)` — with focus areas

## Workflow 7: Comprehensive Article Report

**User says**: "Give me a complete overview of PMID 17299597"

**Script**: `scripts/comprehensive_report.py`

**Process**:
1. Fetch full article metadata (`EFetch`)
2. Get abstract and keywords
3. Find similar articles (`ELink neighbor`)
4. Find citing articles (`ELink citedin`)
5. Attempt full text retrieval (BioC PMC API)
6. Compile comprehensive report

**Example**:
```python
from comprehensive_report import comprehensive_article_report

report = comprehensive_article_report(
    pmid="17299597",
    include_fulltext=True,
    max_similar=5,
    max_citations=10
)
```

**Output**:
```
## Comprehensive Report: PMID 17299597

### Reference
Author1 AB, Author2 CD, et al. Full article title. Journal. Year;Vol(Issue):Pages. doi:DOI. PMID: 17299597. PMC1790863.

### Impact
- Citations: 234
- Citations/year: 15.6
- Full Text: Available (PMC1790863)

### Abstract
[Full abstract...]

### Similar Articles (Top 5)
1. Smith J, et al. Similar title. Cell. 2021. PMID: 21234567.

### Recent Citations (Top 10)
1. Author AB, et al. Citing title. Journal. 2024. PMID: XXXXX.

### Key Contributions
[Extracted from abstract and full text]
```

## Error Handling

| Error | Solution |
|-------|----------|
| No reviews found | Broaden query, try without date filter |
| Rate limit exceeded | Use NCBI_API_KEY or wait |
| Full text not available | Report uses abstract only |
| Network timeout | Retry with exponential backoff |

## Available Scripts

- `scripts/strategic_literature_search.py` — `strategic_literature_search(topic, **options)`
- `scripts/comprehensive_report.py` — `comprehensive_article_report(pmid, **options)`
- `scripts/utils/helpers.py` — `format_citation(article, style="vancouver")`
- `scripts/utils/cache_manager.py` — `cache_response(key, data, ttl)`, `get_cached(key)`
- `scripts/utils/rate_limiter.py` — `RateLimiter(requests_per_second)`

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `NCBI_API_KEY` | None | API key for 10 req/sec |
| `NCBI_EMAIL` | None | Required for production use |
| `PUBMED_CACHE_DIR` | `data/cache` | Cache directory |
