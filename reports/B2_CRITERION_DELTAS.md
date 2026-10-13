# B2 Criterion Deltas

No gold labels: no F1/precision/recall scores reported. E has no B routes. Frozen B1 is the actual comparison baseline. All original inputs and real FHIR outputs are in experiment/b2-official-contract/results.json.

B2A adds 85 category; B2B adds official-compatible 625; B2C adds safe 295 OR/time handling and preserves truthful 225 status; B2D adds 85/205 event constraints; B2E combines clinical-strict 625, safe 295 and event constraints also for 3/465/475/495. Untargeted profiles retain B1 behavior.

Explicit event/procedure ID outranks encounter, hospital namespaces ID, differing dates separate unlinked records. With no event information, same-day/implicit records can still combine: real-event binding cannot be guaranteed from absent metadata. No invented encounter references.

|case|variant|B1|new|
|---|---|---|---|
|625_negative_4|B2B|NO_MATCH|MATCH|
|625_partial|B2B|NO_MATCH|MATCH|
|625_good_then_bad|B2B|MATCH|NO_MATCH|
|625_different_dates|B2B|NO_MATCH|MATCH|
|625_bad_then_good|B2B|MATCH|NO_MATCH|
|625_same_day_different_encounter|B2B|NO_MATCH|MATCH|
|295_or_veto|B2C|NO_MATCH|MATCH|
|295_old|B2C|MATCH|NO_MATCH|
|85_cross_event|B2D|MATCH|NO_MATCH|
|85_good_and_emergency|B2D|NO_MATCH|MATCH|
|205_cross_event|B2D|MATCH|NO_MATCH|
|205_good_and_emergency|B2D|NO_MATCH|MATCH|
|625_hospital_ranges|B2E|NO_MATCH|MATCH|
|295_or_veto|B2E|NO_MATCH|MATCH|
|295_old|B2E|MATCH|NO_MATCH|
|85_cross_event|B2E|MATCH|NO_MATCH|
|85_good_and_emergency|B2E|NO_MATCH|MATCH|
|205_cross_event|B2E|MATCH|NO_MATCH|
|205_good_and_emergency|B2E|NO_MATCH|MATCH|
|3_cross_event|B2E|MATCH|NO_MATCH|
|465_cross_event|B2E|MATCH|NO_MATCH|
|495_cross_event|B2E|MATCH|NO_MATCH|
|475_cross_event|B2E|MATCH|NO_MATCH|
