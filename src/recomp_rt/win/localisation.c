/* Russian text overlay for the original Langlib formatter.
 *
 * The original has ten .lng files for translated database names and a separate
 * language.ldb table for interface text. This layer deliberately does not
 * alter either binary format or any original language index. "System" leaves
 * the original behaviour untouched; "Russian" overlays exact catalogue
 * matches and falls back to the original English source for everything else.
 *
 * The game renderer understands #XXXX# Unicode escapes. Keeping the shipped
 * C strings ASCII avoids passing UTF-8 Cyrillic through the original ANSI API.
 */
#include "localisation.h"
#include "options.h"
#include "win.h"
#include "russian_catalog.h"

#include <string.h>

#define LANG_INDEX 0x009eb2dcu

void o_0066f4e0(void);

int localisation_is_russian(void)
{
    return options_enum(OPT_LANGUAGE) == OPT_LANGUAGE_RUSSIAN;
}

static const LocalisationEntry *find_translation(const char *source, size_t *index)
{
    if (!source) return NULL;
    for (size_t i = 0; i < RUSSIAN_CATALOG_COUNT; i++) {
        if (strcmp(source, russian_catalog[i].source) == 0) {
            if (index) *index = i;
            return &russian_catalog[i];
        }
    }
    return NULL;
}

const char *localisation_text(const char *source)
{
    const LocalisationEntry *entry;
    if (!localisation_is_russian()) return source;
    entry = find_translation(source, NULL);
    return entry ? entry->target : source;
}

static uint32_t target_address(size_t index)
{
    static uint32_t addresses[RUSSIAN_CATALOG_COUNT];
    if (index >= RUSSIAN_CATALOG_COUNT) return 0;
    if (!addresses[index]) {
        size_t n = strlen(russian_catalog[index].target) + 1;
        addresses[index] = win_static_alloc((uint32_t)n);
        memcpy(g_mem + addresses[index], russian_catalog[index].target, n);
    }
    return addresses[index];
}

/* Langlib::langlib_sprintf(char *dst, const char *format, ...), cdecl.
 * Stack: [esp+4] = dst, [esp+8] = format. */
RT_WRAP(0066f4e0, russian_langlib_sprintf)
{
    if (!localisation_is_russian()) {
        o_0066f4e0();
        return;
    }

    uint32_t format_at = cpu.esp + 8u;
    uint32_t format = rd32(g_mem, format_at);
    uint32_t old_language = rd32(g_mem, LANG_INDEX);
    size_t index = 0;

    if (format >= 0x10000u && format < 0xfff00000u) {
        const char *source = win_str(format);
        if (find_translation(source, &index)) {
            uint32_t translated = target_address(index);
            if (translated) wr32(g_mem, format_at, translated);
        }
    }

    /* Bypass the original language.ldb lookup for the duration of this call.
     * Restore both the caller's format pointer and locale selector afterwards. */
    wr32(g_mem, LANG_INDEX, 0);
    o_0066f4e0();
    wr32(g_mem, format_at, format);
    wr32(g_mem, LANG_INDEX, old_language);
}
