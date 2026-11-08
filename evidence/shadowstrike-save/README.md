# Shadowstrike save condition — A-019

This narrow correction binds the three Shadowstrike curse descriptions in the
current Guide to the retained [DDO Wiki Shadowdancer page](https://ddowiki.com/page/Shadowdancer),
[revision 720964](https://ddowiki.com/index.php?title=Shadowdancer&oldid=720964).
The exact operative clause is:

> On hit, opponent must make a Fortitude save vs (DC 20 + highest ability score + Assassinate Bonuses) or be cursed with Shadow Loss.

The Guide now names the failed Fortitude save in the destiny table, active-ability
prose and ability table (baseline lines 652, 1229 and 1268). The prose retains the
literal DC formula once; “highest ability score” is not replaced with a modifier.
This supersedes the unconditional “a curse on everything it hits” wording, not
other Shadowstrike effect claims. Geometry and ranged-damage wording remain
unchanged and outside this correction's verified scope.

## Retained provenance

[source.json](source.json) records the exact quote, subject context, `/text`
Unicode character range `[4245, 4592)`, identities and SHA-256 hashes. It reuses
[the existing public retained fixture](../../tools/fixtures/endgame-evidence/retained/Shadowdancer.live.json)
without copying the unmerged audit suite. That fixture is the existing public
redaction of the original `intiana-audit-2026-11-01/trees/sources/Shadowdancer.live.json`:
only the footer's editor metadata differs. Its entire Wiki text and revision
match the original, independently read for this correction. Original SHA-256:
`ab3c5298ae4058da84421ff0b900b6db4caacc66a39db197bc898335de1c84fe`.

The original body observation time is missing. The page footer's last-modified
date is not an observation time; the filename does not prove a live read.
The canonical URL is a citation, not a newly observed page identity. This is
retained documentary evidence, not fresh Wiki verification or a game test.
Other source conflicts, full-build legality, stacking and totals are not resolved.

## Regression scope

`tools/test_shadowstrike_save.py` checks the exact retained source and operative
clause, all three actual Guide occurrences, their source link and the literal DC.
Positive cases preserve harmless inline markup; negative cases remove or hide
the condition, substitute the save/subject/DC, introduce guaranteed curses,
corrupt source/quote/identity or invent observation timestamps. These are narrow
structural and source-contract checks, not a general natural-language proof or
browser visibility/gameplay certification. Standard discovery also checks the
new generated snapshot, print reference, local links and inherited build/model
contracts. Actual browser and print QA are reported separately.

The inherited whole-build preservation guard reverses only the exact corrected
destiny-table phrase before comparing its original hash. The hash and all
selected ranks, costs and purchases remain unchanged; mutations of adjacent
values still fail. No preservation contract is silently rebaselined.
