# V5S forensic comparison

The official train shell and both decoded candidate families preserve the same A16 MessageHeader plus sixteen Library entries. V5A uses the local endpoint http://127.0.0.1:1213/v1/chat/completions, model local-model, one patient-level call per criterion, and a long English-heavy criterion prompt assembled from typed specifications. The online log shows 816/816 transport OK and parse success but only 8 MATCH decisions, so transport and parsing are not the limiting factor.

V2.4.3 is the control artifact with macro F1 0.14375. Its production sources use shorter criterion-oriented prompts and legacy per-report evidence handling. V5A selects evidence through a whole-report ranking and can then truncate the selected report before the relevant late sentence reaches the model. V5S therefore uses sentence/clause anchor windows and concise Chinese YES/NO prompts. This is a concrete behavioral difference; no claim is made that it alone explains the score gap.

Both generations retain retry behavior for timeout/connect/5xx and the proven FHIR shell. V5S does not alter the shell or endpoint; it changes retrieval and decision presentation and records route/evidence metrics.
