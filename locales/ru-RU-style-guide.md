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

## Names and proper nouns

- Preserve player and club names exactly as supplied by the active database. Do not silently transliterate names.
- Translate generic competition words (League, Cup, Championship) while preserving official sponsor/brand names.
- Country names use established Russian exonyms (England — Англия, Holland — Нидерланды, Germany — Германия).
- City and stadium names follow the official Russian spelling when one is established; otherwise use a consistent practical transliteration.
- Awards use a translated generic title but retain a proper-name honouree.
- Do not change database identifiers, abbreviations, short codes or IDs.

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
