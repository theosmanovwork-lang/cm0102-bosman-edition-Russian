# Russian localisation: implementation status

Branch: `feature/russian-language-foundation`

## Implemented in this branch

- A new `language = system|russian` option is appended to `settings.txt`. Existing options keep their identifiers and defaults.
- The Bosman Edition Options box has a fourth tab, Language, with a Game text choice: System / Russian.
- A UTF-8 source catalogue at `locales/ru-RU.tsv` contains the first 80 contextual UI translations.
- `tools/localisation/build_catalog.py` validates unique IDs, printf placeholder signatures, game markup and the game's four-digit Unicode escape range. It generates an ASCII-only C header for the runtime.
- `src/recomp_rt/win/localisation.c` wraps the original Langlib formatter. When Russian is selected, exact catalogue matches are substituted; missing strings fall back to the original source text. The original language selector/index is not renumbered or overwritten outside the duration of the formatter call.
- Tests cover the new setting, persistence, catalogue validation and generated-header consistency.

## What this stage is — and is not

This is a Russian text overlay prototype, not yet the complete native eleventh language in the original Game Settings language drop-down. It deliberately leaves the ten original language indices and the ten original `.lng` files untouched. That avoids corrupting existing saves or default-nation selection while the binary language table is still being researched.

The initial catalogue covers only a subset of the interface and Bosman settings. News, match commentary, tactical descriptions, attributes, dynamic plural/case forms and all database names still need extraction and translation.

## Fonts

The current full recompile uses the original T2K renderer. Its font scanner accepts `.ttf`, `.ttc` and `.t2k` files under `Data/FONTS`. The next font slice should package IBM Plex Sans Regular, Medium, SemiBold and Bold under the OFL licence, then verify Cyrillic coverage and layout in the original executable. No font binary is bundled in this slice: rendering and clipping cannot be certified without the clean game files and an in-game test.

## Required next steps

1. Build the current branch with the clean 3.9.68 executable and run CTest.
2. Verify that the original T2K text path decodes the `#XXXX#` Unicode escape sequence used by the existing text decoder.
3. Test the Language tab and Cyrillic on every font size in classic and widescreen modes.
4. Extract the full source-string inventory and translate it in contextual batches with a single glossary.
5. Extend the native language drop-down only after the `language.ldb` and `.lng` loader paths, save compatibility and default-nation mapping are verified.
6. Add and test the IBM Plex Sans font files, then decide whether they can be made the default font family for every existing language.

## Build requirements

A source build still needs the player's own `CM0102.iso` and official 3.9.68 patch, as described in the repository README. These proprietary inputs are not stored in this repository.
