"""Eight exact selected ability definitions and four named WIS/CON interactions.

The new frozen audit retains its original investigation status. New proofs bind
its actual fragments/context and unchanged older observations to this selected
kit only; they never repair prior evidence or certify a whole character.
Skull remains a required conflicting family member, never a qualified operand.
Every public check rereads actual source and selection bytes without caching.
"""
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = 'selected-wisdom-constitution-v1'
PACKET_PATH = 'evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json'
PACKET_SHA256 = 'fae2de021955cdc4112c0f78f6ab3cbb77045375923d92f1c9f5a8cb95060d9d'
MANIFEST_PATH = 'tools/fixtures/wisdom-loadout/selection.json'
MANIFEST_SHA256 = '8223bd8e25ed9dc4ad9454439ead42dfb693cc008d18d0ddfeb270d33863c37d'

NEW_SOURCES = {'wiscon-nearly-complete-20261116': {'path': 'evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json',
                                     'sha256': 'fae2de021955cdc4112c0f78f6ab3cbb77045375923d92f1c9f5a8cb95060d9d',
                                     'pointer': ['observations', 1, 'exact_fragments', 2],
                                     'quote': 'Wisdom +15',
                                     'record_pointer': ['observations', 1],
                                     'url_key': 'source_url',
                                     'url': 'https://ddowiki.com/page/Nearly_Complete',
                                     'revision_pointer': ['revision_link'],
                                     'revision': 'https://ddowiki.com/index.php?title=Nearly_Complete&oldid=705751',
                                     'observed_pointer': ['body_observation', 'started_at_utc'],
                                     'observed': '2026-11-16T03:27:13.149Z',
                                     'source_contract': 'selected-wisdom-constitution-v1',
                                     'freshness_limit': 'Original scoped browser observation '
                                                        '2026-11-16T03:27:13.149Z through '
                                                        '2026-11-16T03:27:13.171Z. Literal cache notice: '
                                                        '(this is up to 5 hours old). The register preserves '
                                                        'exact short fragments and separately labelled '
                                                        'context, not a complete raw DOM archive. Displayed '
                                                        'permalink was observed, not independently reopened. '
                                                        'Later integration does not change the original '
                                                        'audit status or older evidence.'},
 'wiscon-claws-20261116': {'path': 'evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json',
                           'sha256': 'fae2de021955cdc4112c0f78f6ab3cbb77045375923d92f1c9f5a8cb95060d9d',
                           'pointer': ['observations', 2, 'exact_fragments', 0],
                           'quote': 'granting a +15 Enhancement bonus to Wisdom.',
                           'record_pointer': ['observations', 2],
                           'url_key': 'source_url',
                           'url': 'https://ddowiki.com/page/Item:Legendary_Burrowing_Claws',
                           'revision_pointer': ['revision_link'],
                           'revision': 'https://ddowiki.com/index.php?title=Item:Legendary_Burrowing_Claws&oldid=707232',
                           'observed_pointer': ['body_observation', 'started_at_utc'],
                           'observed': '2026-11-16T03:27:27.449Z',
                           'source_contract': 'selected-wisdom-constitution-v1',
                           'freshness_limit': 'Original scoped browser observation 2026-11-16T03:27:27.449Z '
                                              'through 2026-11-16T03:27:27.481Z. Literal cache notice: (this '
                                              'is up to 17 hours old). The register preserves exact short '
                                              'fragments and separately labelled context, not a complete raw '
                                              'DOM archive. Displayed permalink was observed, not '
                                              'independently reopened. Later integration does not change the '
                                              'original audit status or older evidence.'},
 'wiscon-queen-20261116': {'path': 'evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json',
                           'sha256': 'fae2de021955cdc4112c0f78f6ab3cbb77045375923d92f1c9f5a8cb95060d9d',
                           'pointer': ['observations', 3, 'exact_fragments', 0],
                           'quote': 'granting a +7 Insight bonus to Constitution.',
                           'record_pointer': ['observations', 3],
                           'url_key': 'source_url',
                           'url': 'https://ddowiki.com/page/Item:The_Queen_of_Rot',
                           'revision_pointer': ['revision_link'],
                           'revision': 'https://ddowiki.com/index.php?title=Item:The_Queen_of_Rot&oldid=715898',
                           'observed_pointer': ['body_observation', 'started_at_utc'],
                           'observed': '2026-11-16T03:27:48.675Z',
                           'source_contract': 'selected-wisdom-constitution-v1',
                           'freshness_limit': 'Original scoped browser observation 2026-11-16T03:27:48.675Z '
                                              'through 2026-11-16T03:27:48.698Z. Literal cache notice: (this '
                                              'is up to 17 hours old). The register preserves exact short '
                                              'fragments and separately labelled context, not a complete raw '
                                              'DOM archive. Displayed permalink was observed, not '
                                              'independently reopened. Later integration does not change the '
                                              'original audit status or older evidence.'},
 'wiscon-solar-20261116': {'path': 'evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json',
                           'sha256': 'fae2de021955cdc4112c0f78f6ab3cbb77045375923d92f1c9f5a8cb95060d9d',
                           'pointer': ['observations', 4, 'exact_fragments', 0],
                           'quote': 'Slotted Effect: +4 Artifact Bonus to Constitution.',
                           'record_pointer': ['observations', 4],
                           'url_key': 'source_url',
                           'url': 'https://ddowiki.com/page/Item:Solar_Gem_of_Constitution_(Legendary)',
                           'revision_pointer': ['revision_link'],
                           'revision': 'https://ddowiki.com/index.php?title=Item:Solar_Gem_of_Constitution_(Legendary)&oldid=691768',
                           'observed_pointer': ['body_observation', 'started_at_utc'],
                           'observed': '2026-11-16T03:28:06.959Z',
                           'source_contract': 'selected-wisdom-constitution-v1',
                           'freshness_limit': 'Original scoped browser observation 2026-11-16T03:28:06.959Z '
                                              'through 2026-11-16T03:28:06.980Z. Literal cache notice: (this '
                                              'is up to 10 hours old). The register preserves exact short '
                                              'fragments and separately labelled context, not a complete raw '
                                              'DOM archive. Displayed permalink was observed, not '
                                              'independently reopened. Later integration does not change the '
                                              'original audit status or older evidence.'},
 'wiscon-dolorous-20261116': {'path': 'evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json',
                              'sha256': 'fae2de021955cdc4112c0f78f6ab3cbb77045375923d92f1c9f5a8cb95060d9d',
                              'pointer': ['observations', 5, 'exact_fragments', 0],
                              'quote': 'Slotted Effect: +3 Quality bonus to Constitution.',
                              'record_pointer': ['observations', 5],
                              'url_key': 'source_url',
                              'url': 'https://ddowiki.com/page/Item:Dolorous_Quality_Constitution_(legendary)',
                              'revision_pointer': ['revision_link'],
                              'revision': 'https://ddowiki.com/index.php?title=Item:Dolorous_Quality_Constitution_(legendary)&oldid=702234',
                              'observed_pointer': ['body_observation', 'started_at_utc'],
                              'observed': '2026-11-16T03:28:34.938Z',
                              'source_contract': 'selected-wisdom-constitution-v1',
                              'freshness_limit': 'Original scoped browser observation '
                                                 '2026-11-16T03:28:34.938Z through 2026-11-16T03:28:34.957Z. '
                                                 'Literal cache notice: (this is up to 15 hours old). The '
                                                 'register preserves exact short fragments and separately '
                                                 'labelled context, not a complete raw DOM archive. '
                                                 'Displayed permalink was observed, not independently '
                                                 'reopened. Later integration does not change the original '
                                                 'audit status or older evidence.'},
 'wiscon-coldlight-host-20261116': {'path': 'evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json',
                                    'sha256': 'fae2de021955cdc4112c0f78f6ab3cbb77045375923d92f1c9f5a8cb95060d9d',
                                    'pointer': ['observations', 6, 'exact_fragments', 0],
                                    'quote': 'Lamordia: Dolorous Slot (Accessory)',
                                    'record_pointer': ['observations', 6],
                                    'url_key': 'source_url',
                                    'url': 'https://ddowiki.com/page/Item:Legendary_Coldlight_Runners',
                                    'revision_pointer': ['revision_link'],
                                    'revision': 'https://ddowiki.com/index.php?title=Item:Legendary_Coldlight_Runners&oldid=685297',
                                    'observed_pointer': ['body_observation', 'started_at_utc'],
                                    'observed': '2026-11-16T03:28:57.431Z',
                                    'source_contract': 'selected-wisdom-constitution-v1',
                                    'freshness_limit': 'Original scoped browser observation '
                                                       '2026-11-16T03:28:57.431Z through '
                                                       '2026-11-16T03:28:57.450Z. Literal cache notice: '
                                                       '(this is up to 16 hours old). The register preserves '
                                                       'exact short fragments and separately labelled '
                                                       'context, not a complete raw DOM archive. Displayed '
                                                       'permalink was observed, not independently reopened. '
                                                       'Later integration does not change the original audit '
                                                       'status or older evidence.'},
 'wiscon-reflection-host-20261116': {'path': 'evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json',
                                     'sha256': 'fae2de021955cdc4112c0f78f6ab3cbb77045375923d92f1c9f5a8cb95060d9d',
                                     'pointer': ['observations', 7, 'exact_fragments', 0],
                                     'quote': 'Sun Augment Slot',
                                     'record_pointer': ['observations', 7],
                                     'url_key': 'source_url',
                                     'url': 'https://ddowiki.com/page/Item:Light_Armor_of_the_Warblade%27s_Reflection',
                                     'revision_pointer': ['revision_link'],
                                     'revision': 'https://ddowiki.com/index.php?title=Item:Light_Armor_of_the_Warblade%27s_Reflection&oldid=685449',
                                     'observed_pointer': ['additional_slot_observation', 'started_at_utc'],
                                     'observed': '2026-11-16T03:30:06.826Z',
                                     'source_contract': 'selected-wisdom-constitution-v1',
                                     'freshness_limit': 'Original explicit Sun-slot browser observation '
                                                        '2026-11-16T03:30:06.826Z through '
                                                        '2026-11-16T03:30:06.875Z; the item-context '
                                                        'observation is separately retained at '
                                                        '2026-11-16T03:29:42.853Z through '
                                                        '2026-11-16T03:29:42.871Z. Literal cache notice: '
                                                        '(this is up to 6 hours old). Exact short fragments '
                                                        'and separately labelled context are retained, not a '
                                                        'complete raw DOM archive. Displayed permalink was '
                                                        'observed, not independently reopened. Later '
                                                        'integration does not change the original audit '
                                                        'status or older evidence.'},
 'wiscon-sun-system-20261116': {'path': 'evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json',
                                'sha256': 'fae2de021955cdc4112c0f78f6ab3cbb77045375923d92f1c9f5a8cb95060d9d',
                                'pointer': ['observations', 11, 'exact_fragments', 0],
                                'quote': 'Players can slot Lunar and Solar Gems into these slots to provide '
                                         'their bonuses.',
                                'record_pointer': ['observations', 11],
                                'url_key': 'source_url',
                                'url': 'https://ddowiki.com/page/Lunar_and_Solar_Gems',
                                'revision_pointer': ['revision_link'],
                                'revision': 'https://ddowiki.com/index.php?title=Lunar_and_Solar_Gems&oldid=707220',
                                'observed_pointer': ['body_observation', 'started_at_utc'],
                                'observed': '2026-11-16T03:33:55.511Z',
                                'source_contract': 'selected-wisdom-constitution-v1',
                                'freshness_limit': 'Original scoped browser observation '
                                                   '2026-11-16T03:33:55.511Z through '
                                                   '2026-11-16T03:33:57.629Z. Literal cache notice: (this is '
                                                   'up to 12 hours old). The register preserves exact short '
                                                   'fragments and separately labelled context, not a '
                                                   'complete raw DOM archive. Displayed permalink was '
                                                   'observed, not independently reopened. Later integration '
                                                   'does not change the original audit status or older '
                                                   'evidence.'}}

SOURCE_BINDINGS = {'wiscon-nearly-complete-20261116': (1, ['exact_fragments', 2]),
 'wiscon-claws-20261116': (2, ['exact_fragments', 0]),
 'wiscon-queen-20261116': (3, ['exact_fragments', 0]),
 'wiscon-solar-20261116': (4, ['exact_fragments', 0]),
 'wiscon-dolorous-20261116': (5, ['exact_fragments', 0]),
 'wiscon-coldlight-host-20261116': (6, ['exact_fragments', 0]),
 'wiscon-reflection-host-20261116': (7, ['exact_fragments', 0]),
 'wiscon-sun-system-20261116': (11, ['exact_fragments', 0])}

SOURCE_SHA256 = {'wiscon-nearly-complete-20261116': '4310ecb6cc4c44d9f3b9bbfe73cfbae57ec6c01bbc6ae2a510f73bfb7117e590',
 'wiscon-claws-20261116': '0332993d150659b263550857ee7d9dafe6902953a7b58e27db89b5b637c234fd',
 'wiscon-queen-20261116': '1830bc76e0a49d429056d05447ccc27e2895115528b0b74d045a158815ed3df1',
 'wiscon-solar-20261116': '033b978cef28c6c0ffc167eb373d75bc838c9bc09821f376f7cc805dc25718b8',
 'wiscon-dolorous-20261116': '30d992d7e3772f5e3cee88dbe15b4295dd2a1b9e1be1db84049323a63283932e',
 'wiscon-coldlight-host-20261116': 'c0e8edef7e52c1afaf905665e80b2fb98e1b5566bb61c09f0eadbd4ee7c54d34',
 'wiscon-reflection-host-20261116': 'fbf759129cd019d6c4da24db966b20b3291f1fa27cb8ca541a255bd1ed1e7496',
 'wiscon-sun-system-20261116': '57654a4894994169acd6366887e4738b05dba3f06143de18d437ee2483f0cf44'}

REUSED_SOURCE_SHA256 = {'globe-int-live-20261115': '53c8207000552fa7541f6761aa87aae61bfa3f4ce4cc51f3ea70e9c814fa9613',
 'celestial-profane-int-live-20261115': 'c657f4353b3a013f1f5f0ac95669dce6ba31d02aeefe742d28ed590ee8e633d7',
 'chains-intelligence-membership-20261115': '3a101d18d89e3c08c1cad9115ae0917b91567d8e2f9c48f5fd881d724f097cae',
 'tip179-live-20261115': '1a69280033c40da1478ebf5380e8b3be50a9369026eee721ecaeb7ea771a1355',
 'artifact': 'baacef6765852862f63a7d5427fbbf2b2e0159bd2d47f14d4b154c7a80bedfa5',
 'exceptional': '10d870a299cc5f47dda6b7fe63be4c860b1360633aace3632b1d60d2a3c8edaa'}

CONFLICT_SOURCE_SHA256 = {'skull-con': 'd0fa468a2fbbac6aadf0a91e3ff3b7cb873ec097a5bcb64ac7f839f99f056a12',
 'nearly-complete': 'ed6a67d5efb6de9ba311f6978457594a8efd7edebfb1027f0befb2fcd9322f3a'}

PROOFS = {'claws-wisdom': {'contract': 'selected-wisdom-constitution-v1',
                  'method': 'selected-nearly-complete',
                  'sources': {'item': 'wiscon-claws-20261116', 'craft': 'wiscon-nearly-complete-20261116'}},
 'queen-insight-con': {'contract': 'selected-wisdom-constitution-v1',
                       'method': 'selected-nearly-complete',
                       'sources': {'item': 'wiscon-queen-20261116',
                                   'craft': 'wiscon-nearly-complete-20261116'}},
 'boots-quality-con': {'contract': 'selected-wisdom-constitution-v1',
                       'method': 'selected-lamordia-accessory',
                       'sources': {'item': 'wiscon-dolorous-20261116',
                                   'host': 'wiscon-coldlight-host-20261116'}},
 'solar-con': {'contract': 'selected-wisdom-constitution-v1',
               'method': 'selected-sun-socket',
               'sources': {'item': 'wiscon-solar-20261116',
                           'host': 'wiscon-reflection-host-20261116',
                           'slot_rule': 'wiscon-sun-system-20261116'}},
 'celestial-profane-wisdom': {'contract': 'selected-wisdom-constitution-v1',
                              'method': 'selected-all-ability-membership',
                              'sources': {'item': 'celestial-profane-int-live-20261115',
                                          'membership': 'chains-intelligence-membership-20261115'}},
 'globe-wisdom': {'contract': 'selected-wisdom-constitution-v1',
                  'method': 'selected-colorless-all-abilities',
                  'sources': {'item': 'globe-int-live-20261115'}},
 'celestial-profane-constitution': {'contract': 'selected-wisdom-constitution-v1',
                                    'method': 'selected-all-ability-membership',
                                    'sources': {'item': 'celestial-profane-int-live-20261115',
                                                'membership': 'chains-intelligence-membership-20261115'}},
 'globe-constitution': {'contract': 'selected-wisdom-constitution-v1',
                        'method': 'selected-colorless-all-abilities',
                        'sources': {'item': 'globe-int-live-20261115'}}}

COMPONENT_DEFINITIONS = {'globe-constitution': {'id': 'globe-constitution',
                        'stat': 'Constitution',
                        'amount': 1,
                        'bonus_type': 'Exceptional',
                        'host': 'Legendary Calamitous Longbow / Purple',
                        'source': '',
                        'value_pattern': '',
                        'type_evidence': '',
                        'state': 'verified',
                        'requires': [],
                        'channel': 'gear',
                        'kit_min_level': 36,
                        'definition_proof': {'contract': 'selected-wisdom-constitution-v1',
                                             'method': 'selected-colorless-all-abilities',
                                             'sources': {'item': 'globe-int-live-20261115'}}},
 'queen-insight-con': {'id': 'queen-insight-con',
                       'stat': 'Constitution',
                       'amount': 7,
                       'bonus_type': 'Insight',
                       'host': 'Cloak Nearly Complete',
                       'source': '',
                       'value_pattern': '',
                       'type_evidence': '',
                       'state': 'verified',
                       'requires': [],
                       'channel': 'gear',
                       'kit_min_level': 36,
                       'definition_proof': {'contract': 'selected-wisdom-constitution-v1',
                                            'method': 'selected-nearly-complete',
                                            'sources': {'item': 'wiscon-queen-20261116',
                                                        'craft': 'wiscon-nearly-complete-20261116'}}},
 'boots-quality-con': {'id': 'boots-quality-con',
                       'stat': 'Constitution',
                       'amount': 3,
                       'bonus_type': 'Quality',
                       'host': 'Legendary Coldlight Runners / Dolorous',
                       'source': '',
                       'value_pattern': '',
                       'type_evidence': '',
                       'state': 'verified',
                       'requires': [],
                       'channel': 'gear',
                       'kit_min_level': 36,
                       'definition_proof': {'contract': 'selected-wisdom-constitution-v1',
                                            'method': 'selected-lamordia-accessory',
                                            'sources': {'item': 'wiscon-dolorous-20261116',
                                                        'host': 'wiscon-coldlight-host-20261116'}}},
 'solar-con': {'id': 'solar-con',
               'stat': 'Constitution',
               'amount': 4,
               'bonus_type': 'Artifact',
               'host': 'Light Armor of the Warblade’s Reflection / Sun',
               'source': '',
               'value_pattern': '',
               'type_evidence': '',
               'state': 'verified',
               'requires': [],
               'channel': 'gear',
               'kit_min_level': 36,
               'definition_proof': {'contract': 'selected-wisdom-constitution-v1',
                                    'method': 'selected-sun-socket',
                                    'sources': {'item': 'wiscon-solar-20261116',
                                                'host': 'wiscon-reflection-host-20261116',
                                                'slot_rule': 'wiscon-sun-system-20261116'}}},
 'claws-wisdom': {'id': 'claws-wisdom',
                  'stat': 'Wisdom',
                  'amount': 15,
                  'bonus_type': 'Enhancement',
                  'host': 'Legendary Burrowing Claws / Nearly Complete',
                  'source': '',
                  'value_pattern': '',
                  'type_evidence': '',
                  'state': 'verified',
                  'requires': [],
                  'channel': 'gear',
                  'kit_min_level': 36,
                  'definition_proof': {'contract': 'selected-wisdom-constitution-v1',
                                       'method': 'selected-nearly-complete',
                                       'sources': {'item': 'wiscon-claws-20261116',
                                                   'craft': 'wiscon-nearly-complete-20261116'}}},
 'celestial-profane-constitution': {'id': 'celestial-profane-constitution',
                                    'stat': 'Constitution',
                                    'amount': 2,
                                    'bonus_type': 'Profane',
                                    'host': 'Legendary Celestial Sapphire Ring',
                                    'source': '',
                                    'value_pattern': '',
                                    'type_evidence': '',
                                    'state': 'verified',
                                    'requires': [],
                                    'channel': 'gear',
                                    'kit_min_level': 36,
                                    'definition_proof': {'contract': 'selected-wisdom-constitution-v1',
                                                         'method': 'selected-all-ability-membership',
                                                         'sources': {'item': 'celestial-profane-int-live-20261115',
                                                                     'membership': 'chains-intelligence-membership-20261115'}}},
 'celestial-profane-wisdom': {'id': 'celestial-profane-wisdom',
                              'stat': 'Wisdom',
                              'amount': 2,
                              'bonus_type': 'Profane',
                              'host': 'Legendary Celestial Sapphire Ring',
                              'source': '',
                              'value_pattern': '',
                              'type_evidence': '',
                              'state': 'verified',
                              'requires': [],
                              'channel': 'gear',
                              'kit_min_level': 36,
                              'definition_proof': {'contract': 'selected-wisdom-constitution-v1',
                                                   'method': 'selected-all-ability-membership',
                                                   'sources': {'item': 'celestial-profane-int-live-20261115',
                                                               'membership': 'chains-intelligence-membership-20261115'}}},
 'globe-wisdom': {'id': 'globe-wisdom',
                  'stat': 'Wisdom',
                  'amount': 1,
                  'bonus_type': 'Exceptional',
                  'host': 'Legendary Calamitous Longbow / Purple',
                  'source': '',
                  'value_pattern': '',
                  'type_evidence': '',
                  'state': 'verified',
                  'requires': [],
                  'channel': 'gear',
                  'kit_min_level': 36,
                  'definition_proof': {'contract': 'selected-wisdom-constitution-v1',
                                       'method': 'selected-colorless-all-abilities',
                                       'sources': {'item': 'globe-int-live-20261115'}}}}

SKULL_CORE = {'id': 'skull-con',
 'stat': 'Constitution',
 'amount': 16,
 'bonus_type': 'Enhancement',
 'host': 'Helmet',
 'source': 'skull-con',
 'value_pattern': '\\+(?P<value>16) Enhancement bonus to Constitution',
 'type_evidence': 'Enhancement bonus to Constitution',
 'state': 'conflicting',
 'requires': [],
 'channel': 'gear',
 'kit_min_level': 36,
 'related_sources': ['nearly-complete']}

CORE_SHA256 = {'globe-constitution': 'eb5e0e0aa57cb51b31787b8bc8ca0777bc04ba9d7fe2d770e54f4044afaa3964',
 'queen-insight-con': '13435e6bcc038d971062508baae37e8664593867178bec55816459f623a93281',
 'boots-quality-con': 'f34ef045cfe139a03afa7801e74760d26f6977d6fe94578f6f944ed2a2df57f1',
 'solar-con': 'fac5cefd3f5b8d27ee0f178e80780886b75dd7500b1e009479d4285dca5c28be',
 'claws-wisdom': '819fedd19f622ae0ada658b7e49858cb44ea09d0fd72c41ab3c7a76369194745',
 'celestial-profane-constitution': 'fca9850e034a03c9a9a5a58af1b77704084bd45a30662e3c00a27089d67047d4',
 'celestial-profane-wisdom': 'd652740d563bc66a395c08c023804ece282631d70069416daba76708842a6dcb',
 'globe-wisdom': '03dd023ed95af747240e6be47a09b2f1ada97fea6ce6c189e8e5fa724f3b69ae',
 'skull-con': 'f7ce8b6c1b4b32c10b19594371fc741d3c04f65721369987e4efedb099b8cc5f'}

FAMILIES = {'Wisdom': ('claws-wisdom', 'celestial-profane-wisdom', 'globe-wisdom'),
 'Constitution': ('skull-con',
                  'queen-insight-con',
                  'boots-quality-con',
                  'solar-con',
                  'celestial-profane-constitution',
                  'globe-constitution')}

RULES = {'wisdom-claws-celestial': {'id': 'wisdom-claws-celestial',
                            'source': 'tip179-live-20261115',
                            'quote': 'Different types of bonuses stack',
                            'kind': 'selected_pairs',
                            'types': ['Enhancement', 'Profane'],
                            'stats': ['Wisdom'],
                            'channel': 'gear',
                            'component_pairs': [['claws-wisdom', 'celestial-profane-wisdom']]},
 'constitution-queen-boots': {'id': 'constitution-queen-boots',
                              'source': 'tip179-live-20261115',
                              'quote': 'Different types of bonuses stack',
                              'kind': 'selected_pairs',
                              'types': ['Insight', 'Quality'],
                              'stats': ['Constitution'],
                              'channel': 'gear',
                              'component_pairs': [['queen-insight-con', 'boots-quality-con']]},
 'constitution-queen-celestial': {'id': 'constitution-queen-celestial',
                                  'source': 'tip179-live-20261115',
                                  'quote': 'Different types of bonuses stack',
                                  'kind': 'selected_pairs',
                                  'types': ['Insight', 'Profane'],
                                  'stats': ['Constitution'],
                                  'channel': 'gear',
                                  'component_pairs': [['queen-insight-con',
                                                       'celestial-profane-constitution']]},
 'constitution-boots-celestial': {'id': 'constitution-boots-celestial',
                                  'source': 'tip179-live-20261115',
                                  'quote': 'Different types of bonuses stack',
                                  'kind': 'selected_pairs',
                                  'types': ['Quality', 'Profane'],
                                  'stats': ['Constitution'],
                                  'channel': 'gear',
                                  'component_pairs': [['boots-quality-con',
                                                       'celestial-profane-constitution']]}}

EXISTING_RULES = {'artifact-other-types': {'id': 'artifact-other-types',
                          'source': 'artifact',
                          'quote': 'This bonus stacks with all other bonuses.',
                          'kind': 'different_types',
                          'types': ['Artifact'],
                          'stats': ['*']},
 'exceptional-other-types': {'id': 'exceptional-other-types',
                             'source': 'exceptional',
                             'quote': 'Exceptional bonuses are rare bonuses generally only found on high '
                                      'level loot. Exceptional bonuses stack with all other bonuses, but not '
                                      'with other exceptional bonuses.',
                             'kind': 'different_types',
                             'types': ['Exceptional'],
                             'stats': ['*']}}

DEFINITION_IDS = COMPONENT_IDS = frozenset(PROOFS)
FAMILY_IDS = frozenset(CORE_SHA256)
RULE_IDS = frozenset(RULES)


def _require(condition, message):
    if not condition:
        raise AssertionError(message)


def _fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _resolve(value, pointer):
    for part in pointer:
        value = json.loads(value) if part == '$json' else value[part]
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
    """Keep new packet aliases outside unrelated legacy inference routes."""
    return (sid in SOURCE_SHA256 or source.get('path') == PACKET_PATH
            or source.get('sha256') == PACKET_SHA256
            or source.get('source_contract') == CONTRACT
            or _fingerprint(source) in SOURCE_SHA256.values()
            or any((source.get('url'), source.get('observed')) ==
                   (expected['url'], expected['observed']) for expected in NEW_SOURCES.values()))


def uses_contract(data):
    """Detect incomplete upgrades even if one new proof or rule is removed."""
    return (any(bounded_source(source, sid) for sid, source in data.get('sources', {}).items())
            or any(rule.get('id') in RULE_IDS for rule in data.get('rules', ()))
            or any(row.get('id') in DEFINITION_IDS and row.get('state') in {'verified', 'conditional'}
                   or isinstance(row.get('definition_proof'), dict)
                   and row['definition_proof'].get('contract') == CONTRACT
                   for row in data.get('components', ())))


def observation_context(source):
    """The additional slot observation is admitted only through its exact pin."""
    return (_fingerprint(source) in SOURCE_SHA256.values()
            and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z',
                             source.get('observed', '')) is not None)


def _source_record(data, sid, root):
    _require(sid in SOURCE_SHA256, 'Unreviewed ability source identity')
    source = data['sources'][sid]
    _require(_fingerprint(source) == SOURCE_SHA256[sid], 'Changed ability source binding')
    index, suffix = SOURCE_BINDINGS[sid]
    pointer = ['observations', index]
    packet = _packet(root)
    record = _resolve(packet, pointer)
    _require(source['path'] == PACKET_PATH and source['sha256'] == PACKET_SHA256
             and source['source_contract'] == CONTRACT, 'Wrong source contract')
    _require(source['record_pointer'] == pointer and source['pointer'] == pointer + suffix
             and source['quote'] == _resolve(record, suffix), 'Changed or joined source clause')
    _require(source['url_key'] == 'source_url' and source['url'] == record['source_url']
             and source['revision_pointer'] == ['revision_link']
             and source['revision'] == record['revision_link'], 'Wrong source page or revision')
    parsed = urlparse(source['revision'])
    query = parse_qs(parsed.query)
    _require((parsed.scheme, parsed.netloc, parsed.path) == ('https', 'ddowiki.com', '/index.php')
             and set(query) == {'title', 'oldid'} and len(query['oldid']) == 1
             and query['oldid'][0].isdigit(), 'Unqualified Wiki revision')
    _require(observation_context(source)
             and source['observed'] == _resolve(record, source['observed_pointer']),
             'Missing genuine source-bound observation')
    return record


def validate_source(data, sid, root=ROOT):
    try:
        _source_record(data, sid, root)
        return True
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError):
        return False


def _existing_record(data, sid, root, *, conflict=False):
    """Read unchanged old bindings, including their original observation dates."""
    expected = CONFLICT_SOURCE_SHA256 if conflict else REUSED_SOURCE_SHA256
    _require(sid in expected, 'Unreviewed retained source identity')
    source = data['sources'][sid]
    _require(_fingerprint(source) == expected[sid], 'Changed retained source binding: ' + sid)
    packet = _pinned_json(root, source['path'], source['sha256'])
    record = _resolve(packet, source['record_pointer'])
    clause = _resolve(packet, source['pointer'])
    _require(isinstance(clause, str) and source['quote'] in clause,
             'Retained clause is absent from its exact context')
    _require(source['url'] == record[source['url_key']]
             and source['revision'] == _resolve(record, source['revision_pointer'])
             and source['observed'] == _resolve(record, source['observed_pointer']),
             'Retained provenance does not resolve to its original record')
    oldid = parse_qs(urlparse(source['revision']).query).get('oldid', ())
    _require(len(oldid) == 1 and oldid[0].isdigit()
             and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z', source['observed']),
             'Missing retained observation or revision')
    return record


def _retained_record(name, root):
    """Follow only exact reuse pointers inside the independently pinned audit."""
    audit = _packet(root)
    matches = [record for record in audit['reused_sources'] if record['id'] == name]
    _require(len(matches) == 1, 'Unreviewed retained premise')
    premise = matches[0]
    packet = _pinned_json(root, premise['path'], premise['sha256'])
    record = _resolve(packet, premise['record_pointer'])
    if name == 'lamordia-variant-match-retained':
        url, revision, observed = record['url'], record['permalink'], record['captureTimestamp']
    elif name in {'artifact-positive-rule-retained', 'exceptional-positive-rule-retained'}:
        url, revision = record['observed_normal_url'], record['revision_metadata']['permanent_link']
        observed = record['body_observation']['started_at_utc']
    else:
        url, revision = record['source_url'], record['revision_link']
        observed = record['body_observation']['started_at_utc']
    expected_observed = (premise['body_observation']['started_at_utc']
                         if 'body_observation' in premise else premise['observed_at_utc'])
    _require((url, revision, observed) ==
             (premise['source_url'], premise['revision_link'], expected_observed),
             'Retained identity or original observation changed')
    for anchor in premise['anchors']:
        text = _resolve(packet, anchor['pointer'])
        start = anchor['start_character']
        _require(text[start:start + anchor['length']] == anchor['exact_fragment'],
                 'Changed exact retained source anchor')
    return record


def _selection(root, cid):
    selected = _pinned_json(root, MANIFEST_PATH, MANIFEST_SHA256)
    _require(selected['selection']['id'] == 'artifact-wisdom-canonical-spot-luck'
             and selected['selection']['full_kit_ml'] == 36, 'Changed selected kit or applicability floor')
    _require([item['id'] for item in selected['items'] if item['minor_artifact']] == ["Yeenoghu's Reign"],
             'Changed selected Minor Artifact')
    host_id, slot, base, filled = {
        'claws-wisdom': ('Legendary Burrowing Claws', 'Gloves', 35, 35),
        'queen-insight-con': ('The Queen of Rot', 'Cloak', 35, 35),
        'boots-quality-con': ('Legendary Coldlight Runners', 'Boots', 34, 34),
        'solar-con': ("Light Armor of the Warblade's Reflection", 'Armor', 33, 33),
        'celestial-profane-wisdom': ('Legendary Celestial Sapphire Ring', 'Ring', 29, 30),
        'celestial-profane-constitution': ('Legendary Celestial Sapphire Ring', 'Ring', 29, 30),
        'globe-wisdom': ('Legendary Calamitous Longbow', 'Main Hand', 34, 34),
        'globe-constitution': ('Legendary Calamitous Longbow', 'Main Hand', 34, 34),
    }[cid]
    hosts = [item for item in selected['items'] if item['id'] == host_id]
    _require(len(hosts) == 1, 'Missing or duplicated selected host')
    host = hosts[0]
    _require((host['slot'], host['base_ml'], host['filled_ml']) == (slot, base, filled),
             'Changed selected host or level')
    definition = COMPONENT_DEFINITIONS[cid]
    affix = (definition['stat'], definition['bonus_type'], definition['amount'])
    if cid in {'claws-wisdom', 'queen-insight-con', 'boots-quality-con'}:
        family, craft_slot, category, name = {
            'claws-wisdom': ('Nearly Complete', 'Ability Score', 'Ability Score', 'Wisdom'),
            'queen-insight-con': ('Nearly Complete', 'Insightful Ability Score',
                                  'Insightful Ability Score', 'Constitution'),
            'boots-quality-con': ('Viktranium', 'Dolorous', 'Accessory',
                                  'Dolorous Quality Constitution (legendary)'),
        }[cid]
        crafts = [craft for craft in host['crafts'] if craft['slot'] == craft_slot]
        _require(len(crafts) == 1 and crafts[0] == {
            'host': host_id, 'family': family, 'slot': craft_slot, 'pool': None,
            'category': category, 'tier': 'legendary', 'name': name,
            'affixes': [{'stat': affix[0], 'type': affix[1], 'value': affix[2]}]},
            'Changed selected craft, tier, category or contribution')
    elif cid.startswith('celestial-profane-'):
        _require(host['crafts'] == [] and host['empty_craft_slots'] == [
            {'family': 'Nearly Finished', 'slot': 'Nearly Finished', 'selected': False}],
            'Optional ring craft is no longer deliberately empty')
        _require(any((a['stat'], a['type'], a['value'], a.get('via')) ==
                     affix + ('Profane Well Rounded',) for a in host['native_affixes']),
                 'Missing selected native all-ability contribution')
    else:
        index, color, augment, augment_color, ml = (
            (0, 'Sun', 'Solar Gem of Constitution (Legendary)', 'Sun', 30)
            if cid == 'solar-con' else (1, 'Purple', 'Globe of True Imperial Blood', 'Colorless', 25))
        sockets = [socket for socket in host['sockets'] if socket['index'] == index]
        _require(len(sockets) == 1 and sockets[0]['color'] == color, 'Changed selected socket')
        fill = sockets[0]['fill']
        _require((fill['id'], fill['kind'], fill['color'], fill['ml']) ==
                 (augment, 'augment', augment_color, ml), 'Changed augment identity or level')
        _require(any((a['stat'], a['type'], a['value']) == affix for a in fill['affixes']),
                 'Changed selected augment contribution')
        if cid == 'solar-con':
            _require(selected['query']['race'] == 'Human', 'Changed selected armor race applicability')
    return host


class _Markup(HTMLParser):
    """Read the actual associated type links without manufacturing a quote."""
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.text, self.links = [], []
        self.feed(markup)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.append(dict(attrs).get('href'))

    def handle_data(self, data):
        self.text.append(data)


def _placement(root):
    record = _retained_record('augment-placement-retained', root)
    _require(record['level_rule_visible_text'] ==
             'Every augment has an associated minimum level requirement to use it. '
             'Slotting any augment also increases the slotted item’s minimum level to the level '
             'of the slotted augment for as long as that augment is slotted, unless the item\'s '
             'minimum level is already equal or higher.', 'Changed augment level premise')
    return record


def validate_component(data, component, root=ROOT):
    """Qualify exactly eight definitions; never Skull or other all-ability stats."""
    try:
        cid = component['id']
        _require(cid in DEFINITION_IDS, 'Unreviewed ability definition')
        matches = [row for row in data['components'] if row['id'] == cid]
        _require(len(matches) == 1 and matches[0] == component, 'Duplicate or detached definition')
        _require(_fingerprint({k: v for k, v in component.items() if k != 'note'}) == CORE_SHA256[cid]
                 and component['definition_proof'] == PROOFS[cid], 'Changed selected definition core')
        host = _selection(root, cid)
        records = {role: (_source_record(data, sid, root) if sid in SOURCE_SHA256
                          else _existing_record(data, sid, root))
                   for role, sid in PROOFS[cid]['sources'].items()}
        item = records['item']
        if cid in {'claws-wisdom', 'queen-insight-con'}:
            wisdom = cid == 'claws-wisdom'
            amount, kind, stat = (15, 'Enhancement', 'Wisdom') if wisdom else (7, 'Insight', 'Constitution')
            clause = f'granting a +{amount} {kind} bonus to {stat}.'
            markup = _Markup(item['exact_html_fragments'][0])
            _require(item['exact_fragments'] == [clause] and ''.join(markup.text) == clause
                     and markup.links == [f'/page/{kind}_bonus'], 'Changed typed own-item clause')
            family = 'Nearly Complete: ' + ('Ability Score' if wisdom else 'Insightful Ability Score')
            option = 'Wisdom +15' if wisdom else 'Insightful Constitution +7'
            _require(item['context']['item'] == host['id'] and item['context']['minimum_level'] == 35
                     and item['context']['selected_craft_family'] == family
                     and item['context']['selected_option'] == option, 'Wrong own-item craft context')
            craft = records['craft']
            _require(option in craft['exact_fragments']
                     and craft['context']['ability_score_legendary'] == 15
                     and craft['context']['insightful_ability_score_legendary'] == 7
                     and craft['context']['bonus_type_for_ability_score'] == 'Enhancement'
                     and craft['context']['replacement_allowed'] is False, 'Changed selected craft premise')
        elif cid == 'boots-quality-con':
            _require(item['exact_fragments'] == ['Slotted Effect: +3 Quality bonus to Constitution.']
                     and item['context']['minimum_level'] == 34
                     and item['context']['augment_type'] == 'Lamordia: Dolorous (Accessory)'
                     and item['context']['selected_host'] == host['id'], 'Wrong Dolorous variant or effect')
            _require(records['host']['exact_fragments'] == ['Lamordia: Dolorous Slot (Accessory)']
                     and records['host']['context'] == {'minimum_level': 34, 'item_slot': 'Feet'},
                     'Wrong accessory host or minimum level')
            variant = _retained_record('lamordia-variant-match-retained', root)['visibleText']
            _require('Each augment type can only fit into an augment slot that exactly matches its type.'
                     in variant, 'Missing exact Lamordia variant-matching premise')
        elif cid == 'solar-con':
            _require(item['exact_fragments'] == ['Slotted Effect: +4 Artifact Bonus to Constitution.']
                     and item['context'] == {'minimum_level': 30, 'augment_type': 'Sun',
                                             'selected_host': host['id'], 'selected_host_socket_index': 0},
                     'Wrong Legendary Sun augment or effect')
            armor = records['host']
            markup = _Markup(armor['exact_html_fragments'][0])
            _require(armor['exact_fragments'] == ['Sun Augment Slot']
                     and ''.join(markup.text).replace('\u00a0', ' ') == 'Sun Augment Slot'
                     and markup.links == ['/page/Lunar_and_Solar_Gems']
                     and armor['context'] == {'minimum_level': 33, 'feat_requirement': 'Light Armor Proficiency',
                                             'race_absolutely_excluded': 'Warforged',
                                             'selected_query_race': 'Human'}, 'Changed selected armor context')
            system = records['slot_rule']
            _require(system['exact_fragments'] == [
                'Players can slot Lunar and Solar Gems into these slots to provide their bonuses.']
                and system['context']['preceding_slots'] == 'special Moon and Sun Augment Slots'
                and 'Armor' in system['context']['Sun_equipment_slots']
                and system['context']['legendary_gem_minimum_level'] == 30,
                'Missing selected Sun-system compatibility')
            _placement(root)
        elif cid.startswith('celestial-profane-'):
            _require(component['stat'] in {'Wisdom', 'Constitution'}, 'Unreviewed ability membership')
            original = _retained_record('celestial-abilities-retained', root)
            _require(item == original, 'Different original native-ability record')
            markup = _Markup(item['profane_tooltip_html'])
            _require(markup.links == ['/page/Ability', '/page/Ability', '/page/Profane_bonus']
                     and ''.join(markup.text) ==
                     'Profane Well Rounded +2Profane Well Rounded +2: +2 Profane bonus to all abilities.'
                     and 'Minimum level\t29\t' in item['item_table_visible_text'],
                     'Changed native all-abilities definition or source host level')
            membership = _retained_record('ability-membership-retained', root)
            _require(records['membership'] == membership
                     and 'Constitution (CON), Intelligence (INT), Wisdom (WIS)' in
                     membership['ability_members_visible_text'], 'Missing explicit reviewed ability membership')
            _placement(root)
        else:
            _require(component['stat'] in {'Wisdom', 'Constitution'}, 'Unreviewed Globe ability')
            _require(item == _retained_record('globe-abilities-retained', root)
                     and item['effect_visible_text'] ==
                     'Drag this augment into a slot to upgrade an item with a +1 Exceptional Bonus to '
                     'Strength, Dexterity, Constitution, Intelligence, Wisdom, and Charisma. '
                     'This augment can go in any color Augment Slot.'
                     and 'Minimum Level\t25\t' in item['item_header_visible_text']
                     and 'Augment Type\tColorless' in item['item_header_visible_text'],
                     'Changed explicit Globe definition, type or level')
            bow = _retained_record('calamitous-host-retained', root)
            _require(bow['item_level_visible_text'] == 'Minimum Level\t34'
                     and 'Purple\u00a0Augment\u00a0Slot' in bow['slots_visible_text'],
                     'Missing selected bow level or Purple slot')
            placement = _placement(root)
            _require(placement['compatibility_headers_visible_text'].split('\t')[7] == 'Colorless Augment'
                     and placement['selected_rows_visible_text'][0].split('\t')[0] ==
                     'Purple\u00a0Augment\u00a0Slot'
                     and placement['selected_rows_visible_text'][0].split('\t')[7] == '✔',
                     'Missing Colorless-in-Purple compatibility')
        return True
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError):
        return False


def _skull_conflict(data, root):
    """Retain both conflicting definitions without qualifying either case."""
    own = _existing_record(data, 'skull-con', root, conflict=True)
    generic = _existing_record(data, 'nearly-complete', root, conflict=True)
    _require('+16 Enhancement bonus to Constitution' in own['tooltips'][0]
             and 'Constitution +15' in generic['excerpts'][2], 'Lost Skull conflict premises')
    audit = _packet(root)
    _require(audit['recommended_implementation']['skull_treatment'].startswith(
        'Retain the exact conflicting core and existing 15/16 model cases.'), 'Changed conflict boundary')


def family_valid(data, stat, arguments=(), root=ROOT):
    """Keep WIS3 and CON6 intact; the required Skull still cannot be an operand."""
    try:
        expected = FAMILIES[stat]
        rows = data['components']
        family = [row for row in rows if row['stat'] == stat and row['channel'] == 'gear']
        _require(len(family) == len(expected) and {row['id'] for row in family} == set(expected),
                 'Missing, extra, duplicated or substituted selected ability family')
        selected = {}
        for cid in expected:
            matches = [row for row in rows if row['id'] == cid]
            _require(len(matches) == 1, 'Duplicate or moved selected family member')
            row = matches[0]
            _require(_fingerprint({k: v for k, v in row.items() if k != 'note'}) == CORE_SHA256[cid],
                     'Changed selected family core')
            if cid == 'skull-con':
                _require(row['state'] == 'conflicting' and 'definition_proof' not in row,
                         'Conflicting Skull was promoted')
                _skull_conflict(data, root)
            else:
                _require(validate_component(data, row, root), 'Unqualified selected ability definition')
            selected[cid] = row
        _require(all(argument['id'] in DEFINITION_IDS and argument == selected[argument['id']]
                     for argument in arguments), 'Detached, conflicting or unreviewed operand')
        return True
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError):
        return False


def validate_rule_source(data, root=ROOT):
    """Four closed pairs adopt Tip179 while retaining the original Stack caveat."""
    try:
        tip = _existing_record(data, 'tip179-live-20261115', root)
        _require(tip == _retained_record('tip179-retained', root)
                 and 'Different types of bonuses stack' in tip['scoped_visible_text'],
                 'Missing affirmative different-type premise')
        audit = _packet(root)
        premise = next(row for row in audit['reused_sources'] if row['id'] == 'tip179-retained')
        packet = _pinned_json(root, premise['path'], premise['sha256'])
        context = premise['contextual_caveat']
        stack = _resolve(packet, context['same_file_record_pointer'])
        _require(stack['source_url'] == context['source_url']
                 and stack['revision_link'] == context['revision_link']
                 and stack['body_observation'] == context['body_observation']
                 and 'Benefits from the same family, like Fortification or False Life, do not stack.'
                 in stack['scoped_visible_text']
                 and _resolve(packet, context['same_file_interpretation_pointer']).startswith(
                     "The Stack article's general same-family bullet is retained, not hidden."),
                 'Lost retained same-family caveat or historical interpretation')
        return True
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError, StopIteration):
        return False


def validate_existing_rule(data, rule, root=ROOT):
    """Recheck actual Artifact/Exceptional evidence for these new ability uses."""
    try:
        _require(rule == EXISTING_RULES[rule['id']], 'Changed or unrelated existing rule')
        sid = rule['source']
        record = _existing_record(data, sid, root)
        _require(record == _retained_record(sid + '-positive-rule-retained', root),
                 'Wrong retained positive-rule context')
        source = data['sources'][sid]
        _require(rule['quote'] == source['quote'], 'Changed positive rule clause')
        return True
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError):
        return False


def validate_pair(data, rule, stat, a, b, root=ROOT):
    try:
        _require(rule == RULES[rule['id']]
                 and stat == a['stat'] == b['stat'] == rule['stats'][0]
                 and a['channel'] == b['channel'] == 'gear'
                 and a['id'] != b['id'] and {a['id'], b['id']} == set(rule['component_pairs'][0]),
                 'Unreviewed named pair, ability or channel')
        return family_valid(data, stat, (a, b), root) and validate_rule_source(data, root)
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError):
        return False
