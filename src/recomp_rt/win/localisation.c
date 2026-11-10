/* Russian language selection and text overlay for the original Langlib.
 *
 * The original language.ldb format supports an ID list in its header. Candidate ID 13 is
 * appended by the release builder; the original IDs are not renumbered. The older database
 * name and match-event loaders have fixed 0..12 language switches, so their wrappers map
 * ID 13 to the English loader branch while substituting rus.lng / events_rus.cfg.
 */
#include "localisation.h"
#include "options.h"
#include "win.h"
#include "russian_catalog.h"

#include <string.h>

#define LANG_INDEX 0x009eb2dcu
#define RUSSIAN_LANGUAGE_ID 13u
#define DB_NAMES_LANGUAGE 0x009b5984u
#define DB_NAMES_FILENAME 0x009b632cu
#define MATCH_EVENT_LANGUAGE 0x00a1599cu
#define MATCH_EVENT_FILENAME 0x00a15c3cu

static int system_language = -1;

void o_0066e790(void);
void o_0066f4e0(void);
void o_005d8480(void);
void o_006d9e50(void);
void o_00535930(void);

int localisation_is_russian(void)
{
    return options_enum(OPT_LANGUAGE) == OPT_LANGUAGE_RUSSIAN;
}

int localisation_russian_names_available(void)
{
    char path[2048];
    return win_existing_file("rus.lng", path, sizeof path);
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

/* A callback into the original cdecl function. Preserve the game registers after a normal return. */
static uint32_t call_cdecl(uint32_t target, int nargs, const uint32_t *args)
{
    Cpu saved = cpu;
    uint32_t result = rt_callback(target, nargs, args);
    if (!rt_unwinding) cpu = saved;
    return result;
}

static int native_language(void)
{
    if (localisation_is_russian()) return (int)RUSSIAN_LANGUAGE_ID;
    return system_language >= 0 && system_language <= 12 ? system_language : 0;
}

/* Used by the Language tab: switch the text table now, and reload database names when a database
 * is already in memory. The match-event table will switch safely at the next event-config load. */
void localisation_language_changed(void)
{
    int language = native_language();
    uint32_t args[2] = {(uint32_t)language, 0};
    uint32_t loaded = call_cdecl(0x0066eb40u, 2, args);
    if (rt_unwinding) return;
    if (!loaded) {
        fprintf(stderr, "recomp: language: the original language.ldb did not load language ID %d\n", language);
        return;
    }
    if (rd32(g_mem, 0x00ae23a8u) != 0) {
        uint32_t names[2] = {(uint32_t)language, 0};
        call_cdecl(0x005339a0u, 2, names);
    }
}

/* Langlib setup first chooses the operating-system language. Remember it for "System", then
 * load the appended ID 13 when the Bosman option asks for Russian. */
RT_WRAP(0066e790, russian_langlib_setup)
{
    o_0066e790();
    if (rt_unwinding) return;

    int current = (int32_t)rd32(g_mem, LANG_INDEX);
    if (current < 0 || current > 12) current = 0;
    system_language = current;

    if (localisation_is_russian()) {
        uint32_t args[2] = {RUSSIAN_LANGUAGE_ID, 0};
        if (!call_cdecl(0x0066eb40u, 2, args) && !rt_unwinding) {
            fprintf(stderr, "recomp: language: Russian ID 13 is not present in language.ldb\n");
        }
    }
}

/* The settings object's language word (+0x08) is applied before the game writes game.cfg.
 * Keep that setting in step with the separate Bosman language choice. */
RT_WRAP(005d8480, russian_config_apply)
{
    uint32_t settings = cpu.ecx;
    if (settings >= 0x10000u && settings < 0xfff00000u)
        wr32(g_mem, settings + 8u, (uint32_t)native_language());
    o_005d8480();
}

/* Langlib::langlib_sprintf(char *dst, const char *format, ...), cdecl.
 * Only the small legacy overlay catalogue bypasses the native ID-13 table. Everything else
 * goes through the new language.ldb block, including news and dynamically formatted messages. */
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
    if (format < 0x10000u || format >= 0xfff00000u ||
        !find_translation(win_str(format), &index)) {
        o_0066f4e0();
        return;
    }

    uint32_t translated = target_address(index);
    if (!translated) {
        o_0066f4e0();
        return;
    }

    wr32(g_mem, format_at, translated);
    wr32(g_mem, LANG_INDEX, 0);
    o_0066f4e0();
    if (!rt_unwinding) {
        wr32(g_mem, format_at, format);
        wr32(g_mem, LANG_INDEX, old_language);
    }
}

/* The original name loader has a switch for IDs 0..12. Map Russian ID 13 to its
 * English branch, whose filename pointer is temporarily changed from eng.lng to rus.lng.
 * The database-name language marker is restored to 13 after a successful load. */
RT_WRAP(006d9e50, russian_match_events_read_config)
{
    if (!localisation_is_russian() || rd32(g_mem, LANG_INDEX) != RUSSIAN_LANGUAGE_ID) {
        o_006d9e50();
        return;
    }

    char old_name[15];
    memcpy(old_name, g_mem + MATCH_EVENT_FILENAME, sizeof old_name);
    uint32_t old_language = rd32(g_mem, LANG_INDEX);
    wr32(g_mem, LANG_INDEX, 1);
    memcpy(g_mem + MATCH_EVENT_FILENAME, "events_rus.cfg", sizeof "events_rus.cfg");
    o_006d9e50();
    if (!rt_unwinding) {
        memcpy(g_mem + MATCH_EVENT_FILENAME, old_name, sizeof old_name);
        wr32(g_mem, LANG_INDEX, old_language);
        wr32(g_mem, MATCH_EVENT_LANGUAGE, RUSSIAN_LANGUAGE_ID);
    }
}


/* The database's old name-file switch knows only IDs 0..12. ID 13 uses the English
 * branch's path slot, temporarily pointed at rus.lng. Missing rus.lng deliberately
 * falls back to eng.lng rather than raising the original database error box. */
RT_WRAP(005339a0, russian_database_names)
{
    uint32_t language_at = cpu.esp + 4u;
    uint32_t requested = rd32(g_mem, language_at);
    if (requested != RUSSIAN_LANGUAGE_ID) {
        o_005339a0();
        return;
    }

    uint32_t old_language = rd32(g_mem, 0x009b5984u);
    uint32_t old_arg = requested;
    char old_name[8];
    memcpy(old_name, g_mem + 0x009b632cu, sizeof old_name);
    wr32(g_mem, language_at, 1);
    if (localisation_russian_names_available())
        memcpy(g_mem + 0x009b632cu, "rus.lng", sizeof "rus.lng");
    o_005339a0();
    if (!rt_unwinding) {
        wr32(g_mem, language_at, old_arg);
        memcpy(g_mem + 0x009b632cu, old_name, sizeof old_name);
        /* Keep 13 as the public name-language marker so switching back to System reloads. */
        wr32(g_mem, 0x009b5984u, RUSSIAN_LANGUAGE_ID);
        (void)old_language;
    }
}

/* The separate availability check has the same fixed switch. */
RT_WRAP(00535930, russian_database_name_exists)
{
    uint32_t arg_at = cpu.esp + 4u;
    uint32_t requested = rd32(g_mem, arg_at);
    if (requested != RUSSIAN_LANGUAGE_ID) {
        o_00535930();
        return;
    }
    char old_name[8];
    memcpy(old_name, g_mem + 0x009b632cu, sizeof old_name);
    wr32(g_mem, arg_at, 1);
    if (localisation_russian_names_available())
        memcpy(g_mem + 0x009b632cu, "rus.lng", sizeof "rus.lng");
    o_00535930();
    if (!rt_unwinding) {
        wr32(g_mem, arg_at, requested);
        memcpy(g_mem + 0x009b632cu, old_name, sizeof old_name);
    }
}
