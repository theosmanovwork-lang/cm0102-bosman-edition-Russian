# Russian localisation: implementation status

Branch: `feature/russian-language-foundation`

## Implemented in this branch

- A new `language = system|russian` option is appended to `settings.txt`. Existing options keep their identifiers and defaults.
- The Bosman Edition Options box has a fourth tab, Language, with a Game text choice: System / Russian.
- A UTF-8 source catalogue at `locales/ru-RU.tsv` contains the first 80 contextual UI translations for the Bosman overlay.
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
