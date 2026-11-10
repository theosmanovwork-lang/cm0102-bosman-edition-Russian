# Russian localisation: implementation status

Branch: `feature/russian-language-foundation`

## Implemented in this branch

- A new `language = system|russian` option is appended to `settings.txt`. Existing options keep their identifiers and defaults.
- The Bosman Edition Options box has a fourth tab, Language, with a Game text choice: System / Russian.
- A UTF-8 source catalogue at `locales/ru-RU.tsv` contains the contextual overlay catalogue, expanded to 212 verified UI entries.
- A separate `locales/ru-RU-native.tsv` adds 27 native `language.ldb` translations for the start menu, game setup and navigation, using stable source-record IDs and Russian text. The native batch now has 88 entries: the first 27 menu/setup labels plus 61 football-role, player-attribute, staff-role and squad terms.
- `tools/localisation/build_extended_language_ldb.py` builds a separate extended copy of the original `language.ldb`, appending candidate language ID 13 and one text/grammar block per record. It refuses to overwrite the source, checks the original fixed-record size and runtime ID-table capacity, and writes through a temporary file.
- The supplied clean 3.9.68 `language.ldb` was processed locally: all 9,807 original record payloads were checked byte-for-byte against the source, the ten original IDs remained `(0,2,3,4,5,6,7,8,9,10)`, and 27 Russian text slots were verified in the appended block. The resulting test file is 225,149,162 bytes and is not committed because it is derived from proprietary game data.
- The new LDB builder has isolated unit tests and is registered with CTest as `localisation_extended_ldb`.
- IBM Plex Sans Regular, Medium, SemiBold and Bold, plus Sans Condensed Regular and Bold, are bundled under the SIL OFL. The release staging script decodes the checked-in base64 assets into `Data/FONTS` and records their hashes in the download manifest. The original font selector exposes them; the default font is not changed until in-game QA is complete.
- `tools/localisation/build_catalog.py` validates unique IDs, printf placeholder signatures, game markup and the game's four-digit Unicode escape range. It generates an ASCII-only C header for the runtime.
- `src/recomp_rt/win/localisation.c` wraps the original Langlib formatter. When Russian is selected, exact catalogue matches are substituted; missing strings fall back to the original source text. The original language selector/index is not renumbered or overwritten outside the duration of the formatter call.
- Tests cover the new setting, persistence, catalogue validation and generated-header consistency.

## What this stage is — and is not

This remains a staged prototype, not a finished native eleventh language. The `language.ldb` reader appears to iterate the language count from the file header and has a 19-entry ID array, so an eleventh block is structurally plausible. However, the separate database-name loader is explicitly bounded to language IDs 0–12 and its `.lng` filename resolver treats 0, 1, 11 and 12 as English. Candidate ID 13 therefore needs a coordinated hook or loader change for database names, plus a matching Russian `.lng` and match-event resource path. The native menu/default-nation mapping and save/load behaviour are not yet wired. The ten original language IDs and source `.lng` files remain unchanged.

The initial overlay catalogue covers a subset of the interface and Bosman settings; the separate native LDB batch currently has 88 translations. The resource inventory has been extracted locally from the user's supplied files: 9,807 LDB entries, 30,453 aligned database-name rows across ten languages, and 2,997 aligned match-event variants. The repeatable extractor and full inventory are staged locally but have not yet been committed to the repository. News, match commentary, tactical descriptions, attributes, dynamic plural/case forms and all database names still need translation.

## Fonts

The current full recompile uses the original T2K renderer. Its font scanner accepts `.ttf`, `.ttc` and `.t2k` files under `Data/FONTS`. The next font slice should package IBM Plex Sans Regular, Medium, SemiBold and Bold under the OFL licence, then verify Cyrillic coverage and layout in the original executable. The font files are now included as optional choices, but the game has not yet been run with them. Rendering, glyph coverage and clipping cannot be certified without the clean game files and an in-game test.

## Required next steps

1. Build the current branch with the clean 3.9.68 executable and run CTest.
2. Verify that the original T2K text path decodes the `#XXXX#` Unicode escape sequence used by the existing text decoder.
3. Test the Language tab and Cyrillic on every font size in classic and widescreen modes.
4. Extract the full source-string inventory and translate it in contextual batches with a single glossary.
5. Wire candidate ID 13 through the native language selector, database-name loader and `.lng` filename mapping; add `ru.lng` and `events_rus.cfg` only after the default-nation mapping and save compatibility are verified.
6. Add and test the IBM Plex Sans font files, then decide whether they can be made the default font family for every existing language.

## Build requirements

A source build still needs the player's own `CM0102.iso` and official 3.9.68 patch, as described in the repository README. These proprietary inputs are not stored in this repository.


## News and match commentary batch (2026-11-10)

- Added `locales/ru-RU-news.tsv`: 47 native `language.ldb` translations covering transfer negotiations, bids, contracts, scouting, player availability, work permits, match outcomes and press statements. The source IDs and the ten grammatical argument slots are retained.
- Added `tools/localisation/build_russian_events.py`: creates a separate `events_rus.cfg` from `events_eng.cfg`; it only replaces G/R text lines, uses `#XXXX#` escapes for Cyrillic, and validates source strings, special placeholders (`<p1>`, `<Rf>`, `<t>`), and multi-part separators. Event IDs, occurrence order, flags, probability, delays, sounds, comments and line endings remain unchanged. Missing rows fall back to English.
- Added `locales/ru-RU-match-events.tsv`: the committed catalogue now contains 67 translated variants across the first nine match-event groups. The builder validates event IDs, occurrence/variant ordering, source strings, placeholders and multi-part separators.
- The extended LDB builder now accepts multiple TSV batches, checks each supplied source string and format signature when present, and validates the number and ordering of argument markers. Combining the 88-entry UI/football batch and 47-entry news batch creates 135 Russian LDB rows.
- Local verification against the supplied original files: the extended 9,807-entry LDB is 225,149,162 bytes; all ten original language IDs and every original record payload remain byte-for-byte unchanged, with candidate ID 13 appended. The separate match CFG retains all 10,857 lines; only the translated G/R text lines change.
- The isolated Python test suite currently contains 14 tests across the extended-LDB, match-event and `.lng` builders. A full CMake/CTest run, clean game build and in-game launch have not yet been confirmed.
- Important: the game's match-event loader still chooses only the ten original `events_<language>.cfg` filenames. The new `events_rus.cfg` is generated and ready for loader integration, but is not automatically selected in the current game.


## Runtime language bridge (2026-11-10, prototype)

- The persisted Bosman Language option now calls the runtime language switch immediately. The native Langlib setup remembers the system language and loads candidate ID 13 when Russian is selected; the Setup Game default-nation selector temporarily uses the remembered system language so ID 13 does not enter its unsupported nation switch.
- The native database-name loader and its availability check now map ID 13 through the original English branch while temporarily substituting the `rus.lng` path. The `.lng` fitter now copies the curated `Data/rus.lng` (including custom-database Data overrides) into CM3_TEMP before fitting it to the loaded database. It falls back to `eng.lng` only if no Russian resource is present. This is explicitly an English-name fallback, not yet Russian club/country/city/stadium translation.
- The match-event loader now selects `events_rus.cfg` through the original default event-file slot while the Russian language is active. The marker is kept at the English slot value so the game reloads when switching between System and Russian.
- The release staging script now generates the 135-row extended `language.ldb` and `events_rus.cfg` from the player's clean files, and updates the download manifest for the changed/additional resources.
- Verification completed locally against the supplied clean files: 10 Python unit tests passed; the generated 11-language LDB has 9,807 records, IDs `(0,2,3,4,5,6,7,8,9,10,13)`, and all 9,807 original record payloads are byte-identical. The generated event CFG has 10,857 lines; only G/R text for 67 translated variants changes.
- Not verified yet: compiling the C runtime after the new wrappers, full CMake/CTest, a clean game launch, in-game Cyrillic/font rendering, language switching during a loaded save, and event/grammar behaviour. The current committed match-event TSV is a 22-variant starter; the 67-variant working batch is present in the generated local package but is not yet the release source in git.


## Russian database names and full starter commentary batch (2026-11-10)

- Added `tools/localisation/build_russian_lng.py` and `locales/ru-RU-database-names.tsv`. The builder validates the real fixed-width section counts and source names in the clean `eng.lng`, encodes Cyrillic through `#XXXX#`, rejects any value that does not fit, preserves the header/record counts/flags/country codes and writes a separate `rus.lng`.
- The curated name batch now has 319 long-name fields and 152 short-name fields: 6 continents, 19 national competitions, 188 countries/nations, 56 selected clubs, 34 selected cities and 16 selected stadiums. The club/city/stadium set prioritises widely recognised teams and grounds; remaining rows and most club/staff competitions still need translation. It is a partial name translation, not a full database-name localisation.
- Corrected the nation short-name slot from 51 to 26 bytes (the remaining 30 bytes are nation metadata) and strengthened the test to verify both flag bytes and all 30 metadata bytes remain unchanged. The earlier generated `.lng` candidate must not be used; the corrected file was rebuilt from clean `eng.lng`: 1,993,486 bytes, same size and header/counts, with differences limited exactly to the translated name slots. The source `eng.lng` was not modified.
- Expanded `locales/ru-RU-match-events.tsv` from 22 to 67 variants, and the release script now generates the matching `events_rus.cfg` from clean `events_eng.cfg`.
- Added four isolated tests for the `.lng` builder and registered them with CTest. Local verification: 4 `.lng` tests, 3 match-event builder tests and 7 extended-LDB builder tests passed; the corrected real `.lng` build generated 319 long and 152 short Russian fields. A byte-level comparison found zero changes outside the 319 long-name and 152 short-name slots. C runtime compilation, complete CTest, and an in-game launch/render test remain outstanding.

- Follow-up fix: `season_lng.c` now reads `Data/rus.lng` from the normal game/custom-database path when it creates the runtime CM3_TEMP copy; without this, the native loader would have replaced the curated Russian file with an English copy. This path change is committed, but still needs an in-game verification.

- Follow-up terminology review: corrected `Holland` to `Нидерланды` and retained the era-appropriate `Свазиленд` for the game's 2001/02 database; disambiguated the Oceania Nations Cup, Euro qualifying, American Samoa and Guinea-Bissau labels so they no longer collide with other Russian names. The 319-row catalogue has no duplicate section/row keys or blank long-name translations.
- Competition-label review: clarified the Asian Cup and its qualifying stage, the Olympic football tournament, Confederations Cup and Africa Cup of Nations; distinguished Spartak Moscow from the generic Spartak entry. The only repeated Russian name remaining in the 319-row database catalogue is the Milan/Milano city alias pair.

## Scope correction — interface only (2026-11-10)

The project owner clarified the requirement: Russian is to translate the game interface and football-management terminology, not the database. The target is comparable to the Russian interface localisation in current Football Manager releases.

- In scope: all menus, buttons, tabs, settings, screens, dialogs, actions/functions, tactical labels, formations, positions, player roles, attributes and statuses.
- Out of scope: player/person names, club names, city and stadium names, nation names and competition names. These must remain exactly as provided by the active database, with no translation or transliteration.
- News prose and match commentary are also outside the current interface-only scope.
- The release script has been corrected: it now builds the Russian language table from `ru-RU-native.tsv` only. It no longer adds the news batch, creates `rus.lng`, or creates `events_rus.cfg`. Thus the historical database-name and match-event TSVs/builders are not release inputs.
- Removed the out-of-scope `ru-RU-database-names.tsv`, `ru-RU-news.tsv`, and `ru-RU-match-events.tsv` catalogues, their two resource builders, and their dedicated tests from this branch. The release must not generate or install translated database-name or match-event resources.
- The 88-entry native catalogue is the current interface/football-terminology source batch. It is not yet a complete translation: the next work is to inventory and translate every remaining interface string, with context and consistent terminology. Proper-name source rows must be excluded from the translation catalogue.

The scope correction is reflected in `docs/specs/russian-localisation-foundation.md` and `tools/release/make_release.sh`. A clean build and runtime test are still required to confirm that the release leaves all database identities untouched.


## Authoritative scope and current branch state (2026-11-10)

This section supersedes any earlier scope, coverage or next-step statements above that conflict with it.

- **Scope is interface-only.** Translate menus, buttons, tabs, settings, dialogs, screen labels, actions, tactics, formations, positions, roles, attributes and statuses.
- **Never translate or transliterate database identities:** player/staff names, clubs, cities, stadiums, countries/nations, or named competitions/tournaments remain exactly as supplied by the active database.
- News prose and match commentary remain English and are not localisation targets.
- The branch no longer contains the former database-name, news or match-event TSV catalogues, their builders, or their dedicated tests. The release script stages only the interface catalogue(s). The runtime uses the original English name/commentary resources.
- Current catalogue sizes are 355 contextual overlay entries in `locales/ru-RU.tsv` and 88 native language-table entries in `locales/ru-RU-native.tsv`. These are an initial subset, not complete interface coverage.
- Earlier sections describing 27/135 translations, Russian name/news/event resources, or adding `rus.lng` / `events_rus.cfg` are historical notes and are not the current implementation plan.

## Interface catalogue expansion (2026-11-10)

A screen-research pass added 107 source-grounded overlay entries in one batch. The catalogue now has 212 contextual UI entries; the separate native language-table catalogue remains at 88. The new overlay entries cover squad filters and actions, club navigation tabs, team selectors, tactics-menu commands and preset labels, player-comparison prompts and statistics, tactical position labels, additional Game Settings rows, and club information headings. The entries were admitted only where research notes identify the string as a control, tab, heading, filter, status or other interface label. No player/staff/club/city/stadium/nation/competition identity, news prose or match commentary was added.

This is a materially broader interface pass, **not yet a complete translation of every game screen**. The available checked-in research does not yet enumerate every in-game label, tooltip, dialog, transfer/scouting workflow, calendar/table view or staff/training screen. Those areas still need a complete source-string inventory and contextual validation. A final full-coverage claim must wait until that inventory and in-game screen review are finished.

## Interface inventory: translation work still required

Use the existing reverse-engineered screen research as the source of UI context, then verify each candidate string against the actual runtime screen before adding it to a catalogue. Do not bulk-translate every string found in the executable or language table: those sources also contain database values and out-of-scope prose.

| UI area | Required inventory | Current coverage |
|---|---|---|
| Start screen and new-game setup | Main menu, league selection controls, manager creation, nationality/team selection, confirmations, progress labels | Partial; initial labels exist |
| Global navigation and daily flow | Main tabs, inbox/news navigation labels, continue/day advance, save/load, manager status, dialogs | Partial |
| Squad and player screens | Squad views, filters, column headings, profile tabs, attributes, condition, morale, preferred foot, contract/status labels | Expanded initial batch: squad filters, club tabs/actions, comparison labels and profile stats; deeper profile/status screens remain |
| Tactics and match controls | Formation names, positions, player instructions, team instructions, set pieces, tactical view names, action buttons | Core tactics menu actions, preset labels and tactical positions added; detailed team/player instructions remain |
| Transfers and recruitment | Transfer/loan actions, offers/bids, shortlist, scouting controls, search filters and report labels | Not yet inventoried as a complete UI domain |
| Training and staff | Training controls, schedules, coach/physio/scout roles, staff actions and status labels | Partial terminology only |
| Club, competitions and calendar UI | Generic interface labels, fixture/calendar controls, tables, standings and navigation | Not yet inventoried as a complete UI domain; named entities stay untouched |
| Settings and dialogs | All Bosman Edition and game settings, confirmations, errors, tooltips and keyboard hints | Overlay settings partly covered |

## Next implementation slice

1. Build a screen-by-screen candidate-string inventory from the existing research notes and actual UI call sites. Record source text, UI context, source location/ID, placeholder signature, and an explicit `interface` / `identity` / `news` / `commentary` classification.
2. Admit only `interface` rows into the Russian catalogues. Reject all identity values and all news/commentary prose by construction.
3. Translate in contextual batches using `locales/ru-RU-style-guide.md`; review tactical roles and position labels consistently across squad, profile and tactics screens.
4. Add automated checks for duplicate source IDs, unchanged placeholder/control tokens, and accidental inclusion of excluded categories. Do not claim full coverage until every inventoried UI surface has been checked.
5. Build and run the native target, CTest, and in-game Cyrillic/layout checks before describing the branch as playable. These checks have not yet been completed.


## Additional interface screen pass (2026-11-10)

A second source-grounded batch adds 108 overlay strings. It covers the left navigation and news filters, holiday options and confirmations, manager/network status labels, club squad-number and tournament actions, player profile tabs and status values, all 31 player attributes, and the researched tactics list views and individual instructions. News category names are treated as UI navigation; article/news body text and match commentary remain excluded. The batch also preserves intentional line breaks and leading whitespace in the relevant source labels.

The overlay catalogue now contains 355 contextual strings and the native language-table terminology batch remains at 88. This is still not full interface coverage: several screens are represented only by function-level research, without complete literal-string inventories. All 31 player attributes now have overlay translations, but in-game width and wording review remains outstanding. Transfer/scouting workflows, full training/staff screens, calendar/table views, and the remaining dialogs/tooltips still need full extraction and validation.


## System and network UI pass (2026-11-10)

Added 10 more verified strings for network navigation, connection/progress messages, startup and disk errors, network exit confirmation, manager-control resumption, the sweeper position label, and the dynamic news screen heading. The heading retains its original formatter-note tag and %s placeholder. Catalogue size: 330 overlay entries. This addition does not include any news article content or match commentary.


## Transfer and profile controls pass (2026-11-10)

Added 13 source-grounded labels for the player transfer-status and discipline dialogs, asking-price control and its two fine levels, player profile tabs, the contract column, club Stats and history View menus, and list sorting/action menus. The discipline options are interface choices only; no generated disciplinary news or match text was translated. The overlay catalogue now contains 343 entries. Training schedule field labels and complete player/staff search criteria were not included because the checked-in research describes those screens at function level without a verified literal-string inventory.


## Match and manager-status UI pass (2026-11-10)

Added 7 further interface labels from the match-screen and manager-status inventories: the tactics captain marker and match navigation tabs (overview, statistics, action zones, report, player ratings and latest scores). The manager status values and single-player exit confirmation already had existing source entries in the catalogue and were not duplicated. 'Match Report' here is only the screen-tab caption; report prose and match commentary remain untranslated. Catalogue size: 350 overlay entries.


## Comparison and tactics UI follow-up (2026-11-10)

Added two source-grounded interface strings from the player-comparison and tactics screen inventories: the “On loan from ” prefix that precedes a linked club name, and the message shown when no tactics are available for the last reserve match. The prefix retains its trailing space so the club link and its database name remain untouched. The overlay catalogue now contains 352 contextual entries; the native language-table batch remains at 88. No player/staff/club/city/stadium/nation/competition names, news prose or match commentary were added.


## Interface labels added in the latest pass

- Added the two Screen Mode choices, Full and Windowed, from the original Game Settings dialog.
- These are interface captions only; database values and match/news prose remain outside the translation scope.
- Current overlay catalogue: 354 contextual entries.


## Game Options menu follow-up

- Added “Hall of Fame” as a Game Options menu item, translated as “Зал славы”.
- Existing Game Options entries were checked against the same inventory and left unchanged where already present.
- Current overlay catalogue: 355 contextual entries.


## Past meetings filter labels

- Added the verified “Period” and “Venue” filter captions from the club screen inventory, translated as “Период” and “Место проведения”.
- These are filter labels only; venue, club and competition database names remain unchanged.
- Current overlay catalogue: 357 contextual entries.


## Squad selector labels

- Added the verified generic squad-choice captions “First Team”, “Reserve Team” and “Youth Team”, translated as “Основной состав”, “Резервный состав” and “Молодёжный состав”.
- These are interface labels, not club or player database names.
- Current overlay catalogue: 360 contextual entries.


## Player and staff search interface labels

- Added ten verified captions from the Player & Staff Search interface: Short List, Player Search, Staff Search, Filters, Search, Scout #1, Scout #2, Basic Wage, Contract Expiry and Value.
- These are search tabs, controls and result-column headings only; player, staff and club identities remain unchanged.
- Current overlay catalogue: 370 contextual entries.


## Assistant and holiday interface follow-up

- Added nine verified assistant-selection and holiday captions/messages from the original UI inventory and runtime string references.
- Other holiday preference labels and confirmation prompts were already present in the catalogue and were not duplicated.
- Current overlay catalogue: 379 contextual entries.
