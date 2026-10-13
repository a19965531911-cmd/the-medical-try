# V6.0.1 Experiment E Provenance Audit

## Result

**FROZEN_E_EXACT_ARTIFACT_FOUND**

The historical artifact is recoverable from Git commit `6639cf7`:

- path: `submission/a_test_message_bundle_v5s2_expe_aggressive_candidate.json`
- blob: `2449a4427bf3cf936e70b470434adf3856e4404c`
- size: `702059`
- SHA256: `40457de3149c7db34daf9c3545199c7c8f409ec65b6ae4412f6ca6a77df6d96e`

The current workspace file is tracked at the same logical path but differs at the byte level:

- size: `702624`
- SHA256: `831385ec9deab93d19e54c8319027978eee4b6843c32ddbc5714795b50ad27e8`

The two parsed Bundles are equal. All 16 decoded Library Python sources are equal, and the current builder reproduces the historical source for all `16/16` criteria. Classification: **BYTE_ONLY** serialization difference, not a clinical or runtime semantic delta.

The current workspace E file was not overwritten. The exact historical bytes were read directly from Git for replay.

Full machine-readable evidence: `analysis/V6_E_PROVENANCE_INVENTORY.json`.
