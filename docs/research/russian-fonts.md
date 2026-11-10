# IBM Plex font package

Source: [IBM/plex](https://github.com/IBM/plex), official IBM typeface repository.

The package contains static TrueType files for:
- IBM Plex Sans Regular, Medium, SemiBold and Bold
- IBM Plex Sans Condensed Regular and Bold

IBM states that Plex Sans supports extended Latin and Cyrillic. The font software is licensed under the SIL Open Font License 1.1; the original licence is kept beside the source assets as `OFL.txt`.

The source TTFs are stored as base64 text in this repository because the connected GitHub file-writing interface only creates UTF-8 text files. `tools/fonts/install_ibm_plex.py` validates the TrueType signature and decodes them into the staged game's `Data/FONTS` directory. The release manifest records the decoded files and licence.

The current game uses the original T2K renderer and scans TTF files under `Data/FONTS`. These files are exposed through the original font selection mechanism; this stage does not force a new default. The selected font affects every language, while the original font remains available as a fallback.

Before changing the default, test the six files in the clean executable at all eight logical font sizes (0–7), in classic and widescreen modes, with Latin, Cyrillic, diacritics, digits, punctuation and long football labels. Review tables, player profiles, news, tactics and match commentary for clipping, line height, glyph coverage and performance.
