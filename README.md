# PubMed Reader - Biomedical Literature Explorer

A Claude Code skill for reading PubMed articles like a real biologist would - browsing pages, extracting information, following citations, and discovering related research.

## Features

- **Search PubMed**: Find articles with complex queries, date filters, and field tags
- **Read Abstracts**: Fetch complete article metadata, abstracts, and keywords
- **Full Text Access**: Retrieve full text for ~3 million Open Access articles
- **Citation Tracking**: Find papers that cite a given article
- **Related Research**: Discover similar articles based on content and MeSH terms
- **Comprehensive Reports**: Generate complete analysis combining all data sources

## Quick Start

### Installation

```bash
# Install the skill
/install-plugin git@github.com:yuanhao96/pubmed-reader-cskill.git
```

### Optional: Configure API Key

For higher rate limits (10 req/sec vs 3 req/sec), get a free NCBI API key:

1. Visit https://www.ncbi.nlm.nih.gov/account/settings/
2. Create account or log in
3. Generate API key
4. Set environment variable:

```bash
export NCBI_API_KEY="your_api_key_here"
```

### Usage Examples

Once installed, simply ask Claude:

```
"Search PubMed for CRISPR gene editing 2024"
"Read abstract for PMID 32756549"
"Find similar articles to PMID 17299597"
"What papers cite PMID 32756549?"
"Get full text of PMC1790863"
"Give me a comprehensive report on PMID 17299597"
```

## Capabilities

### 1. Literature Search

Search PubMed with natural language or advanced queries:

```
"Find papers about mRNA vaccines from 2023"
"Search for CRISPR cancer therapy reviews"
"Papers by Zhang F on gene editing"
```

Supports:
- Date filtering (by year, date range, or relative dates)
- Author filtering
- Journal filtering
- MeSH term searching
- Publication type filtering (reviews, clinical trials, etc.)

### 2. Article Reading

Read article abstracts and metadata:

```
"Read PMID 38123456"
"Get abstract for this paper"
"Show me the details of PMID 32756549"
```

Returns:
- Title and authors
- Journal, volume, pages
- DOI and PMC ID
- Full abstract
- Keywords and MeSH terms
- Publication types

### 3. Full Text Access

Access full text for Open Access articles (~3 million available):

```
"Get full text of PMID 17299597"
"Read the methods section of PMC1790863"
```

Returns:
- Structured sections (Introduction, Methods, Results, Discussion)
- Figure and table references
- Complete reference list

Note: Only articles in the PMC Open Access subset are available.

### 4. Citation Exploration

Discover citation relationships:

```
"What papers cite PMID 17299597?"
"Find citing articles for this study"
"Show citation metrics for PMID 32756549"
```

Returns:
- Total citation count
- Citations grouped by year
- Recent citation velocity
- Citations per year average

### 5. Related Research

Find similar and related articles:

```
"Find similar papers to PMID 17299597"
"Related articles on this topic"
"More papers like this"
```

Returns:
- Similar articles with similarity scores
- Papers sharing MeSH terms
- Other papers by same authors
- Related review articles

### 6. Comprehensive Analysis

Get complete article analysis:

```
"Give me a full report on PMID 17299597"
"Comprehensive analysis of this paper"
```

Returns:
- Full article metadata
- Citation metrics
- Similar articles
- Citing articles
- References
- Full text (if available)
- Auto-generated summary

## Testing

### Run All Tests

```bash
cd pubmed-reader-cskill
python3 tests/test_integration.py
```

### Run Specific Tests

```bash
python3 tests/test_helpers.py
```

### Expected Output

```
======================================================================
INTEGRATION TESTS - PubMed Reader Skill
======================================================================

 Testing search_pubmed()...
  Found 12345 articles
  Returned 5 summaries

 Testing fetch_abstract()...
  Title: Sample article title...
  Authors: 5 authors
  Year: 2024

...

======================================================================
SUMMARY
======================================================================
PASS: PubMed Search (basic)
PASS: Fetch Abstract
PASS: Find Similar Articles
...

Results: 13/13 passed
```

## API Reference

### Core Functions

| Function | Description |
|----------|-------------|
| `search_pubmed(query, ...)` | Search PubMed |
| `fetch_abstract(pmid)` | Get article abstract |
| `get_fulltext(pmid)` | Get full text (OA only) |
| `find_similar_articles(pmid)` | Find similar papers |
| `get_citing_articles(pmid)` | Get citing papers |
| `comprehensive_article_report(pmid)` | Full analysis |

### Rate Limits

| Access Level | Rate | How to Get |
|--------------|------|------------|
| No API Key | 3 req/sec | Default |
| With API Key | 10 req/sec | Free at NCBI |

## Data Sources

- **E-utilities API**: NCBI's official API for PubMed access
- **BioC PMC API**: Full text access for Open Access articles

## Limitations

1. **Full text**: Only ~3M Open Access articles have full text
2. **Rate limits**: 3-10 requests/second depending on API key
3. **Real-time data**: Updates propagate within 24 hours
4. **Citation data**: May lag behind actual publications

## Troubleshooting

### "PMID not found"
- Verify the PMID is correct
- Check if article exists in PubMed

### "Full text not available"
- Article may not be in Open Access subset
- Try fetching just the abstract

### "Rate limit exceeded"
- Get a free NCBI API key
- Wait and retry

### "Network error"
- Check internet connection
- NCBI servers may be temporarily unavailable

## License

This skill is provided as-is for educational and research purposes.
Data from NCBI is subject to their terms of use.

## Links

- [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
- [NCBI E-utilities Documentation](https://www.ncbi.nlm.nih.gov/books/NBK25497/)
- [PMC Open Access](https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/)
- [Get NCBI API Key](https://www.ncbi.nlm.nih.gov/account/settings/)
