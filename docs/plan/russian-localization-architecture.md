# Russian localisation: architecture and implementation plan

Status: investigation in progress (2026-11-10)

## Scope

Add Russian as an additional selectable language without removing or renumbering existing languages. Preserve existing game data and save compatibility. Build a consistent football glossary and a Cyrillic-capable font path; validate text layout, formatting, and in-game rendering before treating the translation as complete.

## Verified repository facts

- The repository README describes the shipped game as a recompiled version of the original program. It also states that a source build needs the user's own copy of the 2008 game release and the official 3.9.68 patch; those original game files are not part of this source repository.
- The root CMake target currently lists a smaller src/si implementation (gui_font.c, gui_text.c, langlib.c, etc.). Its text-and-fonts spec says this path uses seven legacy bitmap .fnt fonts and does not include the original T2K path.
- The separate research note docs/research/2026-10-16-hd-text.md describes the full recompiled game path: the original T2K engine is the default; the original font chooser can scan Data/FONTS for .ttf, .ttc, and .t2k; the clean game data contains small.t2k, medium.t2k, large.t2k, and symbol.ttf.
- These are distinct implementation paths and must not be conflated. Before changing font code, establish which target/build/release path this fork intends to ship and identify whether the src/si target is a development/demo path or the active game.
- In the src/si path, g_language_index is initialised to 0, langlib.c formats plain English strings, and langlib.h explicitly says the language table is not implemented.
- src/cm3/setup.c contains a 13-entry language-index-to-default-nation table and rejects indices above 12. That is game-start default-league behaviour, not proof that the language table itself has 13 user-facing choices.
- The repository does not contain the original game data needed to inspect or regenerate language.ldb. The binary layout, encoding, lookup rules, and language selection persistence therefore remain unverified.

## Architecture decisions (provisional)

1. **Additive language slot.** Keep all existing language IDs and labels stable. Determine the real language table and persisted settings format from clean 3.9.68 data/executable before assigning the Russian ID. Do not simply append 13 to the src/si nation map and assume that implements localisation.
2. **Translation data pipeline.** Build an extractor/compiler around the actual language resource format (once reverse-engineered), with stable string IDs, source context, translator notes, placeholder signatures, and a glossary. Keep source strings and translation data separate from rendering code.
3. **Formatting safety.** Preserve printf-style placeholders, the original <...> translator-note convention, and any {...} / [...] substitution tags if present in the active path. Add automated checks for placeholder parity, malformed tags, encoding, duplicate IDs, and truncation.
4. **Encoding and text layout.** Prefer UTF-8 internally in the port where possible, but only convert at the resource/API boundary once the original encoding and renderer expectations are known. Ensure glyph coverage for Russian Cyrillic and punctuation. Test width measurement, wrapping, centring, clipping, tables, and input fields.
5. **Fonts.** Do not replace the legacy .fnt assets blindly. First confirm the active rendering path. If the full recompiled path uses the original T2K font chooser, test an OFL-licensed IBM Plex Sans family through the existing .ttf path before considering new dependencies. Use a condensed companion only where table density requires it; keep font sizes and metrics configurable by role.
6. **Football glossary.** Use consistent football terminology across menus, news, tactics, attributes, match commentary, competitions, awards, and settings. Preserve player and club identity according to a documented transliteration policy. Treat country/city/stadium/competition naming as a separate editorial decision.
7. **QA.** Add automated resource and placeholder checks, then perform screenshot-based visual review on the main menu, setup, squad, player profile, tactics, news, match commentary, and dense tables. Test all supported platforms and confirm existing languages and saves remain unaffected.

## Required inputs / unresolved questions

- A clean 3.9.68 Data directory and executable (or a lawful local copy supplied by the user) to inspect language.ldb, fonts, and original language-selection behaviour.
- Confirmation of the release target that this fork is intended to build and ship.
- A representative set of in-game screens or an executable test environment for visual QA.

## First implementation milestones

1. Map the active build graph and language-selection/persistence path.
2. Extract and document the language resource format; create a round-trip test before editing any game text.
3. Prototype Russian text and IBM Plex Sans Cyrillic on one screen, including width and wrapping checks.
4. Implement the additional language slot and settings persistence without changing existing IDs.
5. Expand the translation corpus by functional area, with glossary and automated QA.
