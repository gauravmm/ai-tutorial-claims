# Instructor: generate the receipts

Run `python3 .instructor/generate/build.py` to emit `source_01..03.txt`, the hidden ground truth, and `dataset/claim.reference.csv`. Do not hand-write those receipts or back-fill answers.

`source_04.txt` (a chat thread) and `extra/source_05.txt` (out-of-scope documents) are hand-authored prose, so nothing regenerates them. Their rows still live in `planted()`, so edit both sides together; `test_claims.py` checks that the ids and vendors line up.
