# JOURNAL PROFILES

Each journal lives under `journals/<slug>/`:

```
journals/<slug>/
  profile.yaml        # publisher, ISSN, scope, limits
  requirements.yaml   # list with source_url, evidence, confidence, evidence_level
  style-guide.md      # journal-level style (Phase 10)
  rejection-patterns.md
  sources/            # cached guideline pages
  example-papers/     # PDFs for style analysis
```

Rules (Requirements 13-15):
- Every requirement must have `source_url`, `source_title`, `retrieved_at`, `evidence`, `confidence`.
- `evidence_level`: OFFICIAL_REQUIREMENT | OBSERVED_PATTERN | MODEL_ASSESSMENT — never mix.
- On `Update Journal`, diff old vs new and ask Apply/Reject.
