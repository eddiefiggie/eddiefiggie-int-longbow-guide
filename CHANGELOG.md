# Changelog

Build numbers are MM-DD-YY.x, x being the iteration published that day. Earlier entries used v-numbers; v44 was 10-29-26.7.

## Build 11-04-26.11 (local candidate; unpublished)
- Reconciled repeated Walker’s Guidance early-use advice with the existing character-level-14 purchase in both progression tables. The tier summary, abilities explanation and levelling survival checklist now reflect that selected timing; the survival timeline distinguishes it from a universal earliest unlock.
- Purchase order, allocations, effect descriptions, build choices, model, styles and scripts are unchanged. This is internal consistency, not a new mechanics verification. Added focused regression controls and a matching snapshot; exact-source browser QA pending.

## Build 11-04-26.10 (local candidate; unpublished)
- Desktop sidebar subsection links now open when their section receives keyboard focus and remain visible while focus is within that group, independently of the scroll-selected section.
- Automatic sidebar recentering pauses while focus is inside the sidebar. Existing links, focus styling, page content and narrow-screen layout are unchanged. Focused regression checks and matching snapshot added; exact-source browser and assistive-technology QA pending.

## Build 11-04-26.9 (local candidate; unpublished)
- Clarified early equipment timing in the milestone summary, levelling introduction and first band, set-bonus summary, and the repeated Amethyst Loupe wording, using the minimum levels already printed in the Guide. A complete level 1–2 kit remains unresolved.
- This is internal consistency, not fresh item eligibility verification. Item rows, bonuses, acquisition claims, weapons, quiver, selected kit, model, styles and scripts are unchanged. Added focused regression checks and a matching snapshot; browser QA pending.

## Build 11-04-26.8 (local candidate; unpublished)
- Added a visible horizontal-scroll instruction and explicitly keyboard-focusable, labelled bow-ladder region using the existing roadmap pattern. The cue points readers to the offscreen Where column on narrow screens.
- Preserved all bow-table bytes, full-width derived subtotal and purchase link, styles, scripts, source qualifications and model results. Added structural/negative controls and a fresh matching snapshot; exact-source browser and accessibility QA pending.

## Build 11-04-26.7 (local candidate; unpublished)
- Added a derived listed-ingredient subtotal for the four selected heroic Calamitous purchases: 25 of each named Bleak part plus 20 Bleak Wires. The subtotal explicitly excludes any claim about all possible costs or current availability.
- Moved the subtotal into normal full-width prose immediately before the bow ladder after narrow-screen QA found cramped wrapping inside the acquisition cell. It explicitly names the heroic Calamitous context and links to the four purchases.
- Separate purchases, source/naming caveats, selected crafts, model outputs and styles are unchanged. Regression ties the subtotal to the retained heroic purchase costs. Fresh matching snapshot; exact-source browser QA pending.

## Build 11-04-26.6 (local candidate; unpublished)
- Reconciled the Skills summary and blanket “not trained” description with the existing life-specific examples for Diplomacy, Hide, Move Silently and Concentration. This is an internal consistency correction, not fresh Wiki or skill-mechanics verification.
- Preserved every numeric allocation, life-specific table, build choice and model output. Added focused repeated-wording and negative-case checks with a fresh matching snapshot; exact-source browser QA remains pending.

## Build 11-04-26.5 (local candidate; unpublished)
- Clarified four separate heroic Calamitous purchases and which selected augment lists Bleak Wires. Retained the heroic Dolorous/Dreadful naming caveat and limited claims to listed costs.
- Reused the released crafting capture and retained heroic item capture with focused source/context guards. No stats, model values, selected crafts, CSS or other Guide instructions change. Fresh matching snapshot; exact-source browser QA pending.

## Build 11-04-26.4 (draft)
- Explained the bow-model score scale beside its table: normalization within each comparison, approximate whole-number table summaries versus one-decimal script percentages, and apparent ties from rounding. Scores are not DPS or cross-level comparisons.
- Model code, all values/rankings, build choices, evidence qualifications, CSS and table structure are unchanged. Added focused regression checks and a fresh matching snapshot; exact-source browser QA is pending.

## Build 11-04-26.3 (local reconciliation; unpublished)
- Reconciled Sapphire draft df2b581 onto merged Lamordia main 93747790b89e34e5722c2942bcb4402b7d9e7daa. Retains the reviewed listed-profile / “Keen is not listed” qualifications, exact revision 700645 evidence and guardrails; no new mechanics claims.
- Fresh matching snapshot preserves published Lamordia handling and roadmap accessibility, all historical snapshots, model arithmetic and build choices. Recipe and extended alacrity candidates remain excluded. Exact-source browser QA is pending; reconcile main and build stamps before publication.

## Build 11-04-26.2 (local candidate; unpublished)
- Added a Lamordia handling checklist: match family and Weapon variant, avoid raising a heroic item to ML34, and recover a wanted augment with a Viktranium Pick before replacing it. Retained Wiki revision 720728 lists possible Pick sources, not guaranteed rewards.
- Isolated on merged roadmap main d6d2732518bb9b8e13517b86b8574aaa4ff15442. Recipe costs, alacrity, selected build and model are unchanged. Added bounded source checks and a fresh snapshot; exact-source browser QA is pending. Reconcile current main and build stamps before publication.

## Build 11-04-26.1 (isolated local candidate; unpublished)
- Added a visible horizontal-scroll cue before the levelling roadmap and made its existing scroll area keyboard-focusable, named by its heading and described by the cue. Table contents and mechanics are unchanged.
- Built directly from main 3f8aea54974d81da65919463ab92acd025ab431b. The same design passed private desktop/500px/400px and keyboard QA on separate candidate 4d7ae7a; that result does not validate this exact source. Exact-source browser QA remains pending.
- Added standalone regression coverage and a freshly generated matching snapshot. Sapphire, recipe, alacrity and Lamordia candidates are excluded. This local stamp is not reserved; reconcile main and stamps before release.

## Build 11-03-26.2
- Corrected the alacrity paragraph’s ratio notation from 20/15 to 1.20/1.15, about +4.35% under the existing model’s Haste-always-up assumption. Explicitly retained the need for direct-source review of attack-speed stacking; this is arithmetic consistency, not mechanics certification.
- Added focused model-arithmetic regression checks and the matching snapshot. Model code, outputs, build choices and historical snapshots are unchanged.

## Build 11-03-26.1
- Aligned the delayed-IPS roadmap with the existing detailed selections: Weapon Finesse 12, Improved Precise Shot 15, Weapon Focus: Ranged 18. Scourge prose now follows its existing table, with Power Critical 18 and Sneak of Shadows as the optional alternative there; removed stale spare-level-12 and eighth-slot descriptions.
- Repeated the existing Legendary Trick Shot slot-eligibility caveat in the one-page summary and roadmap, and the existing Harbinger of Chaos alignment condition in the imbue summaries. No feat, timing, gear, total or model change; this is internal consistency work, with no new wiki verification.
- Added focused editorial regression checks and the matching snapshot. The existing dynamic integrity test now solely owns the current-build snapshot check; removed the redundant test tied to the previous build. Historical snapshots are unchanged.

## Build 11-02-26.1
- Focused bow correction: Spectral Longbow (level 4) is ML4, not a level-1 recommendation. Its own item sheet conflicts with the aggregate table; the guide follows the item sheet and states the discrepancy.
- Sapphire Sting is ML7 with native 19-20/x3 and no Keen. Corrected related milestone, critical-profile and Keen explanations without inferring its post-Improved-Critical behavior.
- The existing level-8 model comparison retains its numeric outputs; unsupported Sapphire/Improved Critical inputs now fail explicitly. Added focused regression tests and the matching version snapshot. Other builds, gear and broad model assumptions are unchanged.

## Build 10-31-26.7
- Synergy and overlap audit re-run against the Build 10-31-26.6 kit. Six rows rewritten (fortification bypass itemised by type, threat, sneak attack dice with the +3 Artifact gem and Improved Deception, Displacement without the old bracers, fortification on you from the Bracers of the Battlerager, the optimizer blind-spot row) and four rows added: Greater Marksmanship on three kit items (counts once), ability bonus types (the Litany's Profane and the Globe's Exceptional lines under the Lunar Gems and the bow's Miserable slot), Salt, and Doubleshot on items (the goggles' 9% under the cloak's 10%). No kit pick changes; the "What the audit changed" paragraph, the crafted bow's Miserable row (Exceptional Intelligence +2 to match the kit), the Appendix bonus-types bullet, Sources (Marksmanship, Improved Deception) and the audit log updated.

## Build 10-31-26.6
- Endgame kit replaced by the INTiana Jones Salt optimizer solve: ranking Intelligence, Ranged Power, Doubleshot, Seeker, Armor-Piercing, Physical Sheltering (max 132), Constitution, Sneak Attack Dice (required), Dodge (max 23), Will, Distant Diversion, Fortification, Reflex, Fortitude, False Life, Deadly, MRR, Healing Amplification, Accuracy, Legendary Salt (required), Immunity to Fear, True Seeing, Blindness Immunity, Dexterity; crafting and augments on; the Legendary Calamitous Longbow pinned so Salt is the eight-stack Woeful version. Four test solves recorded in the Appendix. Same offence ceilings; Armor-Piercing 76, +3 sneak dice, Fortification 283, Will 25, Immunity to Fear, Salt on the bow, Constitution 32 (36 with one gem swap). Six items change: Skull of the Horned King, Goggles of the Archer, Pendant of Subtle Pain, The Unbreakable Cord, Coldlight Runners, Bracers of the Battlerager. Every item checked on its wiki page.
- Rewritten to match: milestone wear-in table, Survivability from gear (with the Reaper/Ghost Touch row pointing at Shiradi's Vision), the crafted bow's Woeful row (Salt), the dodge arithmetic in the audit and Reaper 10, the Action Boost row, the optimizer check, the Appendix ranking paragraph with the four tests, the one-page rows, Sources and the audit log.

## Build 10-31-26.5
- Reverted: the endgame kit is the R10 v3 solve again, with every dependent section as in Build 10-31-26.3. Build 10-31-26.4 (the INTiana Jones kit) is withdrawn; its version file stays in versions/ for reference.

## Build 10-31-26.4
- Endgame kit replaced by the INTiana Jones optimizer solve (ranking: Intelligence, Constitution, Ranged Power, Doubleshot, Seeker, Armor-Piercing, Sneak Attack Dice, Physical Sheltering, Dodge, Distant Diversion, Deadly, then the survivability block; crafting and augments on). Same offence ceilings; Armor-Piercing 76, Constitution 36, Fortification 160, Dodge 23 (at the cap), Will 25, +2 sneak dice and Improved Deception on two items. Eight items change: Legendary Downcast Vest, The Skull of the Horned King, Doctor Gustav's Warped Lenses, Pendant of Subtle Pain, Belt of the Burrower, Coldlight Runners, Rocard's Cuffs, and the Legendary Calamitous Longbow's crafts. Every item checked on its wiki page; the Skull's Nearly Complete is Intelligence +16 on the wiki (the solver credits +15).
- Rewritten to match: the milestone wear-in table, Survivability from gear, the crafted bow's Woeful row (Shadow with the Downcast Vest), the dodge arithmetic in the audit and Reaper 10, the Action Boost row, the optimizer check, the one-page rows, Sources and the audit log.

## Build 10-31-26.3
- All seven tree images re-captured from the BuildHub build in one session at one resolution (748 px wide, builder point counters cropped), replacing the mixed-age set. The picks are unchanged. No content changes.

## Build 10-31-26.2
- Sourcing made visible: every "<Name> page" reference in the text is now a link to that wiki page (about 100 inline citations); every "(wiki)" table tag links to Sources; sections that have been audited carry a "Checked against the wiki" line with the date and scope (heroic feats, skills, enhancements, epic destinies, bow ladder, endgame kit, Playing it).
- New "Audit log" section before Sources (and AUDITS.md in the repository): date, scope, what was checked and what was found and corrected, for every audit run so far, with a link for reporting a mismatch.

## Build 10-31-26.1
- Item audit after forum feedback on the filigree note and bow stats. Every bow in the ladder (35 rows) was checked against its wiki item page: damage dice and multiplier, enhancement bonus, critical profile, every affix, binding, source and sentience. All 35 match. The four filigree set bonuses were checked against the Sentient Weapon/Filigrees page and match.
- One real error corrected: the synergy audit called the Overfocus fix "the Sentience jewel"; the fix is the Sustaining Symbiont, an ML15 trinket (The Sane Asylum), which costs the trinket slot. The filigree paragraph now gives every set's bonuses at every piece count from the wiki, and a new Overfocus paragraph spells out the -10 Search and Spot on Bow of Sinew at 14-19 and the trapper's options.
- Bow ladder: Bow of Sinew row notes Overfocus's penalty and that the bow does not accept sentience. Levelling survival: the Spectral Longbow line's Ghostbane (Ghost Touch) named as the pre-23 Reaper swap bow. Sources: Sentient Weapon/Filigrees, Overfocus, Sustaining Symbiont, Stealth Strike.

## Build 10-30-26.10
- Stamp under the title reads "Last updated <date>" with the build number beside it, no wider than the cover image.
- Orphan audit after the 10-29/10-30 changes: Dreadnought comparison said Pianissimo at 22 (destiny order buys it at 25); roadmap level-29 row called Cover of Darkness the second threat reducer (it is the third, after Pianissimo 25 and Queen's Diplomacy 26); Horizon Walker core listed as "Haste (Greater Marking)" (wiki name is Haste); Shadowdancer "not taken" line contradicted the Technician note that follows it; three history remarks ("the short version used to be", "earlier builds listed", "the old target") removed; the levelling-survival section's promise of a "next build" reworded as the planned Gear rework.
- Flow: Playing it's intro now lists its parts in order and points back to Reaper 10 for the cap numbers; Reaper 10 points forward to the per-skull table; Start here describes the new Playing it. Contents checked against every heading.

## Build 10-30-26.9
- The build line under the title is now a stamp: guide name, the build number in a slab-face chip, and the date written out with the revision number, in an accent-bordered band. No content changes.

## Build 10-30-26.8
- Skills: "Skill augments by level" note: the colourless Diamond of Spot / Search / Disable Device / Open Lock ladder by minimum level (wiki Augment table), the enhancement-bonus stacking rule, and the standing rule to carry the level-appropriate Diamond of Spot in every levelling band without a better worn Spot line (repeated in the levelling-gear intro). Augment page added to Sources.

## Build 10-30-26.7
- Skills: Spot raised to maximum (it is the passive trap and secret-door warning, a threshold with no roll); per-life allocation rows and the one-page row updated. New "Spotting and Auto-Search" note: Spot versus Auto-Search, the sources of Auto-Search (Nothing Is Hidden, Mind Like Iron, Watchful Eye / Pierce Deception at 23, traps only since U81). Sources: Spot, Auto-Search.

## Build 10-30-26.6
- Playing it, the escapes: Walker's Guidance explained against the Evasion the build already has (Improved Evasion on a failed save, +5 vs traps, Evasion for an ally, Evasion outright before Ranger 9 / Rogue 2), with when to press it.

## Build 10-30-26.5
- Shadowdancer tier 1, Technician note revised: Cover of Darkness stays at 3 (rank 3 is the permanent Nightshield: missile protection and resistance to saves, wiki); the point that moves is Stealthy 1, which only fills the tier-2 gate; Technician ranks 2-3 are where spare destiny points go on a trapping life. Build 10-30-26.4's version of the note (which swapped Cover of Darkness) is withdrawn.

## Build 10-30-26.3
- New optional subsection at the end of Enhancements: Mechanic 4 AP (Arbalester, Mechanics 3) for the trapper, with the wiki lines, what it buys, where the points come from and the Skill Boost step beyond it.

## Build 10-30-26.2
- Harper Agent: on Aasimar Scourge lives, Know Your Foe: Undead is replaced by the second core, Harper Training I (+1 Intelligence, same 2 AP), because the Scourge tree already carries the undead damage (Scourge aura, Strike Down; wiki). Note under the Harper table, AP-by-level level-20 row, Sources.

## Build 10-30-26.1
- "Playing it" rewritten in full prose (about 6,600 words): what the character is; every ability explained by job (standing buffs, the Mark, the shots, the bursts, the escapes); the rotation with the standing-still rule and the Hunter's Focus stutter-step note; the seven defensive layers with their wiki numbers (threat, the three miss rolls, PRR/MRR, fortification, saves, HP, healing); what kills the character ranked (melee packs, Monster Champions by variety, every Reaper type, Will saves, knockdown, elemental damage, archers and casters, Dungeon Alert, traps) with the response to each; a five-situation survival routine; the per-skull Reaper table; and a levelling-survival section (why the levelling set dies, the skull count to run, hirelings, Walker's Guidance as Evasion, Grim Barricade first, Ghost Touch before 23, the order the defences arrive).
- Sources: Reaper race, Monster Champion, MRR, Dodge bonus, Concealment, Incorporeal, Ghost Touch, Fortification, Evasion, Improved Evasion, Saving throw, Helpless, Knockdown, Balance, Threat, Dungeon Alert, Hireling, Potion added.

## Build 10-29-26.11
- Wiki audit of every enhancement and destiny cost, rank, progression gate and prerequisite (Horizon Walker, Deepwood Stalker, Harper Agent, Arcane Archer, Shiradi Champion, Shadowdancer, Fatesinger pages). All costs and totals matched; one layout did not.
- Deepwood Stalker fixed: the tree had 4 AP below its 5-AP gates (tier 2 and the Sneak Attack core), which the game enforces and the builder does not. Favored Defense 1 added in tier 1; Thrill of the Hunt reduced to rank 2. Still 17 AP.
- Action points by level re-sequenced from level 5 to 18 so every purchase meets its gate at the level it is made (Sneak Attack core at 6, Survivalist before Sniper Shot at 7, Horizon Walker one level later than before); roadmap rows updated to match.
- Tree images: builder point counters cropped off (its data prices Crooked Touch and Shadowdancer's Epic Strike differently from the wiki); Deepwood re-rendered for the new picks; Deepwood and Arcane Archer re-captured at the same resolution as the other trees.

## Build 10-29-26.10
- New Skills section after the feats: the two wiki rules (one Rogue level unlocks full maximum ranks; cross-class ranks cost 2), the point budget, a priority table (Search, Disable Device, UMD to max; Tumble 10 for the third charge; Jump 10; Listen and Spot on Ranger levels; Open Lock and Balance with the remainder), the skills not trained and why, and a per-life allocation table (class, racial, Aasimar Scourge, other iconic). One-page row and Sources added.
- Heroic feats: a dedicated Aasimar Scourge table (eight picks, which are chosen at creation, where Ranger 11 grants IPS at 12).

## Build 10-29-26.9
- Title changed to "A Levelling Chassis That Can Run R10"; the guide name and build number sit beneath it.

## Build 10-29-26.8
- Heading changed to "INT Longbow Guide" with the build number beneath it; versions/ files now named by build number.

## v44 — 2026-10-29
- Theme drawn from the cover: parchment page with a faint torch glow, temple-stone table headers, amber rules and chips, a pulp-poster slab face for the title and section headings; dark mode is the night-temple version of the same palette. Tables no longer overflow on wide screens. No content changes.

## v43 — 2026-10-29
- Side navigation: a sticky section list on the left (wide screens) that tracks the section being read and expands its subsections, plus a reading-progress line at the top. No content changes.

## v42 — 2026-10-29
- The ML33-34 "first raid kit" section removed: from level 30 only the endgame kit matters, worn piece by piece as each item's minimum level arrives (the milestone table now gives that order at 31, 32, 33-34, 35 and 36). Filigree notes moved under the endgame kit. Every "ledger" term removed; the levelling set is cited as a wiki-sourced item dataset. Doubleshot, audit, crafted-bow and Sources lines that referred to the old kit rewritten.

## v41 — 2026-10-29
- Sweep after the v39-v40 changes: every remaining reference to Killer, Favored Defense, Survivalist II and Empower Healing as part of the build removed or rewritten in the present tense; the Haste Boost alternative retitled; the Favored Enemy audit row corrected; the Start-here outline says four enhancement trees. Images and versions now referenced from this repository instead of the Drive folder.

## v40 — 2026-10-29
- Heroic feats: Weapon Finesse at 15 (+2 to hit, +10% fortification bypass since U76), Weapon Focus: Ranged at 18. Power Critical moves to the eighth slot that Aasimar Scourge lives have (Improved Precise Shot free at 12); the seven-versus-eight-slot rule is explained. Empower Healing removed. "Feats not taken, and why": Quicken, Empower Healing, Shot on the Run (declined), Power Critical.

## v39 — 2026-10-29
- Enhancement layout changed to Horizon Walker 41 / Deepwood Stalker 17 / Harper Agent 14 / Arcane Archer 8 (core, Elemental Arrows: Flaming, Awareness 3, Morphic Arrows, Elemental Inferno). Killer, Favored Defense and Survivalist II dropped. The imbue uses the Harbinger of Chaos and Scion of Arborea dice (4d6 per arrow at cap); Morphic Arrows ends the 25% DR penalty against bludgeoning and slashing DR. New Arcane Archer section and tree image; Deepwood tree image re-rendered; AP-by-level, roadmap, alternatives, survivability dial, audit, Reaper 10, Playing it and Sources updated.

## v38 — 2026-10-29
- Playing it: the standing-still rule spelled out (Archer’s Focus decay of one stack per 3 seconds moving, 6-second rebuild, the -4 moving penalty, range as position, jumping in place does not count as moving (wiki), when to spend Inexorable Advance, Misty Step and Trick Shot as the moving bursts); first-session checklist updated.

## v37 — 2026-10-28
- Journey re-ordered into blocks of three: each bonus finished to three stacks before the next starts, in order of value to the bow (Ranger, Doubleshot, Rogue/Dodge, Fighter/PRR, Monk, Enchant Weapon, then Completionist, then Tier B triples, then the Divine PRR with the Intelligence races).

## v36 — 2026-10-28
- Journey table made readable: a definition of a trip (iconic 15-30 vs heroic-race 1-30 with an Epic Heart then a Heroic or Racial Heart), a worked example, a Type column, and every past life shown with its stack count (1 of 3, 2 of 3, 3 of 3).

## v35 — 2026-10-28
- Past-life section deepened: a mechanics table (stacking, archetypes, iconic double-dip, epic-then-heroic in one trip, the iconic Epic Heart rule, completionist feats, XP and hearts), the journey rebuilt as 45 trips / 90 past lives where every trip to 30 pays two lives, and an end-state table of what the plan pays line by line.

## v34 — 2026-10-28
- Past-life sequence rebuilt around iconic double-dipping: each iconic forces a class (Iconic Heroes page), so Aasimar Scourge carries Ranger, Shadar-kai Rogue, Purple Dragon Knight Fighter, Tabaxi Monk, and so on; eleven of fifteen classes are collected with an iconic feat attached. Dark Hunter and Dragon Disciple stay heroic lives (iconics cannot take an archetype of their forced class).

## v33 — 2026-10-28
- New section "Past-life priority" after Class split: class lives ranked and sequenced (Ranger, Dark Hunter, Rogue, Fighter, Monk first; Completionist; stacks), racial and iconic lives ranked, epic lives by sphere (Primal Doubleshot, then Divine for PRR, then Arcane Enchant Weapon). Every bonus from the wiki past-life pages.

## v32 — 2026-10-28
- Levelling gear set (Bolt & Rebirth Ledger) cut at level 29; endgame gear from 30.

## v31 — 2026-10-28
- Added "Levelling gear, levels 1-32 (the ledger set)": the Bolt & Rebirth Ledger loadout per band, with the bow ladder in the weapon slot and the rune arm dropped.

## v30 — 2026-10-28
- Restructured for reading flow: glossary, section lead sentences, a merged Levelling roadmap, a gear milestone table, the audit moved after Gear, a first-session checklist, and the optimizer material moved to an appendix.
- Styled as a reading document (serif column, striped tables, build-decision chips, light and dark mode).

## v29 — 2026-10-28
- Edge-case tests on the affix order; Physical Sheltering ranked third (bundle INT Longbow R10 v3); ML35-36 kit re-solved (seven items changed); Incite trap on Black Earth Guardian's Lenses documented.
