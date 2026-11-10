# Russian localisation style guide

## Language and tone

- Write concise, natural Russian used by football managers, coaches, journalists and supporters.
- Prefer familiar football terms over literal English calques. Match the period and vocabulary of CM 01/02 rather than modern football-business jargon where it feels anachronistic.
- Keep labels short enough for the original UI. Use a full phrase only when a shorter term would be unclear.
- Use sentence case for ordinary labels; preserve uppercase only where the original uses it for a status or emphasis.
- Do not add exclamation marks or extra punctuation for tone.

## Core glossary

| English | Approved Russian | Notes |
|---|---|---|
| Manager | менеджер | The player-controlled club manager |
| Club | клуб | |
| Squad | состав | The first-team squad, not a roster list |
| First Team | основная команда | |
| Reserve Team | резервная команда | |
| Youth Team | молодёжная команда | |
| Player | игрок | |
| Staff | персонал | People employed by the club |
| Coach | тренер | |
| Assistant Manager | помощник главного тренера | Use «ассистент» only where space is tight |
| Ball-winner | полузащитник-разрушитель | A midfield role focused on winning possession |
| Scout | скаут | |
| Physio | физиотерапевт | |
| Transfer | трансфер | |
| Transfer Listed | выставлен на трансфер | |
| Loan | аренда | As a verb: «отдать в аренду» / «взять в аренду» by direction |
| Contract | контракт | |
| Wage | зарплата | Weekly wage in the game |
| Fee | сумма трансфера | |
| Bid | предложение | Transfer bid |
| Offer | предложение | Use context to distinguish a bid from a contract offer |
| League | лига | |
| Cup | кубок | |
| Fixture | матч / календарь | Use «матч» for one game, «календарь» for the schedule |
| Tactics | тактика | |
| Formation | схема | |
| Team Instructions | командные установки | |
| Passing | пас | Attribute/context dependent |
| Work Rate | работоспособность | Player attribute |
| Stamina | выносливость | Player attribute |
| Condition | физическое состояние | Short UI label may be «состояние» |
| Morale | моральное состояние | Short UI label may be «мораль» |
| Fitness | физическая готовность | |
| Injury | травма | |
| Suspension | дисквалификация | |
| Scout Report | отчёт скаута | |
| News | новости | |
| Inbox | входящие | |
| Continue | продолжить | Button/action |
| Holiday | отпуск | The game's time-advance mode, not annual leave |
| Retire | завершить карьеру | |
| Chairman | председатель | Club chairman; do not use «владелец» automatically |
| Board | руководство | |
| Fans | болельщики | |
| Attendance | посещаемость | |
| Reputation | репутация | |
| Nationality | гражданство / национальность | Context determines player nationality vs national team |

## Names and proper nouns — strict preservation rule

- Preserve every database identity exactly as supplied: player and staff names, club names, city names, stadium names, country/nation names, and competition/tournament names. Do not translate, transliterate, respell, or normalise them.
- This rule applies even when a proper name contains an ordinary English word such as “United”, “City”, “County”, “Town”, “League” or “Cup”.
- Translate only generic interface labels and controls such as “League”, “Cup”, “Nation”, “Club”, “Stadium” or “Competition” when they are labels rather than the actual database value.
- Preserve database abbreviations, short codes, IDs, and source spelling byte-for-byte.
- News prose and match commentary are not part of the current interface-only localisation scope.

## Interface wording

- Translate menu items, buttons, tabs, settings, dialogs, screen headings, actions, tactical labels, formations, positions, roles, attributes and statuses.
- Keep one approved Russian equivalent for each concept across all screens. Record context-specific exceptions in the glossary rather than silently varying terminology.

## Grammar and formatting

- Keep every printf placeholder and its argument order unchanged.
- Keep game tags, note delimiters, colour/control codes and leading spaces exactly unless a reviewed rule explicitly says otherwise.
- Prefer rephrasing to avoid grammatical agreement around dynamic names when the formatter cannot inflect them.
- Where Russian plural forms are needed, use an explicit plural rule or neutral wording; do not rely on English singular/plural logic.
- Check long forms in context, especially case endings after club/player names.
- Keep deliberate line breaks. Never split a placeholder or a game tag across lines.

## Review checklist

- Does the phrase sound like football Russian rather than translated software copy?
- Is the meaning correct in the actual screen and surrounding sentence?
- Are placeholders and markup byte-for-byte intact?
- Does the text fit the original width at all font sizes?
- Are names, competition terms and abbreviations consistent with the glossary?
