# Legendary Trick Shot prerequisite evidence

This is a bounded offline check of two necessary prerequisites, not a legality
certificate. The published Guide already lists “Level 30, Trick Shot” and selects
Trick Shot at 33 before Legendary Trick Shot at 36 in its detailed table,
one-page summary and levelling roadmap. Those selected levels are build choices.
No player-facing text or build choice changes in this candidate.

`Legendary_Trick_Shot.browser.json` is the full retained browser response. Its
13,743 bytes have SHA-256
`3787c98e40d2be79e2efb6096c0db3362c2c95a5269f0d192ef071f0da9c84cf`.
`source.json` records the canonical URL, revision 714089 and permanent URL,
subject, verbatim surrounding prerequisite context, fields, values, types,
qualifiers and the published claim location. Nodes 90–99 place the explicit
level and linked required feat together beneath the Legendary Trick Shot heading.
The required-feat relation comes from that prerequisite context, not from two
unrelated mentions. The schedule check requires a strictly earlier selected feat;
it does not adjudicate ordering of selections at the same level.

The retained response has `isError: false`. It came from member
`intiana-audit-2026-11-01/progression/Legendary_Trick_Shot.browser.json` in
`INTiana-retained-legality-correction-2026-11-03.tar.gz` (490,909 bytes;
SHA-256 `a57229a3bcc636df51db2e73471fb3acbcde3694dcb575bac96ff9ab6c6cd729`).
Library identity: `libfile_a354bd1dc5508191aab559cbab9bffd2`, version 0.
No source refresh was performed. Capture timestamp is absent. The page's
modification date is not a capture timestamp. Hashes establish retained-byte
identity, not freshness or authenticity. The separate error-flagged Improved
Precise Shot capture is excluded.

Run the repository's standard unittest discovery command. The new test module
checks retained-byte identity, source/claim context, the displayed prerequisite
cell and both necessary conditions in all three published schedules. Negative
controls alter each schedule's level or prerequisite selection, move prerequisite
selection to the same/later level, corrupt evidence/record/claim context, and
remove the slot caveat. A citation, or agreement among repeated selections, cannot
make an unsupported prerequisite claim pass. An intentional source or Guide
representation change needs human review and corresponding test maintenance;
this parser is deliberately specific to the existing tables and summary.

Passing establishes only agreement with this retained prerequisite passage.
It does not establish complete legality, eligible Epic/Legendary/Epic Destiny
feat slots, live-game behavior, stacking, other feat prerequisites, or damage
calculations. The Guide's “confirm the slot accepts it” caveats remain required.
All other claims retain their existing evidence status. New source records must
not be created by inferring rules from unrelated facts.

## Separate classification slice

`classification.json` and `test_legendary_trick_shot_classification.py` bind the
existing “Listed as a Legendary feat on the wiki” statement to the full retained
page-category container (nodes 110–117), specifically the linked
`Category:Legendary_feats`. This is page category membership, not an eligible
feat slot. The exact existing uncertainty caveat remains required. Negative
controls change the published category, corrupt retained or maintained
subject/revision/category context, and substitute an unsupported eligibility
assertion. No player-facing content or base Trick Shot values are changed.
This slice depends on the prerequisite candidate and reuses its unchanged
capture and small test parsing helpers. Neither slice proves slot compatibility,
stacking, capture freshness/authenticity or complete legality.

## Retained capture limits and integration

Reconciled onto released main `a6d8840` on 4 November 2026 without changing
Guide HTML, selections, build 11-04-26.4, model or runtime assets. Original local
candidates `4a2ac70` and `2c02cef` remain preserved. The capture bytes and both
source records are unchanged from those candidates; no source refresh occurred.
The capture includes a logged-out cache warning (“this is up to 13 hours old”,
node 73). Its footer reports modification at 13:49 on 16 September 2026 (Update
81.3), not the capture time. Neither that footer nor the hash establishes current
Wiki freshness, independent authenticity or live-game correctness. Credit and
Attribution-ShareAlike 2.5 links remain in the full retained response.
