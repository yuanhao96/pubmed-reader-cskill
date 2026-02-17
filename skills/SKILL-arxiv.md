---
name: arxiv
description: Search arXiv preprints, read paper abstracts, and retrieve full text for papers in CS, physics, math, and quantitative biology using the arXiv API
---

# arXiv — Search, Read & Full Text

Use this skill for all arXiv operations: searching for preprints, reading paper abstracts by arXiv ID, and retrieving full HTML text.

## When to Use This Skill

- **Search**: "Search arXiv for LLM memory", "Find arXiv papers on diffusion models"
- **Read paper**: "Read arXiv 1706.03762", "Get the paper at arxiv.org/abs/2301.12345"
- **Full text**: "Get full text of arXiv 2602.04557v1", "Read the full arXiv paper"
- **Identifiers**: Any query containing an arXiv ID (YYMM.NNNNN), arXiv URL, or "arxiv"

### Keywords That Trigger Activation

`arxiv`, `arXiv`, `search arxiv`, `read arxiv`, `arxiv paper`, `arxiv preprint`, `cs.CL`, `cs.AI`, `cs.LG`, `cs.CV`, `machine learning papers`, `AI papers`, `deep learning papers`, `NLP papers`, `computer science papers`, `physics papers`, `math papers`, `quantitative biology`

### Do NOT use for

- PubMed queries → use `pubmed-lookup`
- bioRxiv/medRxiv queries → use `biorxiv`

## Data Source: arXiv API

**Search endpoint**: `https://export.arxiv.org/api/query`

| Parameter | Description |
|-----------|-------------|
| `search_query` | Terms with field prefixes: `ti:`, `au:`, `abs:`, `cat:`, `all:` |
| `id_list` | Comma-separated arXiv IDs for direct lookup |
| `start` | Pagination offset (0-based) |
| `max_results` | Results per page (max 2000) |
| `sortBy` | `relevance`, `lastUpdatedDate`, `submittedDate` |

**HTML full text**: `https://arxiv.org/html/{id}` (LaTeXML-rendered, not all papers)

**Rate limits**: 1 request per 3 seconds minimum. No authentication required.

## Workflow 8: Search arXiv

**User says**: "Search arXiv for LLM memory augmentation"

**Script**: `scripts/search_arxiv.py`

**Process**:
1. Parse query and extract terms
2. Build arXiv query with field prefixes
3. Call arXiv API
4. Format results with arXiv citation format

**Example**:
```python
from search_arxiv import search_arxiv, build_arxiv_query

# Basic search
results = search_arxiv("LLM memory", max_results=10)

# With category filter
results = search_arxiv("attention mechanism", category="cs.CL", max_results=10)

# By category
from search_arxiv import search_arxiv_by_category
results = search_arxiv_by_category("cs.AI", "reasoning", max_results=10)
```

**Output**:
```
## arXiv Search Results: "LLM memory augmentation"

Found 456 papers. Showing 10:

1. Smith A, Jones B, et al. Memory-Augmented Language Models. arXiv:2501.12345. 2025. [cs.CL].
   Abstract: We propose a novel memory architecture...

2. Chen X, Wang Y, et al. Efficient Long-Term Memory in Transformers. arXiv:2412.67890. 2024. [cs.LG].
   Abstract: This paper introduces...
```

## Workflow 9: Read arXiv Paper

**User says**: "Read arXiv 1706.03762"

**Script**: `scripts/fetch_arxiv.py`

**Process**:
1. Extract and validate arXiv ID (format: YYMM.NNNNN or YYMM.NNNNNvN)
2. Call `fetch_arxiv_paper(arxiv_id)`
3. Format as structured reference with abstract

**Example**:
```python
from fetch_arxiv import fetch_arxiv_paper

result = fetch_arxiv_paper("1706.03762")
# Also accepts URLs: fetch_arxiv_paper("https://arxiv.org/abs/1706.03762")
```

**Output**:
```
## arXiv Paper: 1706.03762v7

**Reference**: Vaswani A, Shazeer N, Parmar N, et al. Attention Is All You Need. arXiv:1706.03762. 2017. [cs.CL].

**Abstract**:
The dominant sequence transduction models are based on complex recurrent or
convolutional neural networks...

**Categories**: cs.CL, cs.AI
**Comment**: 15 pages, 5 figures
**PDF**: https://arxiv.org/pdf/1706.03762
**HTML**: https://arxiv.org/html/1706.03762
```

## Workflow 10: Get arXiv Full Text (HTML)

**User says**: "Get full text of arXiv 2602.04557v1"

**Script**: `scripts/fetch_arxiv_fulltext.py`

**Process**:
1. Extract and validate arXiv ID
2. Fetch HTML from `https://arxiv.org/html/{id}`
3. Parse LaTeXML structure: sections, figures, references
4. Return structured full text

**Example**:
```python
from fetch_arxiv_fulltext import get_arxiv_fulltext, check_html_availability

avail = check_html_availability("2602.04557v1")
if avail:
    result = get_arxiv_fulltext("2602.04557v1")
```

**Output**:
```
## Full Text: arXiv:2602.04557v1

**Title**: Paper Title Here
**Word Count**: 8,500 words

### Abstract
[...]

### Introduction
[...]

### Methods
[...]

### Results
[...]

### Conclusion
[...]

### Figures (5 total)
- fig1: Architecture overview...
- fig2: Performance comparison...

### References (42 total)
- Vaswani A, et al. Attention Is All You Need. NeurIPS 2017.
```

**Note**: Not all papers have HTML versions — only those processed by LaTeXML. If unavailable, direct user to the PDF.

## Error Handling

| Error | Solution |
|-------|----------|
| arXiv ID not found | Verify format is YYMM.NNNNN |
| HTML not available | Direct user to PDF at arxiv.org/pdf/{id} |
| Rate limit | Wait 3 seconds between requests |

## Available Scripts

- `scripts/search_arxiv.py` — `search_arxiv(query, max_results, category)`, `build_arxiv_query(...)`
- `scripts/fetch_arxiv.py` — `fetch_arxiv_paper(arxiv_id)`, `batch_fetch_arxiv(arxiv_ids)`
- `scripts/fetch_arxiv_fulltext.py` — `get_arxiv_fulltext(arxiv_id)`, `check_html_availability(arxiv_id)`
- `scripts/utils/helpers.py` — `validate_arxiv_id(arxiv_id)`, `format_arxiv_citation(article)`
