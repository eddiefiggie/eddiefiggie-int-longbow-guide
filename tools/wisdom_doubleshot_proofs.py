"""One selected Quickblade definition and six exact Doubleshot interactions.

The original four native definitions, source dates and Artifact rule stay fixed.
This closed contract checks saved evidence and selected construction/occupancy;
it does not authenticate historical page bytes or live-game behavior. Each
public check reads actual source bytes again; no result is cached across calls.
"""
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = 'selected-gear-doubleshot-v1'
PACKET_PATH = 'evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json'
PACKET_SHA256 = '49798b85597ad45f027d52754388336325cde0441484bbee5de90c0bf4d59ed5'
MANIFEST_PATH = 'tools/fixtures/wisdom-loadout/selection.json'
MANIFEST_SHA256 = '8223bd8e25ed9dc4ad9454439ead42dfb693cc008d18d0ddfeb270d33863c37d'
LOADOUT_PATH = 'evidence/wisdom-loadout/loadout.json'
LOADOUT_SHA256 = '20f5bca4573d803a196695aa999f4acc07e71db077e3b66fde51a560b6da0843'
RULE_ID = 'doubleshot-selected-six-pairs'
FAMILY_IDS = ('goggles-ds', 'ring-ds', 'boots-ds', 'armor-ds', 'quickblade-ds')
NATIVE_IDS = FAMILY_IDS[:-1]
DEFINITION_IDS = COMPONENT_IDS = frozenset({'quickblade-ds'})
FAILURES = (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError, StopIteration)

NEW_SOURCES = {'ds-augment-system-20261116': {'path': 'evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json',
                                'sha256': '49798b85597ad45f027d52754388336325cde0441484bbee5de90c0bf4d59ed5',
                                'pointer': ['observations', 0, 'exact_excerpts', 'set_augment_rules'],
                                'quote': 'These level 30 Set augments can be slotted in any augment color '
                                         'slot. The item into which they are slotted becomes part of a unique '
                                         'three-piece item set. They can be crafted in the Hut from Beyond '
                                         '(lower north harbor) in the Cauldron of Cadence. Be aware that '
                                         'slotting a Set Augment into an item with any existing sets will '
                                         'suppress those sets while the Set Augment is slotted, so you should '
                                         'avoid slotting set augments into items that are part of sets you '
                                         'intend to complete.',
                                'record_pointer': ['observations', 0],
                                'url_key': 'source_url',
                                'url': 'https://ddowiki.com/page/Augment_Slot#Augment_Slot',
                                'revision_pointer': ['displayed_permalink'],
                                'revision': 'https://ddowiki.com/index.php?title=Augment_Slot&oldid=717357',
                                'observed_pointer': ['started_at_utc'],
                                'observed': '2026-11-16T05:04:12.273Z',
                                'source_contract': 'selected-gear-doubleshot-v1',
                                'freshness_limit': 'Original scoped browser observation '
                                                   '2026-11-16T05:04:12.273Z through 2026-11-16T05:04:14.556Z. '
                                                   'Literal cache notice: (this is up to -4 hours old). The '
                                                   'record is an attributed transcription, not complete '
                                                   'DOM/HTTP bytes or live-game verification. Displayed '
                                                   'permalink was observed, not independently reopened; '
                                                   'transcluded tooltips may have separate revision histories. '
                                                   'The separately timed Slave Lords metadata supplement '
                                                   'remains linked context, never a backdated standalone '
                                                   'source. Later adoption does not refresh original '
                                                   'observations or prior evidence grades.'},
 'ds-quickblade-20261116': {'path': 'evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json',
                            'sha256': '49798b85597ad45f027d52754388336325cde0441484bbee5de90c0bf4d59ed5',
                            'pointer': ['observations', 1, 'exact_item_fields', 'Description'],
                            'quote': 'Slotting this Augment in any Augment Slot will override its Set Bonus to '
                                     'the Quickblade set.\n'
                                     '\n'
                                     'Quickblade:\n'
                                     '\n'
                                     '3 pieces equipped: +15% Artifact bonus to Doublestrike and Doubleshot',
                            'record_pointer': ['observations', 1],
                            'url_key': 'source_url',
                            'url': 'https://ddowiki.com/page/Item:Set_Augment:_Quickblade',
                            'revision_pointer': ['displayed_permalink'],
                            'revision': 'https://ddowiki.com/index.php?title=Item:Set_Augment:_Quickblade&oldid=643217',
                            'observed_pointer': ['started_at_utc'],
                            'observed': '2026-11-16T05:06:23.132Z',
                            'source_contract': 'selected-gear-doubleshot-v1',
                            'freshness_limit': 'Original scoped browser observation 2026-11-16T05:06:23.132Z '
                                               'through 2026-11-16T05:06:23.156Z. Literal cache notice: (this '
                                               'is up to 5 hours old). The record is an attributed '
                                               'transcription, not complete DOM/HTTP bytes or live-game '
                                               'verification. Displayed permalink was observed, not '
                                               'independently reopened; transcluded tooltips may have separate '
                                               'revision histories. The separately timed Slave Lords metadata '
                                               'supplement remains linked context, never a backdated '
                                               'standalone source. Later adoption does not refresh original '
                                               'observations or prior evidence grades.'},
 'ds-set-table-20261116': {'path': 'evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json',
                           'sha256': '49798b85597ad45f027d52754388336325cde0441484bbee5de90c0bf4d59ed5',
                           'pointer': ['observations', 2, 'exact_quickblade_row'],
                           'quote': 'Set Augment: Quickblade\tColorless\t30\t\n'
                                    'Thread of Fate x 50\n'
                                    'Empty Soul Vessel\n'
                                    'Guided Sight\n'
                                    '\t3 Pieces Equipped: +15% Artifact bonus to Doublestrike and Doubleshot\t'
                                    'Riding the Storm Out',
                           'record_pointer': ['observations', 2],
                           'url_key': 'source_url',
                           'url': 'https://ddowiki.com/page/Augment_Slot/Set_Augment',
                           'revision_pointer': ['displayed_permalink'],
                           'revision': 'https://ddowiki.com/index.php?title=Augment_Slot/Set_Augment&oldid=726131',
                           'observed_pointer': ['started_at_utc'],
                           'observed': '2026-11-16T05:06:46.834Z',
                           'source_contract': 'selected-gear-doubleshot-v1',
                           'freshness_limit': 'Original scoped browser observation 2026-11-16T05:06:46.834Z '
                                              'through 2026-11-16T05:06:48.404Z. Literal cache notice: (this '
                                              'is up to 12 hours old). The record is an attributed '
                                              'transcription, not complete DOM/HTTP bytes or live-game '
                                              'verification. Displayed permalink was observed, not '
                                              'independently reopened; transcluded tooltips may have separate '
                                              'revision histories. The separately timed Slave Lords metadata '
                                              'supplement remains linked context, never a backdated standalone '
                                              'source. Later adoption does not refresh original observations '
                                              'or prior evidence grades.'},
 'ds-set-rules-20261116': {'path': 'evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json',
                           'sha256': '49798b85597ad45f027d52754388336325cde0441484bbee5de90c0bf4d59ed5',
                           'pointer': ['observations', 3, 'exact_excerpts', 'augment_sets'],
                           'quote': 'Collect 3 of the same BtC raid loot across your account. Take them to the '
                                    'Cauldron of Cadence in the Hut from Beyond and combine them with 50 '
                                    'Threads of Fate and an Empty Soul Vessel each, to forge BtA Colorless '
                                    'Augments. Then slot them into 3 items across equipment slots of one '
                                    'character to gain 3 piece Set Bonueses listed below. Be aware that '
                                    'slotting a Set Augment into an item with any existing sets will suppress '
                                    'those sets while the Set Augment is slotted. For the list of other '
                                    'Essence Augments see Augment Slot#Essence augments.',
                           'record_pointer': ['observations', 3],
                           'url_key': 'source_url',
                           'url': 'https://ddowiki.com/page/Named_item_sets#Quickblade',
                           'revision_pointer': ['displayed_permalink'],
                           'revision': 'https://ddowiki.com/index.php?title=Named_item_sets&oldid=730838#Quickblade',
                           'observed_pointer': ['started_at_utc'],
                           'observed': '2026-11-16T05:07:35.550Z',
                           'source_contract': 'selected-gear-doubleshot-v1',
                           'freshness_limit': 'Original scoped browser observation 2026-11-16T05:07:35.550Z '
                                              'through 2026-11-16T05:07:40.967Z. Cache notice is absent from '
                                              'this scoped observation; no value is inferred. The record is an '
                                              'attributed transcription, not complete DOM/HTTP bytes or '
                                              'live-game verification. Displayed permalink was observed, not '
                                              'independently reopened; transcluded tooltips may have separate '
                                              'revision histories. The separately timed Slave Lords metadata '
                                              'supplement remains linked context, never a backdated standalone '
                                              'source. Later adoption does not refresh original observations '
                                              'or prior evidence grades.'},
 'ds-goggles-host-20261116': {'path': 'evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json',
                              'sha256': '49798b85597ad45f027d52754388336325cde0441484bbee5de90c0bf4d59ed5',
                              'pointer': ['observations', 4, 'exact_doubleshot_clause'],
                              'quote': 'Passive: 9% Enhancement bonus to Doubleshot.',
                              'record_pointer': ['observations', 4],
                              'url_key': 'source_url',
                              'url': 'https://ddowiki.com/page/Item:Legendary_Goggles_of_the_Archer',
                              'revision_pointer': ['displayed_permalink'],
                              'revision': 'https://ddowiki.com/index.php?title=Item:Legendary_Goggles_of_the_Archer&oldid=685336',
                              'observed_pointer': ['started_at_utc'],
                              'observed': '2026-11-16T05:09:47.770Z',
                              'source_contract': 'selected-gear-doubleshot-v1',
                              'freshness_limit': 'Original scoped browser observation 2026-11-16T05:09:47.770Z '
                                                 'through 2026-11-16T05:09:48.797Z. Literal cache notice: '
                                                 '(this is up to 8 hours old). The record is an attributed '
                                                 'transcription, not complete DOM/HTTP bytes or live-game '
                                                 'verification. Displayed permalink was observed, not '
                                                 'independently reopened; transcluded tooltips may have '
                                                 'separate revision histories. The separately timed Slave '
                                                 'Lords metadata supplement remains linked context, never a '
                                                 'backdated standalone source. Later adoption does not refresh '
                                                 'original observations or prior evidence grades.'},
 'ds-chains-host-20261116': {'path': 'evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json',
                             'sha256': '49798b85597ad45f027d52754388336325cde0441484bbee5de90c0bf4d59ed5',
                             'pointer': ['observations', 5, 'exact_excerpts', 'augment_channel'],
                             'quote': "Legendary Slaver's Augment Slot: Apply a Slaver's shard to this item.",
                             'record_pointer': ['observations', 5],
                             'url_key': 'source_url',
                             'url': 'https://ddowiki.com/page/Item:Legendary_Chains',
                             'revision_pointer': ['displayed_permalink'],
                             'revision': 'https://ddowiki.com/index.php?title=Item:Legendary_Chains&oldid=631926',
                             'observed_pointer': ['started_at_utc'],
                             'observed': '2026-11-16T05:11:05.432Z',
                             'source_contract': 'selected-gear-doubleshot-v1',
                             'freshness_limit': 'Original scoped browser observation 2026-11-16T05:11:05.432Z '
                                                'through 2026-11-16T05:11:06.418Z. Literal cache notice: (this '
                                                'is up to 5 hours old). The record is an attributed '
                                                'transcription, not complete DOM/HTTP bytes or live-game '
                                                'verification. Displayed permalink was observed, not '
                                                'independently reopened; transcluded tooltips may have '
                                                'separate revision histories. The separately timed Slave Lords '
                                                'metadata supplement remains linked context, never a backdated '
                                                'standalone source. Later adoption does not refresh original '
                                                'observations or prior evidence grades.'},
 'ds-yeenoghu-host-20261116': {'path': 'evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json',
                               'sha256': '49798b85597ad45f027d52754388336325cde0441484bbee5de90c0bf4d59ed5',
                               'pointer': ['observations', 6, 'exact_green_tooltip'],
                               'quote': 'Blue, Green, Yellow, and/or Colorless',
                               'record_pointer': ['observations', 6],
                               'url_key': 'source_url',
                               'url': 'https://ddowiki.com/page/Item:Yeenoghu%27s_Reign',
                               'revision_pointer': ['displayed_permalink'],
                               'revision': 'https://ddowiki.com/index.php?title=Item:Yeenoghu%27s_Reign&oldid=700306',
                               'observed_pointer': ['started_at_utc'],
                               'observed': '2026-11-16T05:11:06.418Z',
                               'source_contract': 'selected-gear-doubleshot-v1',
                               'freshness_limit': 'Original scoped browser observation '
                                                  '2026-11-16T05:11:06.418Z through 2026-11-16T05:11:07.083Z. '
                                                  'Literal cache notice: (this is up to 14 hours old). The '
                                                  'record is an attributed transcription, not complete '
                                                  'DOM/HTTP bytes or live-game verification. Displayed '
                                                  'permalink was observed, not independently reopened; '
                                                  'transcluded tooltips may have separate revision histories. '
                                                  'The separately timed Slave Lords metadata supplement '
                                                  'remains linked context, never a backdated standalone '
                                                  'source. Later adoption does not refresh original '
                                                  'observations or prior evidence grades.'},
 'ds-green-recipe-20261116': {'path': 'evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json',
                              'sha256': '49798b85597ad45f027d52754388336325cde0441484bbee5de90c0bf4d59ed5',
                              'pointer': ['observations', 10, 'exact_excerpts', 'green_recipe_row'],
                              'quote': 'Green\xa0Augment\xa0Slot\t\n'
                                       '30   Staff Splinters\n'
                                       '20   Broken Shackles\n'
                                       '20   Chain Links\n'
                                       '20   Broken Collars\n'
                                       '\t\n'
                                       '100   Legendary Staff Splinters\n'
                                       '50   Legendary Broken Shackles\n'
                                       '50   Legendary Chain Links\n'
                                       '50   Legendary Broken Collars',
                              'record_pointer': ['observations', 10],
                              'url_key': 'source_url',
                              'url': 'https://ddowiki.com/page/Slave_Lords_Crafting',
                              'revision_pointer': ['displayed_permalink'],
                              'revision': 'https://ddowiki.com/index.php?title=Slave_Lords_Crafting&oldid=715666',
                              'observed_pointer': ['started_at_utc'],
                              'observed': '2026-11-16T05:14:35.225Z',
                              'source_contract': 'selected-gear-doubleshot-v1',
                              'freshness_limit': 'Original scoped browser observation 2026-11-16T05:14:35.225Z '
                                                 'through 2026-11-16T05:14:51.536Z. Cache notice is absent '
                                                 'from this scoped observation; no value is inferred. The '
                                                 'record is an attributed transcription, not complete DOM/HTTP '
                                                 'bytes or live-game verification. Displayed permalink was '
                                                 'observed, not independently reopened; transcluded tooltips '
                                                 'may have separate revision histories. The separately timed '
                                                 'Slave Lords metadata supplement remains linked context, '
                                                 'never a backdated standalone source. Later adoption does not '
                                                 'refresh original observations or prior evidence grades.'}}

SOURCE_BINDINGS = {'ds-augment-system-20261116': (0, ['exact_excerpts', 'set_augment_rules']),
 'ds-quickblade-20261116': (1, ['exact_item_fields', 'Description']),
 'ds-set-table-20261116': (2, ['exact_quickblade_row']),
 'ds-set-rules-20261116': (3, ['exact_excerpts', 'augment_sets']),
 'ds-goggles-host-20261116': (4, ['exact_doubleshot_clause']),
 'ds-chains-host-20261116': (5, ['exact_excerpts', 'augment_channel']),
 'ds-yeenoghu-host-20261116': (6, ['exact_green_tooltip']),
 'ds-green-recipe-20261116': (10, ['exact_excerpts', 'green_recipe_row'])}

SOURCE_SHA256 = {'ds-augment-system-20261116': '6db0b84a30ab15d41769dd70a65e794a226855a015f7c2f18e48a34b724ca811',
 'ds-quickblade-20261116': '4d5129f5de36f089eca4be67cf1b0cc5bdf32643007028abe9456f5d00798bf5',
 'ds-set-table-20261116': '75543334d368ddb0f009508f6de705e4984198de400342892cc60d2f880def94',
 'ds-set-rules-20261116': '125b93addf34cb75f749f61a83d09522aa184caeeb514f4c5677890c8ce8c14f',
 'ds-goggles-host-20261116': 'ecf6ff92b086aab61e1dceab2c57080ac74cfd7ad64c00580a87697ed257d47c',
 'ds-chains-host-20261116': '43591fd8452c7afb53069bfb51813f484ac8251a86058fad0971fe1cdb3bdf46',
 'ds-yeenoghu-host-20261116': '01491357107abecea41de74478ca64d1f43deeeff6272b6c5c0ff6cb77dc675c',
 'ds-green-recipe-20261116': 'd4a20476bbed0b3b8b8c72e39f7abbc5dca1aa7b65f9d4e3a8eaece7c369037d'}

OBSERVATION_IDS = {'ds-augment-system-20261116': 'augment-system',
 'ds-quickblade-20261116': 'quickblade-own-item',
 'ds-set-table-20261116': 'set-augment-table-direct',
 'ds-set-rules-20261116': 'named-sets-quickblade-context',
 'ds-goggles-host-20261116': 'goggles-host-and-definition',
 'ds-chains-host-20261116': 'chains-host',
 'ds-yeenoghu-host-20261116': 'yeenoghu-host',
 'ds-green-recipe-20261116': 'slave-lords-crafted-green-slot'}

PROOF = {'contract': 'selected-gear-doubleshot-v1',
 'method': 'three-selected-equipped-hosts',
 'sources': {'system': 'ds-augment-system-20261116',
             'item': 'ds-quickblade-20261116',
             'table': 'ds-set-table-20261116',
             'set_rules': 'ds-set-rules-20261116',
             'goggles_host': 'ds-goggles-host-20261116',
             'chains_host': 'ds-chains-host-20261116',
             'artifact_host': 'ds-yeenoghu-host-20261116',
             'green_recipe': 'ds-green-recipe-20261116'}}

COMPONENT_CORES = {'goggles-ds': {'id': 'goggles-ds',
                'stat': 'Doubleshot',
                'amount': 9,
                'bonus_type': 'Enhancement',
                'host': 'Goggles',
                'source': 'goggles-ds',
                'value_pattern': '(?P<value>9)% Enhancement bonus',
                'type_evidence': 'Enhancement bonus to Doubleshot',
                'state': 'verified',
                'requires': [],
                'channel': 'gear',
                'kit_min_level': 36},
 'ring-ds': {'id': 'ring-ds',
             'stat': 'Doubleshot',
             'amount': 3,
             'bonus_type': 'Quality',
             'host': 'Legendary Ring of Unnatural Accuracy',
             'source': 'ring-ds',
             'value_pattern': '(?P<value>3)% Quality bonus',
             'type_evidence': 'Quality bonus to Doubleshot',
             'state': 'verified',
             'requires': [],
             'channel': 'gear',
             'kit_min_level': 36},
 'boots-ds': {'id': 'boots-ds',
              'stat': 'Doubleshot',
              'amount': 5,
              'bonus_type': 'Insight',
              'host': 'Boots',
              'source': 'boots-ds',
              'value_pattern': '(?P<value>5)% Insight bonus',
              'type_evidence': 'Insight bonus to Doubleshot',
              'state': 'verified',
              'requires': [],
              'channel': 'gear',
              'kit_min_level': 36},
 'armor-ds': {'id': 'armor-ds',
              'stat': 'Doubleshot',
              'amount': 3,
              'bonus_type': 'Profane',
              'host': 'Armor',
              'source': 'armor-ds',
              'value_pattern': '\\+(?P<value>3)% Profane',
              'type_evidence': 'Profane',
              'state': 'verified',
              'requires': [],
              'channel': 'gear',
              'kit_min_level': 36},
 'quickblade-ds': {'id': 'quickblade-ds',
                   'stat': 'Doubleshot',
                   'amount': 15,
                   'bonus_type': 'Artifact',
                   'host': 'Quickblade: Goggles Colorless / Chains Green / Yeenoghu Green',
                   'source': '',
                   'value_pattern': '',
                   'type_evidence': '',
                   'state': 'verified',
                   'requires': [],
                   'channel': 'gear',
                   'kit_min_level': 36,
                   'definition_proof': {'contract': 'selected-gear-doubleshot-v1',
                                        'method': 'three-selected-equipped-hosts',
                                        'sources': {'system': 'ds-augment-system-20261116',
                                                    'item': 'ds-quickblade-20261116',
                                                    'table': 'ds-set-table-20261116',
                                                    'set_rules': 'ds-set-rules-20261116',
                                                    'goggles_host': 'ds-goggles-host-20261116',
                                                    'chains_host': 'ds-chains-host-20261116',
                                                    'artifact_host': 'ds-yeenoghu-host-20261116',
                                                    'green_recipe': 'ds-green-recipe-20261116'}}}}

CORE_SHA256 = {'goggles-ds': 'f8bbfabc2031969ac48d01607d8b2a65ed6fc17bf042159d9e560ee71dc4ee46',
 'ring-ds': '9c860a3c18c165640d87b72ad5d5a7ef411f42c5a255c764bc272a9c6861ceb7',
 'boots-ds': '9de79f467e493f0aa82ac1fb720c811f33a3411d01332818ba1711d5a808da79',
 'armor-ds': '9da7e9e3e563797b5b033fa7632c3bb0cc7d502f3958dcbd7e1be3ead4bc9ef2',
 'quickblade-ds': '85ad266c56e4127cc7dcb232cadacd39a16a8324faaef9705da61793dd2f69e0'}

RETAINED_SOURCE_SHA256 = {'goggles-ds': 'eb28b5740eed5f58979ba29fdad50c2bbd92435e2585635485273d13bbcfc259',
 'ring-ds': '8a7e9188cc421a7f0202665f495aac65d4e28d47447586f5df41e2b516b785d8',
 'boots-ds': 'a4481ec46e0542b5addad4633c25ab10e1f0d31b3025d1675e4096b96b104128',
 'armor-ds': 'aba1dbe426bd07384184bfa8a94dcc72259fd4d2a9131da182f193032dc8d69a',
 'tip179-live-20261115': '1a69280033c40da1478ebf5380e8b3be50a9369026eee721ecaeb7ea771a1355',
 'artifact': 'baacef6765852862f63a7d5427fbbf2b2e0159bd2d47f14d4b154c7a80bedfa5',
 'stack': '5d2bc6dc5301356455e78de391d1756c2947fb050d4121f490a50222a594b2b0'}

DS_RULE = {'id': 'doubleshot-selected-six-pairs',
 'source': 'tip179-live-20261115',
 'quote': 'Different types of bonuses stack',
 'kind': 'selected_pairs',
 'types': ['Enhancement', 'Quality', 'Insight', 'Profane'],
 'stats': ['Doubleshot'],
 'channel': 'gear',
 'component_pairs': [['goggles-ds', 'ring-ds'],
                     ['goggles-ds', 'boots-ds'],
                     ['goggles-ds', 'armor-ds'],
                     ['ring-ds', 'boots-ds'],
                     ['ring-ds', 'armor-ds'],
                     ['boots-ds', 'armor-ds']]}

ARTIFACT_RULE = {'id': 'artifact-other-types',
 'source': 'artifact',
 'quote': 'This bonus stacks with all other bonuses.',
 'kind': 'different_types',
 'types': ['Artifact'],
 'stats': ['*']}

RULES = {RULE_ID: DS_RULE}
RULE_IDS = frozenset(RULES)
PAIRS = tuple(tuple(pair) for pair in DS_RULE['component_pairs'])

HOSTS = {
    'goggles-ds': ('Legendary Goggles of the Archer', 'Goggles', 33, 36),
    'ring-ds': ('Legendary Ring of Unnatural Accuracy', 'Ring', 32, 32),
    'boots-ds': ('Legendary Coldlight Runners', 'Boots', 34, 34),
    'armor-ds': ("Light Armor of the Warblade's Reflection", 'Armor', 33, 33),
}
QUICKBLADE_PLACEMENTS = (
    ('Legendary Goggles of the Archer', 'Goggles', 33, 36, 2, 'Colorless'),
    ('Legendary Chains', 'Belt', 28, 30, 0, 'Green'),
    ("Yeenoghu's Reign", 'Bracers', 35, 36, 1, 'Green'),
)
SLOT_MAPPING = {
    'Legendary Goggles of the Archer': {'source': 'Eye', 'selection': 'Goggles'},
    'Legendary Chains': {'source': 'Waist', 'selection': 'Belt'},
    "Yeenoghu's Reign": {'source': 'Wrist', 'selection': 'Bracers'},
}
GREEN_COST = {'Legendary Staff Splinters': 100, 'Legendary Broken Shackles': 50,
              'Legendary Chain Links': 50, 'Legendary Broken Collars': 50}
STACK_CAVEAT = 'Benefits from the same family, like Fortification or False Life, do not stack.'


def _require(condition, message):
    if not condition:
        raise AssertionError(message)


def _fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _resolve(value, pointer):
    for part in pointer:
        value = value[part]
    return value


def _pinned_json(root, path, digest):
    root = Path(root)
    target = root / path
    _require(target.resolve().is_relative_to(root.resolve()), 'Source path escapes root')
    raw = target.read_bytes()
    _require(sha256(raw).hexdigest() == digest, 'Changed reviewed file: ' + path)
    return json.loads(raw)


def _packet(root):
    return _pinned_json(root, PACKET_PATH, PACKET_SHA256)


def bounded_source(source, sid=None):
    """New packet aliases cannot become unrelated direct-source definitions."""
    if not isinstance(source, dict):
        return sid in SOURCE_SHA256
    return (sid in SOURCE_SHA256 or source.get('path') == PACKET_PATH
            or source.get('sha256') == PACKET_SHA256
            or source.get('source_contract') == CONTRACT
            or _fingerprint(source) in SOURCE_SHA256.values()
            or any((source.get('url'), source.get('observed')) ==
                   (expected['url'], expected['observed']) for expected in NEW_SOURCES.values()))


def definition(component):
    proof = component.get('definition_proof')
    return isinstance(proof, dict) and proof.get('contract') == CONTRACT


def uses_contract(data):
    """A damaged upgrade cannot escape through an older rule profile."""
    return (any(bounded_source(source, sid) for sid, source in data.get('sources', {}).items())
            or any(rule.get('id') == RULE_ID for rule in data.get('rules', ()))
            or any(row.get('id') == 'quickblade-ds' and row.get('state') in {'verified', 'conditional'}
                   or definition(row) for row in data.get('components', ())))


def observation_context(source):
    """Admit started_at_utc only for these exact independently pinned bindings."""
    return (isinstance(source, dict) and _fingerprint(source) in SOURCE_SHA256.values()
            and source.get('observed_pointer') == ['started_at_utc']
            and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z',
                             source.get('observed', '')) is not None)


def _source_record(data, sid, root):
    _require(sid in SOURCE_SHA256, 'Unreviewed Doubleshot source identity')
    source = data['sources'][sid]
    _require(_fingerprint(source) == SOURCE_SHA256[sid], 'Changed Doubleshot source binding')
    index, suffix = SOURCE_BINDINGS[sid]
    pointer = ['observations', index]
    record = _resolve(_packet(root), pointer)
    _require(record['id'] == OBSERVATION_IDS[sid], 'Wrong scoped observation')
    _require(source['path'] == PACKET_PATH and source['sha256'] == PACKET_SHA256
             and source['source_contract'] == CONTRACT, 'Wrong source contract')
    _require(source['record_pointer'] == pointer and source['pointer'] == pointer + suffix
             and source['quote'] == _resolve(record, suffix), 'Changed or joined source clause')
    _require(source['url_key'] == 'source_url' and source['url'] == record['source_url']
             and source['revision_pointer'] == ['displayed_permalink']
             and source['revision'] == record['displayed_permalink'], 'Wrong source page or revision')
    parsed = urlparse(source['revision'])
    query = parse_qs(parsed.query)
    _require((parsed.scheme, parsed.netloc, parsed.path) == ('https', 'ddowiki.com', '/index.php')
             and set(query) == {'title', 'oldid'} and len(query['oldid']) == 1
             and query['oldid'][0].isdigit(), 'Unqualified Wiki revision')
    _require(observation_context(source) and source['observed'] == record['started_at_utc']
             and record['started_at_utc'] <= record['ended_at_utc'], 'Unbound observation interval')
    return record


def validate_source(data, sid, root=ROOT):
    try:
        _source_record(data, sid, root)
        return True
    except FAILURES:
        return False


def _existing_record(data, sid, root):
    """Read original metadata and actual bytes, never a refreshed source alias."""
    _require(sid in RETAINED_SOURCE_SHA256, 'Unreviewed retained source')
    source = data['sources'][sid]
    _require(_fingerprint(source) == RETAINED_SOURCE_SHA256[sid], 'Changed original source: ' + sid)
    packet = _pinned_json(root, source['path'], source['sha256'])
    record = _resolve(packet, source['record_pointer'])
    clause = _resolve(packet, source['pointer'])
    _require(clause == source['quote'] and source['url'] == record[source['url_key']]
             and source['revision'] == _resolve(record, source['revision_pointer'])
             and source['observed'] == _resolve(record, source['observed_pointer']),
             'Retained source does not resolve to its original context')
    oldid = parse_qs(urlparse(source['revision']).query).get('oldid', ())
    _require(len(oldid) == 1 and oldid[0].isdigit()
             and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z', source['observed']),
             'Missing retained observation or revision')
    binding = _packet(root)['retained_source_bindings'][sid]
    _require(binding['metadata_fingerprint'] == RETAINED_SOURCE_SHA256[sid]
             and binding['path'] == source['path'] and binding['sha256'] == source['sha256']
             and binding['record_pointer'] == source['record_pointer']
             and binding['quote_pointer'] == source['pointer']
             and binding['source_url'] == source['url'] and binding['revision'] == source['revision']
             and binding['observed'] == source['observed'], 'Changed retained adoption binding')
    anchor = binding['exact_fragment']
    offset = binding['fragment_start_character']
    _require(clause[offset:offset + len(anchor)] == anchor, 'Missing retained exact fragment')
    return record


def _selection(root):
    return _pinned_json(root, MANIFEST_PATH, MANIFEST_SHA256)


def _selected_context(root):
    """Verify intended equipment/occupancy, without claiming owned game state."""
    data = _selection(root)
    packet = _packet(root)
    _require(data['selection']['id'] == 'artifact-wisdom-canonical-spot-luck'
             and data['selection']['full_kit_ml'] == 36 and data['query']['race'] == 'Human'
             and data['selection']['primary_bow'] == 'Legendary Calamitous Longbow', 'Changed selected kit')
    items = data['items']
    _require(len({item['id'] for item in items}) == len(items), 'Duplicate selected host')
    by_id = {item['id']: item for item in items}
    _require([item['id'] for item in items if item['minor_artifact']] == ["Yeenoghu's Reign"],
             'Changed sole Minor Artifact')
    for cid, (name, slot, base_ml, filled_ml) in HOSTS.items():
        item = by_id[name]
        _require((item['slot'], item['base_ml'], item['filled_ml']) == (slot, base_ml, filled_ml),
                 'Changed native host applicability')
        expected = COMPONENT_CORES[cid]
        if cid == 'armor-ds':
            _require(any(a['stat'] == 'Shadow Striker' and a['type'] == 'Bool' and a['value'] == 1
                         for a in item['native_affixes']), 'Lost native Shadow Striker')
        else:
            native = [a for a in item['native_affixes'] if a['stat'] == 'Doubleshot']
            _require(len(native) == 1 and (native[0]['type'], native[0]['value']) ==
                     (expected['bonus_type'], expected['amount']), 'Changed selected native Doubleshot')
        model = [a for a in item['model_affixes'] if a['stat'] == 'Doubleshot']
        _require(model == [{'stat': 'Doubleshot', 'type': expected['bonus_type'], 'value': expected['amount']}],
                 'Changed native contribution accounting')
    groups = [group for group in data['augment_sets'] if group['name'] == 'Quickblade']
    _require(len(groups) == 1, 'Missing or duplicate Quickblade set')
    group = groups[0]
    expected_places = [{'host': name, 'color': color} for name, _, _, _, _, color in QUICKBLADE_PLACEMENTS]
    _require(group['threshold'] == 3 and group['placements'] == expected_places,
             'Quickblade requires three exact distinct hosts')
    _require([e for e in group['effects'] if e['stat'] == 'Doubleshot'] ==
             [{'stat': 'Doubleshot', 'type': 'Artifact', 'value': 15}], 'Changed once-only set reward')
    _require(packet['selected_occupancy']['selected_set_record'] == group
             and packet['explicit_slot_mapping'] == SLOT_MAPPING, 'Changed selected interpretation')
    expected_fill = {'kind': 'set-augment', 'id': 'Quickblade', 'color': 'Colorless', 'ml': 30, 'affixes': []}
    found = []
    for name, slot, base_ml, filled_ml, index, color in QUICKBLADE_PLACEMENTS:
        item = by_id[name]
        _require((item['slot'], item['base_ml'], item['filled_ml']) == (slot, base_ml, filled_ml),
                 'Changed Quickblade host or level')
        sockets = [socket for socket in item['sockets'] if socket['index'] == index]
        _require(len(sockets) == 1 and sockets[0]['color'] == color and sockets[0]['fill'] == expected_fill,
                 'Wrong ordinary slot or selected Quickblade copy')
        set_fills = [socket for socket in item['sockets'] if socket['fill']['kind'] == 'set-augment']
        _require(set_fills == sockets, 'Competing selected set augment on Quickblade host')
        found.append((name, index))
    actual = [(item['id'], socket['index']) for item in items for socket in item['sockets']
              if socket['fill']['id'] == 'Quickblade']
    _require(actual == found and len({name for name, _ in found}) == 3, 'Wrong equipped-set copy accounting')
    all_places = [p['host'] for g in data['augment_sets'] for p in g['placements']]
    _require(all(all_places.count(name) == 1 for name, _ in found), 'Multiple selected sets on one host')
    chains = by_id['Legendary Chains']
    _require(len(chains['sockets']) == 1 and len(chains['crafts']) == 4
             and {c['slot'] for c in chains['crafts']} == {'Prefix', 'Suffix', 'Bonus', 'Extra'},
             'Invented second socket or credited native Slavers set')
    prerequisites = [row for row in data['construction_prerequisites'] if row['host'] == 'Legendary Chains']
    _require(len(prerequisites) == 1
             and prerequisites[0]['communityCorroboratedIngredients'] == GREEN_COST
             and prerequisites[0] == packet['selected_occupancy']['construction_prerequisite']
             and "Green Augment Slot upgrade before placing the Quickblade set augment" in prerequisites[0]['requirement'],
             'Missing selected Green-slot construction prerequisite')
    loadout = _pinned_json(root, LOADOUT_PATH, LOADOUT_SHA256)
    catalog = loadout['catalog_metadata']['items']
    for name, _ in found:
        matches = [item for item in catalog if item['id'] == name]
        _require(len(matches) == 1 and matches[0]['native_sets'] == [], 'Changed selected native-set credit')
    return by_id


def _native(data, component, root):
    cid = component['id']
    record = _existing_record(data, cid, root)
    source = data['sources'][cid]
    amount, kind = component['amount'], component['bonus_type']
    suffix = r'Doublestrike and Doubleshot' if cid == 'armor-ds' else 'Doubleshot'
    matches = re.findall(r'\+?(\d+)% ' + re.escape(kind) + r' bonus to ' + suffix + r'\b', source['quote'])
    _require(matches == [str(amount)], 'Wrong native numeric/type/stat clause')
    base_ml = HOSTS[cid][2]
    _require(any(re.fullmatch(r'Minimum\s+level\s+' + str(base_ml), text, re.I)
                 for text in record['excerpts']), 'Missing native host base level')


def _quickblade(data, component, root):
    _require(component['definition_proof'] == PROOF, 'Changed Quickblade proof roles or method')
    records = {role: _source_record(data, sid, root) for role, sid in PROOF['sources'].items()}
    own = records['item']['exact_item_fields']
    _require(own['Minimum Level'] == '30' and own['Augment Type'] == 'Colorless', 'Wrong Quickblade variant')
    _require(re.search(r'3 pieces equipped: \+15% Artifact bonus to Doublestrike and Doubleshot\b', own['Description'])
             and 'override its Set Bonus to the Quickblade set' in own['Description'], 'Missing typed threshold reward')
    table = records['table']
    _require(table['headers'] == ['Set Augment', 'Color', 'ML', 'Items to Consume', 'Set bonus effect', 'Item drop sites']
             and table['observed_row_display'] == 'table-row'
             and table['exact_quickblade_row'].startswith('Set Augment: Quickblade\tColorless\t30\t')
             and '3 Pieces Equipped: +15% Artifact bonus to Doublestrike and Doubleshot' in table['exact_quickblade_row'],
             'Wrong or unobserved headed set row')
    rules = records['set_rules']['exact_excerpts']
    _require('items in that same "set" are worn together' in rules['activation']
             and 'lost if the number of items worn falls below the minimum' in rules['deactivation']
             and 'does not give additional bonuses unless the set bonus states such' in rules['no_extra_reward']
             and 'slot them into 3 items across equipment slots of one character' in rules['augment_sets']
             and 'will suppress those sets while the Set Augment is slotted' in rules['augment_sets'],
             'Missing equipped/distinct-host/once-only/set-suppression conditions')
    system = records['system']['exact_excerpts']
    _require('Colorless augments can be used anywhere' in system['ordinary_colorless']
             and 'These level 30 Set augments' in system['set_augment_rules']
             and 'unique three-piece item set' in system['set_augment_rules']
             and 'will suppress those sets while the Set Augment is slotted' in system['set_augment_rules']
             and 'increases the slotted item’s minimum level to the level of the slotted augment' in system['minimum_level']
             and "unless the item's minimum level is already equal or higher" in system['minimum_level'],
             'Missing ordinary-slot, level or set-system premise')
    goggles, chains, artifact = (records[r] for r in ('goggles_host', 'chains_host', 'artifact_host'))
    _require(goggles['exact_item_fields']['Slot'] == SLOT_MAPPING['Legendary Goggles of the Archer']['source']
             and goggles['exact_item_fields']['Minimum level'] == '33'
             and 'Colorless Augment Slot' in goggles['observed_slot_labels']
             and 'Colorless' in goggles['exact_slot_tooltips'], 'Wrong Goggles host slot')
    _require(chains['exact_item_fields']['Minimum level'] == '28'
             and chains['exact_item_fields']['Slot'] == 'Neck'
             and 'Neck slot or the Waist slot' in chains['exact_excerpts']['equip_choice']
             and chains['exact_excerpts']['augment_channel'] ==
             "Legendary Slaver's Augment Slot: Apply a Slaver's shard to this item.", 'Wrong Chains host/channel')
    _require(artifact['exact_item_fields']['Slot'] == SLOT_MAPPING["Yeenoghu's Reign"]['source']
             and artifact['exact_item_fields']['Minimum level'] == '35'
             and 'Green Augment Slot' in artifact['observed_slot_labels']
             and artifact['exact_green_tooltip'] == 'Blue, Green, Yellow, and/or Colorless'
             and 'This Minor Artifact' in artifact['exact_minor_artifact_tip'], 'Wrong Artifact host slot')
    recipe = records['green_recipe']
    _require(recipe['headers'] == ['Group', 'Enchantment name', 'Enchantment value', 'Ingredient cost',
                                    'Heroic\nML 8', 'Legendary\nML 28', 'Heroic', 'Legendary'],
             'Lost Legendary recipe column identity')
    row = recipe['exact_excerpts']['green_recipe_row']
    _require(re.match(r'^Green\s+Augment\s+Slot\s', row), 'Wrong slot recipe row')
    ingredients = re.findall(r'(\d+)\s+(Legendary (?:Staff Splinters|Broken Shackles|Chain Links|Broken Collars))', row)
    _require(len(ingredients) == 4 and {name: int(count) for count, name in ingredients} == GREEN_COST
             and recipe['derived_legendary_recipe'] == GREEN_COST
             and 'augment slot (clear, yellow, blue, or green)' in recipe['exact_excerpts']['crafting_channels'],
             'Wrong Legendary Green construction')
    # This later observation has its own time, and is related context rather
    # than a synthetic standalone source with the earlier record's revision.
    supplement = _packet(root)['observations'][11]
    _require(recipe['metadata_supplement_id'] == supplement['id'] == 'slave-lords-metadata-supplement'
             and supplement['source_url'] == recipe['source_url']
             and supplement['started_at_utc'] == '2026-11-16T05:15:00.324Z'
             and supplement['ended_at_utc'] == '2026-11-16T05:15:00.346Z'
             and recipe['ended_at_utc'] < supplement['started_at_utc']
             and 'displayed_permalink' not in supplement
             and supplement['exact_green_slot_tooltip'] == 'Blue, Green, Yellow, and/or Colorless',
             'Changed or backdated related Green-slot context')


def validate_component(data, component, root=ROOT):
    try:
        cid = component['id']
        _require(cid in FAMILY_IDS and _fingerprint({k: v for k, v in component.items() if k != 'note'}) ==
                 CORE_SHA256[cid], 'Changed selected Doubleshot core')
        _selected_context(root)
        if cid == 'quickblade-ds':
            _quickblade(data, component, root)
        else:
            _native(data, component, root)
        return True
    except FAILURES:
        return False


def family_valid(data, stat='Doubleshot', arguments=(), root=ROOT):
    try:
        _require(stat == 'Doubleshot', 'Wrong selected family stat')
        rows = data['components']
        family = [row for row in rows if row['stat'] == stat and row['channel'] == 'gear']
        _require(len(family) == 5 and {row['id'] for row in family} == set(FAMILY_IDS),
                 'Missing, duplicate, extra or substituted Doubleshot member')
        selected = {}
        for cid in FAMILY_IDS:
            matches = [row for row in rows if row['id'] == cid]
            _require(len(matches) == 1 and validate_component(data, matches[0], root),
                     'Moved, duplicate or unqualified selected Doubleshot member')
            selected[cid] = matches[0]
        _require(all(argument == selected[argument['id']] for argument in arguments), 'Detached proof operand')
        return True
    except FAILURES:
        return False


def validate_rule_source(data, root=ROOT):
    try:
        tip = _existing_record(data, 'tip179-live-20261115', root)
        legacy_stack = _existing_record(data, 'stack', root)
        packet = _packet(root)
        context = packet['retained_stack_context']
        retained = _pinned_json(root, context['path'], context['sha256'])
        stack = _resolve(retained, context['record_pointer'])
        _require('Different types of bonuses stack' in tip['scoped_visible_text']
                 and tip['body_observation'] == packet['retained_tip179_context']['body_observation'],
                 'Lost affirmative different-type premise or original interval')
        _require(STACK_CAVEAT in legacy_stack['text']
                 and stack['source_url'] == context['source_url']
                 and stack['revision_link'] == context['revision_link']
                 and stack['body_observation'] == context['body_observation']
                 and STACK_CAVEAT in stack['scoped_visible_text']
                 and _resolve(retained, context['historical_interpretation_pointer']) == context['historical_interpretation'],
                 'Lost same-family caveat or historical interpretation')
        return True
    except FAILURES:
        return False


def validate_artifact_rule(data, rule, root=ROOT):
    try:
        _require(rule == ARTIFACT_RULE, 'Changed reused Artifact rule')
        record = _existing_record(data, 'artifact', root)
        _require(record['exact_source_sections'][0]['following_paragraph'] == ARTIFACT_RULE['quote']
                 and 'no longer stack with each other' in record['exact_source_sections'][1]['paragraph']
                 and record['body_observation'] == _packet(root)['retained_artifact_context']['body_observation'],
                 'Missing positive Artifact rule or its typed-history limit')
        return True
    except FAILURES:
        return False


def validate_pair(data, rule, stat, a, b, root=ROOT):
    try:
        _require(rule == DS_RULE and stat == a['stat'] == b['stat'] == 'Doubleshot'
                 and a['channel'] == b['channel'] == 'gear' and a['id'] != b['id']
                 and frozenset((a['id'], b['id'])) in {frozenset(pair) for pair in PAIRS},
                 'Unreviewed Doubleshot interaction')
        return family_valid(data, stat, (a, b), root) and validate_rule_source(data, root)
    except FAILURES:
        return False

