---
name: biorxiv
description: Search bioRxiv and medRxiv preprints, read abstracts, and retrieve full text for biology and medical preprints using the bioRxiv/medRxiv API
---

# bioRxiv/medRxiv — Search, Read & Full Text

Use this skill for all bioRxiv and medRxiv operations: searching for biology and medical preprints, reading a preprint by DOI, and retrieving full text.

## When to Use This Skill

- **Search bioRxiv**: "Search bioRxiv for CRISPR delivery", "Find biology preprints on gene therapy"
- **Search medRxiv**: "Search medRxiv for COVID-19 vaccines", "Find medical preprints on..."
- **Browse recent**: "Show recent bioRxiv preprints on gene therapy from last week"
- **Read preprint**: "Read bioRxiv 10.1101/2024.01.15.575889"
- **Full text**: "Get full text of bioRxiv preprint 10.1101/..."
- **Identifiers**: Any query containing a bioRxiv/medRxiv DOI (`10.1101/...`), or biorxiv.org/medrxiv.org URL

### Keywords That Trigger Activation

`biorxiv`, `bioRxiv`, `medrxiv`, `medRxiv`, `biology preprint`, `medical preprint`, `life sciences preprint`, `10.1101`, `search biorxiv`, `read biorxiv`, `search medrxiv`, `read medrxiv`, `gene therapy preprint`, `COVID preprint`, `biorxiv.org`, `medrxiv.org`

### Do NOT use for

- PubMed queries → use `pubmed-lookup`
- arXiv queries → use `arxiv`

## Data Source: bioRxiv/medRxiv API

**Details endpoint**: `https://api.biorxiv.org/details/[server]/[DOI]/na/json`
- `server`: `biorxiv` or `medrxiv`
- `DOI`: Full DOI, e.g. `10.1101/2024.01.15.575889`

**Browse endpoint**: `https://api.biorxiv.org/details/[server]/[start_date]/[end_date]/[cursor]/json`
- Returns 100 papers per page, use cursor for pagination

**DOI formats**:
- Legacy: `10.1101/YYYY.MM.DD.XXXXXX`
- New: `10.64898/YYYY.MM.DD.XXXXXX`

**Full text**: JATS XML via `jatsxml` field, HTML at `biorxiv.org/content/[DOI].full`

**Rate limits**: No documented limit; use reasonable delays between requests.

## Workflow 11: Search bioRxiv/medRxiv

**User says**: "Search bioRxiv for CRISPR delivery systems"

**Script**: `scripts/search_biorxiv.py`

**Process**:
1. Parse query, identify server (biorxiv or medrxiv)
2. Search via website or browse API
3. Format results with bioRxiv citation format

**Example**:
```python
from search_biorxiv import search_biorxiv, browse_biorxiv_recent

# Website search
results = search_biorxiv("CRISPR gene editing", max_results=10)

# Search medRxiv
results = search_biorxiv("COVID-19 vaccine", max_results=10, server="medrxiv")

# Browse recent papers
results = browse_biorxiv_recent(days=7, server="biorxiv", max_results=20)
```

**Output**:
```
## bioRxiv Search Results: "CRISPR delivery systems"

Found 456 preprints. Showing 10:

1. Smith J, Jones M, et al. Novel lipid nanoparticle delivery of CRISPR-Cas9. bioRxiv. 2024. doi:10.1101/2024.01.15.575889. [Preprint]. [Genetics].
   Abstract: We developed a novel lipid nanoparticle formulation...

2. Chen X, Wang Y, et al. AAV-mediated CRISPR delivery to the CNS. bioRxiv. 2024. doi:10.1101/2024.01.10.573456. [Preprint]. [Neuroscience].
```

## Workflow 12: Read bioRxiv/medRxiv Paper

**User says**: "Read bioRxiv 10.1101/2024.01.15.575889"

**Script**: `scripts/fetch_biorxiv.py`

**Process**:
1. Extract and validate DOI (`10.1101/YYYY.MM.DD.XXXXXX`)
2. Call `fetch_biorxiv_paper(doi)`
3. Format as structured reference with abstract

**Example**:
```python
from fetch_biorxiv import fetch_biorxiv_paper, batch_fetch_biorxiv

result = fetch_biorxiv_paper("10.1101/2024.01.15.575889")
# Also accepts URLs: fetch_biorxiv_paper("https://www.biorxiv.org/content/10.1101/...")

# Batch fetch
results = batch_fetch_biorxiv(["10.1101/2024.01.15.575889", "10.1101/2024.01.10.573456"])
```

**Output**:
```
## bioRxiv Preprint: 10.1101/2024.01.15.575889

**Reference**: Smith J, Jones M, Wilson K, et al. Novel lipid nanoparticle delivery of CRISPR-Cas9. bioRxiv. 2024. doi:10.1101/2024.01.15.575889. [Preprint]. [Genetics].

**Abstract**:
We developed a novel lipid nanoparticle formulation for efficient delivery...

**Category**: Genetics
**Version**: 2
**License**: CC-BY-NC-ND 4.0
**PDF**: https://www.biorxiv.org/content/10.1101/2024.01.15.575889.full.pdf
**Page**: https://www.biorxiv.org/content/10.1101/2024.01.15.575889
```

## Workflow 13: Get bioRxiv/medRxiv Full Text

**User says**: "Get full text of bioRxiv preprint 10.1101/2024.01.15.575889"

**Script**: `scripts/fetch_biorxiv_fulltext.py`

**Process**:
1. Extract and validate DOI
2. Try JATS XML first, fall back to HTML
3. Parse sections, figures, references
4. Return structured full text

**Example**:
```python
from fetch_biorxiv_fulltext import get_biorxiv_fulltext, check_fulltext_availability

avail = check_fulltext_availability("10.1101/2024.01.15.575889")
result = get_biorxiv_fulltext("10.1101/2024.01.15.575889")
```

**Output**:
```
## Full Text: bioRxiv:10.1101/2024.01.15.575889

**Title**: Novel lipid nanoparticle delivery of CRISPR-Cas9
**Word Count**: 8,500 words
**Format**: JATS

### Abstract
[...]

### Introduction
[...]

### Materials and Methods
[...]

### Results
[...]

### Discussion
[...]

### Figures (5 total)
- fig1: Overview of experimental design...

### References (42 total)
- First reference...
```

## Error Handling

| Error | Solution |
|-------|----------|
| DOI not found | Verify format is 10.1101/YYYY.MM.DD.XXXXXX |
| Full text not available | Fall back to abstract only |
| Server error | Retry; biorxiv.org may be temporarily slow |

## Available Scripts

- `scripts/search_biorxiv.py` — `search_biorxiv(query, max_results, server)`, `browse_biorxiv_recent(days, server)`
- `scripts/fetch_biorxiv.py` — `fetch_biorxiv_paper(doi, server)`, `batch_fetch_biorxiv(dois)`
- `scripts/fetch_biorxiv_fulltext.py` — `get_biorxiv_fulltext(doi, server)`, `check_fulltext_availability(doi)`
- `scripts/utils/helpers.py` — `validate_biorxiv_doi(doi)`, `format_biorxiv_citation(article)`
