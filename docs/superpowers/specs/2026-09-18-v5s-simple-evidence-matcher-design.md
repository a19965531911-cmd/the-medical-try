# V5S Simple Evidence Matcher

## Goal

V5S is a diagnostic production candidate intended to recover positive recall after the V5A online result (8 MATCH decisions out of 816). It keeps the proven A16 FHIR shell and local semantic endpoint, while replacing the layered V5 runtime with one self-contained standard-library Python template per Library.

## Production shape

Each decoded Library contains one generated source made from `src/v5s/runtime_template.py` plus literal criterion constants. It defines only `FHIRResourceBundleGenerator` as a public class and uses plain dictionaries, lists, tuples, strings, regexes, and small functions. It has no dataclasses, Enums, dynamic imports, AST namespace rewriting, V4 typed graph, or repo-local runtime dependencies.

The runtime path is normalize reports → sentence/clause segmentation → criterion-aware anchor-window retrieval → deterministic rule where safe → one short Chinese YES/NO model request when unresolved → minimal contradiction guard → grounded payload extraction → existing proven FHIR resource builder. It makes at most one model request plus one retry for timeout, connection, or HTTP 5xx errors.

## Retrieval and decision behavior

Retrieval selects the sentence containing each criterion anchor and adjacent sentences, or a bounded character window for long lines. It covers separate anchor groups for multi-condition criteria and can combine evidence across reports. A small character/token overlap fallback ranks non-empty records without becoming a hard gate.

Rule-first handling covers 265, 485, 615, 755, and 805, with hybrid handling for 555, 635, and 855. The remaining criteria use the same retrieval and a concise Chinese criterion-specific prompt. The parser accepts YES/NO, MATCH/NO_MATCH, Chinese equivalents, JSON decision, and boolean JSON. Clinical values, dates, durations, units, branches, and statuses are extracted only from grounded text.

635 and 855 interpretations are written into separate audit reports before implementation. 875 retains EVER_PRESENT policy. 745 retains the proven parent/partOf FHIR mapping.

## Artifact and observability

The builder preserves the exact MessageHeader and sixteen Library shell and writes only `submission/a_test_message_bundle_v5s_candidate.json`. Metrics are privacy-safe and include criterion, route, evidence window and anchor counts, model call/transport/parse status, decision, resource count, reason, and prompt length. No patient text, prompt, evidence, patient identifier, or PHI is printed.

## Verification gates

Tests cover late-position and cross-report retrieval, rule-first branches, 96 or more semantic fixtures, FHIR/service replay, security, complexity, and real decoded Library execution. Every Library must compile and exec, instantiate the generator, load all 16 criterion constants, and execute positive and negative/unknown fixtures with a fake transport. V4 and all V5A artifacts remain unchanged; Tianchi is not submitted.
