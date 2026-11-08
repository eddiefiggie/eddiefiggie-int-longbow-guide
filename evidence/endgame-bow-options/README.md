# Endgame bow-choice evidence

The [Guide's bow-choice note](../../index.html#endgame-bow-choice) adds Legendary
Demogorgon's Sinew alongside the existing Calamitous loadout. It preserves all 14
original equipment rows, every non-bow item/craft/augment and the selected build.
Calamitous remains the reference for the existing selected-loadout audit. The
historical damage model has a different weapon/craft scenario; its numbers do not
certify this comparison or the Sinew alternate.

## Source provenance

[source-ledger.md](source-ledger.md) is a transcription of the compact exact-quote
ledger supplied by the independent source reviewer on 8 November 2026. It records
14 normal cloud-browser page reads at 17:50:01–17:52:41 UTC. The displayed oldids
are permanent-link metadata, not claims that historical URLs were opened.
Anonymous cache ages range from 4 to 14 hours. These are Wiki observations, not
live-game measurements.

The implementing task read the transmitted ledger. It did **not** materialize or
read the separate raw-body/hover JSON packet named in that ledger. Its direct web
tool attempts to open Wiki pages failed. The source reviewer supplied the original
ledger and raw-packet hashes; [receipt.json](receipt.json) records those separately
from the actual local transcription hash. The local transcription does not match
the transmitted original checksum, so original ledger byte identity is unverified;
the local hash protects this retained rendition, not the unseen original bytes.

## Claim map and derivations

| Guide claim | Ledger sections | Scope |
|---|---|---|
| Calamitous ML34; Sinew ML35, printed profile and effects | 1–2 | Exact variant; no item ranking inferred from printed dice |
| Calamitous recommended for lawful/Paladin lives | 1, 8 | Build decision from lawful-wielder penalty and required Lawful Good alignment; no wielding prohibition or doubled penalty |
| All four Calamitous crafts are absent from Sinew | 1–7 | Slot compatibility and bow-supplied effects; no claim that every other character source of material/alignment bypass disappears |
| Dimlight removal reduces Exceptional INT contribution from 2 to 1 | 6, 12–13 | Derived from unchanged Globe and same-type non-stacking; no modifier, KTA or DPS calculation |
| Purple Defense40 and Orange Treatise work on either bow | 1–2, 9–11 | Defense is Blue and fits Purple; Treatise is Orange; no new augment choice |
| Both filled bows are ML36 | 9–11 | Derived from Defense40 ML36 and host-level rule, distinct from raw item ML |
| Ordinary augment reuse requires extraction and re-slotting | 11 | Jeweler's Tool Kit returns the ordinary augment; overwriting loses it. No free/automatic transfer or promise of owned duplicate copies |
| Paralyzing117 is conditional and does not make targets helpless | 1, 14 | DC117 Will, subsequent saves and immunities; distinct from Legendary Paralysis |
| Elasticity adds a critical multiplier, not threat range | 1 | +1 on natural19/20 ranged criticals; conditional on a critical, not guaranteed critical damage |

Anarchic 7's hover excludes chaos-aligned targets; Anarchic Burst's listed damage
requires lawful targets. Joint stacking and expected damage are not established.
The exact Dolorous Flames item gives neither a numeric proc chance nor a damage
amount. The lawful-wielder tooltips do not establish two cumulative negative
levels. Sentient gems, XP and filigree transfer are outside this source check.
Nothing in this change grants neutral characters the build's chaotic-only
Harbinger benefits.

## Scope checks

`tools/test_endgame_bow_options.py` checks the two choices, alignment and effect
qualifications, ordinary socket handling, ML36 consequence, source receipt and
actual visible document placement. Mutation cases reject altered gear, crafts,
augments, chassis, model values, hidden notes and unsupported claims.

The exact-scope contract records published main
`78feccf7567a86386b332a3d6ffed14e95bc7748`. Reversing only the five reviewed
bow-prose/build-stamp replacements and removing the two new blocks reconstructs
its full `index.html` SHA256
`e01b72ac3132c2235fdfcffe66cf7dd628583dc4367f434b67f04ffc41341a2d`.
The complete original endgame table SHA256 is
`dae8395b121fb48bed8894e24ec83f1b083eb7ac75edab03e1264fe20cd88a54`.
The existing model-preservation test reverses only the concluding bow-choice
recommendation; all assumptions, values and model code retain their prior checks.

These tests establish source-file and scope consistency, not game truth. Before
release: independently review this exact candidate and source rendition, recheck
main/concurrent releases and build numbering, run checks on any revised head, then
verify successful Pages deployment and observed live content after authorized
merge. Live-game interactions remain unmeasured.
