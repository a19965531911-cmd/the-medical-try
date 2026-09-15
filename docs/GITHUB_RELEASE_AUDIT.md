# GitHub Release Audit

## Scope

The release audit covered ten requested historical snapshots: V2.4.3, V2.5, V3.0, V3.1, V4.0, V4.1, V4.2, V4.2.1, V4.2.2, and the V4.3 architecture-research directory.

The metadata pass examined 3,651 files totaling 509,704,294 bytes. Historical source directories were treated as immutable.

## Inclusion Policy

- Retain the V2.4.3 rule-based source snapshot.
- Retain the V4.2.2 V3 safety layer and V4 evidence/constraint modules.
- Retain synthetic-only tests and examples.
- Rewrite V4.3 architecture material into concise, path-free documentation.
- Summarize intermediate versions instead of copying duplicate snapshots.

## Exclusion Summary

| Category | Audit findings | Policy |
|---|---:|---|
| Competition input | 37 | Excluded |
| Other data | 435 | Excluded |
| Potential patient data | 201 | Excluded conservatively |
| Submission artifacts | 152 | Excluded |
| Logs | 93 | Excluded |
| Caches | 243 | Excluded |
| Secret-risk files | 1 | Excluded; secret value not recorded |
| Personal-path findings | 26 | Original files excluded or documentation rewritten |
| Unknown files | 53 | Excluded |
| Files over 5 MB | 13 | Excluded with V4.3 third-party vendor material |
| Files over 20 MB | 5 | Excluded |
| Files over 50 MB | 2 | Excluded |

The detailed working audit is `GITHUB_UPLOAD_AUDIT.md`. It is intentionally ignored and is not part of the Git release.

## Testing

Fresh post-copy verification with Python 3.12.14 and pytest completed 9 tests with 9 passed and 0 failed. Tests use only synthetic identifiers and synthetic clinical text.

## Release Constraints

- No official dataset or generated submission artifact may be tracked.
- No patient-level record may be tracked.
- No detected secret-risk file may be tracked.
- No source project is modified.
- The GitHub repository remains private.
