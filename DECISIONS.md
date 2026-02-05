# Architecture Decisions

This document records the key decisions made during the creation of the PubMed Reader skill.

## 1. API Selection

### Selected: NCBI E-utilities + BioC PMC API

**Decision Date**: 2026-02-04

**Alternatives Considered**:

| API | Coverage | Cost | Rate Limit | Decision |
|-----|----------|------|------------|----------|
| NCBI E-utilities | 35M+ articles | Free | 3-10/sec | **Selected** |
| PubMed API (legacy) | Same | Free | Same | Deprecated |
| Europe PMC | 40M+ | Free | 25/sec | Less US coverage |
| Semantic Scholar | 200M+ | Free | 100/day | Different focus |

**Justification**:

- **Official source**: E-utilities is the official NCBI API
- **Comprehensive**: Access to PubMed (35M+ citations), PMC, and related databases
- **Free**: No cost, just optional API key for higher limits
- **Well-documented**: Extensive official documentation
- **Reliable**: Maintained by NIH/NLM
- **Full text**: BioC API provides structured full text for ~3M OA articles

**Trade-offs Accepted**:
- Lower rate limit than some alternatives (mitigated with caching)
- No direct access to paywalled content (by design - respects publishers)

## 2. Architecture Pattern

### Selected: Simple Skill (Single SKILL.md)

**Justification**:
- Single coherent domain (PubMed literature)
- <2000 lines of primary logic
- All functions closely related
- Easier maintenance as single package

**Structure**:
```
pubmed-reader-cskill/
├── SKILL.md              # Main skill documentation
├── scripts/              # Python implementation
│   ├── search_pubmed.py
│   ├── fetch_article.py
│   ├── fetch_fulltext.py
│   ├── find_similar.py
│   ├── find_citations.py
│   └── comprehensive_report.py
├── tests/                # Test suite
└── references/           # Additional documentation
```

## 3. Caching Strategy

### Selected: File-based TTL Cache

**TTL Values**:

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Article metadata | 30 days | Rarely changes after publication |
| Search results | 1 hour | New articles published frequently |
| Citation counts | 7 days | Updates periodically |
| Full text | 30 days | Static once published |

**Justification**:
- Reduces API calls significantly
- Respects NCBI server resources
- Improves response time for repeated queries
- File-based is portable and debuggable

**Trade-offs**:
- Slightly stale citation counts (acceptable for research use)
- Disk space usage (minimal, <100MB typical)

## 4. Full Text Strategy

### Selected: BioC PMC API for Open Access Only

**Justification**:
- Legal access to ~3M Open Access articles
- Structured format (sections, figures, tables)
- No paywall circumvention
- Clear messaging when full text unavailable

**Alternatives Rejected**:
- Web scraping: Legal/ethical issues
- Sci-Hub integration: Copyright concerns
- Institutional proxies: Not portable

## 5. Error Handling Philosophy

### Selected: Graceful Degradation with Detailed Errors

**Approach**:
- Return partial data when possible
- Include error details in response
- Provide actionable suggestions
- Never crash on API errors

**Example**:
```python
{
    "success": False,
    "error": {
        "code": "NOT_AVAILABLE",
        "message": "Full text not in PMC Open Access",
        "suggestion": "Try fetching just the abstract"
    }
}
```

## 6. Validation Strategy

### Selected: Multi-layer Validation

**Layers**:
1. **Parameter validation**: Before API calls
2. **Response validation**: After API responses
3. **Data validation**: During parsing

**Justification**:
- Catches errors early
- Provides clear error messages
- Ensures data quality
- Facilitates debugging

## 7. Rate Limiting Approach

### Selected: Adaptive Rate Limiter

**Features**:
- Auto-detects API key presence
- Reduces rate on errors
- Recovers after sustained success
- Thread-safe

**Default Rates**:
- Without API key: 3 req/sec
- With API key: 10 req/sec

## 8. Naming Convention

### Selected: "-cskill" Suffix

**Full Name**: `pubmed-reader-cskill`

**Justification**:
- Identifies as Claude Skill
- Created by Agent-Skill-Creator
- Consistent with convention
- Easy to identify in plugin list

## 9. Comprehensive Report Function

### Selected: All-in-One Function with Graceful Degradation

**Design**:
- Single function for complete analysis
- Calls all individual functions
- Continues if some fail
- Returns combined result

**Justification**:
- Best UX for users wanting "everything"
- Graceful handling of partial failures
- Automatic summary generation
- Alert detection for important findings

## 10. Documentation Approach

### Selected: SKILL.md + README.md + Inline Docstrings

**SKILL.md**: Complete reference for Claude (6000+ words)
- All workflows
- All functions
- All error cases
- Keywords for activation

**README.md**: Quick start for users
- Installation
- Basic usage
- Testing instructions

**Docstrings**: In-code documentation
- Function signatures
- Parameters
- Return types
- Examples

## Future Considerations

### Potential Enhancements (v2.0)
- Batch search across multiple queries
- Export to citation managers (BibTeX, RIS)
- Integration with local reference libraries
- Semantic similarity using embeddings
- Automatic literature review generation

### Not Planned
- Paywall circumvention
- PDF downloading
- Journal subscription integration
