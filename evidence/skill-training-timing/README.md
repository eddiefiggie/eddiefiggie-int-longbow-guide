# Skill training eligibility and rank ceilings (A-035)

The correction separates three questions: whether a skill can be trained at the
current step, its maximum purchased ranks, and the price charged by the class
being advanced. It changes no class order, skill priorities or targets, feats,
enhancement/destiny purchases, equipment, or filled augments. The existing point
estimates and partial allocation examples are not certified as a complete budget.

## Evidence actually read

This implementation read the exact committed
[A-018 source ledger](../class-skill-costs/source-ledger.md), a transmitted report
of 8 November 2026 normal-page Wiki observations. Its local length is 12,204 bytes
and SHA-256 is
`40321e74f4fa57542cb41b529284a9ae1c326064f4d26f5dc40fd5cb654b8eac`.
The existing [A-018 receipt](../class-skill-costs/receipt.json) is a metadata
manifest; it is **not** the original browser packet. Its
`raw_packet_materialized_or_read: false` remains accurate for this executor.

The original `a018-goldfinger-skill-source-receipt.json` has not been recovered
or read here. The recorded 412,046-byte length and SHA-256
`283c4470f9a69602e9f51ac57e23ef967a3df1e564a8befca35e4cd2456cbdbe`
are reported metadata, not local raw-file verification. No original source
capture has been reconstructed from the ledger. The original A-018 ledger,
receipt, and dated excluded-scope history remain unchanged.

The ledger reports displayed revision metadata from normal pages, not separate
historical-endpoint reads. Anonymous caching limits freshness; there was no
in-game test. A-035 uses these dated, relayed quotations and rule summaries; it
does not claim a fresh Wiki read or silently upgrade them into original captures.

## Claim map

| Current correction | Exact ledger context | Reported observation / displayed revision |
|---|---|---|
| Disable Device and Open Lock require at least one already-taken class that has the skill | “A-035 observation, explicitly excluded from A-018 implementation” says both skill pages impose that eligibility rule, unlike other skills | Disable Device: 8 Nov 22:54:44.251 UTC / 689700; Open Lock: 22:54:49.224 UTC / 690107 |
| Ordinary Ranger 1 cannot train either skill; this is not a 2-point purchase | The complete displayed Ranger class-skill list in “Direct class-page lists” excludes both, combined with the quoted eligibility rule | Ranger: 8 Nov 22:55:10.283 UTC / 683710 |
| UMD and Tumble can be trained cross-class at Ranger 1, maximum 2 ranks each | Same Ranger list, the two-skill-only eligibility restriction, and the ledger’s A-035 `(3 + character level) / 2` summary (a ledger statement, not a locally inspected raw-page quotation) | Cross-class skill: 8 Nov 22:54:23.304 UTC / 578481 |
| Rogue 1 at character level 2 permits DD/Open Lock; its class-skill maximum is 5 at that level, then character level + 3 | Rogue’s complete displayed list; “Positive cost and maximum rules” explicitly preserves the growing character-level maximum | Rogue: 8 Nov 22:55:03.706 UTC / 683705; Skill point: 22:55:16.558 UTC / 532220 |
| Price follows the class currently being advanced | “Positive cost and maximum rules”; 1 point/rank for a current class skill, 2 for trainable cross-class skills | Class skill: 8 Nov 22:54:31.330 UTC / 449534; Skill point as above |
| Available points cannot be banked for a later level | Skill point quotation in “Positive cost and maximum rules” | Skill point as above |

The reported cache limits for these pages range from 6 to 17 hours (Skill point
says an hour). The raw pages and their exact DOM contexts are unavailable locally;
the ledger’s own words and its metadata establish this limited evidence chain.

## Application and boundaries

This application concerns heroic training at character levels 1–20; it does not
extend purchased-rank formulas into epic or legendary levels. At Scourge’s
ordinary Ranger-1 step, DD and Open Lock are unavailable. UMD and
Tumble are eligible cross-class purchases at 2 points per rank, capped at
`(3 + 1) / 2 = 2` purchased ranks each. Taking Rogue 1 at character level 2 changes
DD/Open Lock eligibility and supplies the full maximum for Rogue class skills:
`2 + 3 = 5`, subsequently `3 + 3 = 6` at character level 3 and `20 + 3 = 23` at
character level 20. These are rank ceilings, not an instruction or guarantee to
purchase all those ranks. Later ordinary Ranger levels again charge 2 points
per rank for those trainable Rogue skills.

Rogue-first class and racial lives qualify at character level 1, with a ceiling
of 4. Other iconics use their actual forced first class’s eligibility, ceiling
and price; Scourge’s ordinary Ranger restrictions are not universal iconic
rules. The existing Shadar-kai Rogue-first exception remains. Choosing iconic
levels 1–15 in one sitting does not make a later class already taken at an earlier
training step; this is the application of the rule to the Guide’s fixed order,
not a new class progression.

The Guide retains its partial skill examples and priorities without assigning
the remaining points. Correcting eligibility, ceilings and prices does not
resolve the full point budget, tome timing, affordability of all targets,
Barbarian Balance or Dark Hunter Spot pricing, or unrelated skill mechanics.
Ordinary Ranger is not conflated with Dark Hunter. The historical A-018 exclusion
was a scope boundary; this separately authorized A-035 correction now handles the
narrow first-training and ceiling questions.

The focused regressions bind the claims to the exact transmitted ledger, check
the visible training-step distinctions and rank ceilings, reject unsupported source
upgrades, and reverse only the approved A-035 changes before older scope hashes
apply. Tests do not certify live-game behavior.

Source credit: [DDO Wiki](https://ddowiki.com/),
[CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/). The original normal
URLs, capture times, displayed revisions and cache notices remain in the ledger.
