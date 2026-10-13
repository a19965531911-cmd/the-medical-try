REGRESSION_STATUS = PASS1130
LIBRARIES_VERIFIED =16/16
MOCK_CALL_TOTAL =60
MOCK_PRODUCTIVE_CALL_RATE =13.33% (8/60)
MOCK_VALID_FACTS_ACCEPTED =14
B7_1H_EXCLUSIVE_RESCUES =3 relative toB6/B7; preserved
B7_2H_EXCLUSIVE_RESCUES =0 relative toB7.1
ROBUST_RESCUES =22/23 positive perturbations;6/6 negatives; one ambiguity abstention
INTRODUCED_FALSE_POSITIVES =0
FHIR_SERVICE_VALIDATION =8/8 original-case new rescues hit original offline Service
FAST_TEST_SECONDS =6.630
FULL_REGRESSION_SECONDS =187.690
PLATFORM_LIVE_INFERENCE_VERIFIED =NO
PUBLICATION_IDENTITY_VERIFIED =NO
FSH_VIOLATIONS_REMAINING =18 historical; local subset only
B_OFFLINE_BEST =B2E retained
B7_2H_RECOMMENDATION =offline engineering validation candidate; stronger source contract and fewer impossible calls, no new clinical recall
B_BOARD_READY =NO

MOCK/SYNTHETIC ONLY. Facts-per-call .20588 -> .23333; calls-per-rescue8.5 ->7.5. Original recall .87719 unchanged; F1 .93458 unchanged. Ambiguous duplicate-source case abstains (FN); does not count as successful rescue. Semaphore limits do not cancel slow-trickle workers. Platform time quota/header/IDs/checker unverified. No submission.
