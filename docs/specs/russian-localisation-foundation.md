# Russian localisation and multilingual font foundation

Status: investigation and architecture plan
Target: CM 01/02 Bosman Edition, Russian as an additional language (slot 11)
Working branch: feature/russian-language-foundation

## Goals

- Add Russian as an eleventh selectable language. Preserve all ten existing language choices and their identifiers.
- Translate the game interface and player-facing controls in natural football Russian: menus, buttons, tabs, settings, screens, functions, tactical labels, positions, roles, attributes and statuses.
- Strictly preserve database identity fields: player/person names, club names, city and stadium names, nation names and competition names remain exactly as supplied by the selected database. Do not transliterate or translate these proper names.
- News prose and match commentary are outside the current interface-only scope unless the user explicitly expands it.
- Preserve format placeholders, control tokens, colour codes and game-specific markup exactly.
- Keep club and player identity stable. Use original Latin spelling by default for proper names unless the relevant data set already supplies a localised name.
- Introduce a coherent modern sports font family with Cyrillic and extended Latin coverage. Agreed direction: Modern Sports / Balanced Density, IBM Plex Sans preferred (Regular, Medium, SemiBold, Bold); condensed face only for dense tables after layout tests.
- Avoid changing game simulation, save-game semantics or existing language data.

## Repository findings

- This repository is a native recompile of the original game, not just the older hand-port in src/si/. The README describes the recompiler in tools/recomp, runtime hooks in src/recomp_rt, and the original executable/data as build inputs.
- The current branch history is active and contains season/competition work. Localisation changes must be isolated from that work.
- src/si/gui_font.c loads seven legacy bitmap .fnt files into 256-glyph tables. That path is not, by itself, the font path used by the shipped full recompile.
- The text-and-fonts specification dated 2026-10-13 explicitly scopes out language files, T2K and TTF support; it documents the older bitmap-font implementation.
- The later HD text research (2026-10-16) reports that the running 0.5.0 full build uses the original T2K path by default, loads Data/small.t2k, medium.t2k, large.t2k and symbol.ttf, and offers font selection in Game Settings. Revalidate against the current 0.6.1-era code and executable before implementation.
- include/langlib.h and src/si/langlib.c describe a language-index/formatting path in the older src/si port. Do not assume it controls the full recompiled game.
- src/cm3/setup.c contains a 13-entry language-to-default-nation mapping in the older port. This is not proof that the current product has a working ten-language selector.

## Architecture investigation required before code changes

1. Trace the current full-build startup and settings path: persisted language preference and valid range; language selection UI; language-table lookups and binary layout/version; propagation into news, UI, commentary and database names; representation of the ten current languages and reserved indices.
2. Trace text rendering in the current executable: confirm active renderer; font discovery/loading path and size mapping; whether TTF/TTC files can be selected in the current release; Unicode support and encoding expected by the T2K layer.
3. Inspect clean game files and representative language data. Do not infer the binary language table format from the older port.
4. Build a minimal Cyrillic proof of concept before bulk translation. Check glyph coverage, shaping, kerning, fallback, clipping, wrapping and save/reload behaviour.
5. Establish whether translation can ship as text/data files or needs a data compiler/converter. Keep proprietary original game data out of this repository.

## Implementation slices

### A. Language inventory and extraction
- Inventory interface text by domain: menus, settings, buttons, tabs, labels, dialogs, tactical terms, positions, player roles, attributes and statuses.
- Keep a separate exclusion list for database proper names and non-interface prose (news and match commentary); do not include these in the Russian interface build.
- Build a repeatable extractor emitting stable string IDs, source text, context, placeholders/tokens and source location.
- Store translation source in maintainable UTF-8 (for example JSON/TSV) and compile to the runtime format only after that format is documented.
- Add a glossary and style guide before bulk translation.

### B. Eleventh language slot
- Add Russian without renumbering or replacing any existing language.
- Update selector labels, validation bounds, defaults and persistence atomically.
- Confirm compatibility with existing configuration files and saves; unknown/older values must safely fall back.
- Keep default nation/league selection independent from UI language unless the original game explicitly couples them.

### C. Russian translation
- Use football-native Russian rather than literal translation.
- Preserve placeholders, tags, colour/control codes and line-break semantics.
- Handle plural forms, grammatical cases, gender and names through explicit formatting rules where supported; never silently alter placeholder order.
- Preserve all proper names and database identity fields byte-for-byte; no transliteration or localised names.
- Review in-game context, not just isolated strings.

### D. Fonts
- Prefer the existing supported T2K/TTF route if it passes Cyrillic tests; do not add SDL_ttf or FreeType without evidence a new renderer is needed.
- IBM Plex Sans is preferred, subject to verifying Cyrillic and extended Latin coverage and obtaining exact OFL-licensed font files.
- Keep legacy .fnt assets unchanged. Add new font assets in a separate directory and document their licence.
- Test all seven logical font sizes and dense tables, including long Russian words and uppercase text.

### E. Quality assurance
- Automated checks: untranslated-string report, duplicate IDs, missing glyphs, malformed placeholders/tokens, invalid encoding, line-length and overflow heuristics.
- Visual checks: main menu, settings, squad, player profile, tactics,  tables and popups.
- Regression checks: all ten existing languages remain selectable and visually unchanged; existing saves still load; Russian selection persists across restart.
- Simulation checks: language/font changes must not alter match results or save-game state beyond explicitly expected settings fields.

## Translation style baseline

- Use concise, natural Russian sports language.
- Prefer established football terms (for example: «состав», «тактика», «трансфер», «арендовать», «игра в пас», «работоспособность») and validate each against source context.
- Avoid overlong literal phrases where a shorter conventional label is clear.
- Preserve all club, player, city, stadium, nation and competition names exactly as supplied by the database. Transliteration is not permitted.
- Maintain one glossary with one approved translation per concept; document contextual exceptions.

## Acceptance criteria

- Eleven language entries are visible; all original ten remain present and unchanged.
- Russian can be selected, persists after restart and is used consistently in all supported text domains.
- Cyrillic renders correctly in every game font size, with no missing glyph boxes, mojibake or systematic clipping.
- Placeholders, dynamic values, plural/case handling and markup remain correct.
- Automated localisation checks pass, and representative screens are manually reviewed.
- Existing language and save-game regression tests pass.

## Current status / limitations

Implementation progress is tracked in [russian-localisation-status.md](../research/russian-localisation-status.md). The first Russian overlay stage now has a persisted setting, a dedicated Language tab, a 357-entry UTF-8 catalogue, a T2K-escape generator, a Langlib wrapper and automated catalogue/settings tests. This is not yet the native eleventh item in the original language dropdown. The original language.ldb and .lng binary formats still need a verified extension, and the Cyrillic font path must be tested against the clean executable before shipping.


## Scope correction (2026-11-10)

The project owner clarified that “Russian translation” means interface localisation only, in the style of the Russian UI in current Football Manager releases. Earlier work that translated database names, news prose or match-event commentary was outside the requested scope. Those resources must not be included in the Russian release build. The release staging script now builds the Russian language table from `ru-RU-native.tsv` only and no longer generates `rus.lng` or `events_rus.cfg`. The original `eng.lng`, club/player/city/stadium/nation/competition identities and English match-event file must remain unchanged. Out-of-scope database-name, news and match-event TSVs, builders and tests have been removed from this branch; do not reintroduce them unless the owner explicitly changes the scope.
